# @runtime Jython
# Find the parent function of the CAN Task and decompile it
# @category Automotive

import os
from ghidra.app.decompiler import DecompInterface

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    func_mgr = currentProgram.getFunctionManager()
    
    # The addresses of the CAN function calls
    call_sites = [space.getAddress(0x00023200), space.getAddress(0x00023210)]
    
    print("\n--- Tracing the Parent Function ---")
    
    parent_funcs = []
    for site in call_sites:
        func = func_mgr.getFunctionContaining(site)
        if func is not None and func not in parent_funcs:
            parent_funcs.append(func)
            print("\n[PARENT FUNCTION] %s at %s" % (func.getName(), func.getEntryPoint()))
            
            # Find who calls the parent function
            refs = getReferencesTo(func.getEntryPoint())
            if refs is not None:
                for ref in refs:
                    if ref.getReferenceType().isCall():
                        print("  -> Called by: %s" % ref.getFromAddress())
            else:
                print("  -> No direct callers found (might be in a function pointer table).")
                
            # Decompile the parent function to see the task logic
            decompiler = DecompInterface()
            decompiler.openProgram(currentProgram)
            res = decompiler.decompileFunction(func, 60, monitor)
            
            if res.decompileCompleted():
                print("\n--- Decompiled Code for %s ---" % func.getName())
                # Print first 2000 characters to avoid flooding the console
                c_code = res.getDecompiledFunction().getC()
                print(c_code[:2000] + "\n... [truncated] ...")

transaction_id = currentProgram.startTransaction("Trace Main Loop")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)