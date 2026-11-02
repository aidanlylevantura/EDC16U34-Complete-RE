import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

target_hi = 0x7FD9
target_lo = 0xA9A8

print(f"Searching for initialization of 0x{target_hi:04X}{target_lo:04X}...")

for i in range(0, len(d) - 16, 4):
    w1 = struct.unpack(">I", d[i:i+4])[0]
    w2 = struct.unpack(">I", d[i+4:i+8])[0]

    # Look for lis rX, 0x7FD9 (opcode 15, RA=0)
    if ((w1 >> 26) & 0x3F) == 15 and ((w1 >> 16) & 0x1F) == 0:
        rd = (w1 >> 21) & 0x1F
        if (w1 & 0xFFFF) == target_hi:
            # Look for ori rX, rX, 0xA9A8 (opcode 24) or addi rX, rX, 0xA9A8
            op2 = (w2 >> 26) & 0x3F
            ra2 = (w2 >> 16) & 0x1F
            rd2 = (w2 >> 21) & 0x1F
            if op2 in (14, 24) and ra2 == rd and rd2 == rd and (w2 & 0xFFFF) == target_lo:
                print(f"\n[+] Found address construction at 0x{i:06X}:")
                print(f"    0x{w1:08X} lis r{rd}, 0x{target_hi:04X}")
                print(f"    0x{w2:08X} {'ori' if op2==24 else 'addi'} r{rd}, r{rd}, 0x{target_lo:04X}")
                
                # Print the next 6 instructions to see what happens (store/load)
                for j in range(i+8, i+32, 4):
                    w3 = struct.unpack(">I", d[j:j+4])[0]
                    print(f"    0x{j:06X}  {w3:08X}")