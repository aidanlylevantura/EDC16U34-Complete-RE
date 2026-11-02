# @category ECU
# @runtime PyGhidra
# @description Find instructions referencing the low 16-bit offsets of calibration maps.

TARGETS = {
    0x203C: 'ACCCD_aDesLimNeg_CUR',
    0x2052: 'ACCCD_aDesLimPos_CUR',
    0x1D7E: 'ACC_rPedThres_C',
    0x1D94: 'ACC_trqDesMax_C',
    0x1D68: 'ACC_rBrk_CUR',
    0x1D44: 'ACC_dtrqBrkRmpUp_CUR'
}

def run():
    prog = currentProgram
    listing = prog.getListing()
    func_mgr = prog.getFunctionManager()
    
    print("=== Scanning all instructions for ACC Map Offsets ===")
    
    instructions = listing.getInstructions(True)
    count = 0
    
    for inst in instructions:
        mnemonic = inst.getMnemonicString().lower()
        
        # We are looking for offsets used in load/store or math
        if mnemonic not in ['lhz', 'lha', 'lwz', 'sth', 'stw', 'addi', 'addis', 'ori']:
            continue
            
        for i in range(inst.getNumOperands()):
            op_objs = inst.getOpObjects(i)
            for obj in op_objs:
                if hasattr(obj, 'getUnsignedValue'):
                    val = obj.getUnsignedValue()
                    
                    if val in TARGETS:
                        func = func_mgr.getFunctionContaining(inst.getAddress())
                        fname = func.getName() if func else "UNKNOWN"
                        print("FOUND %-22s in %-40s inside %s" % (TARGETS[val], inst, fname))
                        count += 1
                        
    print("\nTotal references found: %d" % count)

if __name__ == '__main__':
    run()