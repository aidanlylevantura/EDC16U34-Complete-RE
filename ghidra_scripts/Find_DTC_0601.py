# @category ECU
# @runtime PyGhidra
# @description Search for the Checksum DTC (P0601) trigger logic.

from ghidra.program.model.symbol import SourceType

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    listing = prog.getListing()
    
    print("=== Searching for Checksum DTC (0x0601 / 601) ===")
    tx = prog.startTransaction("Find Checksum DTC")
    
    # Search for 0x0601 or 0x601 as an immediate value
    for inst in listing.getInstructions(True):
        for i in range(inst.getNumOperands()):
            for obj in inst.getOpObjects(i):
                if hasattr(obj, 'getUnsignedValue'):
                    val = obj.getUnsignedValue()
                    if val in [0x601, 0x0601]:
                        func = fm.getFunctionContaining(inst.getAddress())
                        if func:
                            print("  Found 0x%X in %s @ %s" % (val, func.getName(), inst.getAddress()))
                            # Also check the previous few instructions to see what it's comparing
                            prev = inst.getPrevious()
                            for _ in range(3):
                                if prev: 
                                    print("    Prev: %s" % prev)
                                    prev = prev.getPrevious()

    prog.endTransaction(tx, True)

if __name__ == '__main__':
    run()