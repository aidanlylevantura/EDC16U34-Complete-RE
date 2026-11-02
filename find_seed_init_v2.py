import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

print("=== Search 1: lis rX, 0x7FD9 (any following instruction) ===")
for i in range(0, len(d) - 16, 4):
    w1 = struct.unpack(">I", d[i:i+4])[0]
    # lis (addis) opcode 15, RA=0
    if ((w1 >> 26) & 0x3F) == 15 and ((w1 >> 16) & 0x1F) == 0:
        rd = (w1 >> 21) & 0x1F
        if (w1 & 0xFFFF) == 0x7FD9:
            print(f"\n[+] Found lis r{rd}, 0x7FD9 at 0x{i:06X}")
            # Print next 4 instructions to see how it's used
            for j in range(i, i+20, 4):
                w2 = struct.unpack(">I", d[j:j+4])[0]
                print(f"    0x{j:06X}: {w2:08X}")

print("\n=== Search 2: addi rX, r13, 0x59A8 (offset from SDA base) ===")
# If r13 is ~0x7F8000, then 0x7FD9A8 - 0x7F8000 = 0x59A8
for i in range(0, len(d) - 8, 4):
    w1 = struct.unpack(">I", d[i:i+4])[0]
    if ((w1 >> 26) & 0x3F) == 14: # addi
        ra = (w1 >> 16) & 0x1F
        imm = w1 & 0xFFFF
        rd = (w1 >> 21) & 0x1F
        if ra == 13 and imm == 0x59A8:
            print(f"  Found at 0x{i:06X}: addi r{rd}, r13, 0x59A8")