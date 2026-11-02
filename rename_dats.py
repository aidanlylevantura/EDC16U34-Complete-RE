import re, argparse, collections

GHIDRA_REF = re.compile(r'\b(DAT|LAB|FUN|UNK|SUB|PTR|EXT)_([0-9a-fA-F]{8})\b')

def load_damos(path):
    addr2name = {}
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
            addr2name.setdefault(addr, name)
    return addr2name

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--cfile', required=True)
    ap.add_argument('--out', default=None)
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--keep-marker', action='store_true', default=True)
    a = ap.parse_args()

    addr2name = load_damos(a.csv)
    print("Damos entries loaded: %d" % len(addr2name))

    with open(a.cfile, encoding='utf-8', errors='replace') as f:
        text = f.read()

    hits = collections.Counter()
    def repl(m):
        kind, hexaddr = m.group(1), m.group(2)
        addr = int(hexaddr, 16)
        if addr in addr2name:
            hits[addr] += 1
            suffix = " /* %s_%s */" % (kind, hexaddr) if a.keep_marker else ""
            return addr2name[addr] + suffix
        return m.group(0)

    new_text, count = GHIDRA_REF.subn(repl, text)
    print("Total symbol references rewritten: %d" % count)
    print("Unique addresses touched:           %d" % len(hits))

    if hits:
        print("\nAll annotated symbols (sorted by hit count):")
        for addr, cnt in sorted(hits.items(), key=lambda x: -x[1]):
            print("  0x%08X  %-42s  x%d" % (addr, addr2name[addr], cnt))
    else:
        print("\nNo matches. The calibration block is not referenced by absolute address")
        print("in this decompile. Try ghidra_annotate_damos.py inside Ghidra instead.")

    if a.dry_run:
        print("\n[dry-run] not writing output")
        return

    out = a.out or (a.cfile + ".renamed.c")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("\nWrote: %s" % out)

if __name__ == '__main__':
    main()