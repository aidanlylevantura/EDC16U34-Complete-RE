# @category ECU
# @runtime PyGhidra
# @description Global Auto-Annotator: Renames all Bosch Math functions and automatically resolves RAM variables from Bypass Vectors.

import re
from ghidra.program.model.symbol import SourceType
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    st = prog.getSymbolTable()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    listing = prog.getListing()
    
    print("=== Starting Global ECU Auto-Annotation ===")
    tx = prog.startTransaction("Master Auto Annotate")
    
    math_count = 0
    ram_count = 0
    
    # 1. Auto-Rename Math Functions
    print("\n-- 1. Scanning for Math Functions --")
    for func in fm.getFunctions(True):
        body = func.getBody()
        insts = listing.getInstructions(body, True)
        
        has_max = False
        has_min = False
        
        for inst in insts:
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    if hasattr(obj, 'getUnsignedValue'):
                        val = obj.getUnsignedValue()
                        if val == 0x7fffffff: has_max = True
                        if val == 0x80000000: has_min = True
                        
        if has_max and has_min:
            old_name = func.getName()
            if old_name.startswith("FUN_"):
                new_name = "Math_Sat_" + old_name[4:]
                func.setName(new_name, SourceType.USER_DEFINED)
                math_count += 1

    # 2. Auto-Rename RAM Variables via Bypass Vectors
    print("\n-- 2. Scanning for Bypass Vectors --")
    decomp = DecompInterface()
    decomp.openProgram(prog)
    
    # Matches calls like: FUN_0010b0a4(&System_Vector,&DAT_007f1234)
    vector_pattern = re.compile(r'FUN_0010b0(a4|0c|04|0c)\(\s*&([A-Za-z0-9_]+)_Vector,\s*&([A-Za-z0-9_]+)\)')
    
    for func in fm.getFunctions(True):
        # Skip the bypass functions themselves
        if "FUN_0010b0" in func.getName():
            continue
            
        res = decomp.decompileFunction(func, 2, ConsoleTaskMonitor())
        if res.decompileCompleted():
            c_code = res.getDecompiledFunction().getC()
            matches = vector_pattern.findall(c_code)
            
            for match in matches:
                vector_name = match[1]
                ram_var_name = match[2]
                
                # If the RAM var is a DAT_ address (meaning it's not named yet)
                if "DAT_" in ram_var_name:
                    # Extract the 6 to 8 digit hex address safely
                    hex_match = re.search(r'[0-9a-fA-F]{6,8}', ram_var_name)
                    if hex_match:
                        hex_str = hex_match.group(0)
                        try:
                            addr = space.getAddress("0x" + hex_str)
                            if addr is not None:
                                new_ram_name = vector_name + "_mp"
                                # Check if symbol already exists to prevent duplicates
                                existing = st.getPrimarySymbol(addr)
                                if existing and existing.getName() == new_ram_name:
                                    continue
                                st.createLabel(addr, new_ram_name, SourceType.USER_DEFINED)
                                print("  Auto-Renamed RAM: %s -> %s" % (ram_var_name, new_ram_name))
                                ram_count += 1
                        except Exception as e:
                            pass

    prog.endTransaction(tx, True)
    print("\n=== Done! ===")
    print("Math Functions identified: %d" % math_count)
    print("RAM Variables auto-renamed: %d" % ram_count)

if __name__ == '__main__':
    run()