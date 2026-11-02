import struct

BIN_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
OUT_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\DTC_Table.txt"

def extract_dtcs():
    print("Searching for DTC Table...")
    # Bosch DTC tables are often arrays of 16-bit values located in the calibration area.
    # We can scan the Flash (0x180000 - 0x1FFFFF) for sequences of hex values that look like DTCs.
    
    with open(BIN_FILE, 'rb') as f:
        bin_data = f.read()

    dtcs = []
    # DTCs are 16-bit. We look for sequences of them.
    # This is a heuristic approach. We are looking for the DTC 0x0131 (EGT) to anchor our search.
    target_dtc = 0x0131
    
    print(f"Searching for anchor DTC: 0x{target_dtc:04X}...")
    
    for i in range(0x180000, 0x1FFFFF, 2):
        if i + 1 < len(bin_data):
            val = struct.unpack('>H', bin_data[i:i+2])[0]
            if val == target_dtc:
                print(f"Found anchor DTC at offset: 0x{i:06X}")
                # Dump surrounding 32 bytes (16 DTCs)
                start = max(0, i - 16)
                end = min(len(bin_data), i + 16)
                context = struct.unpack(f'>{ (end-start)//2 }H', bin_data[start:end])
                print("Surrounding DTCs:", [f"0x{x:04X}" for x in context])
                dtcs.extend(context)

    # Save to file
    with open(OUT_FILE, 'w') as f:
        f.write("Extracted DTC Table (Hex):\n")
        for dtc in set(dtcs):
            f.write(f"0x{dtc:04X}\n")

    print(f"Done. Saved {len(set(dtcs))} unique DTCs to {OUT_FILE}")

if __name__ == "__main__":
    extract_dtcs()