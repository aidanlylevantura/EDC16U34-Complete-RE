import argparse
import can
import isotp
import os
import time
import sys

# --- CONFIG ---
CAN_INTERFACE = 'slcan'
DEFAULT_PORT = 'COM4'
BITRATE = 500000
ECU_TX_ID = 0x7E0
ECU_RX_ID = 0x7E8

# --- LFSR POLYNOMIAL TABLE ---
LFSR_TABLE = [
    0x0001C200, 0x0A221289, 0x144890A1, 0x24212491, 0x290A0285, 0x42145091, 0x504822C1, 0x0A24C4C1,
    0x14252229, 0x24250525, 0x2510A491, 0x28488863, 0x29148885, 0x422184A5, 0x49128521, 0x50844A85,
    0x620CC211, 0x124452A9, 0x18932251, 0x2424A459, 0x29149521, 0x42352621, 0x4A512289, 0x52A48911,
    0x11891475, 0x22346523, 0x4A3118D1, 0x64497111, 0x0AE34529, 0x15398989, 0x22324A67, 0x2D12B489,
    0x132A4A75, 0x19B13469, 0x25D2C453, 0x4949349B, 0x524E9259, 0x1964CA6B, 0x24F5249B, 0x28979175,
    0x352A5959, 0x3A391749, 0x51D44EA9, 0x564A4F25, 0x6AD52649, 0x76493925, 0x25DE52C9, 0x332E9333,
    0x68D64997, 0x494947FB, 0x33749ACF, 0x5AD55B5D, 0x7F272A4F, 0x35BD5B75, 0x3F5AD55D, 0x5B5B6DAD,
    0x6B5DAD6B, 0x75B57AD5, 0x5DBAD56F, 0x6DBF6AAD, 0x75775EB5, 0x5AEDFED5, 0x6B5F7DD5, 0x6F757B6B
]

MAGIC = bytes.fromhex("0521350135")
ID_STRING = b"Bosch.p_213.SwitchOver.EDC16.A000"

# --- TARGET DEFINITIONS ---
TARGETS = {
    'flash': {'base': 0x00000000, 'size': 0x200000, 'block_size': 0x1000},
    'micro': {'base': 0x00000000, 'size': 0x80000,  'block_size': 0x1000},
    'eeprom': {'base': 0x00100000, 'size': 0x1000,  'block_size': 0x0100}
}

# EEPROM base candidates for auto-detection
EEPROM_BASES = [0x00100000, 0x00000000, 0x00040000, 0x00080000, 0x001C0000, 0x001F0000]

def compute_key(seed, subfn, attempt=1):
    iter_count = attempt * 0x23
    idx = (subfn + 1) >> 1
    for _ in range(iter_count):
        msb = seed & 0x80000000
        seed = (seed << 1) & 0xFFFFFFFF
        if msb:
            seed ^= LFSR_TABLE[idx]
    return seed

def fix_flash_checksums(data):
    target = 0xD01FE500
    regions = [(0x180000, 0x1BFFFF, 0x1BFFFC), (0x1C0000, 0x1FDFFF, 0x1FDFFC)]
    for start, end, csum_off in regions:
        if end >= len(data): continue
        total = sum(int.from_bytes(data[i:i+4], 'big') for i in range(start, end+1, 4)) & 0xFFFFFFFF
        if total != target:
            delta = (target - total) & 0xFFFFFFFF
            old = int.from_bytes(data[csum_off:csum_off+4], 'big')
            new = (old + delta) & 0xFFFFFFFF
            data[csum_off:csum_off+4] = new.to_bytes(4, 'big')

class CANConnection:
    def __init__(self, port):
        self.bus = can.interface.Bus(bustype=CAN_INTERFACE, channel=port, bitrate=BITRATE)
        addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=ECU_TX_ID, rxid=ECU_RX_ID)
        self.stack = isotp.CanStack(bus=self.bus, address=addr, params={'blocking_send': True})

    def send(self, payload, timeout=1.0):
        self.stack.send(bytearray(payload))
        end = time.time() + timeout
        while time.time() < end:
            self.stack.process()
            if self.stack.available():
                return self.stack.recv()
            time.sleep(0.001)
        return None

    def unlock(self):
        self.send([0x10, 0x03])
        r = self.send([0x27, 0x01])
        if not r or r[0] != 0x67: 
            raise RuntimeError("Seed request failed")
        seed = int.from_bytes(r[2:6], 'big')
        key = compute_key(seed, 0x01)
        r = self.send([0x27, 0x02] + list(key.to_bytes(4, 'big')))
        if not r or r[0] != 0x67: 
            raise RuntimeError("Key rejected")
        print("[+] Unlocked LVL1")

    def auto_detect_eeprom_base(self):
        print("[*] Probing EEPROM base address...")
        for base in EEPROM_BASES:
            payload = (MAGIC + bytes([0x30]) + ID_STRING + bytes([0x08]) +
                       base.to_bytes(4, 'big') + (0x1000).to_bytes(4, 'big'))
            msg = [0x31, 0x01, (len(payload) >> 8) & 0xFF, len(payload) & 0xFF] + list(payload)
            resp = self.send(msg, timeout=1.0)
            if resp and resp[0] == 0x71:
                print(f"[+] EEPROM found at 0x{base:08X}")
                return base
            print(f"    - 0x{base:08X} rejected")
        raise RuntimeError("Could not find EEPROM base.")

    def handshake(self, target_name):
        t = TARGETS[target_name]
        base = t['base']
        size = t['size']

        if target_name == 'eeprom':
            base = self.auto_detect_eeprom_base()
            TARGETS['eeprom']['base'] = base

        payload = (MAGIC + bytes([0x30]) + ID_STRING + bytes([0x08]) +
                   base.to_bytes(4, 'big') + size.to_bytes(4, 'big'))
        msg = [0x31, 0x01, (len(payload) >> 8) & 0xFF, len(payload) & 0xFF] + list(payload)
        
        r = self.send(msg)
        if not r or r[0] != 0x71: 
            raise RuntimeError("Handshake failed")
        print(f"[+] Handshake accepted for {target_name}")

