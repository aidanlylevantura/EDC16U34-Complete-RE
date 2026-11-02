import re

CSV_PATH = "WinOLS (VW (Original) - 380437).csv"

# These are the offsets we saw in FUN_0005fbb8
# (multiplied by 2 because psVar23 is a short*)
OFFSETS_USED = [0x4df*2, 0x4e6*2, 0x4e3*2, 0x4e9*2, 0x4e8*2, 0x4e2*2, 0x4e7*2, 0x4e0*2, 0x4e1*2, 0x4e5*2]

def load_damos(path):
    out = []
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            p = line.rstrip('\n').split(';')
            if len(p) < 2: continue
            name = p[1].strip()
            if not name or not name.startswith("AirCtl"): continue
            m = re.search(r'\$([0-9A-Fa-f]{4,8})', line)
            if not m: continue
            try: addr = int(m.group(1), 16)
            except: continue
            out.append((name, addr))
    return out

def main():
    maps = load_damos(CSV_PATH)
    maps.sort(key=lambda x: x[1])
    
    if not maps:
        print("No AirCtl maps found in CSV.")
        return

    print("=== AirCtl Maps in Damos CSV ===")
    for name, addr in maps:
        print(f"0x{addr:06X}  {name}")
        
    print("\n=== Mapping Offsets to Maps (Assuming Base is the first map) ===")
    base_addr = maps[0][1]
    print(f"Assuming base = 0x{base_addr:06X}")
    
    for off in OFFSETS_USED:
        target = base_addr + off
        # Find the nearest map
        nearest = min(maps, key=lambda x: abs(x[1] - target))
        print(f"Offset {hex(off//2)} -> Target 0x{target:06X} (Nearest Map: {nearest[0]} at 0x{nearest[1]:06X})")

if __name__ == '__main__':
    main()