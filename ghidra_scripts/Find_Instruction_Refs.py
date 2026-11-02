# @category ECU
# @runtime PyGhidra
# @description Scan instructions for hardcoded offsets of ACC calibration maps.

TARGETS = {
    0x203C: 'ACCCD_aDesLimNeg_CUR',
    0x2052: 'ACCCD_aDesLimPos_CUR',
    0x1D7E: 'ACC_rPedThres_C',
    0x1D94: 'ACC_trqDesMax_C',
    0x0A1C: 'ACCCD_stACC_Vector'
}

def run():
    prog = currentProgram
    listing = prog.getListing()
    func_mgr = prog.getFunctionManager()
    
    print("=== Scanning instructions for ACC map offsets ===")
    
    instructions = listing.getInstructions(True)
    count = 0
    
    for inst in instructions:
        # We only care about PowerPC instructions that load addresses (lis, ori, addi)
        mnemonic = inst.getMnemonicString().lower()
        if mnemonic not in ['lis', 'ori', 'addi', 'lwz', 'stw']:
            continue
            
        for i in range(inst.getNumOperands()):
            op_objs = inst.getOpObjects(i)
            for obj in op_objs:
                if hasattr(obj, 'getUnsignedValue'):
                    val = obj.getUnsignedValue()
                    # Check if the value matches our target offset
                    if val in TARGETS:
                        func = func_mgr.getFunctionContaining(inst.getAddress())
                        fname = func.getName() if func else "UNKNOWN"
                        print("Found %s in instruction: %s  (inside %s)" % (TARGETS[val], inst, fname))
                        count += 1

    print("\nTotal references found: %d" % count)

if __name__ == '__main__':
    run()