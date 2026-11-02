# @category ECU
# @runtime PyGhidra
# @description Dump the decompiled C-code of the ACC Torque Limiter.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

TARGET_FUNCTION = "FUN_000f89f4"

def run():
    prog = currentProgram
    decomp = DecompInterface()
    decomp.openProgram(prog)
    func_mgr = prog.getFunctionManager()
    
    for func in func_mgr.getFunctions(True):
        if func.getName() == TARGET_FUNCTION or func.getName() == "FUN_000f89f4":
            print("=== Decompiling %s ===" % func.getName())
            res = decomp.decompileFunction(func, 15, ConsoleTaskMonitor())
            if res.decompileCompleted():
                print(res.getDecompiledFunction().getC())
            else:
                print("Decompilation failed: " + res.getErrorMessage())
            return
            
    print("Function %s not found!" % TARGET_FUNCTION)

if __name__ == '__main__':
    run()