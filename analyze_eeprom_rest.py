PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\Golf_KH_BDM\Eeprom.bin"
d = open(PATH, "rb").read()

print("=== Mapping 4KB EEPROM Structure ===")

# The VIN/IMMO data is at 0x00E0 - 0x0180.
# The IQA (Injector Quantity Adjustment) is usually a block of 5 values.
print("\n--- Searching for IQA (Injector Codes) 0x0100-0x0200 ---")
# IQA values are often 2-byte or 4-byte, usually around 1000-3000 (0x03E8 - 0x0BB8)
for i in range(0x0180, 0x0200, 2):
    val = int.from_bytes(d[i:i+2], "big")
    if 500 <= val <= 5000:
        print(f"0x{i:04X}: {val} (0x{val:04X}) - Possible IQA")

print("\n--- Record Region 0x0200 - 0x0500 ---")
for i in range(0x0200, 0x0500, 16):
    row = d[i:i+16]
    hx = " ".join("%02X" % x for x in row)
    asc = "".join(chr(x) if 0x20 <= x <= 0x7E else "." for x in row)
    print(f"0x{i:04X}  {hx}  {asc}")

print("\n--- Empty/FF Regions ---")
in_ff = False
start = 0
for i in range(len(d)):
    if d[i] == 0xFF:
        if not in_ff:
            start = i
            in_ff = True
    else:
        if in_ff:
            if i - start > 16:
                print(f"0x{start:04X} - 0x{i-1:04X} ({(i-1)-start+1} bytes of 0xFF)")
            in_ff = False