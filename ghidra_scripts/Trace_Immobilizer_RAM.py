# @category ECU
# @runtime PyGhidra
# @description Trace ImmCtl (Immobilizer) RAM variables to find the EEPROM SPI driver.

from ghidra.program.model.symbol import SourceType

def run():
    prog = currentProgram
    st = prog.getSymbolTable()
    ref_mgr = prog.getReferenceManager()
    fm = prog.getFunctionManager()
    
    print("=== Tracing Immobilizer (ImmCtl) Variables ===")
    
    immo_vars = []
    # 1. Find all variables related to Immobilizer
    for sym in st.getAllSymbols(True):
        name = sym.getName()
        if "ImmCtl" in name or "Imm_" in name or "WFS" in name:
            immo_vars.append(sym)
            
    print("Found %d Immobilizer variables." % len(immo_vars))
    
    # 2. Trace who uses them
    found_funcs = set()
    for var in immo_vars:
        refs = ref_mgr.getReferencesTo(var.getAddress())
        for ref in refs:
            func = fm.getFunctionContaining(ref.getFromAddress())
            if func and func.getName() not in found_funcs:
                found_funcs.add(func.getName())
                print("  Immobilizer variable '%s' used in: %s @ %s" % (var.getName(), func.getName(), func.getEntryPoint()))
                
                # Rename the function to make it obvious
                try:
                    if "FUN_" in func.getName():
                        func.setName("Immobilizer_" + func.getName(), SourceType.USER_DEFINED)
                except:
                    pass
                    
    if not found_funcs:
        print("  No Immobilizer RAM variables found or referenced yet.")
        print("  (You may need to run Master_Auto_Annotate.py again to map the RAM variables).")

if __name__ == '__main__':
    run()