# @category ECU
# @runtime PyGhidra
# @description Scan memory for 32-bit pointers to the calibration area, and trace XREFs to code.

CAL_MIN = 0x001C0000
CAL_MAX = 0x001E0000

def run():
    prog = currentProgram
    mem = prog.getMemory()
    ref_mgr = prog.getReferenceManager()
    func_mgr = prog.getFunctionManager()

    print("=== Scanning for pointers to Calibration Area (0x%08X - 0x%08X) ===" % (CAL_MIN, CAL_MAX))
    
    found_ptrs = []
    
    # Iterate through all initialized memory blocks
    for block in mem.getBlocks():
        if not block.isInitialized(): continue
        start = block.getStart()
        end = block.getEnd()
        
        # Don't scan the calibration area itself, we want pointers *to* it
        if start.getOffset() >= CAL_MIN and end.getOffset() <= CAL_MAX:
            continue
            
        addr = start
        while addr <= end:
            try:
                # Read 4 bytes as a big-endian 32-bit int
                val = mem.getInt(addr) & 0xFFFFFFFF
                if CAL_MIN <= val <= CAL_MAX:
                    found_ptrs.append((addr, val))
            except:
                pass
            addr = addr.add(4) # Move to next 32-bit word
            
    if not found_ptrs:
        print("No 32-bit pointers found. Bosch is using Base-Register + Offset addressing (lis/addi).")
        return

    print("Found %d pointers to the calibration area.\n" % len(found_ptrs))

    # Let's only print the ACC-related ones so we aren't flooded
    acc_targets = {
        0x001C203C: "ACCCD_aDesLimNeg_CUR",
        0x001C2052: "ACCCD_aDesLimPos_CUR",
        0x001C1D7E: "ACC_rPedThres_C",
        0x001C1D94: "ACC_trqDesMax_C",
        0x001C0A1C: "ACCCD_stACC_Vector",
        0x001C0A10: "ACC_stCrCtl_Vector"
    }

    for ptr_addr, target_addr in found_ptrs:
        if target_addr in acc_targets:
            name = acc_targets[target_addr]
            print("--- %s (Pointer at %s -> 0x%08X) ---" % (name, ptr_addr, target_addr))
            
            refs = ref_mgr.getReferencesTo(ptr_addr)
            if refs:
                for ref in refs:
                    from_addr = ref.getFromAddress()
                    func = func_mgr.getFunctionContaining(from_addr)
                    func_name = func.getName() if func else "UNKNOWN_FUNC"
                    print("  -> Referenced by code at: %s (inside %s)" % (from_addr, func_name))
            else:
                print("  -> No code cross-references found.")
            print("")
            
    if not any(t in acc_targets for _, t in found_ptrs):
         print("Scanned the whole ROM, but no pointers found for the ACC targets.")
         print("The code loads the calibration base (e.g. 0x1C0000) into a register using 'lis'.")

if __name__ == '__main__':
    run()