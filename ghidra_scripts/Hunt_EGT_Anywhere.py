# @runtime Jython
# Aggressive EGT Address Hunter
# @category Automotive

import ghidra.program.model.address.AddressSet as AddressSet

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    mem = currentProgram.getMemory()
    listing = currentProgram.getListing()
    
    target_addr = 0x001D1240
    print("\n--- Hunting for 0x%08X across the ENTIRE 2MB binary ---" % target_addr)
    
    # =================================================================
    # PART 1: Scan the raw bytes of the entire binary for the 32-bit pointer
    # =================================================================
    target_bytes = [ (target_addr >> 24) & 0xFF, (target_addr >> 16) & 0xFF, (target_addr >> 8) & 0xFF, target_addr & 0xFF ]
    
    start_addr = space.getAddress(0x00000000)
    end_addr = space.getAddress(0x00200000) # 2MB
    
    print("\n[PART 1] Searching raw bytes for pointer...")
    addr_iter = mem.findBytes(start_addr, end_addr, target_bytes, None, True, monitor)
    
    if addr_iter is None:
        print("  -> No raw 32-bit pointer (00 1D 12 40) found anywhere in Flash.")
    else:
        while addr_iter is not None:
            print("  [FOUND RAW POINTER] at %s" % addr_iter)
            refs = getReferencesTo(addr_iter)
            if refs is not None:
                for ref in refs:
                    print("    -> Code reads this pointer at: %s" % ref.getFromAddress())
            addr_iter = mem.findBytes(addr_iter.next(), end_addr, target_bytes, None, True, monitor)

    # =================================================================
    # PART 2: Scan all instructions for immediate values of 0x1D1240
    # =================================================================
    print("\n[PART 2] Scanning instructions for immediate loads...")
    # We scan the first 1MB (usually where code lives)
    code_set = AddressSet(space.getAddress(0x00000000), space.getAddress(0x00180000))
    inst_iter = listing.getInstructions(code_set, True)
    
    found_inst = False
    while inst_iter.hasNext():
        inst = inst_iter.next()
        # Check operands for the target address
        for i in range(inst.getNumOperands()):
            op_objs = inst.getOpObjects(i)
            for obj in op_objs:
                if obj.toString() == "0x1d1240" or obj.toString() == "0x1D1240" or obj.toString() == "1913408":
                    found_inst = True
                    print("\n  [FOUND IMMEDIATE LOAD] at %s : %s" % (inst.getAddress(), inst.toString()))
                    # Print following 10 instructions
                    sub_iter = listing.getInstructions(inst.getAddress(), True)
                    cnt = 0
                    while sub_iter.hasNext() and cnt < 10:
                        sub = sub_iter.next()
                        print("     %s : %s" % (sub.getAddress(), sub.toString()))
                        cnt += 1
                        
    if not found_inst:
        print("  -> No instructions directly load 0x1D1240 as an immediate.")

    # =================================================================
    # PART 3: Verify the r13 SDA Base
    # =================================================================
    print("\n[PART 3] Checking r13 SDA Setup...")
    r13_lis_addr = space.getAddress(0x00000228) # From your previous output
    if listing.getInstructionAt(r13_lis_addr) is not None:
        inst_iter = listing.getInstructions(r13_lis_addr, True)
        cnt = 0
        while inst_iter.hasNext() and cnt < 5:
            inst = inst_iter.next()
            print("  %s : %s" % (inst.getAddress(), inst.toString()))
            cnt += 1

# EXECUTION
transaction_id = currentProgram.startTransaction("Hunt EGT")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)
print("\n>>> Hunt Complete. <<<")