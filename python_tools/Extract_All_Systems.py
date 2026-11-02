import os, re
from collections import defaultdict

REPORT_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\Structure_Map_Report.txt"
CFILE       = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"
OUT_DIR     = r"C:\Users\user\Documents\Complete ECU Disassembly\Extracted_Systems"

def parse_report():
    """Reads the report and returns a dictionary of functions and their map offsets."""
    func_data = {}
    current_func = None
    current_system = None
    current_ptr = None
    
    with open(REPORT_FILE, encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if line.startswith("System: "):
                current_system = line.split("System: ")[1]
            elif line.startswith("Function: "):
                current_func = line.split("Function: ")[1]
            elif line.startswith("Base ptr: "):
                # Extract ptr var name, e.g. "psVar23"
                current_ptr = line.split("Base ptr: ")[1].split(" ")[0]
                func_data[current_func] = {
                    'system': current_system,
                    'ptr': current_ptr,
                    'maps': {}
                }
            elif line.startswith("[") and "->" in line and current_func:
                # Line looks like: [psVar23[0x4DF]] -> AirCtl_rEGRGearChngRgn_MAP
                m = re.search(r'\[0x([0-9A-Fa-f]+)\]\] -> (.*)', line)
                if m:
                    offset = int(m.group(1), 16)
                    map_name = m.group(2).strip()
                    func_data[current_func]['maps'][offset] = map_name
    return func_data

def parse_cfile():
    """Reads the C-file and extracts functions into a dictionary."""
    funcs = {}
    current_func = None
    buf = []
    
    with open(CFILE, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.search(r'// Function: (\S+) @', line)
            if m:
                if current_func and buf:
                    funcs[current_func] = "".join(buf)
                current_func = m.group(1)
                buf = [line]
            elif current_func:
                buf.append(line)
        if current_func and buf:
            funcs[current_func] = "".join(buf)
    return funcs

def main():
    print("Loading Report...")
    report_data = parse_report()
    
    print("Loading C-File...")
    c_functions = parse_cfile()
    
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
        
    system_files = defaultdict(list)
    
    print("Extracting and Annotating Systems...")
    for func_name, data in report_data.items():
        if func_name not in c_functions:
            continue
            
        system = data['system']
        ptr = data['ptr']
        maps = data['maps']
        
        c_code = c_functions[func_name]
        
        # Inject map names as comments right next to the offsets
        for offset, map_name in maps.items():
            hex_off = f"0x{offset:X}"
            hex_off_lower = f"0x{offset:x}"
            
            # Look for ptr[0x4DF] or *(short *)(ptr + 0x4DF)
            pattern1 = re.compile(re.escape(ptr) + r'\[' + hex_off_lower + r'\]', re.IGNORECASE)
            pattern2 = re.compile(r'\(\s*' + re.escape(ptr) + r'\s*\+\s*' + hex_off_lower + r'\s*\)', re.IGNORECASE)
            pattern3 = re.compile(r'\(\s*' + re.escape(ptr) + r'\s*\+\s*' + hex_off + r'\s*\)', re.IGNORECASE)
            
            comment = f" /* MAP: {map_name} */"
            
            c_code = pattern1.sub(lambda m: m.group(0) + comment, c_code)
            c_code = pattern2.sub(lambda m: m.group(0) + comment, c_code)
            c_code = pattern3.sub(lambda m: m.group(0) + comment, c_code)
            
        system_files[system].append(c_code)
        
    for system, codes in system_files.items():
        out_file = os.path.join(OUT_DIR, f"System_{system}.c")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(f"// ==================================================\n")
            f.write(f"// DECODED SYSTEM: {system}\n")
            f.write(f"// Total Functions: {len(codes)}\n")
            f.write(f"// ==================================================\n\n")
            f.write("\n\n".join(codes))
        print(f"  Saved {system} ({len(codes)} functions) -> System_{system}.c")

    print(f"\nAll systems extracted to: {OUT_DIR}")

if __name__ == '__main__':
    main()