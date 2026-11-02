# eeprom_real_hunt.py
# @category ECU
# @runtime PyGhidra
# @description EEPROM driver hunt via register-relative addressing

import os, re
OUT = r"C:\Users\user\Documents\Complete ECU Disassembly\_EEPROM_HUNT.txt"
LINES = []
def w(s): LINES.append(str(s)); print(s)

PROG = currentProgram
fm  = PROG.getFunctionManager()
listing = PROG.getListing()
def A(v): return PROG.getAddressFactory().getDefaultAddressSpace().getAddress(v)

def func_containing(a):
    return fm.getFunctionContaining(a)

# MPC563 SPI/peripheral base ranges
# SIU:    0x2FC000 (in IMMR window)
# DSPI:   0x2FC000+0x2000 area (0x2FC000+offset)
# eQADC:  0x2FC000+0x1000 area
# FlexCAN: 0x2FC000+0x1800 area
# Look for IMMR-relative accesses: lis rX, 0x0002 / 0x0003 etc.
# Also look for known EEPROM opcode shifts: << 1, << 8, << 9, << 10, << 11

candidates = {}

for ins in listing.getInstructions(True):
    s = ins.toString().lower()
    m = ins.getMnemonicString().lower()
    fa = ins.getAddress()

    # Look for 16-bit shifts in the range 8-12 (bit-bang patterns)
    shift = None
    if "<<" in s:
        try:
            amt = int(s.split("<<")[1].strip().split()[0].rstrip(","))
            if 8 <= amt <= 12:
                shift = amt
        except: pass
    if m in ("slwi", "srwi", "rlwinm"):
        try:
            parts = s.split(",")
            if len(parts) >= 3:
                amt = int(parts[2].strip())
                if 8 <= amt <= 12:
                    shift = amt
        except: pass

    if shift is not None:
        f = func_containing(fa)
        if f:
            key = f.getEntryPoint().getOffset()
            candidates.setdefault(key, {"name": f.getName(), "shifts": set(), "count": 0})
            candidates[key]["shifts"].add(shift)
            candidates[key]["count"] += 1

w("=" * 78)
w("EEPM / SPI bit-bang candidates (functions with shifts 8-12)")
w("=" * 78)
ranked = sorted(candidates.items(), key=lambda x: -x[1]["count"])
for ep, info in ranked[:30]:
    w("  %s @ %08x  shifts=%s  count=%d" % (
        info["name"], ep, sorted(info["shifts"]), info["count"]))

w("")
w("=" * 78)
w("DSPI / CAN / SIU absolute access sites")
w("=" * 78)
PERIPH_FUNCS = {}
for ins in listing.getInstructions(True):
    s = ins.toString().lower()
    for tok in re.findall(r'0x[fF][0-9a-fA-F]{7}', s):
        try:
            v = int(tok, 16)
            if 0xF0000000 <= v <= 0xFFFFFFFF:
                f = func_containing(ins.getAddress())
                if f:
                    PERIPH_FUNCS.setdefault(v & 0xFFFF0000, set()).add(f.getName())
        except: pass

for base, fns in sorted(PERIPH_FUNCS.items()):
    w("  block 0x%08x: %d functions" % (base, len(fns)))
    for fn in sorted(fns)[:8]:
        w("    %s" % fn)

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES))
print("[+] wrote %s" % OUT)