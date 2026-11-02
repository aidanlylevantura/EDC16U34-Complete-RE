# md5_disambiguate.py
# @category ECU
# @runtime PyGhidra
# @description Show input buffer contents for each MD5 caller

import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\user\Documents\Complete ECU Disassembly\_MD5_DISAMBIG.txt"
LINES = []
def w(s): LINES.append(str(s)); print(s)

PROG = currentProgram
fm  = PROG.getFunctionManager()
def A(v): return PROG.getAddressFactory().getDefaultAddressSpace().getAddress(v)

di = DecompInterface(); di.openProgram(PROG)

# For each caller, trace what buffer is being hashed
callers = {
    "0x601c (MD5 #1)": [
        (0x6a38, "State_Init_00006a38"),
        (0x6b1c, "State_auto_006b1c"),
    ],
    "0x26768 (MD5 #2)": [
        (0x272f8, "State_auto_0272f8"),
        (0x2723c, "State_Init_0002723c"),
        (0x271c4, "State_auto_0271c4"),
    ],
}

for md5_name, callers_list in callers.items():
    w("=" * 78)
    w("MD5 %s" % md5_name)
    w("=" * 78)
    for addr, name in callers_list:
        f = fm.getFunctionAt(A(addr))
        if not f:
            w("  no function at 0x%x" % addr); continue
        w("")
        w("  --- caller: %s @ 0x%x ---" % (name, addr))
        res = di.decompileFunction(f, 60, ConsoleTaskMonitor())
        c = res.getDecompiledFunction().getC() if res.decompileCompleted() else "// fail"
        # Only show lines with the hash call or buffer references
        for line in c.split("\n"):
            low = line.lower()
            if any(k in low for k in ("md5", "debounce_auto_00601c", "state_helper_auto_026768",
                                       "0x7f8ee4", "0x7f8ed4", "param_2", "0x7fa8", "0x7fd8")):
                w("    " + line)
        w("")

with open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(LINES))
print("[+] wrote %s" % OUT)