# @category ECU
# @runtime PyGhidra
# @description Dump the UDS RoutineControl functions by their exact addresses.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

# These are the addresses we found in the Bootloader scan
TARGET_ADDRS = [0x00014c14, 0x000151d0, 0x000a121c]

def run():
    prog = currentProgram
    decomp = DecompInterface()
    decomp.openProgram(prog)
    fm = prog.getFunctionManager()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    for addr_val in TARGET_ADDRS:
        func = fm.getFunctionAt(space.getAddress(addr_val))
        if func:
            print("\n=== Decompiled C-Code for %s @ %s ===" % (func.getName(), func.getEntryPoint()))
            res = decomp.decompileFunction(func, 15, ConsoleTaskMonitor())
            if res.decompileCompleted():
                c_code = res.getDecompiledFunction().getC()
                # Print the whole function
                print(c_code)
            else:
                print("Decompilation failed.")
        else:
            print("\nNo function found at 0x%X" % addr_val)

if __name__ == '__main__':
    run()