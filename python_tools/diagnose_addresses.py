import re, argparse

ADDR_CSV = re.compile(r'\$([0-9A-Fa-f]{4,8})')
HEX_C    = re.compile(r'(0x[0-9A-Fa-f]{4,8}|[0-9A-Fa-f]{6,8}h|\$[0-9A-Fa-f]{4,8}|\b[0-9A-Fa-f]{8}\b)')

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

    print("=== CSV: first 5 Damos entries ===")
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
                print("  %-42s  $%s  (0x%08X)" % (name, m.group(1), v))
            if len(csv_addrs) >= 500: break

    print("\n=== C-file: hex token styles (top 20) ===")
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
        print("  %-20s  x%d" % (t, c))

    print("\n=== C-file: first lines containing 0x ===")
    for ln, txt in samples:
        print("  L%d: %s" % (ln, txt))

    c_addrs = [to_int(t) for t in counts]
    c_addrs = [v for v in c_addrs if v is not None]
    print("\n=== Address ranges ===")
    if csv_addrs:
        print("  CSV:    0x%08X .. 0x%08X" % (min(csv_addrs), max(csv_addrs)))
    if c_addrs:
        print("  C-file: 0x%08X .. 0x%08X" % (min(c_addrs), max(c_addrs)))
    if csv_addrs and c_addrs:
        print("  Delta:  min %+d  max %+d" % (min(c_addrs)-min(csv_addrs), max(c_addrs)-max(csv_addrs)))

if __name__ == '__main__':
    main()