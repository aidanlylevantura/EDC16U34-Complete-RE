# @category ECU
# @runtime PyGhidra
# @description Dump the C-code of the Turbo Desired Boost calculation.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def run():
    prog = currentProgram
    decomp = DecompInterface()
    decomp.openProgram(prog)
    fm = prog.getFunctionManager()
    
    target = "PCR_CalculateDesiredBoost"
    for func in fm.getFunctions(True):
        if func.getName() == target:
            print("\n=== Decompiled C-Code for %s ===" % func.getName())
            res = decomp.decompileFunction(func, 15, ConsoleTaskMonitor())
            if res.decompileCompleted():
                c_code = res.getDecompiledFunction().getC()
                print("\n".join(c_code.split("\n")[:120])) # Print first 120 lines
            break

if __name__ == '__main__':
    run()