def do_read(conn, target, filename):
    print(f"\n[*] Reading {target}...")
    conn.unlock()
    conn.handshake(target)
    
    base = TARGETS[target]['base']
    size = TARGETS[target]['size']
    block_size = TARGETS[target]['block_size']
    received = bytearray()
    
    print(f"[*] Starting data stream from 0x{base:08X} ({size} bytes)...")
    start_time = time.time()

    for addr in range(base, base + size, block_size):
        # Setup 0x31
        setup = MAGIC + bytes([0x31]) + addr.to_bytes(4, 'big') + block_size.to_bytes(4, 'big') + bytes(34)
        conn.send([0x31, 0x01, 0x00, 0x30] + list(setup))
        
        # Read 0x32 (Request data)
        read_req = MAGIC + bytes([0x32]) + bytes(42)
        resp = conn.send([0x31, 0x01, 0x00, 0x30] + list(read_req), timeout=2.0)
        
        if resp and len(resp) > 4:
            received.extend(resp[4:])
        else:
            print(f"[-] Read failed at 0x{addr:06X}")
            break
            
        # Finish 0x33
        finish = MAGIC + bytes([0x33]) + bytes(44)
        conn.send([0x31, 0x01, 0x00, 0x32] + list(finish))
        
        # Progress
        if (addr - base) % 0x1000 == 0:
            percent = ((addr - base + block_size) / size) * 100
            elapsed = time.time() - start_time
            speed = (addr - base) / elapsed / 1024 if elapsed > 0 else 0
            print(f"    {percent:.1f}% ({addr:08X}) | {speed:.1f} KB/s")
        
    if len(received) >= size:
        with open(filename, 'wb') as f: 
            f.write(received[:size])
        print(f"[+] Saved {size} bytes to {filename}")
    else:
        print(f"[-] Only received {len(received)} bytes. File may be truncated.")

def do_write(conn, target, filename):
    with open(filename, 'rb') as f: 
        data = bytearray(f.read())
    
    if target == 'flash': 
        fix_flash_checksums(data)
    
    conn.unlock()
    conn.handshake(target)
    
    base = TARGETS[target]['base']
    size = TARGETS[target]['size']
    block_size = TARGETS[target]['block_size']
    
    print(f"\n[*] Writing {len(data)} bytes to {target}...")
    start_time = time.time()
    
    for addr_offset in range(0, len(data), block_size):
        block = data[addr_offset:addr_offset+block_size]
        if len(block) < block_size: 
            block += bytes([0xFF] * (block_size - len(block)))
            
        target_addr = base + addr_offset
        
        # Setup 0x31
        setup = MAGIC + bytes([0x31]) + target_addr.to_bytes(4, 'big') + block_size.to_bytes(4, 'big') + bytes(34)
        conn.send([0x31, 0x01, 0x00, 0x30] + list(setup))
        
        # Write Data 0x32
        for i in range(0, block_size, 42):
            chunk = block[i:i+42]
            conn.send([0x31, 0x01, 0x00, 0x30] + list(MAGIC + bytes([0x32]) + chunk))
            
        # Finish 0x33
        finish = MAGIC + bytes([0x33]) + bytes(44)
        conn.send([0x31, 0x01, 0x00, 0x32] + list(finish))
        
        # Progress
        if addr_offset % 0x1000 == 0:
            percent = ((addr_offset + block_size) / len(data)) * 100
            elapsed = time.time() - start_time
            speed = addr_offset / elapsed / 1024 if elapsed > 0 else 0
            print(f"    {percent:.1f}% ({target_addr:08X}) | {speed:.1f} KB/s")
        
    print("[+] Write complete")

def main():
    parser = argparse.ArgumentParser(description="EDC16U34 Full Read/Write Tool")
    parser.add_argument('--port', default=DEFAULT_PORT, help='CANable COM port (e.g. COM4)')
    parser.add_argument('--action', choices=['read','write'], required=True, help='Action to perform')
    parser.add_argument('--target', choices=['flash','micro','eeprom'], required=True, help='Memory area')
    parser.add_argument('--file', required=True, help='Path to binary file')
    args = parser.parse_args()
    
    conn = CANConnection(args.port)
    try:
        if args.action == 'read': 
            do_read(conn, args.target, args.file)
        else: 
            do_write(conn, args.target, args.file)
    except Exception as e:
        print(f"\n[-] ERROR: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()