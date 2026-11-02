# @category ECU
# @runtime PyGhidra
# @description Search for EEPROM and Immobilizer strings and trace their functions (Fixed).

from ghidra.program.model.symbol import SourceType

def run():
    prog = currentProgram
    ref_mgr = prog.getReferenceManager()
    fm = prog.getFunctionManager()
    
    print("=== Searching for EEPROM / Immobilizer Strings ===")
    
    defined_data = prog.getListing().getDefinedData(True)
    found = 0
    
    for data in defined_data:
        if data.hasStringValue():
            # FIXED: Simply use str() instead of .toString()
            val = str(data.getValue()).upper()
            if "EEP" in val or "WFS" in val or "IMMO" in val or "WEGFAHR" in val:
                print("  Found String: '%s' at %s" % (val, data.getAddress()))
                
                refs = ref_mgr.getReferencesTo(data.getAddress())
                for ref in refs:
                    func = fm.getFunctionContaining(ref.getFromAddress())
                    if func:
                        print("    -> Referenced in: %s" % func.getName())
                        try:
                            func.setName("EEPROM_Driver_" + func.getName(), SourceType.USER_DEFINED)
                        except:
                            pass
                        found += 1
                        
    if found == 0:
        print("  No strings found.")

if __name__ == '__main__':
    run()