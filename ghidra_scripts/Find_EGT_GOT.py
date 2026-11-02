# @runtime Jython
# Find GOT pointer for EGT Switch
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    target_addr = 0x001D1240
    
    print("\n--- Searching for GOT pointer to 0x%08X ---" % target_addr)
    
    # Convert address to Big Endian byte array
    target_bytes = [ (target_addr >> 24) & 0xFF, (target_addr >> 16) & 0xFF, (target_addr >> 8) & 0xFF, target_addr & 0xFF ]
    
    # Scan the first 64KB where the SDA/GOT usually lives
    start_addr = space.getAddress(0x00000000)
    end_addr = space.getAddress(0x00010000)
    
    addr_iter = currentProgram.getMemory().findBytes(start_addr, end_addr, target_bytes, None, True, monitor)
    
    found_pointer = False
    while addr_iter is not None:
        found_pointer = True
        ptr_address = addr_iter
        print("\n[FOUND] Pointer to EGT Switch located at: %s" % ptr_address)
        
        # Now find who reads this pointer address
        refs = getReferencesTo(ptr_address)
        if refs is None or len(refs) == 0:
            print("  -> No code references this pointer yet. (Auto-analysis may need more time).")
        else:
            print("  -> Found %d code reference(s) to this pointer:" % len(refs))
            for ref in refs:
                code_addr = ref.getFromAddress()
                print("     Code X-Ref at: %s" % code_addr)
                
                # Print 10 instructions
                inst_iter = listing.getInstructions(code_addr, True)
                count = 0
                while inst_iter.hasNext() and count < 10:
                    inst = inst_iter.next()
                    print("       %s : %s" % (inst.getAddress(), inst.toString()))
                    count += 1
                    
        # Look for the next instance (just in case)
        addr_iter = currentProgram.getMemory().findBytes(addr_iter.next(), end_addr, target_bytes, None, True, monitor)

    if not found_pointer:
        print("Could not find a 32-bit pointer to 0x%08X in the first 64KB." % target_addr)

transaction_id = currentProgram.startTransaction("Find EGT GOT")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)