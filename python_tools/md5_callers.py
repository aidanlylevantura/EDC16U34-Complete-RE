# md5_callers.py
# @category ECU
# @runtime PyGhidra
# @description Find callers of MD5 at 0x601c and 0x26768

import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\user\Documents\Complete ECU Disassembly\_MD5_CALLERS.txt"
LINES = []
def w(s):
    LINES.append(str(s))
    try: print(s)
    except: pass

PROG = currentProgram
fm  = PROG.getFunctionManager()
rm  = PROG.getReferenceManager()
def A(v): return PROG.getAddressFactory().getDefaultAddressSpace().getAddress(v)

di = DecompInterface()
di.openProgram(PROG)

for addr in (0x601c, 0x26768):
    f = fm.getFunctionAt(A(addr))
    if not f:
        w("[!] no function at 0x%x" % addr)
        continue
    w("=" * 78)
    w("MD5 @ 0x%x - %s  (size=%d bytes)"
      % (addr, f.getName(), f.getBody().getNumAddresses()))
    w("=" * 78)
    w("")
    w("Callers:")
    seen = set()
    for r in rm.getReferencesTo(f.getEntryPoint()):
        fa = r.getFromAddress()
        cf = fm.getFunctionContaining(fa)
        if cf:
            ep = cf.getEntryPoint().getOffset()
            w("  %s @ %08x   (call site 0x%08x)"
              % (cf.getName(), ep, fa.getOffset()))
            if ep not in seen:
                seen.add(ep)
    w("")
    w("Decompiled callers (first 3 unique):")
    n = 0
    for ep in list(seen)[:3]:
        cf = fm.getFunctionAt(A(ep))
        if not cf: continue
        w("-" * 78)
        w("%s @ %08x" % (cf.getName(), ep))
        w("-" * 78)
        r2 = di.decompileFunction(cf, 60, ConsoleTaskMonitor())
        cc = r2.getDecompiledFunction().getC() if r2.decompileCompleted() else "// fail"
        for line in cc.split("\n")[:100]:
            w("  " + line)
        w("")
        n += 1

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LINES))
print("[+] wrote %s" % OUT)