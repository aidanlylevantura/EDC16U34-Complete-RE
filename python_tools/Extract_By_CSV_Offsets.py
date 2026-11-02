import os, re
from collections import defaultdict

CFILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"
CSV   = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
OUT   = r"C:\Users\user\Documents\Complete ECU Disassembly\Extracted_Systems"

# System prefix -> (output filename, base addresses to try)
SYSTEMS = {
    "Glw":     ("System_Glw",   [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "GlwCtl":  ("System_GlwCtl",[0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "GlwCD":   ("System_GlwCD", [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "BrkCD":   ("System_BrkCD", [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "StSys":   ("System_StSys", [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "Alt":     ("System_Alt",   [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "EngM":    ("System_EngM",  [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "EngPrt":  ("System_EngPrt",[0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "VSSCD":   ("System_VSSCD", [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "ASMod":   ("System_ASMod", [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "IndSys":  ("System_IndSys",[0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "FBC":     ("System_FBC",   [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "BIP":     ("System_BIP",   [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "DSM":     ("System_DSM",   [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "EepInit": ("System_EepInit",[0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "CoEng":   ("System_CoEng", [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "Rail":    ("System_Rail",  [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "Shtrp":   ("System_Shtrp", [0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
    "BasAdj":  ("System_BasAdj",[0x1C0000, 0x1D0000, 0x1E0000, 0x1F0000]),
}

def load_csv_offsets():
    """Return dict: system_prefix -> set of (offset_hex_str) for addresses in ROM."""
    result = defaultdict(set)
    with open(CSV, encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.rstrip('\n').split(';')
            if len(p) < 2: continue
            name = p[1].strip()
            if not name: continue
            m = re.search(r'\$([0-9A-Fa-f]{4,8})', line)
            if not m: continue
            try: addr = int(m.group(1), 16)
            except: continue
            if addr < 0x1C0000 or addr > 0x200000:
                continue
            # Find matching system prefix
            for sys_prefix in SYSTEMS:
                if name.startswith(sys_prefix + "_") or name.startswith(sys_prefix):
                    # Try each candidate base
                    for base in SYSTEMS[sys_prefix][1]:
                        off = addr - base
                        if 0 < off < 0x10000:
                            # Format variants the decompiler might use
                            result[sys_prefix].add(f"0x{off:x}")
                            result[sys_prefix].add(f"0x{off:X}")
                            break
    return result

def parse_cfile():
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
    print("Loading CSV offsets...")
    offsets = load_csv_offsets()
    for sys_name, offs in offsets.items():
        print(f"  {sys_name}: {len(offs)//2} unique offsets")

    print("\nParsing C-file...")
    funcs = parse_cfile()
    print(f"  {len(funcs)} functions")

    print("\nExtracting by offset pattern...")
    if not os.path.exists(OUT): os.makedirs(OUT)

    for sys_name, (outname, _) in SYSTEMS.items():
        offs = offsets.get(sys_name, set())
        if not offs:
            print(f"  {sys_name}: no offsets in CSV, skipping")
            continue

        # Match functions whose body contains any of these offset strings
        # Use word-boundary to avoid 0x525 matching 0x5256
        patterns = [re.compile(r'\b' + re.escape(o) + r'\b') for o in offs]
        matched = []
        for fname, body in funcs.items():
            if any(p.search(body) for p in patterns):
                matched.append(body)

        if matched:
            outfile = os.path.join(OUT, outname + ".c")
            with open(outfile, 'w', encoding='utf-8') as f:
                f.write(f"// {sys_name}: {len(matched)} functions matched by offset pattern\n")
                f.write(f"// NOTE: These functions use (base + offset) access patterns derived from CSV symbols.\n")
                f.write(f"// Offsets searched: {len(offs)//2} unique values.\n\n")
                f.write("\n\n".join(matched))
            print(f"  {sys_name}: {len(matched)} functions -> {outname}.c")
        else:
            print(f"  {sys_name}: 0 functions (offsets not referenced)")

    print(f"\nAll output in: {OUT}")

if __name__ == '__main__':
    main()