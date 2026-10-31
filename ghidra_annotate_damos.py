# @category ECU
# @runtime PyGhidra
# @description Load WinOLS Damos CSV and create labels + plate comments in the current program.

import re
from ghidra.program.model.symbol import SourceType
from ghidra.program.model.listing import CodeUnit

DAMOS_CSV   = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
BASE_OFFSET = None    # None = auto-detect. Set to 0, 0x80000000, etc. to force.

def parse_csv(path):
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

def detect_base(prog, damos):
    space = prog.getAddressFactory().getDefaultAddressSpace()
    mem   = prog.getMemory()
    candidates = [0, prog.getImageBase().getOffset(), 0x80000000, 0x400000, 0xC0000000]
    sample = damos[:200]
    best, best_hits = None, -1
    for base in candidates:
        hits = sum(1 for _, a, _ in sample if mem.contains(space.getAddress(base + a)))
        print("  candidate base 0x%08X -> %d/%d hits" % (base, hits, len(sample)))
        if hits > best_hits:
            best, best_hits = base, hits
    return best

def run():
    prog = currentProgram
    print("Program: %s" % prog.getName())
    print("Image base: 0x%08X" % prog.getImageBase().getOffset())

    damos = parse_csv(DAMOS_CSV)
    print("Damos rows: %d" % len(damos))

    if not damos:
        print("No Damos rows parsed. Check the CSV path in DAMOS_CSV.")
        return

    base = BASE_OFFSET if BASE_OFFSET is not None else detect_base(prog, damos)
    print("Using base offset: 0x%08X" % base)

    af    = prog.getAddressFactory()
    space = af.getDefaultAddressSpace()
    mem   = prog.getMemory()
    listing = prog.getListing()
    st    = prog.getSymbolTable()

    created, skipped, outside, errors = 0, 0, 0, 0
    tx = prog.startTransaction("Annotate Damos")
    try:
        for name, daddr, desc in damos:
            try:
                gaddr = space.getAddress(base + daddr)
                if not mem.contains(gaddr):
                    outside += 1
                    continue
                existing = st.getPrimarySymbol(gaddr)
                if existing is None or existing.getName() != name:
                    st.createLabel(gaddr, name, SourceType.USER_DEFINED)
                try:
                    listing.setComment(gaddr, CodeUnit.PLATE_COMMENT,
                                       "Damos: %s\n%s" % (name, desc))
                except:
                    pass
                created += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print("  ERR 0x%08X %s : %s" % (daddr, name, str(e)))
    finally:
        prog.endTransaction(tx, True)

    print("\n=== SUMMARY ===")
    print("Created:         %d" % created)
    print("Outside memory:  %d" % outside)
    print("Errors:          %d" % errors)

if __name__ == '__main__':
    run()