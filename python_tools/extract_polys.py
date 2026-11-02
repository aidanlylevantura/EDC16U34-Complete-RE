# extract_polys.py
# @category ECU
# @runtime PyGhidra
# @description Read LFSR poly table at 0x2240

import os

OUT = r"C:\Users\user\Documents\Complete ECU Disassembly\_POLYS.txt"
LINES = []
def w(s):
    LINES.append(str(s))
    try: print(s)
    except: pass

PROG = currentProgram
mem  = PROG.getMemory()
def A(v): return PROG.getAddressFactory().getDefaultAddressSpace().getAddress(v)

def u32(off):
    a = A(off)
    if not mem.contains(a): return None
    return ((mem.getByte(a) & 0xFF) << 24) | \
           ((mem.getByte(a.add(1)) & 0xFF) << 16) | \
           ((mem.getByte(a.add(2)) & 0xFF) << 8) | \
           (mem.getByte(a.add(3)) & 0xFF)

w("LFSR POLY TABLE @ 0x2240 (32-bit BE):")
polys = []
for i in range(64):
    v = u32(0x2240 + i*4)
    if v is None: break
    polys.append(v)
    w("  [%2d] 0x%08x" % (i, v))

def lfsr(seed, poly, rounds):
    x = seed & 0xFFFFFFFF
    for _ in range(rounds):
        if x & 0x80000000:
            x = ((x << 1) & 0xFFFFFFFF) ^ poly
        else:
            x = (x << 1) & 0xFFFFFFFF
    return x

w("")
w("Self-test, seed=0x12345678, level=3 (index=2, rounds=0x26):")
if len(polys) > 2:
    for r in (16, 0x23, 0x26, 0x27, 0x30):
        w("  rounds=0x%02x -> 0x%08x" % (r, lfsr(0x12345678, polys[2], r)))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LINES))
print("[+] wrote %s" % OUT)