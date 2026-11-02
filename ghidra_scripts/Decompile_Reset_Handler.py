# @runtime Jython
# Decompile the System Reset Handler
# @category Automotive

import os
from ghidra.app.decompiler import DecompInterface

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    func_mgr = currentProgram.getFunctionManager()
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    
    # The System Reset Vector target
    reset_target = space.getAddress(0x00000180)
    
    print("\n--- Decompiling System Reset Handler (0x00000180) ---")
    
    func = func_mgr.getFunctionContaining(reset_target)
    if func is None:
        # Create function if Ghidra missed it
        createFunction(reset_target, "System_Reset_Handler")
        func = func_mgr.getFunctionAt(reset_target)
        
    if func is not None:
        print("Function: %s at %s" % (func.getName(), func.getEntryPoint()))
        res = decompiler.decompileFunction(func, 60, monitor)
        if res.decompileCompleted():
            print(res.getDecompiledFunction().getC())

transaction_id = currentProgram.startTransaction("Decompile Reset")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)