# @category ECU
# @runtime PyGhidra
# @description Dump the UDS Security Access (Seed/Key) algorithm.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def run():
    prog = currentProgram
    decomp = DecompInterface()
    decomp.openProgram(prog)
    fm = prog.getFunctionManager()
    
    # We know the function is around 000017a4
    func = fm.getFunctionAt(prog.getAddressFactory().getDefaultAddressSpace().getAddress(0x000017a4))
    if func:
        print("=== Decompiling UDS_27_SecurityAccess ===")
        res = decomp.decompileFunction(func, 15, ConsoleTaskMonitor())
        if res.decompileCompleted():
            print(res.getDecompiledFunction().getC())
        else:
            print("Decompilation failed.")

if __name__ == '__main__':
    run()