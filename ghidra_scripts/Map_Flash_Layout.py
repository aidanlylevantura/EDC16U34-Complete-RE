# @runtime Jython
# Map the Flash Layout (Find erased vs populated blocks)
# @category Automotive

def run():
    mem = currentProgram.getMemory()
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    
    print("\n--- Flash Layout Analysis (Block Size: 64KB) ---")
    
    block_size = 0x10000 # 64KB
    total_size = 0x200000 # 2MB
    
    for start in range(0, total_size, block_size):
        addr = space.getAddress(start)
        is_empty = True
        
        # Check the first 1024 bytes of the block
        for i in range(0, 0x400):
            try:
                if mem.getByte(addr.add(i)) != 0xFF:
                    is_empty = False
                    break
            except:
                break
                
        status = "EMPTY (0xFF)" if is_empty else "DATA / CODE"
        print("  0x%06X - 0x%06X : %s" % (start, start + block_size - 1, status))

transaction_id = currentProgram.startTransaction("Map Layout")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)