import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

# Literal values we want to find in the .sdata_init source block
targets = {
    0x7F87F4: "descriptor table ptr",
    0x7F8834: "valid mask",
    0x7F909C: "entry count",
    0x7F87A4: "scratch block",
    0x007FC0: "signature 12-byte target",
    0x7FEF54: "finish state",
    0x7F8160: "finish payload buffer",
    0x7F90B8: "eeprom state machine",
    0x7F90BC: "eeprom work ptr",
}

print("=== Search 1: literal pointer values ===")
for val, name in targets.items():
    pattern = struct.pack(">I", val)
    hits = []
    for i in range(0, len(d) - 4):
        if d[i:i+4] == pattern:
            hits.append(i)
    if hits:
        print(f"\n0x{val:08X} ({name}): {len(hits)} hit(s)")
        for i in hits[:5]:
            print(f"  0x{i:06X}: {d[max(0,i-16):i+32].hex().upper()}")
    else:
        print(f"\n0x{val:08X} ({name}): not found")

print("\n=== Search 2: any 0x007Fxxxx literal in flash ===")
# Find all 4-byte values in the 0x007F0000-0x007FFFFF range
found_clusters = []
for i in range(0, len(d) - 4, 4):
    val = struct.unpack(">I", d[i:i+4])[0]
    if 0x7F0000 <= val < 0x800000:
        found_clusters.append((i, val))

print(f"  Total: {len(found_clusters)} hits")
for i, val in found_clusters[:30]:
    print(f"  0x{i:06X}: 0x{val:08X}")

print("\nDone.")