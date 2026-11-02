# @category ECU
# @runtime PyGhidra
# @description Search decompiled C-code for specific hex map offsets.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

# Map offsets to search for (including base-relative deltas)
TARGETS = {
    '0x203c': 'ACCCD_aDesLimNeg_CUR',
    '0x2052': 'ACCCD_aDesLimPos_CUR',
    '0x1d7e': 'ACC_rPedThres_C',
    '0x1d94': 'ACC_trqDesMax_C',
    '0x1d68': 'ACC_rBrk_CUR',
    '0x1d44': 'ACC_dtrqBrkRmpUp_CUR',
    '0x162c': 'ACCCD_aDesLimNeg (base delta)',
    '0x1642': 'ACCCD_aDesLimPos (base delta)'
}

def run():
    prog = currentProgram
    func_mgr = prog.getFunctionManager()
    decomp = DecompInterface()
    decomp.openProgram(prog)
    
    print("=== Searching Decompiled C-Code for Map Offsets ===")
    
    funcs = func_mgr.getFunctions(True)
    count = 0
    
    for func in funcs:
        # Decompile the function
        res = decomp.decompileFunction(func, 5, ConsoleTaskMonitor())
        if res.decompileCompleted():
            c_code = res.getDecompiledFunction().getC()
            
            # Check if any of our targets are in the C-code
            for target, name in TARGETS.items():
                if target in c_code.lower():
                    print("FOUND %-15s (%s) inside %s" % (target, name, func.getName()))
                    count += 1
                    
    print("\nTotal references found: %d" % count)

if __name__ == '__main__':
    run()