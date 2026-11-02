# @runtime Jython
# Find the code that uses the RamLoader string
# @category Automotive

import ghidra.program.model.address.AddressSet as AddressSet

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    # The address of the "Bosch.common.RamLoader" string
    string_addr = 0x0006DB8
    
    print("\n--- Searching for code referencing RamLoader (0x%08X) ---" % string_addr)
    
    # Search the first 128KB of code for the address 0x0006DB8
    code_set = AddressSet(space.getAddress(0x00000000), space.getAddress(0x00020000))
    inst_iter = listing.getInstructions(code_set, True)
    
    found = False
    while inst_iter.hasNext():
        inst = inst_iter.next()
        for i in range(inst.getNumOperands()):
            op_str = inst.getDefaultOperandRepresentation(i).lower()
            
            # Look for the 16-bit or 32-bit representation of the string address
            if "0x6db8" in op_str or "0x6d" in op_str:
                found = True
                print("\n[FOUND RAMLOADER REFERENCE] at %s : %s" % (inst.getAddress(), inst.toString()))
                
                # Print surrounding instructions
                start_addr = inst.getAddress().subtract(16)
                sub_iter = listing.getInstructions(start_addr, True)
                cnt = 0
                while sub_iter.hasNext() and cnt < 15:
                    sub = sub_iter.next()
                    print("   %s : %s" % (sub.getAddress(), sub.toString()))
                    cnt += 1
                print("--------------------------------------------------")
                
    if not found:
        print("No direct references found in the startup block.")

transaction_id = currentProgram.startTransaction("Find RamLoader")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)