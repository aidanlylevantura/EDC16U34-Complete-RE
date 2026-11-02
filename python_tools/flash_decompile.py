# flash_decompile.py
# @category ECU
# @runtime PyGhidra
# @description Decompile 0x50110, 0x391c, 0x6a0 + locate flash-write sites

import os
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

OUT = r"C:\Users\user\Documents\Complete ECU Disassembly\_FLASH.txt"
LINES = []
def w(s):
    LINES.append(str(s))
    try: print(s)
    except: pass

PROG = currentProgram
fm  = PROG.getFunctionManager()
listing = PROG.getListing()
def A(v): return PROG.getAddressFactory().getDefaultAddressSpace().getAddress(v)

di = DecompInterface()
di.openProgram(PROG)

targets = [
    (0x50110, "FUN_00050110 - RequestDownload setup"),
    (0x391c,  "FUN_0000391c - TransferData / flash write"),
    (0x6a0,   "DSM_FUN_000006a0 - 0x34 dispatcher / boot init"),
]

for addr, label in targets:
    f = fm.getFunctionAt(A(addr))
    w("=" * 78)
    w(label)
    w("=" * 78)
    if not f:
        w("  (no function defined at 0x%x)" % addr)
        w("")
        continue
    w("Function: %s @ %08x  size=%d bytes"
      % (f.getName(), f.getEntryPoint().getOffset(), f.getBody().getNumAddresses()))
    w("")
    r = di.decompileFunction(f, 90, ConsoleTaskMonitor())
    c = r.getDecompiledFunction().getC() if r.decompileCompleted() else "// decompile failed"
    for line in c.split("\n")[:220]:
        w("  " + line)
    w("")
    w("Flash-write sites (store followed by sync/eieio within 8 insns):")
    insns = list(listing.getInstructions(f.getBody(), True))
    hits = 0
    for i, ins in enumerate(insns):
        m = ins.getMnemonicString().lower()
        if m in ("stw","sth","stb","stwu","sthu","stbu"):
            for j in range(i+1, min(i+9, len(insns))):
                mj = insns[j].getMnemonicString().lower()
                if mj in ("sync","isync","eieio","msync"):
                    w("  0x%08x  %-32s ... %s"
                      % (ins.getAddress().getOffset(), ins.toString(), insns[j].toString()))
                    hits += 1
                    break
    if hits == 0:
        w("  (none in this function)")
    w("")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LINES))
print("[+] wrote %s" % OUT)