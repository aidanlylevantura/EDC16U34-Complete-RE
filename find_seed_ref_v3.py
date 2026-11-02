import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

print("=== Search 1: Raw Address Bytes (0x7FD9A9A8) ===")
# Look for 7F D9 A9 A8 anywhere in the binary
for i in range(0, len(d) - 4):
    if d[i:i+4] == b'\x7F\xD9\xA9\xA8':
        print(f"  Found raw bytes 7F D9 A9 A8 at 0x{i:06X}")

print("\n=== Search 2: lis rX, 0x7FDA (for signed addi) ===")
for i in range(0, len(d) - 16, 4):
    w1 = struct.unpack(">I", d[i:i+4])[0]
    if ((w1 >> 26) & 0x3F) == 15 and ((w1 >> 16) & 0x1F) == 0:
        rd = (w1 >> 21) & 0x1F
        if (w1 & 0xFFFF) == 0x7FDA:
            w2 = struct.unpack(">I", d[i+4:i+8])[0]
            op2 = (w2 >> 26) & 0x3F
            ra2 = (w2 >> 16) & 0x1F
            imm = w2 & 0xFFFF
            if op2 in (14, 24) and ra2 == rd:
                print(f"  0x{i:06X}: lis r{rd}, 0x7FDA -> {op2} imm 0x{imm:04X}")

print("\n=== Search 3: addi/ori with offset 0xA9A8 or -0x5658 ===")
for i in range(0, len(d) - 4, 4):
    w = struct.unpack(">I", d[i:i+4])[0]
    op = (w >> 26) & 0x3F
    if op in (14, 24):
        imm = w & 0xFFFF
        ra = (w >> 16) & 0x1F
        rd = (w >> 21) & 0x1F
        if imm == 0xA9A8:
            print(f"  0x{i:06X}: op {op} r{rd}, r{ra}, 0xA9A8")
        elif imm == 0x5658:
            print(f"  0x{i:06X}: op {op} r{rd}, r{ra}, 0x5658 (-0x5658)")

print("\n=== Search 4: Offset 0x59A8 from base registers (r13, r14, r15) ===")
for i in range(0, len(d) - 4, 4):
    w = struct.unpack(">I", d[i:i+4])[0]
    if ((w >> 26) & 0x3F) == 14: # addi
        imm = w & 0xFFFF
        ra = (w >> 16) & 0x1F
        rd = (w >> 21) & 0x1F
        if imm == 0x59A8 and ra in (13, 14, 15):
            print(f"  0x{i:06X}: addi r{rd}, r{ra}, 0x59A8")