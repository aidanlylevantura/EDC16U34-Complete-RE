#!/usr/bin/env python3
"""Diagnose why Damos addresses don't match C-file tokens."""
import re, argparse

ADDR_CSV = re.compile(r'\$([0-9A-Fa-f]{4,8})')
HEX_C    = re.compile(r'(0x[0-9A-Fa-f]{4,8}|[0-9A-Fa-f]{6,8}h\b|\$[0-9A-Fa-f]{4,8}|\b[0-9A-Fa-f]{8}\b)')

def to_int(s):
    s = s.strip().lower()
    if s.startswith('$'): s = s[1:]
    if s.endswith('h'):   s = s[:-1]
    if s.startswith('0x'):s = s[2:]
    try: return int(s, 16)
    except: return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv',   required=True)
    ap.add_argument('--cfile', required=True)
    a = ap.parse_args()

    # --- CSV sample ---
    print("=== CSV: first 5 parsed Damos entries ===")
    csv_addrs = []
    with open(a.csv, encoding='utf-8', errors='replace') as f:
        for line in f:
            parts = line.rstrip('\n').split(';')
            if len(parts) < 2: continue
            name = parts[1].strip()
            if not name: continue
            m = ADDR_CSV.search(line)
            if not m: continue
            v = to_int(m.group(1))
            if v is None: continue
            csv_addrs.append(v)
            if len(csv_addrs) <= 5:
                print(f"  {name:42s}  ${m.group(1)}  (int 0x{v:08X})")
            if len(csv_addrs) >= 500: break

    # --- C-file token histogram ---
    print("\n=== C-file: token styles seen (top 20) ===")
    counts = {}
    samples = []
    with open(a.cfile, encoding='utf-8', errors='replace') as f:
        for i, line in enumerate(f, 1):
            for m in HEX_C.finditer(line):
                t = m.group(0)
                counts[t] = counts.get(t, 0) + 1
                if len(samples) < 3 and '0x' in t.lower():
                    samples.append((i, line.rstrip()[:160]))
    for t, c in sorted(counts.items(), key=lambda x: -x[1])[:20]:
        print(f"  {t:20s}  x{c}")

    print("\n=== C-file: first lines containing 0x ===")
    for ln, txt in samples:
        print(f"  L{ln}: {txt}")

    # --- Range comparison ---
    c_addrs = [to_int(t) for t in counts]
    c_addrs = [v for v in c_addrs if v is not None]
    print("\n=== Address ranges ===")
    if csv_addrs:
        print(f"  CSV:    0x{min(csv_addrs):08X} .. 0x{max(csv_addrs):08X}")
    if c_addrs:
        print(f"  C-file: 0x{min(c_addrs):08X} .. 0x{max(c_addrs):08X}")
    if csv_addrs and c_addrs:
        print(f"  Delta:  min {min(c_addrs)-min(csv_addrs):+d}  max {max(c_addrs)-max(csv_addrs):+d}")

if __name__ == '__main__':
    main()