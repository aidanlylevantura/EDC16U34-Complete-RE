import re, math
from collections import Counter

PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\Golf_KH_BDM\Eeprom.bin"

def entropy(b):
    if not b: return 0.0
    c = Counter(b); n = len(b)
    return -sum((v/n) * math.log2(v/n) for v in c.values())

data = open(PATH, "rb").read()
print("Size:", len(data), "bytes")

print("\n--- First 256 bytes hex/ascii ---")
for i in range(0, min(256, len(data)), 16):
    row = data[i:i+16]
    hx = " ".join("%02X" % x for x in row)
    asc = "".join(chr(x) if 0x20 <= x <= 0x7E else "." for x in row)
    print("0x%04X  %-47s  %s" % (i, hx, asc))

print("\n--- 16-bit BE words first 128 bytes ---")
for i in range(0, min(128, len(data)), 2):
    print("0x%04X = 0x%04X" % (i, int.from_bytes(data[i:i+2], "big")))

print("\n--- 32-bit BE words first 128 bytes ---")
for i in range(0, min(128, len(data)), 4):
    print("0x%04X = 0x%08X" % (i, int.from_bytes(data[i:i+4], "big")))

print("\n--- ASCII strings >= 4 ---")
for m in re.finditer(rb"[\x20-\x7E]{4,}", data):
    print("0x%04X  %s" % (m.start(), m.group().decode("ascii", "replace")))

print("\n--- VIN candidates (17 chars, valid VIN alphabet) ---")
vin_re = re.compile(rb"[A-HJ-NPR-Z][A-HJ-NPR-Z0-9]{16}")
for m in vin_re.finditer(data):
    print("0x%04X  %s" % (m.start(), m.group().decode("ascii", "replace")))

print("\n--- 5-7 digit WSC candidates ---")
for m in re.finditer(rb"\d{5,7}", data):
    print("0x%04X  %s" % (m.start(), m.group().decode("ascii", "replace")))

print("\n--- Keywords ---")
for kw in [b"IMMO", b"WFS", b"VIN", b"PIN", b"SEAT", b"WVW", b"VSS", b"KEY", b"EEPROM", b"GOLF"]:
    hits = [m.start() for m in re.finditer(re.escape(kw), data, re.I)]
    print("%-8s %d %s" % (kw.decode(), len(hits), ", ".join("0x%04X" % h for h in hits[:10])))

print("\n--- Entropy per 256-byte block ---")
for i in range(0, len(data), 256):
    b = data[i:i+256]
    h = entropy(b)
    tag = ""
    if h < 3.0: tag = " [sparse/structured]"
    elif h > 7.2: tag = " [high entropy/encrypted?]"
    print("0x%04X  h=%.2f%s" % (i, h, tag))