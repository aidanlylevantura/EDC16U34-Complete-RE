# @category ECU
# @runtime PyGhidra
# @description Find the checksum function by searching for loops that iterate over the calibration base.

from ghidra.program.model.symbol import SourceType
from ghidra.program.model.address import AddressSet

CAL_BASE = 0x001C0000
CAL_END  = 0x00200000  # End of 2MB flash

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    st = prog.getSymbolTable()
    listing = prog.getListing()
    
    print("=== Searching for Checksum Loops (Iterating over 0x1C0000 - 0x1FFFFF) ===")
    tx = prog.startTransaction("Find Checksum Loop")
    
    candidates = []
    
    for func in fm.getFunctions(True):
        insts = listing.getInstructions(func.getBody(), True)
        has_xor = False
        has_add = False
        
        for inst in insts:
            mnem = inst.getMnemonicString().lower()
            if mnem in ['xor', 'xori', 'xor.']: has_xor = True
            if mnem in ['add', 'addi', 'addis']: has_add = True
            
        # Checksum functions are usually small and contain XOR/ADD math
        if (has_xor or has_add) and func.getBody().getNumAddresses() < 200:
            candidates.append(func)
            
    print("Found %d candidates. Checking for calibration base references..." % len(candidates))
    
    for func in candidates:
        # Check if this function or its callers reference the calibration base
        insts = listing.getInstructions(func.getBody(), True)
        for inst in insts:
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    if hasattr(obj, 'getUnsignedValue'):
                        val = obj.getUnsignedValue()
                        # If it loads 0x1C0000 or 0x1C (the high 16 bits)
                        if val in [0x1C0000, 0x1C, 0x1D, 0x1E, 0x1F]:
                            print("  Candidate: %s @ %s (references 0x%X)" % (func.getName(), func.getEntryPoint(), val))
                            try:
                                func.setName("Checksum_Calc_Candidate_" + func.getName(), SourceType.USER_DEFINED)
                            except:
                                pass
                            break
                            
    prog.endTransaction(tx, True)
    print("Done!")

if __name__ == '__main__':
    run()
 