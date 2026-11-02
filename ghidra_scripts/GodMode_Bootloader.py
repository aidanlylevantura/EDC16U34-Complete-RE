# @category ECU
# @runtime PyGhidra
# @description Map the Bootloader, UDS Flash routines, and Seed/Key security access.

from ghidra.program.model.symbol import SourceType

def run():
    prog = currentProgram
    st = prog.getSymbolTable()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    fm = prog.getFunctionManager()
    
    print("=== 1. Mapping Bootloader Functions (0x00000000 - 0x00008000) ===")
    tx = prog.startTransaction("Map Bootloader")
    
    boot_funcs = 0
    for func in fm.getFunctions(True):
        addr = func.getEntryPoint().getOffset()
        if 0x00000000 <= addr <= 0x00008000:
            try:
                st.createLabel(func.getEntryPoint(), "BOOT_" + func.getName(), SourceType.USER_DEFINED)
                boot_funcs += 1
            except:
                pass
    print("  Mapped %d Bootloader functions." % boot_funcs)

    print("\n=== 2. Searching for UDS Diagnostic Services ===")
    # Look for the standard UDS service IDs in the code
    uds_services = {0x10: "DiagSessionControl", 0x27: "SecurityAccess(Seed/Key)", 
                    0x34: "RequestDownload", 0x36: "TransferData", 0x31: "RoutineControl"}
    
    for inst in prog.getListing().getInstructions(True):
        mnem = inst.getMnemonicString().lower()
        if mnem in ['cmpi', 'cmpwi', 'cmpdi']:
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    if hasattr(obj, 'getUnsignedValue'):
                        val = obj.getUnsignedValue()
                        if val in uds_services:
                            func = fm.getFunctionContaining(inst.getAddress())
                            if func:
                                print("  Found UDS %02X (%s) in %s at %s" % (val, uds_services[val], func.getName(), inst.getAddress()))
                                # Rename the function if it hasn't been named yet
                                if "FUN_" in func.getName():
                                    func.setName("UDS_%02X_%s" % (val, uds_services[val].split('(')[0]), SourceType.USER_DEFINED)

    prog.endTransaction(tx, True)
    print("\nDone!")

if __name__ == '__main__':
    run()