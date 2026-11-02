# @category ECU
# @runtime PyGhidra
# @description Search decompiled C-code for the full map address strings (0x1c203c).

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

# The full addresses of the maps
TARGETS = {
    '0x1c203c': 'ACCCD_aDesLimNeg_CUR',
    '0x1c2052': 'ACCCD_aDesLimPos_CUR',
    '0x1c1d7e': 'ACC_rPedThres_C',
    '0x1c1d94': 'ACC_trqDesMax_C'
}

def run():
    prog = currentProgram
    func_mgr = prog.getFunctionManager()
    decomp = DecompInterface()
    decomp.openProgram(prog)
    
    print("=== Searching Decompiled C-Code for Full Map Addresses ===")
    
    count = 0
    for func in func_mgr.getFunctions(True):
        res = decomp.decompileFunction(func, 5, ConsoleTaskMonitor())
        if res.decompileCompleted():
            c_code = res.getDecompiledFunction().getC().lower()
            
            for target, name in TARGETS.items():
                # Look for the hex string without the '0x' prefix, as Ghidra sometimes formats it differently
                if target.replace('0x', '') in c_code:
                    print("FOUND %-12s (%s) inside %s" % (target, name, func.getName()))
                    count += 1
                    
    print("\nTotal references found: %d" % count)

if __name__ == '__main__':
    run()