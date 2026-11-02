import argparse
import can
import isotp
import os
import sys
import time

# --- CONFIG ---
CAN_INTERFACE = 'slcan'
DEFAULT_PORT = 'COM4'
BITRATE = 500000
ECU_TX_ID = 0x7E0
ECU_RX_ID = 0x7E8

# --- LFSR TABLE ---
LFSR_TABLE = [0x0001C200, 0x0A221289, 0x144890A1, 0x24212491, 0x290A0285, 0x42145091, 0x504822C1, 0x0A24C4C1, 0x14252229, 0x24250525, 0x2510A491, 0x28488863, 0x29148885, 0x422184A5, 0x49128521, 0x50844A85, 0x620CC211, 0x124452A9, 0x18932251, 0x2424A459, 0x29149521, 0x42352621, 0x4A512289, 0x52A48911, 0x11891475, 0x22346523, 0x4A3118D1, 0x64497111, 0x0AE34529, 0x15398989, 0x22324A67, 0x2D12B489, 0x132A4A75, 0x19B13469, 0x25D2C453, 0x4949349B, 0x524E9259, 0x1964CA6B, 0x24F5249B, 0x28979175, 0x352A5959, 0x3A391749, 0x51D44EA9, 0x564A4F25, 0x6AD52649, 0x76493925, 0x25DE52C9, 0x332E9333, 0x68D64997, 0x494947FB, 0x33749ACF, 0x5AD55B5D, 0x7F272A4F, 0x35BD5B75, 0x3F5AD55D, 0x5B5B6DAD, 0x6B5DAD6B, 0x75B57AD5, 0x5DBAD56F, 0x6DBF6AAD, 0x75775EB5, 0x5AEDFED5, 0x6B5F7DD5, 0x6F757B6B]

MAGIC = bytes.fromhex("0521350135")
ID_STRING = b"Bosch.p_213.SwitchOver.EDC16.A000"

def compute_key(seed, subfn, attempt=1):
    iter_count = attempt * 0x23
    idx = (subfn + 1) >> 1
    for _ in range(iter_count):
        msb = seed & 0x80000000
        seed = (seed << 1) & 0xFFFFFFFF
        if msb:
            seed ^= LFSR_TABLE[idx]
    return seed

def add_checksum(data, seed=0xFAFCE69C):
    total = seed
    for i in range(0, len(data), 4):
        chunk = data[i:i+4].ljust(4, b'\xFF')
        w = int.from_bytes(chunk, 'big')
        swapped = ((w & 0xFF) << 24) | ((w & 0xFF00) << 8) | ((w >> 8) & 0xFF00) | (w >> 24)
        total = (total + swapped) & 0xFFFFFFFF
    return total

def fix_flash_checksums(data):
    target = 0xD01FE500
    regions = [(0x180000, 0x1BFFFF, 0x1BFFFC), (0x1C0000, 0x1FDFFF, 0x1FDFFC)]
    for start, end, csum_off in regions:
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

    def unlock(self, subfn=0x01):
        self.send([0x10, 0x03])
        r = self.send([0x27, 0x01])
        if not r or r[0] != 0x67: raise RuntimeError("Seed request failed")
        seed = int.from_bytes(r[2:6], 'big')
        key = compute_key(seed, subfn)
        r = self.send([0x27, 0x02] + list(key.to_bytes(4, 'big')))
        if not r or r[0] != 0x67: raise RuntimeError("Key rejected")
        print("[+] Unlocked")

    def handshake(self):
        payload = MAGIC + bytes([0x30]) + ID_STRING + bytes([0x08]) + (0).to_bytes(4, 'big') + (0).to_bytes(4, 'big')
        msg = [0x31, 0x01, (len(payload) >> 8) & 0xFF, len(payload) & 0xFF] + list(payload)
        r = self.send(msg)
        if not r or r[0] != 0x71: raise RuntimeError("Handshake failed")
        print("[+] Handshake accepted")

# --- SHELLCODE BUILDERS ---
def build_shellcode_read(start_addr, length):
    sc = bytearray()
    sc += b"\x3C\xC0" + (start_addr >> 16).to_bytes(2, 'big')
    sc += b"\x60\xC6" + (start_addr & 0xFFFF).to_bytes(2, 'big')
    end = start_addr + length
    sc += b"\x3C\xE0" + (end >> 16).to_bytes(2, 'big')
    sc += b"\x60\xE7" + (end & 0xFFFF).to_bytes(2, 'big')
    sc += bytes.fromhex("3C807F9260849200") # r4 = 0x7F9200 buffer
    sc += bytes.fromhex("3C600000606307E8") # r3 = 0x7E8 CAN ID
    sc += bytes.fromhex("3CA0000060A500FD") # r5 = 0xFD marker
    loop = len(sc)
    sc += bytes.fromhex("81060000") # lwz r8, 0(r6)
    sc += bytes.fromhex("91040000") # stw r8, 0(r4)
    sc += bytes.fromhex("3D2000006129243C") # lis r9, 0; ori r9, r9, 0x243C
    sc += bytes.fromhex("7D2903A6") # mtctr r9
    sc += bytes.fromhex("4E800421") # bctrl
    sc += bytes.fromhex("38C60004") # addi r6, r6, 4
    sc += bytes.fromhex("7C063800") # cmpw r6, r7
    off = loop - (len(sc) + 4)
    sc += (0x41800000 | (off & 0xFFFF)).to_bytes(4, 'big') # blt loop
    sc += bytes.fromhex("4E800020") # blr
    return bytes(sc)

