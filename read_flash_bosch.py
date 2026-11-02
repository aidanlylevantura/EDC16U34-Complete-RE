import can
import isotp
import time
import sys

# --- CONFIGURATION ---
CAN_INTERFACE = 'slcan'
CAN_CHANNEL = 'COM4' # UPDATE THIS
BITRATE = 500000
ECU_TX_ID = 0x7E0
ECU_RX_ID = 0x7E8

TABLE = [0x0001C200, 0x0A221289, 0x144890A1, 0x24212491, 0x290A0285, 0x42145091, 0x504822C1, 0x0A24C4C1, 0x14252229, 0x24250525, 0x2510A491, 0x28488863, 0x29148885, 0x422184A5, 0x49128521, 0x50844A85, 0x620CC211, 0x124452A9, 0x18932251, 0x2424A459, 0x29149521, 0x42352621, 0x4A512289, 0x52A48911, 0x11891475, 0x22346523, 0x4A3118D1, 0x64497111, 0x0AE34529, 0x15398989, 0x22324A67, 0x2D12B489, 0x132A4A75, 0x19B13469, 0x25D2C453, 0x4949349B, 0x524E9259, 0x1964CA6B, 0x24F5249B, 0x28979175, 0x352A5959, 0x3A391749, 0x51D44EA9, 0x564A4F25, 0x6AD52649, 0x76493925, 0x25DE52C9, 0x332E9333, 0x68D64997, 0x494947FB, 0x33749ACF, 0x5AD55B5D, 0x7F272A4F, 0x35BD5B75, 0x3F5AD55D, 0x5B5B6DAD, 0x6B5DAD6B, 0x75B57AD5, 0x5DBAD56F, 0x6DBF6AAD, 0x75775EB5, 0x5AEDFED5, 0x6B5F7DD5, 0x6F757B6B]

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

def main():
    bus = can.interface.Bus(bustype=CAN_INTERFACE, channel=CAN_CHANNEL, bitrate=BITRATE)
    addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=ECU_TX_ID, rxid=ECU_RX_ID)
    stack = isotp.CanStack(bus=bus, address=addr, params={'blocking_send': True})

    def send_uds(payload, description):
        print(f"[TX] {description}: {payload.hex().upper()}")
        stack.send(bytearray(payload))
        timeout = time.time() + 2.0
        while time.time() < timeout:
            stack.process()
            if stack.available():
                resp = stack.recv()
                print(f"[RX] Response: {resp.hex().upper()}")
                return resp
            time.sleep(0.01)
        print("[-] No response.")
        return None

    # 1. Extended Session
    if not send_uds([0x10, 0x03], "Start Session"):
        return

    # 2. Security Access (LVL3)
    resp = send_uds([0x27, 0x03], "Request Seed")
    if not resp or resp[0] != 0x67:
        return
    seed = int.from_bytes(resp[2:6], 'big')
    key = compute_key(seed, 0x03)
    if not send_uds([0x27, 0x04] + list(key.to_bytes(4, 'big')), "Send Key"):
        return

    # 3. Start Routine (0x31 0x01)
    # From the Bosch protocol: 0x31 (Start Routine) prepares for transfer
    send_uds([0x31, 0x01], "Start Routine (Prepare Download)")

    # 4. Request Download (0x34)
    # This sets the address and length. Format: 0x34 <addr_hi> <addr_lo> <len_hi> <len_lo>
    # Example: address 0x000000, length 0x1000 (4096 bytes)
    addr_bytes = (0).to_bytes(4, 'big')
    len_bytes = (0x1000).to_bytes(4, 'big')
    send_uds([0x34] + list(addr_bytes) + list(len_bytes), "Request Download @ 0x000000")

    # 5. Transfer Data (0x37)
    # The EDC16 uses 0x37 for reading block data
    # The response contains the actual flash bytes
    resp = send_uds([0x37], "Read Block")
    if resp:
        # We have the data in the response!
        print(f"[+] Received {len(resp)} bytes of data.")

if __name__ == "__main__":
    main()