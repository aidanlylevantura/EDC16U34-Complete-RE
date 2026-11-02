import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

target1 = struct.pack(">I", 0x81BFF1)
target2 = struct.pack(">I", 0x81BF10)

print("File size:", len(d))

print("\nSearching for 0x81BFF1...")
for i in range(0, len(d) - 4):
    if d[i:i+4] == target1:
        print(f"  Found at 0x{i:06X}")
        start = max(0, i-8)
        end = min(len(d), i+24)
        print("  Context:", d[start:end].hex().upper())

print("\nSearching for 0x81BF10...")
for i in range(0, len(d) - 4):
    if d[i:i+4] == target2:
        print(f"  Found at 0x{i:06X}")
        start = max(0, i-8)
        end = min(len(d), i+24)
        print("  Context:", d[start:end].hex().upper())

print("\nDone.")