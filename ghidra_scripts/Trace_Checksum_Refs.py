# @category ECU
# @runtime PyGhidra
# @description Trace references to the end of the flash memory to find the checksum validation code.

from ghidra.program.model.symbol import SourceType

# Common checksum storage addresses at the end of Bosch Flash blocks
CHECKSUM_ADDRS = [
    0x001DFFFC, 0x001DFFFE, 0x001FFFFC, 0x001FFFFE, 
    0x001F0000, 0x001E0000, 0x001CFFFC
]

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    ref_mgr = prog.getReferenceManager()
    fm = prog.getFunctionManager()
    
    print("=== Tracking Checksum Validation Functions ===")
    tx = prog.startTransaction("Trace Checksum")
    
    for addr_val in CHECKSUM_ADDRS:
        addr = space.getAddress(addr_val)
        refs = ref_mgr.getReferencesTo(addr)
        
        for ref in refs:
            from_addr = ref.getFromAddress()
            func = fm.getFunctionContaining(from_addr)
            if func:
                print("  Address 0x%06X accessed by: %s @ %s" % (addr_val, func.getName(), from_addr))
                # Rename the function so we can find it in the C-file
                try:
                    func.setName("Checksum_Validation_Logic", SourceType.USER_DEFINED)
                except:
                    pass
                    
    prog.endTransaction(tx, True)
    print("Done!")

if __name__ == '__main__':
    run()
