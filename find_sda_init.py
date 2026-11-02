import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

print("=== Scanning bootloader (0x0-0x10000) for SDA init loops ===")
print("Looking for: lwz rX, offset(rROM) followed by stw rX, offset(rRAM) with RAM in 0x7Fxxxx\n")

# MPC562 registers: r13 = SDA2, r14 = SDA. Usually set with lis.
# Search for lis r13 or lis r14 in bootloader.
print("--- lis r13/r14 loads in bootloader ---")
for i in range(0, 0x10000, 4):
    w = struct.unpack(">I", d[i:i+4])[0]
    if (w >> 26) & 0x3F == 15 and ((w >> 16) & 0x1F) == 0:
        rd = (w >> 21) & 0x1F
        hi = w & 0xFFFF
        if rd in (13, 14):
            print(f"  0x{i:04X}: lis r{rd},0x{hi:04X}")

print("\n--- looking for stw instructions targeting 0x7Fxxxx ---")
for i in range(0, 0x10000, 4):
    w = struct.unpack(">I", d[i:i+4])[0]
    # stw opcode 36
    if (w >> 26) & 0x3F == 36:
        # Look back 4-8 instructions for a lis rX, 0x7F or 0x80
        for j in range(max(0, i-32), i, 4):
            w2 = struct.unpack(">I", d[j:j+4])[0]
            if (w2 >> 26) & 0x3F == 15 and ((w2 >> 16) & 0x1F) == 0:
                hi = w2 & 0xFFFF
                if hi in (0x7F80, 0x7F00, 0x7FF0, 0x8000, 0x7F90):
                    print(f"  0x{i:04X}: {d[i-8:i+16].hex().upper()} (hi=0x{hi:04X})")
                    break

print("\nDone.")