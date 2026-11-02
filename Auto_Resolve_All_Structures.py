import re, sys
from collections import defaultdict

CSV_PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
CFILE    = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"
OUT      = r"C:\Users\user\Documents\Complete ECU Disassembly\Structure_Map_Report.txt"

# Types that appear in Ghidra's decompiler and their byte-widths
TYPE_WIDTH = {'byte': 1, 'undefined1': 1, 'char': 1,
              'short': 2, 'undefined2': 2, 'ushort': 2,
              'int': 4, 'undefined4': 4, 'uint': 4, 'long': 4}

def load_maps(path):
    """address -> name, and prefix -> [(name, address)]."""
    by_addr, by_prefix = {}, defaultdict(list)
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.rstrip('\n').split(';')
            if len(p) < 2: continue
            name = p[1].strip()
            if not name or not ('_MAP' in name or '_CUR' in name): continue
            m = re.search(r'\$([0-9A-Fa-f]{4,8})', line)
            if not m: continue
            try: addr = int(m.group(1), 16)
            except: continue
            by_addr[addr] = name
            by_prefix[name.split('_')[0]].append((name, addr))
    return by_addr, by_prefix

def parse_functions(lines):
    """Yield (func_name, body_lines, base_ptr_var, base_ram_off, ptr_type)."""
    func_hdr = re.compile(r'// Function: (\S+) @')
    func_name = None
    buf = []
    for line in lines:
        m = func_hdr.search(line)
        if m:
            if func_name and buf: yield func_name, buf
            func_name = m.group(1)
            buf = []
        elif func_name is not None:
            buf.append(line)
    if func_name and buf: yield func_name, buf

def analyze_function(fname, body):
    """Return (ptr_var, ram_off, ptr_type, [offsets]) or None."""
    text = "".join(body)
    # Find base load: psVarXX = *(short **)(unaff_r15 + 0xNNN);
    load = re.search(r'(\w+)\s*\*\s*(\w+)\s*=\s*\*\(\s*(\w+)\s*\*\*\s*\)\s*\(\s*unaff_r15\s*\+\s*(0x[0-9a-fA-F]+)\s*\)', text)
    if not load: return None
    _, ptr_var, ptr_type, ram_off = load.groups()
    if ptr_type not in TYPE_WIDTH: return None
    width = TYPE_WIDTH[ptr_type]
    ram_off = int(ram_off, 16)
    # Find all offset accesses: psVarXX[0xNNN]
    offsets = set()
    for m in re.finditer(re.escape(ptr_var) + r'\[(0x[0-9a-fA-F]+)\]', text):
        offsets.add(int(m.group(1), 16))
    if not offsets: return None
    return (ptr_var, ram_off, width, sorted(offsets))

def resolve_base(offsets, width, by_addr):
    """Try every map as a reference point; find base where most offsets hit valid maps."""
    best = (None, 0)
    # Cap candidates: sample a few offsets to reduce O(n^2)
    sample_offsets = offsets[:min(len(offsets), 5)]
    for ref_map_addr in by_addr.keys():
        for ref_off in sample_offsets:
            base = ref_map_addr - ref_off * width
            if base < 0x1C0000 or base > 0x1F0000:   # calibration region only
                continue
            hits = sum(1 for o in offsets if (base + o * width) in by_addr)
            if hits > best[1]:
                best = (base, hits)
    return best

def main():
    print("Loading CSV maps...")
    by_addr, by_prefix = load_maps(CSV_PATH)
    print(f"  {len(by_addr)} calibration maps loaded")

    with open(CFILE, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    results = []
    unresolved = []

    print("Scanning functions...")
    for fname, body in parse_functions(lines):
        parsed = analyze_function(fname, body)
        if not parsed: continue
        ptr_var, ram_off, width, offsets = parsed
        base, hits = resolve_base(offsets, width, by_addr)

        if base is None or hits == 0:
            unresolved.append((fname, ptr_var, ram_off, len(offsets)))
            continue

        # Which system? Look at prefixes of hit maps
        hit_prefixes = defaultdict(int)
        for o in offsets:
            a = base + o * width
            if a in by_addr:
                hit_prefixes[by_addr[a].split('_')[0]] += 1
        system = max(hit_prefixes, key=hit_prefixes.get) if hit_prefixes else "?"

        results.append({
            'func': fname, 'ptr_var': ptr_var, 'ram_off': ram_off,
            'ptr_type': 'short' if width == 2 else ('int' if width == 4 else 'byte'),
            'base': base, 'hits': hits, 'total': len(offsets),
            'system': system,
            'maps': [(o, by_addr.get(base + o * width)) for o in offsets]
        })

    # Write report
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write("=== AUTO-RESOLVED SYSTEM STRUCTURES ===\n\n")
        for r in sorted(results, key=lambda x: x['system']):
            f.write(f"System: {r['system']}\n")
            f.write(f"  Function: {r['func']}\n")
            f.write(f"  Base ptr: {r['ptr_var']} ({r['ptr_type']}*) from unaff_r15 + 0x{r['ram_off']:X}\n")
            f.write(f"  Base ROM: 0x{r['base']:06X}  ({r['hits']}/{r['total']} offsets resolved)\n")
            for o, name in r['maps']:
                mark = "" if name else "  ??"
                f.write(f"    [{r['ptr_var']}[0x{o:X}]] -> {name or '??'}{mark}\n")
            f.write("\n")

        f.write(f"\n=== UNRESOLVED ({len(unresolved)}) ===\n")
        for fname, var, off, n in unresolved:
            f.write(f"  {fname}  ({var} from unaff_r15 + 0x{off:X}, {n} offsets)\n")

    # Console summary
    print(f"\nResolved: {len(results)} functions   Unresolved: {len(unresolved)}")
    print("\nSystems discovered:")
    sys_count = defaultdict(int)
    for r in results: sys_count[r['system']] += 1
    for s, c in sorted(sys_count.items(), key=lambda x: -x[1]):
        print(f"  {s:12s}  {c} functions  ")
    print(f"\nFull report written to: {OUT}")

if __name__ == '__main__':
    main()