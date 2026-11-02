import sys
import struct

if len(sys.argv) < 2:
    print("Usage: python extract_lfsr.py <path_to_leon_or_full_bdm.bin>")
    sys.exit(1)

path = sys.argv[1]
d = open(path, "rb").read()

print("File:", path)
print("Size:", len(d), "bytes")

if len(d) < 0x2240 + 256:
    print("[-] File is too small to contain the table at 0x2240")
    sys.exit(1)

table = []
for i in range(64):
    off = 0x2240 + i * 4
    val = struct.unpack(">I", d[off:off+4])[0]
    table.append(val)

print("\n=== LFSR polynomial table at 0x2240 (64 x 32-bit BE words) ===")
for i in range(0, 64, 4):
    print(", ".join("0x%08X" % x for x in table[i:i+4]) + ",")

print("\nPython list:")
print("TABLE = [")
for i in range(0, 64, 4):
    print("    " + ", ".join("0x%08X" % x for x in table[i:i+4]) + ",")
print("]")