# @category ECU
# @runtime PyGhidra
# @description Trace references to the end of the calibration block to find the checksum function.

from ghidra.program.model.symbol import SourceType

# The end of the calibration block in EDC16U34
CAL_END = 0x001E0000

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    ref_mgr = prog.getReferenceManager()
    fm = prog.getFunctionManager()
    
    print("=== Tracing Checksum Function References ===")
    
    # Check the last 16 bytes of the calibration block
    for offset in range(-16, 0, 2):
        addr_val = CAL_END + offset
        addr = space.getAddress(addr_val)
        
        refs = ref_mgr.getReferencesTo(addr)
        for ref in refs:
            from_addr = ref.getFromAddress()
            func = fm.getFunctionContaining(from_addr)
            if func:
                print("  Checksum address 0x%06X referenced in: %s @ %s" % (addr_val, func.getName(), from_addr))
                
                # Rename the function so we can find it later
                if "FUN_" in func.getName():
                    try:
                        func.setName("Checksum_Calculation", SourceType.USER_DEFINED)
                    except:
                        pass

if __name__ == '__main__':
    run()
