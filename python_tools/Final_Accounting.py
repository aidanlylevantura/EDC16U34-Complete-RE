import re
from collections import Counter

CFILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v9.c"

def main():
    names = []
    with open(CFILE, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.search(r'// Function: (\S+) @', line)
            if m:
                names.append(m.group(1))

    total = len(names)
    named = [n for n in names if not n.startswith("FUN_")]
    unnamed = [n for n in names if n.startswith("FUN_")]

    prefixes = Counter()
    for n in named:
        prefix = n.split('_')[0]
        prefixes[prefix] += 1

    print("=" * 60)
    print(f"SEAT LEON EDC16U34 — FINAL ACCOUNTING")
    print(f"File: {CFILE.split(chr(92))[-1]}")
    print("=" * 60)
    print(f"TOTAL FUNCTIONS: {total}")
    if total > 0:
        print(f"  Named:    {len(named)}  ({100*len(named)/total:.1f}%)")
        print(f"  Unnamed:  {len(unnamed)} ({100*len(unnamed)/total:.1f}%)")
    print("=" * 60)
    print()
    print("Top 40 named prefixes by function count:")
    for p, c in prefixes.most_common(40):
        print(f"  {p:25s} {c:4d}")
    print()
    print(f"Unnamed FUN_ sample (first 15):")
    for n in unnamed[:15]:
        print(f"  {n}")

if __name__ == '__main__':
    main()