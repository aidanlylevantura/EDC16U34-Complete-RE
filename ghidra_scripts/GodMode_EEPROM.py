# @category ECU
# @runtime PyGhidra
# @description Map the EEPROM SPI driver and Immobilizer functions.

from ghidra.program.model.symbol import SourceType

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    st = prog.getSymbolTable()
    
    print("=== Mapping EEPROM and Immobilizer Functions ===")
    tx = prog.startTransaction("Map EEPROM")
    
    count = 0
    # Look for functions that reference ImmCtl, Spi, or Eeprom in their string/symbols
    for func in fm.getFunctions(True):
        name = func.getName().lower()
        if "imm" in name or "eeprom" in name or "spi" in name:
            print("  Found EEPROM/Immobilizer function: %s @ %s" % (func.getName(), func.getEntryPoint()))
            count += 1
            
    if count == 0:
        print("  No direct symbol names found. Searching for SPI peripheral registers (0xF0000000 range)...")
        # If symbols aren't there, we look for the SPI hardware registers
        for inst in prog.getListing().getInstructions(True):
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    if hasattr(obj, 'getUnsignedValue'):
                        val = obj.getUnsignedValue()
                        # EDC16 SPI bus is usually mapped to specific peripherals
                        if 0xF0000000 <= val <= 0xF000FFFF:
                            func = fm.getFunctionContaining(inst.getAddress())
                            if func:
                                print("  SPI Register access in: %s @ %s" % (func.getName(), inst.getAddress()))
                                break
                                
    prog.endTransaction(tx, True)

if __name__ == '__main__':
    run()