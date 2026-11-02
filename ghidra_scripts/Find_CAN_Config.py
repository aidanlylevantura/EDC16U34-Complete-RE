# @runtime Jython
# Find CAN Bus Initialization Code
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    # TouCAN register base addresses
    can_modules = {
        "TouCAN_A": 0x00307080,
        "TouCAN_B": 0x00307480,
        "TouCAN_C": 0x00307880
    }
    
    print("\n--- Scanning for CAN Bus Register Accesses ---")
    
    for name, base_addr in can_modules.items():
        print("\n[%s] Base: 0x%08X" % (name, base_addr))
        # Check the first few registers (MCR, ICR, CTRL0, PRESDIV)
        for offset in range(0, 0x14, 2): 
            reg_addr = space.getAddress(base_addr + offset)
            refs = getReferencesTo(reg_addr)
            if refs is not None:
                for ref in refs:
                    code_addr = ref.getFromAddress()
                    # Only print code references (not data)
                    if listing.getInstructionAt(code_addr) is not None:
                        inst = listing.getInstructionAt(code_addr)
                        print("  -> %s at %s : %s" % (reg_addr, code_addr, inst.toString()))

transaction_id = currentProgram.startTransaction("Find CAN")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)