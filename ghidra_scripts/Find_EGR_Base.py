# @category ECU
# @runtime PyGhidra
# @description Scan for the AirCtl_rEGR_mp assignments and calculate the ROM base address.

import re
from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    decomp = DecompInterface()
    decomp.openProgram(prog)
    
    print("=== Searching for EGR Function Base Pointer ===")
    
    # We look for the function that sets AirCtl_rEGR_mp = psVarXX[...]
    for func in fm.getFunctions(True):
        res = decomp.decompileFunction(func, 5, ConsoleTaskMonitor())
        if res.decompileCompleted():
            c_code = res.getDecompiledFunction().getC()
            
            if "AirCtl_rEGR_mp = psVar" in c_code:
                print("\nFound EGR Function: %s @ %s" % (func.getName(), func.getEntryPoint()))
                
                # Extract the variable name (e.g., psVar23)
                match = re.search(r'AirCtl_rEGR_mp = (psVar\d+)\[', c_code)
                if match:
                    var_name = match.group(1)
                    print("  Base pointer variable: %s" % var_name)
                    
                    # Find where that variable is assigned
                    assign_match = re.search(r'%s = \*\(short \*\*\)\(unaff_r15 \+ (0x[0-9a-fA-F]+)\)' % var_name, c_code)
                    if assign_match:
                        offset = assign_match.group(1)
                        print("  Base pointer offset: unaff_r15 + %s" % offset)
                    else:
                        # Try alternative Ghidra decompiler syntax
                        assign_match2 = re.search(r'%s = .*unaff_r15 \+ (0x[0-9a-fA-F]+)' % var_name, c_code)
                        if assign_match2:
                            offset = assign_match2.group(1)
                            print("  Base pointer offset: unaff_r15 + %s" % offset)
                        else:
                            print("  Could not automatically find the offset. Please look at the top of the function in Ghidra.")

if __name__ == '__main__':
    run()