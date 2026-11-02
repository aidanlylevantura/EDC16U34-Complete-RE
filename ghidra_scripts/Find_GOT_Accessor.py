# @runtime Jython
# Find GOT Accessor for EGT Switch
# @category Automotive

import ghidra.program.model.address.AddressSet as AddressSet

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    mem = currentProgram.getMemory()
    listing = currentProgram.getListing()
    
    # The address of the pointer we found in the previous step
    ptr_address = 0x0004CB70
    
    print("\n--- Searching for code that loads the GOT pointer at 0x%08X ---" % ptr_address)
    
    # Search for the 32-bit raw bytes of the pointer address (00 04 CB 70)
    target_bytes = [ (ptr_address >> 24) & 0xFF, (ptr_address >> 16) & 0xFF, (ptr_address >> 8) & 0xFF, ptr_address & 0xFF ]
    
    start_addr = space.getAddress(0x00000000)
    end_addr = space.getAddress(0x00200000)
    
    # Also scan instructions for immediate value 0x4CB70
    code_set = AddressSet(start_addr, end_addr)
    inst_iter = listing.getInstructions(code_set, True)
    
    found = False
    while inst_iter.hasNext():
        inst = inst_iter.next()
        for i in range(inst.getNumOperands()):
            for obj in inst.getOpObjects(i):
                # Check if the instruction loads 0x4CB70
                if obj.toString() == "0x4cb70" or obj.toString() == "0x4CB70" or obj.toString() == "314224":
                    found = True
                    print("\n[FOUND ACCESSOR] Instruction at %s : %s" % (inst.getAddress(), inst.toString()))
                    
                    # Print the 15 instructions around this to see the full context
                    sub_iter = listing.getInstructions(inst.getAddress(), True)
                    cnt = 0
                    while sub_iter.hasNext() and cnt < 15:
                        sub = sub_iter.next()
                        print("   %s : %s" % (sub.getAddress(), sub.toString()))
                        cnt += 1
                    print("--------------------------------------------------")

    if not found:
        print("No immediate loads of 0x4CB70 found. (The code might use a different base register for the GOT).")
        
    # Dump the memory around the pointer to see if it's a struct
    print("\n--- Dumping memory around 0x%08X ---" % ptr_address)
    dump_start = space.getAddress(ptr_address - 0x10)
    for i in range(8): # 8 words (32 bytes)
        addr = dump_start.add(i * 4)
        try:
            val = mem.getInt(addr)
            print("  %s : 0x%08X" % (addr, val & 0xFFFFFFFF))
        except:
            pass

transaction_id = currentProgram.startTransaction("Find GOT Accessor")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)
print("\n>>> Script Complete. <<<")