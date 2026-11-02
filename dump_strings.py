import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

def dump(addr, name):
    print(f"\n--- {name} @ 0x{addr:06X} ---")
    chunk = d[addr:addr+48]
    print("HEX:", chunk.hex().upper())
    print("ASCII:", "".join(chr(b) if 32 <= b < 127 else '.' for b in chunk))

# Pointers from the lookup table
dump(0x168, "Pointer for 0x81BF10")
dump(0x3FBB0, "Pointer for 0x81BFF1 (Bootloader)")
dump(0x1EDDD0, "Pointer for 0x81BFF1 (External)")