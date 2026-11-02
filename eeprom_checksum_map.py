import struct

PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\Golf_KH_BDM\Eeprom.bin"
d = open(PATH, "rb").read()

print("=== EEPROM checksum / duplicate map ===")
print("Size:", len(d))

# Known duplicate blocks from the image
blocks = [
    ("VIN copy A",  0x0145, 17),
    ("VIN copy B",  0x0165, 17),
    ("IMMO copy A", 0x00EC, 14),
    ("IMMO copy B", 0x010C, 14),
    ("IMMO copy C", 0x012C, 14),
    ("ECU ID A",    0x0066, 34),
    ("ECU ID B",    0x00A6, 34),
]

for name, off, n in blocks:
    b = d[off:off+n]
    print("%-12s 0x%04X  %s" % (name, off, b.hex()))

print("\n=== Copy comparisons ===")
print("VIN A == VIN B:", d[0x145:0x156] == d[0x165:0x176])
print("IMMO A == B:", d[0xEC:0xFA] == d[0x10C:0x11A])
print("IMMO A == C:", d[0xEC:0xFA] == d[0x12C:0x13A])
print("ECU ID A == B:", d[0x66:0x88] == d[0xA6:0xC8])

# Checksum calculations
def xor_block(b):
    x = 0
    for v in b: x ^= v
    return x

def sum8(b): return sum(b) & 0xFF
def sum16_be(b): return sum(int.from_bytes(b[i:i+2], "big") for i in range(0, len(b)-1, 2)) & 0xFFFF
def sum16_le(b): return sum(int.from_bytes(b[i:i+2], "little") for i in range(0, len(b)-1, 2)) & 0xFFFF

print("\n=== Block checksums ===")
for name, off, n in blocks:
    b = d[off:off+n]
    print("%-12s xor=0x%02X sum8=0x%02X sum16be=0x%04X sum16le=0x%04X" %
          (name, xor_block(b), sum8(b), sum16_be(b), sum16_le(b)))

print("\n=== Whole-EEPROM checksums (excluding trailing 16 bytes) ===")
body = d[:-16]
tail = d[-16:]
print("tail:", tail.hex())
print("body xor=0x%02X sum8=0x%02X sum16be=0x%04X sum16le=0x%04X" %
      (xor_block(body), sum8(body), sum16_be(body), sum16_le(body)))

print("\n=== Head 8 words ===")
for i in range(0, 8):
    print("0x%04X  u16be=0x%04X  u16le=0x%04X  u32be=0x%08X" %
          (i*4,
           int.from_bytes(d[i*4:i*4+2], "big"),
           int.from_bytes(d[i*4:i*4+2], "little"),
           int.from_bytes(d[i*4:i*4+4], "big")))

print("\n=== Non-FF/00 byte ranges in 0x200-0xF00 ===")
runs = []
start = None
for i in range(0x200, 0xF00):
    b = d[i]
    if b not in (0x00, 0xFF):
        if start is None: start = i
    else:
        if start is not None:
            runs.append((start, i-1)); start = None
if start is not None: runs.append((start, 0xEFF))
for s, e in runs[:40]:
    print("0x%04X-0x%04X  (%d bytes)  %s" % (s, e, e-s+1, d[s:e+1].hex()))