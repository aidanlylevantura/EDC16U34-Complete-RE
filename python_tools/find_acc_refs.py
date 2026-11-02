import re, argparse

TARGETS = {
    'ACCCD_aDesLimNeg_CUR': 0x1C203C,
    'ACCCD_aDesLimPos_CUR': 0x1C2052,
    'ACC_rPedThres_C':      0x1C1D7E,
    'ACC_trqDesMax_C':      0x1C1D94,
    'ACCCD_stACC_Vector':   0x1C0A1C,
    'ACC_stCrCtl_Vector':   0x1C0A10
}

def load_damos(path):
    out = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.rstrip('\n').split(';')
            if len(p) < 2: continue
            name = p[1].strip()
            if not name: continue
            m = re.search(r'\$([0-9A-Fa-f]{4,8})', line)
            if not m: continue
            try: addr = int(m.group(1), 16)
            except: continue
            out.append((name, addr, p[0].strip()[:100]))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cfile', required=True)
    ap.add_argument('--csv',   required=True)
    ap.add_argument('--window', type=int, default=64)
    a = ap.parse_args()

    damos = load_damos(a.csv)
    with open(a.cfile, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    for name, addr in TARGETS.items():
        print(f"\n=== {name} @ 0x{addr:08X} ===")
        
        # We look for the Damos name OR the addresses in various formats
        reps_list = [
            name, 
            f'0x{addr:08X}', f'0x{addr:06X}', 
            f'${addr:06X}', f'${addr:08X}', 
            f'DAT_{addr:08x}', f'DAT_{addr:06x}',
            f'{addr:06X}h'
        ]
        
        pat = re.compile('|'.join(re.escape(t) for t in reps_list), re.I)
        hits = [(i, ln.rstrip()[:180]) for i, ln in enumerate(lines, 1) if pat.search(ln)]
        
        print(f"  References found: {len(hits)}")
        for i, ln in hits[:8]:
            print(f"    L{i}: {ln}")
            
        if len(hits) > 8:
            print(f"    ... and {len(hits)-8} more.")
            
        near = sorted([d for d in damos if 0 < abs(d[1] - addr) <= a.window], key=lambda x: x[1])
        print(f"\n  Nearby symbols (±{a.window} bytes):")
        for n, ad, desc in near:
            print(f"    0x{ad:08X}  {n:42s}  {desc[:60]}")

if __name__ == '__main__':
    main()