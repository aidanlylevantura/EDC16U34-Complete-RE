import csv
import os

CSV_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
C_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_Complete_Disassembly.c"
OUTPUT_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_FINAL_Annotated.c"
DELIMITER = ';'

def load_damos():
    print("Loading Damos data...")
    damos = []
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
            # Strip leading zeros to match Ghidra's output (e.g., "001D1240" -> "1D1240")
            clean_hex = addr_str.lstrip('0').upper()
            if clean_hex:
                damos.append((clean_hex, row[idx_id], row[idx_name]))
    
    # Sort by longest hex string first so we don't replace substrings by accident
    damos.sort(key=lambda x: len(x[0]), reverse=True)
    return damos

def merge():
    damos = load_damos()
    print(f"Loaded {len(damos)} Damos definitions.")
    
    print("Reading C-File...")
    with open(C_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
        
    print("Applying annotations (this may take a moment)...")
    count = 0
    for hex_str, id_name, human_name in damos:
        # Ghidra might write "1D1240", "0x1D1240", or "_DAT_001D1240"
        # We search for the hex string and add the comment
        if hex_str in content:
            # Safely replace the first occurrence or all occurrences
            safe_comment = f"/* [{id_name}] {human_name.replace('*/', '')} */ "
            # We use regex to replace whole words to avoid partial matches
            import re
            pattern = re.compile(r'\b' + hex_str + r'\b', re.IGNORECASE)
            content, n = pattern.subn(safe_comment + hex_str, content)
            count += n
            
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Successfully annotated {count} occurrences in the C-File!")
    print(f"Final file saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    merge()