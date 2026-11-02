import os, re

CFILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"
OUT_DIR = r"C:\Users\user\Documents\Complete ECU Disassembly\Extracted_Systems"

# The prefixes we want to capture in this final sweep
TARGET_PREFIXES = ["Gearbx", "Glw", "GlwCtl", "BrkCD", "FrmMng_Brk"]

def parse_cfile():
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
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)

    print("Loading C-File...")
    all_funcs = parse_cfile()
    
    print("Scanning for remaining systems...")
    system_files = {prefix: [] for prefix in TARGET_PREFIXES}
    
    for func_name, c_code in all_funcs.items():
        for prefix in TARGET_PREFIXES:
            if prefix in c_code:
                system_files[prefix].append(c_code)
                break  # Only add to the first matching system
                
    for prefix, codes in system_files.items():
        if not codes:
            print(f"  {prefix}: No functions found.")
            continue
            
        out_file = os.path.join(OUT_DIR, f"System_{prefix}.c")
        with open(out_file, 'w', encoding='utf-8') as f:
            f.write(f"// ==================================================\n")
            f.write(f"// SYSTEM: {prefix} ({len(codes)} functions)\n")
            f.write(f"// ==================================================\n\n")
            f.write("\n\n".join(codes))
        print(f"  Saved {prefix} ({len(codes)} functions) -> System_{prefix}.c")

if __name__ == '__main__':
    main()