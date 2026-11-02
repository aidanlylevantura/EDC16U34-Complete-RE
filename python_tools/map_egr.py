import re

# Full absolute path to your CSV file
CSV_PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"

# The offsets from FUN_0005fbb8
OFFSETS_USED = [0x4df, 0x4e6, 0x4e3, 0x4e9, 0x4e8, 0x4e2, 0x4e7, 0x4e0, 0x4e1, 0x4e5]

def load_damos(path):
    out = []
    try:
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
                out.append((name, addr, p[0].strip()[:60]))
    except FileNotFoundError:
        print(f"ERROR: Could not find the CSV file at {path}")
        exit(1)
    return out

def main():
    print("Loading Damos CSV...")
    maps = load_damos(CSV_PATH)
    maps.sort(key=lambda x: x[1])
    
    print("\n=== Mapping EGR Offsets from FUN_0005fbb8 ===")
    print("Since psVar23 is a short*, we multiply offsets by 2 to get bytes.")
    print("Look for a block of maps where the addresses match the offsets.\n")
    
    for off in OFFSETS_USED:
        byte_offset = off * 2
        print(f"Code Index [0x{off:X}] = Byte Offset {byte_offset} (0x{byte_offset:X})")

    print("\n=== Closest EGR Maps in the CSV ===")
    interesting_maps = [
        "AirCtl_rEGR2_MAP", "AirCtl_rEGR_MAP", "AirCtl_rRgn1EGR_MAP", 
        "AirCtl_rRgn2EGR_MAP", "AirCtl_rEGRGearChngRgn_MAP", 
        "AirCtl_rEGRGearChng_MAP", "AirCtl_rEGROvrRunRgn_MAP", 
        "AirCtl_rEGROvrRun_MAP", "AirCtl_rTVAGearChngRgn_MAP", 
        "AirCtl_rTVAOvrRunRgn_MAP"
    ]
    
    for name, addr, desc in maps:
        if name in interesting_maps:
            print(f"0x{addr:06X}  {name:30s}  {desc}")

if __name__ == '__main__':
    main()