# @category ECU
# @runtime PyGhidra
# @description Rename the Turbo (PCR) RAM variables based on the C-code analysis.

from ghidra.program.model.symbol import SourceType

RAM_RENAMES = {
    # From PCR_CalculateDesiredBoost
    0x007f9b9a: "PCR_pBDes_mp",           # Desired Boost Pressure
    0x007f9b9e: "PCR_nTrbn_mp",           # Turbo Speed (X-axis)
    0x009ffc96: "PCR_pBDes_Base_mp",      # Base Boost Map Output
    0x009ffc9a: "PCR_pBDes_Gov_mp",       # Governor Output
    0x009ffca8: "PCR_stCtlStatus_mp",     # Control Status Bitfield
    
    # From PCR_Governor_PID
    0x007f9ba2: "PCR_dpBErr_mp",          # Boost Pressure Error (Desired - Actual)
    0x007f9ba4: "PCR_rBPGov_mp",          # PID Governor Duty Cycle
    
    # From PCR_MainController
    0x007f9ba6: "PCR_rBPCtl_mp",          # Final VGT Vane Position (%)
    0x007f9ba8: "PCR_qCtl_mp",            # Turbo Control Quantity
}

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    st = prog.getSymbolTable()

    tx = prog.startTransaction("Finalize Turbo System")
    count = 0
    try:
        for addr_val, new_name in RAM_RENAMES.items():
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