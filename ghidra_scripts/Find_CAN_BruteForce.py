# @runtime Jython
# Brute-force scan for CAN register initialization
# @category Automotive

import ghidra.program.model.address.AddressSet as AddressSet

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    print("\n--- Brute-force scanning instructions for CAN register access ---")
    
    # Scan the whole code section (0x0 to 0x180000)
    code_set = AddressSet(space.getAddress(0x00000000), space.getAddress(0x00180000))
    inst_iter = listing.getInstructions(code_set, True)
    
    found = False
    while inst_iter.hasNext():
        inst = inst_iter.next()
        
        # Check all operands
        for i in range(inst.getNumOperands()):
            op_str = inst.getDefaultOperandRepresentation(i).lower()
            
            # Look for the upper halves of the CAN addresses
            if "0x3070" in op_str or "0x7480" in op_str or "0x7880" in op_str or \
               "0x7080" in op_str or "0x7480" in op_str or "0x7880" in op_str:
                
                found = True
                print("\n[FOUND CAN ACCESS] at %s : %s" % (inst.getAddress(), inst.toString()))
                
                # Print 10 instructions around it to see the initialization sequence
                start_addr = inst.getAddress().subtract(8)
                sub_iter = listing.getInstructions(start_addr, True)
                cnt = 0
                while sub_iter.hasNext() and cnt < 12:
                    sub = sub_iter.next()
                    print("   %s : %s" % (sub.getAddress(), sub.toString()))
                    cnt += 1
                print("--------------------------------------------------")
                
    if not found:
        print("No CAN access instructions found in the first 1.5MB.")
        print("This means either:")
        print("1. The CAN module is initialized in a part of the flash we didn't scan.")
        print("2. The CAN module is accessed via a completely different memory map offset.")

transaction_id = currentProgram.startTransaction("Find CAN BruteForce")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)