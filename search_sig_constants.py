import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

print("=== Search 1: Literal 0x61AF3C8E ===")
target1 = struct.pack(">I", 0x61AF3C8E)
for i in range(0, len(d) - 4, 4):
    if d[i:i+4] == target1:
        print(f"  0x{i:06X}: {d[i-8:i+16].hex().upper()}")

print("\n=== Search 2: Literal 0x9E50C371 ===")
target2 = struct.pack(">I", 0x9E50C371)
for i in range(0, len(d) - 4, 4):
    if d[i:i+4] == target2:
        print(f"  0x{i:06X}: {d[i-8:i+16].hex().upper()}")

print("\n=== Search 3: lis/ori building 0x7FC0 ===")
for i in range(0, 0x40000, 4):
    w1 = struct.unpack(">I", d[i:i+4])[0]
    if ((w1 >> 26) & 0x3F) != 15: continue
    if ((w1 >> 16) & 0x1F) != 0: continue
    rd = (w1 >> 21) & 0x1F
    hi = w1 & 0xFFFF
    if hi != 0x0007: continue
    # Look for ori rX, rX, 0xFC0
    w2 = struct.unpack(">I", d[i+4:i+8])[0]
    if ((w2 >> 26) & 0x3F) != 24: continue
    ra2 = (w2 >> 16) & 0x1F
    rd2 = (w2 >> 21) & 0x1F
    lo = w2 & 0xFFFF
    if ra2 == rd and rd2 == rd and lo == 0x0FC0:
        print(f"  0x{i:06X}: lis r{rd},0x0007 ; ori r{rd},r{rd},0x0FC0")
        print(f"    Context: {d[i-8:i+16].hex().upper()}")

print("\n=== Search 4: any 0x0007 high-half loads in bootloader ===")
for i in range(0, 0x40000, 4):
    w = struct.unpack(">I", d[i:i+4])[0]
    if ((w >> 26) & 0x3F) == 15 and ((w >> 16) & 0x1F) == 0:
        if (w & 0xFFFF) == 0x0007:
            rd = (w >> 21) & 0x1F
            print(f"  0x{i:06X}: lis r{rd},0x0007  (context: {d[i:i+8].hex().upper()})")