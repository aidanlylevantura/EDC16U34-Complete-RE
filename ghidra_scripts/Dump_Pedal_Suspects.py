# @category ECU
# @runtime PyGhidra
# @description Dump the C-code of candidate Pedal Plausibility functions.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

TARGET_FUNCS = ["FUN_000deb38", "FUN_0009a58c"]

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
                    # Print only the first 80 lines to keep it readable
                    c_code = res.getDecompiledFunction().getC()
                    print("\n".join(c_code.split("\n")[:80]))
                else:
                    print("Decompilation failed.")
                break

if __name__ == '__main__':
    run()