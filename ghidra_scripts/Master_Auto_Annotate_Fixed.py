# @category ECU
# @runtime PyGhidra
# @description Global Auto-Annotator: Robust version that skips duplicates.

import re
from ghidra.program.model.symbol import SourceType
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    st = prog.getSymbolTable()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    print("=== Starting Global ECU Auto-Annotation (Robust) ===")
    tx = prog.startTransaction("Master Auto Annotate Fixed")
    
    ram_count = 0
    
    decomp = DecompInterface()
    decomp.openProgram(prog)
    
    # Fixed Regex to catch a4, 0c, 04
    vector_pattern = re.compile(r'FUN_0010b0(a4|0c|04)\(\s*&([A-Za-z0-9_]+)_Vector,\s*&([A-Za-z0-9_]+)\)')
    
    for func in fm.getFunctions(True):
        if "FUN_0010b0" in func.getName():
            continue
            
        res = decomp.decompileFunction(func, 2, ConsoleTaskMonitor())
        if res.decompileCompleted():
            c_code = res.getDecompiledFunction().getC()
            matches = vector_pattern.findall(c_code)
            
            for match in matches:
                vector_name = match[1]
                ram_var_name = match[2]
                
                if "DAT_" in ram_var_name:
                    hex_match = re.search(r'[0-9a-fA-F]{6,8}', ram_var_name)
                    if hex_match:
                        hex_str = hex_match.group(0)
                        try:
                            addr = space.getAddress("0x" + hex_str)
                            if addr is not None:
                                new_ram_name = vector_name + "_mp"
                                existing = st.getPrimarySymbol(addr)
                                
                                # Skip if it's already named correctly
                                if existing and existing.getName() == new_ram_name:
                                    continue
                                    
                                # Use try/except to catch Java InvalidInputExceptions
                                try:
                                    st.createLabel(addr, new_ram_name, SourceType.USER_DEFINED)
                                    print("  Auto-Renamed RAM: %s -> %s" % (ram_var_name, new_ram_name))
                                    ram_count += 1
                                except Exception as e:
                                    # Silently skip conflicts, don't crash the whole script
                                    pass
                        except Exception:
                            pass

    prog.endTransaction(tx, True)
    print("\n=== Done! ===")
    print("Additional RAM Variables auto-renamed: %d" % ram_count)

if __name__ == '__main__':
    run()