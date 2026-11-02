# @category ECU
# @runtime PyGhidra
# @description Find the ECU ID string for the 0x30 handshake

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    addr = space.getAddress(0x24600)
    func = fm.getFunctionContaining(addr)
    
    print(f"Decompiling Debounce_Def_00024600 @ {func.getEntryPoint()}")
    decomp = DecompInterface()
    decomp.openProgram(prog)
    res = decomp.decompileFunction(func, 30, ConsoleTaskMonitor())
    if res.decompileCompleted():
        print(res.getDecompiledFunction().getC())
    else:
        print("[-] Decompilation failed.")

if __name__ == '__main__':
    run()