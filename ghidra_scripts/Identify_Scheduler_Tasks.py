# @runtime Jython
# Identify the tasks called by the main scheduler
# @category Automotive

import os
from ghidra.app.decompiler import DecompInterface

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    func_mgr = currentProgram.getFunctionManager()
    decompiler = DecompInterface()
    decompiler.openProgram(currentProgram)
    
    # The unique tasks called in FUN_00023214
    tasks = [
        0x00021d44,
        0x0001782c,
        0x000238bc,
        0x0002343c,
        0x0001b1f4,
        0x0001da2c,
        0x000138f0,
        0x00013788,
        0x000219a4
    ]
    
    print("\n--- Decompiling Scheduler Tasks ---")
    
    for task_addr in tasks:
        addr = space.getAddress(task_addr)
        func = func_mgr.getFunctionAt(addr)
        if func is None:
            func = func_mgr.getFunctionContaining(addr)
            
        if func is not None:
            print("\n=======================================================")
            print("TASK: %s at %s" % (func.getName(), func.getEntryPoint()))
            print("=======================================================")
            
            res = decompiler.decompileFunction(func, 30, monitor)
            if res.decompileCompleted():
                c_code = res.getDecompiledFunction().getC()
                # Print only the first 15 lines to see what it's doing
                lines = c_code.split('\n')
                for line in lines[:15]:
                    print(line)
                print("... [truncated] ...")

transaction_id = currentProgram.startTransaction("Identify Tasks")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)