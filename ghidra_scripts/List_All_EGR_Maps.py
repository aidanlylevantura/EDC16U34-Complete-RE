# @category ECU
# @runtime PyGhidra
# @description List all AirCtl calibration maps from the Damos CSV.

import re

CSV_PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"

def run():
    print("=== All AirCtl Maps in Damos CSV ===\n")
    maps = []
    
    try:
        with open(CSV_PATH, encoding='utf-8', errors='replace') as f:
            for line in f:
                p = line.rstrip('\n').split(';')
                if len(p) < 2: continue
                name = p[1].strip()
                
                # Only looking for MAP and CUR (calibration data)
                if not name or not name.startswith("AirCtl"): 
                    continue
                if not ("_MAP" in name or "_CUR" in name):
                    continue
                    
                m = re.search(r'\$([0-9A-Fa-f]{4,8})', line)
                if not m: continue
                try: 
                    addr = int(m.group(1), 16)
                except: 
                    continue
                maps.append((name, addr, p[0].strip()[:50]))
    except Exception as e:
        print("Error reading CSV: %s" % str(e))
        return

    if not maps:
        print("No AirCtl maps found.")
        return

    maps.sort(key=lambda x: x[1])
    
    for name, addr, desc in maps:
        print("0x%06X  %-30s  %s" % (addr, name, desc))
        
    print("\n=== Total: %d Maps ===" % len(maps))
    print("\nHint: If psVar23 is a short* (2 bytes), offset 0x4df = 0x9BE bytes.")
    print("Look for a map in the list above that is 0x9BE bytes away from another map.")

if __name__ == '__main__':
    run()