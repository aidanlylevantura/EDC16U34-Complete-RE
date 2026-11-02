# dump_functions.py
# @category ECU
# @runtime Jython
# @description Dump function names to _FUNCTIONS.txt
import os

OUT = r"C:\Users\user\Documents\Complete ECU Disassembly\_FUNCTIONS.txt"

lines = []
fm = currentProgram.getFunctionManager()
for f in fm.getFunctions(True):
    name = f.getName()
    ep = f.getEntryPoint().getOffset()
    sz = f.getBody().getNumAddresses()
    lines.append("%s  0x%08X  %d" % (name, ep, sz))

with open(OUT, "w") as fh:
    fh.write("\n".join(lines))

print("[+] wrote %s (%d functions)" % (OUT, len(lines)))