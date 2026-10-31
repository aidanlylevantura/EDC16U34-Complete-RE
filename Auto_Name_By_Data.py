# @category ECU
# @runtime PyGhidra
# @description Name unnamed functions based on the Damos data they access.

import re
from collections import Counter
from ghidra.program.model.symbol import SourceType

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    st = prog.getSymbolTable()
    
    all_funcs = list(fm.getFunctions(True))
    unnamed = [f for f in all_funcs if f.getName().startswith("FUN_")]
    print("Unnamed functions to process: %d" % len(unnamed))
    
    # 1. Build a map of Data Addresses -> Damos Prefix
    addr_to_prefix = {}
    prefix_re = re.compile(r'^([A-Za-z][A-Za-z0-9]{1,10})_')
    
    for sym in st.getAllSymbols(True):
        name = sym.getName()
        if name.startswith("FUN_") or name.startswith("LAB_") or name.startswith("DAT_"):
            continue
        m = prefix_re.match(name)
        if m:
            addr_to_prefix[sym.getAddress().getOffset()] = m.group(1)
            
    print("Mapped %d Damos data addresses to system prefixes." % len(addr_to_prefix))

    renamed = 0
    tx = prog.startTransaction("Auto Name By Data")
    try:
        for f in unnamed:
            prefixes_hit = Counter()
            peripheral_pfx = None
            
            inst_iter = prog.getListing().getInstructions(f.getBody(), True)
            for inst in inst_iter:
                # Ask Ghidra for the references this instruction makes
                for ref in inst.getReferencesFrom():
                    target_addr = ref.getToAddress().getOffset()
                    if target_addr in addr_to_prefix:
                        prefixes_hit[addr_to_prefix[target_addr]] += 1
                
                # Check for peripheral strings if no data refs
                if not prefixes_hit:
                    s = inst.toString().lower()
                    if "0x6fc" in s:
                        peripheral_pfx = "CAN_HAL"
                    elif "0x6f8" in s:
                        peripheral_pfx = "ADC_HAL"
                    elif "0x6f80" in s:
                        peripheral_pfx = "eTPU_HAL"
                                
            new_name = None
            if prefixes_hit:
                best_prefix, hits = prefixes_hit.most_common(1)[0]
                new_name = "%s_Func_%06X" % (best_prefix, f.getEntryPoint().getOffset())
            elif peripheral_pfx:
                new_name = "%s_%06X" % (peripheral_pfx, f.getEntryPoint().getOffset())
                
            if new_name:
                try:
                    f.setName(new_name, SourceType.USER_DEFINED)
                    renamed += 1
                except:
                    pass
                    
    finally:
        prog.endTransaction(tx, True)
        
    print("Renamed %d functions based on data usage." % renamed)
    print("Unnamed remaining: %d" % (len(unnamed) - renamed))

if __name__ == '__main__':
    run()