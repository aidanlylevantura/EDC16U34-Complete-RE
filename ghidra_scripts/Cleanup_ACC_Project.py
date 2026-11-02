# @category ECU
# @runtime PyGhidra
# @description Auto-rename key ACC functions and RAM variables discovered during reverse engineering.

from ghidra.program.model.symbol import SourceType
from ghidra.program.model.address import AddressSet

# 1. Functions to rename
FUNCTION_RENAMES = {
    0x00056180: "ACC_StateMachine_Main",
    0x00054804: "ACC_TorqueCalculation_Core",
    0x0005882c: "ACC_PedalTorqueDesired",
    0x00058d4c: "ACC_PedalTorqueCalculation",
    0x00058694: "ACC_InterpolateLimitMap",
    0x000f8948: "Math_SatAdd",
    0x000f89f4: "Math_SatSub",
    0x000f8a50: "Math_Mul",
    0x000f8ae4: "Math_Div",
    0x000f8c00: "Math_Mul_Shift"
}

# 2. Global RAM variables to rename (Damos mapped)
RAM_RENAMES = {
    0x007f92b0: "ACCCD_stACC_mp",
    0x007f92b2: "ACCCD_stACCnew_mp",
    0x007f92b3: "ACCCD_stBrk_mp",
    0x007f9cbc: "ACCCD_trqDesRaw_mp",
    0x007f9e2c: "ACCCD_trqDesLim_mp",
    0x007ffdc4: "ACCCD_trqDesRamped_mp",
    
    0x007f93f0: "ACC_stMainSwitch_mp",
    0x007f9447: "ACC_stSystemState_mp",
    0x007f9427: "ACC_stShutOff_mp",
    0x007f951a: "ACC_stCrCtl_Input_mp",
    
    0x007f92be: "ACC_stCrCtl_Out_mp",
    0x007f92bf: "ACC_stDrvBrk_Out_mp",
    0x007f92c1: "ACC_stOvrRun_Out_mp",
    
    0x007f9cd0: "ACC_trqDes_mp",
    0x007f9cd8: "ACC_trqLead_mp",
    
    0x007f9d44: "AccPed_trqDes_mp",
    0x007f9d4c: "AccPed_trqLead_mp",
    
    0x007ffdd8: "ACCCD_stRampState_mp",
    0x007ffddc: "ACCCD_stRampCtrl_mp"
}

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    st = prog.getSymbolTable()
    space = prog.getAddressFactory().getDefaultAddressSpace()

    print("=== Starting ACC Project Cleanup ===")
    
    tx = prog.startTransaction("Cleanup ACC Project")
    
    func_count = 0
    var_count = 0
    
    # Rename Functions
    print("\n-- Renaming Functions --")
    for addr_val, new_name in FUNCTION_RENAMES.items():
        addr = space.getAddress(addr_val)
        func = fm.getFunctionAt(addr)
        if func:
            old_name = func.getName()
            try:
                func.setName(new_name, SourceType.USER_DEFINED)
                print("  %s -> %s" % (old_name, new_name))
                func_count += 1
            except Exception as e:
                print("  Failed to rename function at 0x%08X: %s" % (addr_val, str(e)))
        else:
            print("  No function found at 0x%08X" % addr_val)

    # Rename RAM Variables
    print("\n-- Renaming RAM Variables --")
    for addr_val, new_name in RAM_RENAMES.items():
        addr = space.getAddress(addr_val)
        try:
            # createLabel will overwrite the DAT_xxxx or existing label
            st.createLabel(addr, new_name, SourceType.USER_DEFINED)
            print("  Renamed variable at 0x%08X -> %s" % (addr_val, new_name))
            var_count += 1
        except Exception as e:
            print("  Failed to rename variable at 0x%08X: %s" % (addr_val, str(e)))

    prog.endTransaction(tx, True)
    
    print("\n=== SUMMARY ===")
    print("Functions renamed: %d" % func_count)
    print("Variables renamed: %d" % var_count)
    print("Done! Open the Decompiler to see the changes.")

if __name__ == '__main__':
    run()