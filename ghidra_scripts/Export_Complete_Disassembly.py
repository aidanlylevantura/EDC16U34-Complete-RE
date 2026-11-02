# @runtime Jython
# Export all decompiled functions to a text file
# @category Automotive

import os
from ghidra.app.decompiler import DecompInterface

def run():
    print("\n--- Decompiling entire ECU (This will take 5-10 minutes) ---")
    
    # Set output path
    out_path = "C:\\Users\\user\\Documents\\Complete ECU Disassembly\\EDC16U34_Complete_Disassembly.c"
    
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    
    func_mgr = currentProgram.getFunctionManager()
    funcs = func_mgr.getFunctions(True)
    
    count = 0
    with open(out_path, 'w') as f:
        f.write("// =====================================================================\n")
        f.write("// COMPLETE SOFTWARE DISASSEMBLY: EDC16U34 (Seat Leon 1.9 TDI)\n")
        f.write("// Generated via Ghidra\n")
        f.write("// =====================================================================\n\n")
        
        while funcs.hasNext():
            func = funcs.next()
            
            # Skip thunks or external functions if necessary
            if func.isThunk():
                continue
                
            res = decompiler.decompileFunction(func, 60, monitor)
            
            if res.decompileCompleted():
                f.write("\n\n// =====================================================================\n")
                f.write("// FUNCTION: %s at %s\n" % (func.getName(), func.getEntryPoint()))
                f.write("// =====================================================================\n")
                f.write(res.getDecompiledFunction().getC())
                count += 1
                
            if count % 200 == 0:
                print("Exported %d functions..." % count)

    print("\nFinished! Exported %d functions to:\n%s" % (count, out_path))

transaction_id = currentProgram.startTransaction("Export Code")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)