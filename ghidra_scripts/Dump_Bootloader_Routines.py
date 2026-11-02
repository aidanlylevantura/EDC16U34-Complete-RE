# @category ECU
# @runtime PyGhidra
# @description Dump Bootloader RoutineControl functions to find the checksum algorithm.

from ghidra.app.decompiler import DecompInterface
from ghidra.util.task import ConsoleTaskMonitor

TARGET_FUNCS = ["FUN_00014c14", "FUN_000151d0", "FUN_000a121c"]

def run():
    prog = currentProgram
    decomp = DecompInterface()
    decomp.openProgram(prog)
    fm = prog.getFunctionManager()
    
    for target in TARGET_FUNCS:
        func = fm.getFunctionAt(prog.getAddressFactory().getDefaultAddressSpace().getAddress(target))
        if func:
            print("\n=== %s ===" % func.getName())
            res = decomp.decompileFunction(func, 15, ConsoleTaskMonitor())
            if res.decompileCompleted():
                c_code = res.getDecompiledFunction().getC()
                # Print lines that contain math or pointers
                for line in c_code.split("\n"):
                    if any(x in line for x in ['*', '^', '+', '0x', 'ptr', 'Ptr']):
                        print(line.strip())