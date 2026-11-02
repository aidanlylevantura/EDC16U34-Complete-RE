# @category ECU
# @runtime PyGhidra
# @description Trace back PowerPC register instructions to find the map address building sequence.

from ghidra.program.model.lang import OperandType

TARGET_OFFSETS = [0x203C, 0x2052]

def run():
    prog = currentProgram
    listing = prog.getListing()
    func_mgr = prog.getFunctionManager()
    
    print("=== Searching for Address Build Sequence (lis 0x1C + addi 0x203C/0x2052) ===")
    
    instructions = listing.getInstructions(True)
    
    for inst in instructions:
        mnemonic = inst.getMnemonicString().lower()
        
        # Check for addi rX, rY, 0x203C
        if mnemonic == 'addi':
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    if hasattr(obj, 'getUnsignedValue'):
                        val = obj.getUnsignedValue()
                        if val in TARGET_OFFSETS:
                            func = func_mgr.getFunctionContaining(inst.getAddress())
                            fname = func.getName() if func else "UNKNOWN"
                            print("FOUND addi %s inside %s" % (inst, fname))
                            # Now look backwards up to 5 instructions to find the 'lis'
                            prev = inst.getPrevious()
                            for _ in range(5):
                                if prev is None: break
                                if prev.getMnemonicString().lower() == 'lis':
                                    print("  -> Base loaded by: %s" % prev)
                                    break
                                prev = prev.getPrevious()

if __name__ == '__main__':
    run()