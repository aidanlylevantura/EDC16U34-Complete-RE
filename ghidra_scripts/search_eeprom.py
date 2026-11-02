import re

CFILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"

def main():
    print("=== Searching for Immobilizer and EEPROM Logic ===")
    
    with open(CFILE, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        
    found_immo = False
    found_spi = False
    
    current_func = "UNKNOWN"
    
    for i, line in enumerate(lines):
        # Track function headers
        if "// Function:" in line:
            current_func = line.split("// Function: ")[1].strip()
            
        # 1. Search for Immobilizer logic
        if "ImmCtl" in line or "WFS" in line:
            print(f"L{i} [{current_func}] IMMO: {line.strip()[:120]}")
            found_immo = True
            
        # 2. Search for SPI/EEPROM hardware registers
        # EDC16 typically uses 0xC0000000 or 0xF0000000 for EEPROM/SPI
        if "0xC0000" in line or "0xF0000" in line or "spi" in line.lower():
            print(f"L{i} [{current_func}] SPI/EEPROM: {line.strip()[:120]}")
            found_spi = True
            
    if not found_immo:
        print("No Immobilizer text found in the C-file. (Bosch may have compiled it out of this specific ECU variant).")
    if not found_spi:
        print("No SPI hardware registers found in this C-file. (The EEPROM driver might be in the Bootloader, not the Flash).")

if __name__ == '__main__':
    main()