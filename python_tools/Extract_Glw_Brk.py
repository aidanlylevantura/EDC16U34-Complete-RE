import os, re

CFILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"
CSV   = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
OUT   = r"C:\Users\user\Documents\Complete ECU Disassembly\Extracted_Systems"

# Which prefixes/symbols to hunt for
TARGET_SYMBOLS = ["Glw", "GlwCtl", "GlwCD", "BrkCD", "FrmMng_BRK", "FrmMng_RecBrk"]

def load_target_symbols():
    """Read CSV, return list of symbol names whose name contains any target."""
    names = set()
    with open(CSV, encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.rstrip('\n').split(';')
            if len(p) < 2: continue
            name = p[1].strip()
            if not name: continue
            if any(t in name for t in TARGET_SYMBOLS):
                names.add(name)
    return names

def parse_cfile():
    """Split C-file into functions, return dict func_name -> body."""
    funcs = {}
    cur, buf = None, []
    with open(CFILE, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.search(r'// Function: (\S+) @', line)
            if m:
                if cur and buf: funcs[cur] = "".join(buf)
                cur, buf = m.group(1), [line]
            elif cur:
                buf.append(line)
    if cur and buf: funcs[cur] = "".join(buf)
    return funcs

def main():
    print("Loading target symbols from CSV...")
    targets = load_target_symbols()
    print(f"  {len(targets)} Glw/Brk symbols found in Damos")
    
    print("Parsing C-file...")
    funcs = parse_cfile()
    print(f"  {len(funcs)} total functions")
    
    # Group functions by which target symbols they reference
    glw_funcs   = []
    brk_funcs   = []
    other_funcs = []
    
    for fname, body in funcs.items():
        hits_glw = [t for t in targets if 'Glw' in t and t in body]
        hits_brk = [t for t in targets if 'Brk' in t and t in body]
        
        if hits_glw:
            glw_funcs.append(body)
        elif hits_brk:
            brk_funcs.append(body)
    
    # Save
    if not os.path.exists(OUT):
        os.makedirs(OUT)
    
    outfile = os.path.join(OUT, "System_Glw.c")
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(f"// Glow plug system: {len(glw_funcs)} functions\n\n")
        f.write("\n\n".join(glw_funcs))
    print(f"  Saved System_Glw.c ({len(glw_funcs)} functions)")
    
    outfile = os.path.join(OUT, "System_Brk.c")
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(f"// Brake system: {len(brk_funcs)} functions\n\n")
        f.write("\n\n".join(brk_funcs))
    print(f"  Saved System_Brk.c ({len(brk_funcs)} functions)")
    
    print("\nIf both are 0, the symbols are annotated in Ghidra but not referenced in the decompiled C text.")
    print("In that case, the systems exist only as RAM variables or data tables — nothing to extract.")

if __name__ == '__main__':
    main()