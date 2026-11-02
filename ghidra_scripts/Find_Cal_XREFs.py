# @category ECU
# @runtime PyGhidra
# @description Find calibration maps by searching for their 4-byte Big-Endian pointers, then trace code XREFs.

import re
from ghidra.program.model.address import AddressSet

# Change these if you want to search for different variables
TARGETS = {
    'ACCCD_aDesLimNeg_CUR': 0x001C203C,
    'ACCCD_aDesLimPos_CUR': 0x001C2052,
    'ACC_rPedThres_C':      0x001C1D7E,
    'ACC_trqDesMax_C':      0x001C1D94
}

def search_pointer(prog, target_addr):
    # Create 4-byte big-endian byte pattern (PowerPC)
    b = [ (target_addr >> 24) & 0xFF, (target_addr >> 16) & 0xFF, (target_addr >> 8) & 0xFF, target_addr & 0xFF ]
    pattern = " ".join(["%02x" % x for x in b])
    print("  Searching memory for bytes: %s (Big-Endian pointer)" % pattern)
    
    hits = []
    mem = prog.getMemory()
    # Search only initialized memory
    search_set = AddressSet()
    for block in mem.getBlocks():
        if block.isInitialized():
            search_set.addRange(block.getStart(), block.getEnd())
            
    addr_iter = prog.getAddressFactory().getDefaultAddressSpace().getAddress(0)
    current = search_set.getMinAddress()
    while current is not None:
        found = mem.findBytes(current, search_set.getMaxAddress(), b, None, True, None)
        if found is not None:
            hits.append(found)
            current = found.add(1)
        else:
            break
    return hits

def run():
    prog = currentProgram
    print("=== Tracing Calibration Variables ===")
    
    for name, target_addr in TARGETS.items():
        print("\n--- %s (0x%08X) ---" % (name, target_addr))
        ptr_locations = search_pointer(prog, target_addr)
        
        if not ptr_locations:
            print("  No pointers found in memory. The map might not be referenced in this calibration.")
            continue
            
        for ptr_addr in ptr_locations:
            print("  Found pointer at address: %s" % ptr_addr)
            
            # Get cross-references to this pointer location
            refs = prog.getReferenceManager().getReferencesTo(ptr_addr)
            if refs:
                for ref in refs:
                    from_addr = ref.getFromAddress()
                    func = prog.getFunctionManager().getFunctionContaining(from_addr)
                    func_name = func.getName() if func else "UNKNOWN_FUNC"
                    print("    -> Referenced by code at: %s (inside %s)" % (from_addr, func_name))
            else:
                print("    -> No code cross-references found (might be loaded via base register offset).")

if __name__ == '__main__':
    run()