# @runtime Jython
# Find where the EGT threshold is copied from Flash to RAM
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    # The RAM address we calculated (r13 - 0x640c)
    ram_target = space.getAddress(0x007F9BE4)
    
    print("\n--- Searching for instructions writing to 0x%08X ---" % ram_target.getOffset())
    
    code_set = ghidra.program.model.address.AddressSet(space.getAddress(0x00000000), space.getAddress(0x00020000))
    inst_iter = listing.getInstructions(code_set, True)
    
    found = False
    while inst_iter.hasNext():
        inst = inst_iter.next()
        for i in range(inst.getNumOperands()):
            op_str = inst.getDefaultOperandRepresentation(i).lower()
            
            # Look for the immediate address or the offset
            if "0x7f9be4" in op_str or "0x9be4" in op_str or "-0x640c" in op_str:
                found = True
                print("\n[FOUND INIT] at %s : %s" % (inst.getAddress(), inst.toString()))
                # Print 8 instructions to see the source register
                sub_iter = listing.getInstructions(inst.getAddress().subtract(16), True)
                cnt = 0
                while sub_iter.hasNext() and cnt < 12:
                    sub = sub_iter.next()
                    print("   %s : %s" % (sub.getAddress(), sub.toString()))
                    cnt += 1
                print("--------------------------------------------------")
                
    if not found:
        print("No direct initialization found in the first 128KB.")

transaction_id = currentProgram.startTransaction("Find RAM Init")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)