# @category ECU
# @runtime PyGhidra
# @description Rename Turbo (PCR) functions and identify the structure base.

from ghidra.program.model.symbol import SourceType

FUNCTION_RENAMES = {
    0x000d6420: "PCR_CalculateDesiredBoost",
    0x000d6abc: "PCR_Governor_PID",
    0x000d5fa0: "PCR_MainController",
    0x000d7ddc: "PCR_AntiClatterDamping"
}

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    tx = prog.startTransaction("Rename Turbo Functions")
    for addr_val, new_name in FUNCTION_RENAMES.items():
        func = fm.getFunctionAt(space.getAddress(addr_val))
        if func:
            old_name = func.getName()
            func.setName(new_name, SourceType.USER_DEFINED)
            print("Renamed %s -> %s" % (old_name, new_name))
    prog.endTransaction(tx, True)
    print("Done.")

if __name__ == '__main__':
    run()