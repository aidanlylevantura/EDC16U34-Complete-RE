import re

PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\Golf_KH_BDM\Eeprom.bin"
d = open(PATH, "rb").read()

def dump(name, off, n=64):
    print("\n--- %s @ 0x%04X ---" % (name, off))
    for i in range(off, min(off+n, len(d)), 16):
        row = d[i:i+16]
        hx = " ".join("%02X" % x for x in row)
        asc = "".join(chr(x) if 0x20 <= x <= 0x7E else "." for x in row)
        print("0x%04X  %-47s  %s" % (i, hx, asc))

def xor8(b):
    x=0
    for v in b: x ^= v
    return x & 0xFF

def sum8(b): return sum(b) & 0xFF
def sum16be(b): return sum(int.from_bytes(b[i:i+2],"big") for i in range(0,len(b)-1,2)) & 0xFFFF
def sum16le(b): return sum(int.from_bytes(b[i:i+2],"little") for i in range(0,len(b)-1,2)) & 0xFFFF

def crc16_ccitt(b, init=0xFFFF):
    crc=init
    for v in b:
        crc ^= v << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc

def crc16_xmodem(b, init=0x0000):
    return crc16_ccitt(b, init)

def hex2(v): return "0x%02X" % v
def hex4(v): return "0x%04X" % v

# Dump key regions
dump("Header", 0x0000, 0x40)
dump("ECU ID block", 0x0040, 0x80)
dump("PIN + FIN/IMMO block", 0x00E0, 0xA0)
dump("VIN block", 0x0140, 0x80)
dump("Record region start", 0x0200, 0x60)
dump("Tail", 0x0F00, 0x100)

print("\n=== Candidate checksum match search after known blocks ===")
blocks = [
    ("ECU ID A", 0x0066, 34),
    ("IMMO A", 0x00EC, 14),
    ("VIN A", 0x0145, 17),
    ("VIN B", 0x0165, 17),
]

for name, off, n in blocks:
    body = d[off:off+n]
    end = off+n
    window = d[end:end+16]
    cands = {
        "xor8": xor8(body),
        "sum8": sum8(body),
        "sum16be": sum16be(body),
        "sum16le": sum16le(body),
        "crc16ccitt": crc16_ccitt(body),
        "crc16xmodem": crc16_xmodem(body),
    }
    print("\n%s @ 0x%04X end=0x%04X" % (name, off, end))
    print("  window after:", window.hex())
    for k, v in cands.items():
        # search 1- or 2-byte representation in window, both endian
        b1 = bytes([v & 0xFF]) if k in ("xor8","sum8") else None
        b2be = v.to_bytes(2,"big") if k not in ("xor8","sum8") else None
        b2le = v.to_bytes(2,"little") if k not in ("xor8","sum8") else None
        found = []
        if b1 and b1 in window:
            found.append("as byte at +%d" % window.find(b1))
        if b2be and b2be in window:
            found.append("as BE16 at +%d" % window.find(b2be))
        if b2le and b2le in window:
            found.append("as LE16 at +%d" % window.find(b2le))
        print("  %-12s = %s %s" % (k, hex4(v) if v>0xFF else hex2(v), found))

print("\n=== Check tail vs body checksums ===")
body = d[:-16]
tail = d[-16:]
print("tail:", tail.hex())
print("body xor8=0x%02X sum8=0x%02X sum16be=0x%04X sum16le=0x%04X crc16ccitt=0x%04X" % (
    xor8(body), sum8(body), sum16be(body), sum16le(body), crc16_ccitt(body)))
print("tail first 8 as BE32:", " ".join("0x%08X" % int.from_bytes(tail[i:i+4],"big") for i in range(0,8,4)))