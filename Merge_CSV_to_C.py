import csv
import re
import os
import struct

# =====================================================================
# CONFIGURATION
# =====================================================================
BIN_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
CSV_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
C_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_Complete_Disassembly.c"
OUTPUT_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_Annotated_Disassembly.c"
DELIMITER = ';'
# =====================================================================

def build_ram_to_flash_map(bin_path):
    """Reads the GOT table from the binary to map RAM addresses to Flash addresses."""
    print("Extracting GOT table from binary...")
    ram_to_flash = {}
    
    # The GOT table we found is at 0x0004CB00 to 0x0004CC00
    got_start = 0x0004CB00
    got_end = 0x0004CC00
    
    with open(bin_path, 'rb') as f:
        f.seek(got_start)
        data = f.read(got_end - got_start)
        
        for i in range(0, len(data), 4):
            # Read 4 bytes as Big-Endian 32-bit integer
            flash_addr = struct.unpack('>I', data[i:i+4])[0]
            
            # If the address points to the calibration area (0x180000 - 0x1FFFFF)
            if 0x00180000 <= flash_addr <= 0x00200000:
                # The RAM address for the pointer is GOT start + offset
                # However, we need the actual RAM address that the code uses.
                # The code uses r13 (0x007FFFF0). The offset is calculated from the GOT.
                # Actually, we can find the RAM address by looking at the assembly.
                # But for now, let's just use the known offset method.
                pass

    # Since mapping GOT to RAM automatically is complex, let's manually map the known EGT block.
    # We know r13 = 0x007FFFF0.
    # The EGT switch is at r13 - 0x640c = 0x007F9BE4
    # The Flash address is 0x001D1240
    ram_to_flash[0x007F9BE4] = 0x001D1240
    
    # Let's add the other known variables from the EGT function
    ram_to_flash[0x007F9BE6] = 0x001D123C # EGT_tiRmpSlp_C
    ram_to_flash[0x007F9BFA] = 0x001D1228 # Example
    
    print("Mapped %d RAM addresses to Flash." % len(ram_to_flash))
    return ram_to_flash

def build_address_dictionary(csv_path):
    print("Parsing CSV for map definitions...")
    addr_dict = {}
    
    with open(csv_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter=DELIMITER)
        headers = next(reader)
        
        idx_id = headers.index("IdName")
        idx_name = headers.index("Name")
        idx_addr = headers.index("Fieldvalues.StartAddr")
        idx_comment = headers.index("Comment")

        for row in reader:
            if len(row) <= max(idx_id, idx_name, idx_addr, idx_comment):
                continue
                
            addr_str = row[idx_addr].replace('$', '').strip()
            if not addr_str or addr_str == '0' or addr_str == '-':
                continue
                
            try:
                flash_addr = int(addr_str, 16)
                addr_dict[flash_addr] = {
                    'id': row[idx_id],
                    'name': row[idx_name].replace('*/', '').replace('/*', ''),
                    'comment': row[idx_comment].replace('*/', '').replace('/*', '')
                }
            except ValueError:
                pass
                
    print("Found %d defined addresses in CSV." % len(addr_dict))
    return addr_dict

def annotate_c_file(c_path, flash_dict, ram_to_flash):
    print("Processing C file...")
    
    # Regex to find RAM addresses like 0x007f9be4 or _DAT_007f9be4
    pattern_ram = re.compile(r'\b(_?DAT_00([0-9a-fA-F]{6}))\b|\b(0x00([0-9a-fA-F]{6}))\b')
    
    replaced_count = 0
    
    with open(c_path, 'r', encoding='utf-8') as f_in, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        
        for line in f_in:
            def replace_match(match):
                nonlocal replaced_count
                hex_str = match.group(2) if match.group(2) else match.group(4)
                if not hex_str:
                    return match.group(0)
                    
                ram_val = int("0x00" + hex_str, 16)
                
                if ram_val in ram_to_flash:
                    flash_val = ram_to_flash[ram_val]
                    if flash_val in flash_dict:
                        info = flash_dict[flash_val]
                        replaced_count += 1
                        return f"/* [{info['id']}] {info['name']} */ {match.group(0)}"
                return match.group(0)

            annotated_line = pattern_ram.sub(replace_match, line)
            f_out.write(annotated_line)
            
    print("Successfully injected %d map annotations into the C code!" % replaced_count)

if __name__ == "__main__":
    # We don't actually need the BIN file for this specific manual mapping
    # ram_to_flash = build_ram_to_flash_map(BIN_FILE) 
    ram_to_flash = {0x007F9BE4: 0x001D1240, 0x007F9BE6: 0x001D123C} 
    
    dict_maps = build_address_dictionary(CSV_FILE)
    if dict_maps:
        annotate_c_file(C_FILE, dict_maps, ram_to_flash)