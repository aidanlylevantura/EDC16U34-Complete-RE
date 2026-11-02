# @category ECU
# @runtime PyGhidra
# @description Dump the decompiled C-code of the heavy ACC torque calculation functions.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

TARGET_FUNCS = ["FUN_00054804", "FUN_0005882c", "FUN_00058d4c"]

def run():
    prog = currentProgram
    decomp = DecompInterface()
    decomp.openProgram(prog)
    func_mgr = prog.getFunctionManager()
    
    for target in TARGET_FUNCS:
        for func in func_mgr.getFunctions(True):
            if func.getName() == target:
                print("\n\n==================================================")
                print("=== Decompiled C-Code for %s ===" % func.getName())
                print("==================================================")
                res = decomp.decompileFunction(func, 15, ConsoleTaskMonitor())
                if res.decompileCompleted():
                    print(res.getDecompiledFunction().getC())
                else:
                    print("Decompilation failed.")
                break

if __name__ == '__main__':
    run()