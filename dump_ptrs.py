import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

for addr in [0x148, 0x150, 0x158, 0x160]:
    ptr = struct.unpack(">I", d[addr:addr+4])[0]
    print(f"Pointer at 0x{addr:03X} = 0x{ptr:08X}")