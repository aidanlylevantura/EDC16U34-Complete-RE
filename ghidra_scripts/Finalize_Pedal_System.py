# @category ECU
# @runtime PyGhidra
# @description Rename the Pedal Component Driver, Plausibility Check, and Sensor variables.

from ghidra.program.model.symbol import SourceType

FUNCTION_RENAMES = {
    0x0009a58c: "APPCD_PedalSensorDriver",    # Converts raw pedal voltage to %
    0x000deb38: "AccPed_PlausibilityCheck",   # Checks Sensor 1 vs Sensor 2
}

RAM_RENAMES = {
    # Raw Pedal Sensors (from FUN_000deb38)
    0x007f9626: "APPCD_uAPP1_mp",  # Pedal Sensor 1 Voltage
    0x007f9628: "APPCD_uAPP2_mp",  # Pedal Sensor 2 Voltage
    0x007fa072: "APPCD_uAPP_Max_mp", # Maximum Pedal Voltage
    0x007fa0d4: "APPCD_rAPP_Dflt_mp", # Default Pedal Position
    
    # Pedal Plausibility Status
    0x007f9518: "AccPed_stPlausActive_mp",
    0x007f9519: "AccPed_stPlausError_mp",
    0x007f9c0a: "AccPed_rAPP_Raw_mp",
    0x007f98d0: "APPCD_rAPP_Percent_mp",
}

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    st = prog.getSymbolTable()
    space = prog.getAddressFactory().getDefaultAddressSpace()

    print("=== Finalizing Accelerator Pedal System ===")
    tx = prog.startTransaction("Finalize Pedal System")
    
    for addr_val, new_name in FUNCTION_RENAMES.items():
        func = fm.getFunctionAt(space.getAddress(addr_val))
        if func:
            old_name = func.getName()
            func.setName(new_name, SourceType.USER_DEFINED)
            print("  Renamed Function %s -> %s" % (old_name, new_name))

    for addr_val, new_name in RAM_RENAMES.items():
        st.createLabel(space.getAddress(addr_val), new_name, SourceType.USER_DEFINED)
        print("  Renamed Variable at 0x%08X -> %s" % (addr_val, new_name))

    prog.endTransaction(tx, True)
    print("\nDone! Export the C-file again to see the fully mapped Pedal logic.")

if __name__ == '__main__':
    run()