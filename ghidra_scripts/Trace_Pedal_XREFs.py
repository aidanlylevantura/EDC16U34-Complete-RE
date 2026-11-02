# @category ECU
# @runtime PyGhidra
# @description Trace XREFs to the renamed AccPed RAM variables to find the main Pedal logic.

from ghidra.program.model.symbol import SourceType

TARGET_VARS = {
    0x007F98D2: "AccPed_rChkdVal_mp",
    0x007F9D44: "AccPed_trqDes_mp",
    0x007FFDB4: "AccPed_rPrev_mp"
}

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    ref_mgr = prog.getReferenceManager()
    func_mgr = prog.getFunctionManager()

    print("=== Tracing Pedal RAM Variable References ===")
    
    for addr_val, name in TARGET_VARS.items():
        addr = space.getAddress(addr_val)
        print("\n--- References to %s (0x%08X) ---" % (name, addr_val))
        
        refs = ref_mgr.getReferencesTo(addr)
        found_funcs = set()
        
        for ref in refs:
            from_addr = ref.getFromAddress()
            func = func_mgr.getFunctionContaining(from_addr)
            if func:
                fname = func.getName()
                if fname not in found_funcs:
                    found_funcs.add(fname)
                    print("  -> %s (at %s)" % (fname, from_addr))
                    
        if not found_funcs:
            print("  -> No function references found. (Might be read by an inline assembly block or pointer)")

if __name__ == '__main__':
    run()