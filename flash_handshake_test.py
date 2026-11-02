import can
import isotp
import time
import sys

CAN_INTERFACE = 'slcan'
CAN_CHANNEL = 'COM4'  # Update
BITRATE = 500000
ECU_TX_ID = 0x7E0
ECU_RX_ID = 0x7E8

TABLE = [0x0001C200, 0x0A221289, 0x144890A1, 0x24212491, 0x290A0285, 0x42145091, 0x504822C1, 0x0A24C4C1, 0x14252229, 0x24250525, 0x2510A491, 0x28488863, 0x29148885, 0x422184A5, 0x49128521, 0x50844A85, 0x620CC211, 0x124452A9, 0x18932251, 0x2424A459, 0x29149521, 0x42352621, 0x4A512289, 0x52A48911, 0x11891475, 0x22346523, 0x4A3118D1, 0x64497111, 0x0AE34529, 0x15398989, 0x22324A67, 0x2D12B489, 0x132A4A75, 0x19B13469, 0x25D2C453, 0x4949349B, 0x524E9259, 0x1964CA6B, 0x24F5249B, 0x28979175, 0x352A5959, 0x3A391749, 0x51D44EA9, 0x564A4F25, 0x6AD52649, 0x76493925, 0x25DE52C9, 0x332E9333, 0x68D64997, 0x494947FB, 0x33749ACF, 0x5AD55B5D, 0x7F272A4F, 0x35BD5B75, 0x3F5AD55D, 0x5B5B6DAD, 0x6B5DAD6B, 0x75B57AD5, 0x5DBAD56F, 0x6DBF6AAD, 0x75775EB5, 0x5AEDFED5, 0x6B5F7DD5, 0x6F757B6B]

MAGIC_INV = bytes.fromhex("0521350135")
STRING = b"Bosch.p_213.SwitchOver.EDC16.A000"

def compute_key(seed, subfn, attempt=1):
    iter_count = attempt * 0x23
    idx = (subfn + 1) >> 1
    for _ in range(iter_count):
        msb = seed & 0x80000000
        seed = (seed << 1) & 0xFFFFFFFF
        if msb:
            seed ^= TABLE[idx]
    return seed

def main():
    bus = can.interface.Bus(bustype=CAN_INTERFACE, channel=CAN_CHANNEL, bitrate=BITRATE)
    addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=ECU_TX_ID, rxid=ECU_RX_ID)
    stack = isotp.CanStack(bus=bus, address=addr, params={'blocking_send': True})

    def send_uds(payload, desc):
        print(f"\n[TX] {desc}: {payload.hex().upper()}")
        stack.send(bytearray(payload))
        t = time.time() + 3.0
        while time.time() < t:
            stack.process()
            if stack.available():
                r = stack.recv()
                print(f"[RX] {r.hex().upper()}")
                return r
            time.sleep(0.01)
        print("[-] Timeout")
        return None

    # 1. Extended Session
    send_uds([0x10, 0x03], "Start Extended Session")

    # 2. Unlock LVL1 (Write)
    r = send_uds([0x27, 0x01], "Request Seed LVL1")
    if not r or r[0] != 0x67:
        return
    seed = int.from_bytes(r[2:6], 'big')
    key = compute_key(seed, 0x01)
    r = send_uds([0x27, 0x02] + list(key.to_bytes(4, 'big')), "Send Key LVL1")
    if not r or r[0] != 0x67:
        return
    print("[+] LVL1 unlocked")

    # 3. Build 0x30 handshake payload
    handshake = MAGIC_INV + bytes([0x30]) + STRING + bytes([0x00, 0x00])
    print(f"[*] Handshake length: {len(handshake)} bytes")

    # 4. Send via 0x31 RoutineControl with sub 0x01
    total_len = len(handshake)
    payload = [0x31, 0x01, (total_len >> 8) & 0xFF, total_len & 0xFF] + list(handshake)
    r = send_uds(payload, "Bootloader Handshake (0x30)")
    
    if r and r[0] == 0x71:
        print("\n[***] HANDSHAKE ACCEPTED [***]")
    elif r and r[0] == 0x7F:
        nrc = r[2] if len(r) > 2 else 0
        print(f"\n[-] NRC: 0x{nrc:02X}")

if __name__ == "__main__":
    main()