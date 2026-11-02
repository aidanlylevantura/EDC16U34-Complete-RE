import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

print("=== Search 1: Any reference to 0x7F87F4 (descriptor table ptr) ===")
targets = [0x7F87F4, 0x7F8834, 0x7F909C, 0x7F87A4]

for target in targets:
    print(f"\n-- target 0x{target:08X} --")
    found = False
    # Look for lis/ori or lis/addi pairs building this address
    hi = (target >> 16) & 0xFFFF
    lo = target & 0xFFFF
    for i in range(0, 0x40000, 4):
        w1 = struct.unpack(">I", d[i:i+4])[0]
        if ((w1 >> 26) & 0x3F) != 15: continue
        if ((w1 >> 16) & 0x1F) != 0: continue
        if (w1 & 0xFFFF) != hi: continue
        rd1 = (w1 >> 21) & 0x1F
        w2 = struct.unpack(">I", d[i+4:i+8])[0]
        op2 = (w2 >> 26) & 0x3F
        ra2 = (w2 >> 16) & 0x1F
        rd2 = (w2 >> 21) & 0x1F
        if op2 not in (14, 24): continue
        if ra2 != rd1 or rd2 != rd1: continue
        # For addi, imm is signed
        imm_lo = w2 & 0xFFFF
        if op2 == 14 and imm_lo & 0x8000:
            imm_lo = imm_lo - 0x10000
        if op2 == 24:
            imm_lo = imm_lo & 0xFFFF
        target_addr = (hi << 16) + imm_lo
        if target_addr == target:
            print(f"  0x{i:06X}: lis r{rd1},0x{hi:04X} ; {'ori' if op2==24 else 'addi'} r{rd1},r{rd1},0x{w2 & 0xFFFF:04X}")
            print(f"    Context: {d[i-8:i+24].hex().upper()}")
            found = True
    if not found:
        print(f"  (no lis/ori pair found)")

print("\n=== Search 2: stw instructions targeting 0x7Fxxxx range ===")
# Look for stw rX, off(rY) where the computed address is in the 0x7F8000-0x7FFFFF range
for i in range(0, 0x40000, 4):
    w = struct.unpack(">I", d[i:i+4])[0]
    op = (w >> 26) & 0x3F
    if op != 36: continue  # stw
    # Look back 4 instructions for address build
    for j in range(max(0, i-16), i, 4):
        w2 = struct.unpack(">I", d[j:j+4])[0]
        op2 = (w2 >> 26) & 0x3F
        if op2 == 15 and ((w2 >> 16) & 0x1F) == 0:
            hi = w2 & 0xFFFF
            if 0x7F80 <= hi <= 0x7FFF:
                print(f"  0x{i:06X}: {d[i-8:i+16].hex().upper()} (hi=0x{hi:04X})")

print("\nDone.")