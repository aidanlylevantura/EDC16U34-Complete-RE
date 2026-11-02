import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

def dump(addr, length, label):
    print(f"\n{label} @ 0x{addr:06X} ({length} bytes)")
    chunk = d[addr:addr+length]
    print(f"  HEX:   {chunk.hex().upper()}")
    print(f"  ASCII: {''.join(chr(b) if 32<=b<127 else '.' for b in chunk)}")

# Primary target from the decompile
dump(0x7FC0, 32, "Signature @ 0x7FC0 (12 bytes + context)")

# SDA candidates - try different r14 bases
for r14 in [0x7F8000, 0x800000, 0x7F0000, 0x8000]:
    sda_14 = r14 - 0x7205
    sda_4 = r14 - 0x71F7
    if 0 <= sda_14 < len(d):
        dump(sda_14, 16, f"SDA 14-byte constant (r14=0x{r14:08X}, addr=0x{sda_14:06X})")
    if 0 <= sda_4 < len(d):
        dump(sda_4, 8, f"SDA 4-byte constant (r14=0x{r14:08X}, addr=0x{sda_4:06X})")

# Also check what's at 0x168 and 0x3FBB0 to confirm the RSA key structures
dump(0x168, 16, "Alternate key pointer target")
dump(0x3FBB0, 32, "Primary RSA key header")