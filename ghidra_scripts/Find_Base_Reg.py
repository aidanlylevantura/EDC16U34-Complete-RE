# @category ECU
# @runtime PyGhidra
# @description Find where the ECU loads the calibration base address (0x001C0000).

def run():
    prog = currentProgram
    listing = prog.getListing()
    func_mgr = prog.getFunctionManager()
    
    print("=== Searching for 'lis' loading 0x001C (Calibration Base) ===")
    
    instructions = listing.getInstructions(True)
    count = 0
    
    for inst in instructions:
        text = inst.toString().lower()
        # In PowerPC, lis r3, 0x1c loads 0x001C0000
        if inst.getMnemonicString().lower() == 'lis':
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    if hasattr(obj, 'getUnsignedValue') and obj.getUnsignedValue() == 0x1C:
                        func = func_mgr.getFunctionContaining(inst.getAddress())
                        fname = func.getName() if func else "UNKNOWN"
                        print("FOUND %-30s inside %s" % (inst, fname))
                        count += 1
                        
    print("\nTotal references found: %d" % count)

if __name__ == '__main__':
    run()