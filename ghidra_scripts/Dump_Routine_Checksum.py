# @category ECU
# @runtime PyGhidra
# @description Dump the UDS RoutineControl function that likely verifies checksums.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

# The UDS_31_RoutineControl function found in the Bootloader
TARGET = "UDS_31_RoutineControl"

def run():
    prog = currentProgram
    decomp = DecompInterface()
    decomp.openProgram(prog)
    fm = prog.getFunctionManager()
    
    for func in fm.getFunctions(True):
        if func.getName() == TARGET:
            print("\n=== Decompiled C-Code for %s @ %s ===" % (func.getName(), func.getEntryPoint()))
            res = decomp.decompileFunction(func, 20, ConsoleTaskMonitor())
            if res.decompileCompleted():
                c_code = res.getDecompiledFunction().getC()
                # Print the first 150 lines to see the math
                print("\n".join(c_code.split("\n")[:150]))
            else:
                print("Decompilation failed.")
            break

if __name__ == '__main__':
    run()