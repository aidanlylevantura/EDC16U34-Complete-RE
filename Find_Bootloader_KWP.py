# @category ECU
# @runtime PyGhidra
# @description Find KWP dispatcher in bootloader region

def run():
    prog = currentProgram
    fm = prog.getFunctionManager()
    listing = prog.getListing()
    
    print("=== Searching for KWP dispatch in bootloader (0x0-0x40000) ===")
    
    # Look for functions that contain a switch on 0x34 or 0x31
    for func in fm.getFunctions(True):
        entry = func.getEntryPoint().getOffset()
        if entry > 0x40000:
            continue
            
        code = func.getBody()
        found = False
        
        for inst in listing.getInstructions(code, True):
            mnem = inst.getMnemonicString().lower()
            if mnem in ("cmpwi", "cmplwi"):
                text = inst.toString().lower()
                if "0x34" in text or "0x31" in text:
                    found = True
                    break
        
        if found:
            print(f"\n[+] Potential dispatcher found: {func.getName()} @ 0x{entry:06X}")
            print("    First 25 instructions:")
            count = 0
            for i in listing.getInstructions(func.getBody(), True):
                print(f"      {i.getAddress()}: {i.toString()}")
                count += 1
                if count >= 25: 
                    break

if __name__ == '__main__':
    run()