# @category ECU
# @runtime PyGhidra
# @description Dump assembly for key ACC functions to find the map offsets (0x203C, etc).

TARGET_FUNCS = ["FUN_00054804", "FUN_00056180", "FUN_0005882c", "FUN_00058d4c"]

def run():
    prog = currentProgram
    listing = prog.getListing()
    func_mgr = prog.getFunctionManager()
    
    for target in TARGET_FUNCS:
        funcs = func_mgr.getFunctions(True)
        for func in funcs:
            if func.getName() == target:
                print("\n=== Assembly for %s ===" % func.getName())
                instructions = listing.getInstructions(func.getBody(), True)
                for inst in instructions:
                    # Only print instructions that load addresses or use base registers
                    txt = inst.toString()
                    if any(kw in txt for kw in ['lis', 'addi', 'lhz', 'lha', 'lwz', 'ori', 'addis']):
                        print("%s: %s" % (inst.getAddress(), txt))
                break

if __name__ == '__main__':
    run()