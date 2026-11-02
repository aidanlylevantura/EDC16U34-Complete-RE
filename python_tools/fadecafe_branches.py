# seed_source.py
# @category ECU
# @runtime PyGhidra
# @description Find writers of seed at 0x7fd9a8 and decompile them

import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\user\Documents\Complete ECU Disassembly\_SEED_SOURCE.txt"
LINES = []
def w(s): LINES.append(str(s)); print(s)

PROG = currentProgram
fm  = PROG.getFunctionManager()
rm  = PROG.getReferenceManager()
def A(v): return PROG.getAddressFactory().getDefaultAddressSpace().getAddress(v)

di = DecompInterface(); di.openProgram(PROG)

TARGET = 0x7fd9a8
w("=" * 78)
w("Writers/readers of seed storage 0x%x" % TARGET)
w("=" * 78)

seen = set()
for r in rm.getReferencesTo(A(TARGET)):
    fa = r.getFromAddress()
    cf = fm.getFunctionContaining(fa)
    ref_type = str(r.getReferenceType())
    w("  %-30s from %08x in %s" % (
        ref_type, fa.getOffset(), cf.getName() if cf else "(no fn)"))
    if cf and "WRITE" in ref_type.upper():
        ep = cf.getEntryPoint().getOffset()
        if ep not in seen:
            seen.add(ep)
            w("")
            w("  --- writer function: %s @ %08x ---" % (cf.getName(), ep))
            res = di.decompileFunction(cf, 60, ConsoleTaskMonitor())
            c = res.getDecompiledFunction().getC() if res.decompileCompleted() else "// fail"
            for line in c.split("\n")[:80]:
                w("    " + line)
            w("")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES))
print("[+] wrote %s" % OUT)