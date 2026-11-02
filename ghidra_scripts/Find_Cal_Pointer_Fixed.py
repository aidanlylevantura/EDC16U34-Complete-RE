# @category ECU
# @runtime PyGhidra
# @description Search memory for pointers to a specific calibration map and trace xrefs.

TARGET = 0x001C203C

def run():
    prog = currentProgram
    mem = prog.getMemory()
    ref_mgr = prog.getReferenceManager()
    func_mgr = prog.getFunctionManager()
    
    print("=== Searching for pointer to 0x%08X ===" % TARGET)
    
    hits = []
    for block in mem.getBlocks():
        if not block.isInitialized():
            continue
        start = block.getStart()
        end = block.getEnd()
        addr = start
        while addr <= end:
            try:
                # Read 4 bytes as an integer
                val = mem.getInt(addr)
                if val == TARGET:
                    hits.append(addr)
            except:
                pass
            addr = addr.add(4)
            
    if not hits:
        print("No pointers found.")
        return
        
    for ptr_addr in hits:
        print("Found pointer at %s" % ptr_addr)
        refs = ref_mgr.getReferencesTo(ptr_addr)
        if refs:
            for ref in refs:
                from_addr = ref.getFromAddress()
                func = func_mgr.getFunctionContaining(from_addr)
                fname = func.getName() if func else "UNKNOWN"
                print("  -> Referenced by code at: %s (inside %s)" % (from_addr, fname))
        else:
            print("  -> No direct code xrefs (might be loaded via base register).")

if __name__ == '__main__':
    run()