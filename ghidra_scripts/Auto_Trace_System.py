# @category ECU
# @runtime PyGhidra
# @description Automatically trace the entry points, maps, and functions of a specific system.

from ghidra.program.model.symbol import SourceType

# CHANGE THIS TO TRACE OTHER SYSTEMS: "PCR" (Turbo), "EGR", "PFlt" (DPF), "Inj"
SYSTEM_PREFIX = "PCR" 

def run():
    prog = currentProgram
    st = prog.getSymbolTable()
    ref_mgr = prog.getReferenceManager()
    func_mgr = prog.getFunctionManager()
    
    print("=== Auto-Tracing System: %s ===" % SYSTEM_PREFIX)
    
    vectors = []
    maps = []
    
    # 1. Find Vectors and Maps
    for sym in st.getAllSymbols(True):
        name = sym.getName()
        if name.startswith(SYSTEM_PREFIX):
            if "_Vector" in name:
                vectors.append(sym)
            elif "_MAP" in name or "_CUR" in name:
                maps.append(sym)
                
    print("\n-- 1. CALIBRATION MAPS (%d found) --" % len(maps))
    for m in maps[:10]: # Print first 10
        print("  %s @ %s" % (m.getName(), m.getAddress()))
        
    print("\n-- 2. BYPASS VECTORS (%d found) --" % len(vectors))
    for v in vectors:
        print("\n  Vector: %s @ %s" % (v.getName(), v.getAddress()))
        refs = ref_mgr.getReferencesTo(v.getAddress())
        for ref in refs:
            from_addr = ref.getFromAddress()
            func = func_mgr.getFunctionContaining(from_addr)
            if func:
                print("    -> Used in function: %s (%s)" % (func.getName(), func.getEntryPoint()))
                
if __name__ == '__main__':
    run()