def build_shellcode_write(start_addr, length):
    # This shellcode will overwrite target with 0xAA (test pattern)
    # For EEPROM writing, this would need to be replaced with SPI commands
    sc = bytearray()
    sc += b"\x3C\xC0" + (start_addr >> 16).to_bytes(2, 'big')
    sc += b"\x60\xC6" + (start_addr & 0xFFFF).to_bytes(2, 'big')
    end = start_addr + length
    sc += b"\x3C\xE0" + (end >> 16).to_bytes(2, 'big')
    sc += b"\x60\xE7" + (end & 0xFFFF).to_bytes(2, 'big')
    sc += bytes.fromhex("3D0000006108AAAA") # r8 = 0xAAAA (test pattern)
    loop = len(sc)
    sc += bytes.fromhex("91060000") # stw r8, 0(r6)
    sc += bytes.fromhex("38C60004") # addi r6, r6, 4
    sc += bytes.fromhex("7C063800") # cmpw r6, r7
    off = loop - (len(sc) + 4)
    sc += (0x41800000 | (off & 0xFFFF)).to_bytes(4, 'big') # blt loop
    sc += bytes.fromhex("4E800020") # blr
    return bytes(sc)

def build_payload(shellcode):
    buf = bytearray([0xFF] * 0x3FFC)
    uVar6 = 0x80
    buf[0] = uVar6
    buf[1] = ((uVar6 >> 4) | ((uVar6 & 0xF) << 4)) & 0xFF
    buf[2] = ((uVar6 >> 2) | ((uVar6 & 3) << 6)) & 0xFF
    buf[3] = 0x36
    buf[4:8] = (0x7F9808).to_bytes(4, 'big')
    buf[8:8+len(shellcode)] = shellcode
    target = 0xF7EAB8EE
    current = add_checksum(buf)
    delta = (target - current) & 0xFFFFFFFF
    swapped = ((delta & 0xFF) << 24) | ((delta & 0xFF00) << 8) | ((delta >> 8) & 0xFF00) | (delta >> 24)
    buf[-4:] = swapped.to_bytes(4, 'big')
    return bytes(buf)

# --- ACTIONS ---
def do_read(conn, target, filename):
    targets = {
        'flash': (0x00000000, 0x200000),
        'micro': (0x00000000, 0x80000), # External flash bootloader region
        'eeprom': (0x00000000, 0x1000)
    }
    base, size = targets[target]
    print(f"[*] Reading {target} @ 0x{base:08X} ({size} bytes)")
    conn.unlock()
    conn.handshake()
    sc = build_shellcode_read(base, size)
    payload = build_payload(sc)
    msg = [0x36, 0x00, (len(payload) >> 8) & 0xFF, len(payload) & 0xFF] + list(payload)
    conn.send(msg, timeout=2.0)
    
    received = bytearray()
    end_time = time.time() + 30.0
    while len(received) < size and time.time() < end_time:
        conn.stack.process()
        if conn.stack.available():
            resp = conn.stack.recv()
            if len(resp) >= 5:
                received.extend(resp[-4:])
        time.sleep(0.001)
    
    if len(received) >= size:
        with open(filename, 'wb') as f: f.write(received)
        print(f"[+] Saved {len(received)} bytes to {filename}")
    else:
        print(f"[-] Only received {len(received)} bytes")

def do_write(conn, target, filename):
    if target == 'flash':
        with open(filename, 'rb') as f: data = bytearray(f.read())
        fix_flash_checksums(data)
        conn.unlock()
        conn.handshake()
        block_size = 0x1000
        for addr in range(0, len(data), block_size):
            block = data[addr:addr+block_size]
            setup = MAGIC + bytes([0x31]) + (addr).to_bytes(4, 'big') + (block_size).to_bytes(4, 'big') + bytes(34)
            conn.send([0x31, 0x01, 0x00, 0x30] + list(setup))
            for i in range(0, block_size, 42):
                chunk = block[i:i+42].ljust(42, b'\xFF')
                conn.send([0x31, 0x01, 0x00, 0x30] + list(MAGIC + bytes([0x32]) + chunk))
            finish = MAGIC + bytes([0x33]) + bytes(44)
            conn.send([0x31, 0x01, 0x00, 0x32] + list(finish))
            if addr % 0x10000 == 0: print(f"    {addr//0x1000} blocks")
        print("[+] Flash write complete")
    else:
        # RAM Injection Write
        with open(filename, 'rb') as f: data = f.read()
        conn.unlock()
        conn.handshake()
        print(f"[*] Injecting write shellcode for {target}...")
        sc = build_shellcode_write(0x00000000, len(data)) # Example: Writing 0xAA
        payload = build_payload(sc)
        msg = [0x36, 0x00, (len(payload) >> 8) & 0xFF, len(payload) & 0xFF] + list(payload)
        conn.send(msg, timeout=2.0)
        print("[+] Write payload executed.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default=DEFAULT_PORT)
    parser.add_argument('--action', choices=['read','write'], required=True)
    parser.add_argument('--target', choices=['flash','micro','eeprom'], required=True)
    parser.add_argument('--file', required=True)
    args = parser.parse_args()
    
    conn = CANConnection(args.port)
    if args.action == 'read': do_read(conn, args.target, args.file)
    else: do_write(conn, args.target, args.file)

if __name__ == '__main__':
    main()