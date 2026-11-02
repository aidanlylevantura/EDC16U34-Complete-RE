# @runtime Jython
# Trace backwards to find the EGT DTC trigger
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    func_mgr = currentProgram.getFunctionManager()
    
    dtc_start = space.getAddress(0x000dbf24)
    
    print("\n--- Locating DTC block context ---")
    
    # 1. Find the function that contains this DTC block
    func = func_mgr.getFunctionContaining(dtc_start)
    if func is not None:
        print("DTC code is inside function: %s at %s" % (func.getName(), func.getEntryPoint()))
    else:
        print("Function not defined by Ghidra. Showing raw preceding instructions.")
        
    # 2. Find the instructions leading up to the DTC block
    print("\n--- Instructions immediately preceding 0x000DBF24 ---")
    
    # Go back 120 bytes (about 30 instructions)
    start_addr = dtc_start.subtract(120) 
    inst_iter = listing.getInstructions(start_addr, True)
    
    while inst_iter.hasNext():
        inst = inst_iter.next()
        
        # Stop when we hit the DTC block
        if inst.getAddress().compareTo(dtc_start) >= 0:
            break
            
        print("  %s : %s" % (inst.getAddress(), inst.toString()))

    # 3. Look for branches that jump ANYWHERE in the vicinity of the DTC
    print("\n--- Searching for branches to the DTC vicinity (0x000DBF00 - 0x000DBF40) ---")
    
    # We use a loop to check a small range
    for offset in range(0, 0x40, 4):
        check_addr = space.getAddress(0x000dbf00 + offset)
        refs = getReferencesTo(check_addr)
        
        if refs is not None:
            for ref in refs:
                if ref.getReferenceType().isJump() or ref.getReferenceType().isConditional():
                    print("  [BRANCH FOUND] at %s jumping to %s" % (ref.getFromAddress(), check_addr))
                    # Print the branch instruction itself
                    inst = listing.getInstructionAt(ref.getFromAddress())
                    if inst:
                        print("     %s : %s" % (inst.getAddress(), inst.toString()))

transaction_id = currentProgram.startTransaction("Trace DTC")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)
print("\n>>> Trace Complete. <<<")