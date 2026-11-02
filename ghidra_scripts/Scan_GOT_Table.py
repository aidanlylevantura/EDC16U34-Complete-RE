# @runtime Jython
# Brute-force scan for instructions accessing the GOT table range
# @category Automotive

import ghidra.program.model.address.AddressSet as AddressSet

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    print("\n--- Brute-force scanning instructions for GOT access (0x4CB70) ---")
    
    # We scan the entire code section
    code_set = AddressSet(space.getAddress(0x00000000), space.getAddress(0x00180000))
    inst_iter = listing.getInstructions(code_set, True)
    
    found = False
    while inst_iter.hasNext():
        inst = inst_iter.next()
        
        # Check all operands in the instruction
        for i in range(inst.getNumOperands()):
            op_str = inst.getDefaultOperandRepresentation(i).lower()
            
            # Look for the address, the lower half, or the negative offset equivalent
            if "0x4cb" in op_str or "0xcb70" in op_str or "-0x3490" in op_str:
                found = True
                print("\n[FOUND POTENTIAL GOT ACCESS] at %s : %s" % (inst.getAddress(), inst.toString()))
                
                # Print 12 instructions starting from 4 instructions BEFORE the match
                # This shows us the 'lis' instruction that sets up the register
                start_addr = inst.getAddress().subtract(16)
                sub_iter = listing.getInstructions(start_addr, True)
                cnt = 0
                while sub_iter.hasNext() and cnt < 16:
                    sub = sub_iter.next()
                    print("   %s : %s" % (sub.getAddress(), sub.toString()))
                    cnt += 1
                print("--------------------------------------------------")

    if not found:
        print("No instructions matched the GOT access patterns.")
        
        # Alternative: Try finding references to the single exact pointer address
        print("\nTrying Ghidra ReferenceManager directly on 0x0004CB70...")
        ptr_addr = space.getAddress(0x0004CB70)
        refs = getReferencesTo(ptr_addr)
        if refs is None or len(refs) == 0:
            print("ReferenceManager found no references to 0x0004CB70.")
        else:
            for ref in refs:
                print("Found ref at: %s" % ref.getFromAddress())

transaction_id = currentProgram.startTransaction("Scan GOT Table")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)
print("\n>>> Scan Complete. <<<")