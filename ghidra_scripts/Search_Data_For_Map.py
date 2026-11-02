# @category ECU
# @runtime PyGhidra
# @description Search ALL initialized memory for the exact 32-bit value 0x1C203C.

def run():
    prog = currentProgram
    mem = prog.getMemory()
    func_mgr = prog.getFunctionManager()
    ref_mgr = prog.getReferenceManager()
    
    print("=== Searching Data for 0x001C203C ===")
    
    for block in mem.getBlocks():
        if not block.isInitialized(): continue
        
        addr = block.getStart()
        end = block.getEnd()
        while addr <= end:
            try:
                val = mem.getInt(addr)
                if val == 0x001C203C:
                    print("Found 0x1C203C at data address: %s" % addr)
                    refs = ref_mgr.getReferencesTo(addr)
                    for ref in refs:
                        f = func_mgr.getFunctionContaining(ref.getFromAddress())
                        print("  -> Referenced by: %s" % (f.getName() if f else "UNKNOWN"))
            except:
                pass
            addr = addr.add(4)
            
    print("Done.")

if __name__ == '__main__':
    run()