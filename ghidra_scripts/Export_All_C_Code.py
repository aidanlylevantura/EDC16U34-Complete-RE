# @category ECU
# @runtime PyGhidra
# @description Export the fully decompiled C-code of the entire program.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor
import os

OUT_PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    
    decomp = DecompInterface()
    decomp.openProgram(prog)
    
    print("=== Exporting full Decompiled C-Code to %s ===" % OUT_PATH)
    
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("// EDC16U34 Fully Decompiled Code\n\n")
        
        func_count = 0
        for func in fm.getFunctions(True):
            f.write("\n\n// ==================================================\n")
            f.write("// Function: %s @ %s\n" % (func.getName(), func.getEntryPoint()))
            f.write("// ==================================================\n\n")
            
            res = decomp.decompileFunction(func, 30, ConsoleTaskMonitor())
            if res.decompileCompleted():
                c_code = res.getDecompiledFunction().getC()
                f.write(c_code)
                func_count += 1
                
                if func_count % 500 == 0:
                    print("  Exported %d functions..." % func_count)
            else:
                f.write("// Decompilation failed for this function.\n")
                
    print("=== Export Complete! Wrote %d functions to %s ===" % (func_count, OUT_PATH))

if __name__ == '__main__':
    run()