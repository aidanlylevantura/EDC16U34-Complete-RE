import csv
import re
import os

CSV_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
C_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_Complete_Disassembly.c"
OUTPUT_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_FINAL_Annotated.c"
DELIMITER = ';'

def load_damos():
    print("Loading Damos data...")
    damos_dict = {}
    with open(CSV_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter=DELIMITER)
        headers = next(reader)
        idx_id = headers.index("IdName")
        idx_name = headers.index("Name")
        idx_addr = headers.index("Fieldvalues.StartAddr")
        
        for row in reader:
            if len(row) <= max(idx_id, idx_name, idx_addr):
                continue
            addr_str = row[idx_addr].replace('$', '').strip()
            if not addr_str or addr_str == '0':
                continue
            try:
                flash_addr = int(addr_str, 16)
                damos_dict[flash_addr] = {"id": row[idx_id], "name": row[idx_name]}
            except:
                pass
    return damos_dict

def merge():
    damos = load_damos()
    print(f"Loaded {len(damos)} Damos definitions.")
    
    print("Merging into C-File...")
    # Look for Flash addresses (_DAT_001xxxxx) and RAM offsets (RAM_r13_xxxx)
    pattern_flash = re.compile(r'\b(_?DAT_00([0-9a-fA-F]{6}))\b|\b(0x00([0-9a-fA-F]{6}))\b')
    
    count = 0
    with open(C_FILE, 'r', encoding='utf-8') as f_in, open(OUTPUT_FILE, 'w', encoding='utf-8') as f_out:
        for line in f_in:
            def repl_flash(match):
                nonlocal count
                hex_str = match.group(2) if match.group(2) else match.group(4)
                if not hex_str: return match.group(0)
                addr = int("0x00" + hex_str, 16)
                
                if addr in damos:
                    count += 1
                    info = damos[addr]
                    return f"/* [{info['id']}] {info['name']} */ {match.group(0)}"
                return match.group(0)
                
            line = pattern_flash.sub(repl_flash, line)
            f_out.write(line)
            
    print(f"Successfully annotated {count} Flash variables in the C-File!")
    print(f"Final file saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    merge()