# @category ECU
# @runtime PyGhidra
# @description Rename Accelerator Pedal RAM variables based on Damos mappings.

from ghidra.program.model.symbol import SourceType

RENAMES = {
    # From FUN_0005882c (ACC_PedalTorqueDesired)
    0x007f9d44: "AccPed_trqDes_mp",      # The final requested engine torque
    0x007f98d2: "AccPed_rChkdVal_mp",    # The checked pedal position (0-100%)
    0x007f9824: "AccPed_facConv_mp",     # Conversion factor (pedal % to torque)
    
    # From FUN_00058d4c (ACC_PedalTorqueCalculation)
    0x007f9d4c: "AccPed_trqLead_mp",     # The leading requested torque
    0x007f9c90: "VSSCD_v_mp",            # Vehicle speed (X-axis for pedal maps)
    0x007f9622: "Eng_nAvrg_mp",          # Engine speed (Y-axis for pedal maps)
    0x007fa0a0: "VSSCD_v_2_mp",          # Alternate vehicle speed signal
    
    # Pedal Plausibility / Brake interaction
    0x007f932a: "AccPed_swtSport_mp",    # Sport mode active
    0x007f9485: "AccPed_stClutch_mp",    # Clutch pedal status
    0x007ffdb4: "AccPed_rPrev_mp",       # Previous pedal position
}

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    st = prog.getSymbolTable()

    tx = prog.startTransaction("Rename Pedal Variables")
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
