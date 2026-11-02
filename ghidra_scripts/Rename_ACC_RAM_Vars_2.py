# @category ECU
# @runtime PyGhidra
# @description Rename remaining ACC State Machine variables.

from ghidra.program.model.symbol import SourceType

RENAMES = {
    0x007f9e2c: "ACCCD_trqDesLim_mp",      # The limit applied to torque
    0x007f9e28: "ACCCD_aDesLim_mp",        # The raw acceleration limit
    0x007ffdc4: "ACCCD_trqDesRamped_mp",   # The ramped torque request
    0x007f93f0: "ACC_stMainSwitch_mp",     # Main ACC Switch / Radar Status
    0x007f9447: "ACC_stSystemState_mp",    # Overall System State
    0x007f9427: "ACC_stShutOff_mp",        # Shutoff conditions
    0x007f951a: "ACC_stCrCtl_mp"           # Cruise Control active state
}

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    st = prog.getSymbolTable()

    tx = prog.startTransaction("Rename ACC RAM Vars 2")
    count = 0
    try:
        for addr_val, new_name in RENAMES.items():
            addr = space.getAddress(addr_val)
            if addr is not None:
                try:
                    st.createLabel(addr, new_name, SourceType.USER_DEFINED)
                    print("Renamed 0x%08X -> %s" % (addr_val, new_name))
                    count += 1
                except Exception as e:
                    pass
    finally:
        prog.endTransaction(tx, True)
    
    print("Renamed %d variables." % count)

if __name__ == '__main__':
    run()