# @category ECU
# @runtime PyGhidra
# @description Search for SID 0x23 and SID 0x40 handlers in the KWP dispatcher

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    # We know the dispatcher is at 0x10F478
    addr = space.getAddress(0x10F478)
    func = fm.getFunctionContaining(addr)
    
    print(f"Decompiling Main Dispatcher @ {func.getEntryPoint()}")
    decomp = DecompInterface()
    decomp.openProgram(prog)
    res = decomp.decompileFunction(func, 30, ConsoleTaskMonitor())
    
    if res.decompileCompleted():
        c_code = res.getDecompiledFunction().getC()
        # Print the specific cases for 0x23, 0x34, and 0x40
        lines = c_code.split('\n')
        printing = False
        for line in lines:
            if "case 0x23:" in line or "case 0x40:" in line or "case 0x34:" in line:
                printing = True
            elif printing and "case" in line:
                printing = False
            
            if printing:
                print(line)
    else:
        print("[-] Decompilation failed.")

if __name__ == '__main__':
    run()