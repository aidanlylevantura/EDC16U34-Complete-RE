# @runtime Jython
# Decompile the Main Scheduler Loop that calls the CAN Task
# @category Automotive

import os
from ghidra.app.decompiler import DecompInterface

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    func_mgr = currentProgram.getFunctionManager()
    
    # The address of the first caller in the cluster
    caller_site = space.getAddress(0x00023224)
    
    print("\n--- Tracing the Main Scheduler Loop ---")
    
    parent_func = func_mgr.getFunctionContaining(caller_site)
    if parent_func is None:
        print("Could not find parent function.")
        return
        
    print("[MAIN SCHEDULER] %s at %s" % (parent_func.getName(), parent_func.getEntryPoint()))
    
    # Decompile the main scheduler
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    res = decompiler.decompileFunction(parent_func, 90, monitor)
    
    if res.decompileCompleted():
        print("\n--- Decompiled Main Scheduler Code ---")
        c_code = res.getDecompiledFunction().getC()
        print(c_code)
    else:
        print("Decompilation failed or timed out.")

transaction_id = currentProgram.startTransaction("Trace Scheduler")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)