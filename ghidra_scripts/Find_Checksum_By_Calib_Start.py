# @category ECU
# @runtime PyGhidra
# @description Find the checksum function by searching for the calibration base address (0x1C0000).

from ghidra.program.model.symbol import SourceType
from ghidra.program.model.address import AddressSet

CAL_START = 0x001C0000

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    listing = prog.getListing()
    
    print("=== Searching for functions referencing Calibration Start (0x1C0000) ===")
    tx = prog.startTransaction("Find Checksum by Base")
    
    for func in fm.getFunctions(True):
        body = func.getBody()
        insts = listing.getInstructions(body, True)
        
        uses_cal_base = False
        has_xor = False
        has_add = False
        
        for inst in insts:
            mnem = inst.getMnemonicString().lower()
            if mnem in ['xor', 'xori']: has_xor = True
            if mnem in ['add', 'addi']: has_add = True
            
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    if hasattr(obj, 'getUnsignedValue'):
                        val = obj.getUnsignedValue()
                        # Look for 0x1C0000 or the high half 0x1C (from lis instruction)
                        if val == 0x1C0000 or val == 0x1C or val == 0x1C00:
                            uses_cal_base = True
                            
        if uses_cal_base and (has_xor or has_add):
            print("\n  Candidate: %s @ %s" % (func.getName(), func.getEntryPoint()))
            print("  (Contains Calibration Base + Math Operations)")
            
            # Rename it so we can find it later
            try:
                func.setName("Checksum_Candidate_" + func.getName(), SourceType.USER_DEFINED)
            except:
                pass
                
    prog.endTransaction(tx, True)
    print("\nDone!")

if __name__ == '__main__':
    run()