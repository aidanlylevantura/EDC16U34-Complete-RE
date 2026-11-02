import re

CFILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"

def main():
    print("=== 1. Scanning for Checksum Algorithms ===")
    with open(CFILE, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        
    crc_count = 0
    for i, line in enumerate(lines, 1):
        # Look for XOR loops or CRC math patterns
        if "^=" in line or "crc" in line.lower() or "0xEDB88320" in line:
            if "for" in line or "while" in line or "^" in line:
                print(f"L{i}: {line.strip()[:100]}")
                crc_count += 1
                if crc_count > 15: break
                
    print("\n=== 2. Scanning for OBD-II & UDS Services ===")
    obd_count = 0
    for i, line in enumerate(lines, 1):
        # Look for standard OBD/UDS Service IDs and CAN IDs
        if "0x7DF" in line or "0x7E0" in line or "0x7E8" in line:
            print(f"L{i} [CAN ID]: {line.strip()[:100]}")
            obd_count += 1
        elif "0x10" in line and "case" in line:
            pass # Complex to parse, skipping generic
        elif "0x22" in line or "0x2E" in line:
            if "case" in line:
                print(f"L{i} [UDS Service]: {line.strip()[:100]}")
                obd_count += 1
        if obd_count > 15: break

if __name__ == '__main__':
    main()