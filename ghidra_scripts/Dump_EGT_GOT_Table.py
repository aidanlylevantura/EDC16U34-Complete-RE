# @runtime Jython
# Map the entire EGT GOT Table block
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    mem = currentProgram.getMemory()
    
    start_got = 0x0004CB00
    end_got = 0x0004CC00
    
    print("\n--- Dumping GOT Table Block (0x%08X - 0x%08X) ---" % (start_got, end_got))
    
    for i in range(start_got, end_got, 4):
        addr = space.getAddress(i)
        val = mem.getInt(addr) & 0xFFFFFFFF
        
        # Only print valid Flash addresses (0x1C0000 - 0x1FFFFF)
        if 0x00180000 <= val <= 0x00200000:
            flash_addr = space.getAddress(val)
            sym = getSymbolAt(flash_addr)
            sym_name = sym.getName() if sym else "UNKNOWN (Needs Label)"
            
            print("  GOT %s -> Flash 0x%08X (%s)" % (addr, val, sym_name))

transaction_id = currentProgram.startTransaction("Dump GOT")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)