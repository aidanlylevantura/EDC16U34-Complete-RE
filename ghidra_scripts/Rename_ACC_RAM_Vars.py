# @category ECU
# @runtime PyGhidra
# @description Rename the live RAM variables discovered in the ACC State Machine.

from ghidra.program.model.symbol import SourceType

# RAM addresses we discovered in FUN_00056180
RENAMES = {
    0x007f92b0: "ACCCD_stACC_mp",
    0x007f92b2: "ACCCD_stACCnew_mp",
    0x007f92b3: "ACCCD_stBrk_mp",
    0x007f9cbc: "ACCCD_trqDesRaw_mp",
    0x007ffdd8: "ACCCD_stRampState_mp",
    0x007ffddc: "ACCCD_stRampCtrl_mp",
    0x007ffdd5: "ACCCD_stMsg1_mp",
    0x007ffdd6: "ACCCD_stMsg2_mp",
    0x007ffdd9: "ACCCD_stMsg3_mp",
    0x007ffdd4: "ACCCD_RampTimer_mp"
}

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    st = prog.getSymbolTable()

    tx = prog.startTransaction("Rename ACC RAM Variables")
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
                    print("Failed at 0x%08X: %s" % (addr_val, str(e)))
    finally:
        prog.endTransaction(tx, True)
    
    print("Renamed %d variables." % count)

if __name__ == '__main__':
    run()