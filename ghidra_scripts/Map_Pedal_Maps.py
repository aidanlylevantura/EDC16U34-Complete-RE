# @category ECU
# @runtime PyGhidra
# @description Calculate the structure offsets for Pedal maps.

# The base address of the first AccPed map in the Damos file
PEDAL_BASE = 0x1C2394  # AccPed_trqEng0_MAP starts around here in RAM/ROM structure

# Offsets used in the code
OFFSETS = [0x42, 0x1d2, 0x328, 0x47e, 0x5d4, 0x72a, 0x880, 0x9d6, 0xb30, 0xc1c]

def run():
    print("=== Mapping Pedal Calibration Structure ===")
    print("Assuming base pointer aligns with AccPed_trqEng0_MAP...\n")
    
    # We know 0x42 points to the first map. Let's find the true base.
    # If 0x42 = 66 bytes, and base is aligned, base = target - 66
    # Let's just do the math for the user to see.
    
    for off in OFFSETS:
        # 66 bytes = 0x42. The code uses short pointers, so offset is in words (2 bytes)
        # Actually, C-code does `pedal_map_base + 0x42`. Since it's `short*`, 0x42 is 66 * 2 = 132 bytes (0x84).
        # Let's just print the structural order.
        pass
        
    # Better approach: Print the known Damos maps in order and match to code offsets
    maps = [
        ("AccPed_trqEng0_MAP", 0x1C2394),
        ("AccPed_trqEng1_MAP", 0x1C24EA),
        ("AccPed_trqEng2_MAP", 0x1C2640),
        ("AccPed_trqEng3_MAP", 0x1C2796),
        ("AccPed_trqEng4_MAP", 0x1C28EC),
        ("AccPed_trqEng5_MAP", 0x1C2A42),
        ("AccPed_trqEng6_MAP", 0x1C2B98),
        ("AccPed_trqEngLow_MAP", 0x1C2CEE),
        ("AccPed_trqPrpSport_MAP", 0x1C2E40),
        ("AccPed_trqPrp_MAP", 0x1C2F2C)
    ]
    
    base = maps[0][1]
    for name, addr in maps:
        delta = addr - base
        print("%-25s at 0x%08X (offset from base: 0x%X)" % (name, addr, delta))

if __name__ == '__main__':
    run()