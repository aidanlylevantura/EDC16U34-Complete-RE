# @runtime Jython
# Find ACC Logic
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    # --- PUT THE ADDRESS YOU FOUND FROM THE FINDSTR COMMAND HERE ---
    acc_flash_addr = 0x001D3456 # <--- CHANGE THIS
    
    print("\n--- Searching for ACC Address (0x%08X) ---" % acc_flash_addr)
    
    addr = space.getAddress(acc_flash_addr)
    refs = getReferencesTo(addr)
    
    if refs is None:
        print("No direct references found. (Try another ACC address from the CSV)")
    else:
        for ref in refs:
            code_addr = ref.getFromAddress()
            inst = listing.getInstructionAt(code_addr)
            if inst is not None:
                print("\n[FOUND ACC LOGIC] at %s : %s" % (code_addr, inst.toString()))
                # Print 15 instructions
                sub_iter = listing.getInstructions(code_addr, True)
                cnt = 0
                while sub_iter.hasNext() and cnt < 15:
                    sub = sub_iter.next()
                    print("   %s : %s" % (sub.getAddress(), sub.toString()))
                    cnt += 1