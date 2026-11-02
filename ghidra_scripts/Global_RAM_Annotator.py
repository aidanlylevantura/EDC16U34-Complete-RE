# @category ECU
# @runtime PyGhidra
# @description Read WinOLS CSV and apply Damos names to all RAM variables globally.

import re
from ghidra.program.model.symbol import SourceType

CSV_PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    st = prog.getSymbolTable()
    
    print("=== Parsing Damos CSV for RAM Variables ===")
    count = 0
    
    tx = prog.startTransaction("Global RAM Annotate")
    try:
        with open(CSV_PATH, encoding='utf-8', errors='replace') as f:
            for line in f:
                p = line.rstrip('\n').split(';')
                if len(p) < 2: continue
                name = p[1].strip()
                if not name: continue
                
                m = re.search(r'\$([0-9A-Fa-f]{4,8})', line)
                if not m: continue
                
                try: addr_val = int(m.group(1), 16)
                except: continue
                
                # Filter for RAM addresses (usually 0x7F0000 to 0x800000)
                if 0x7F0000 <= addr_val <= 0x800000:
                    addr = space.getAddress(addr_val)
                    if addr is not None:
                        try:
                            st.createLabel(addr, name, SourceType.USER_DEFINED)
                            count += 1
                        except:
                            pass
    finally:
        prog.endTransaction(tx, True)
        
    print("Successfully annotated %d RAM variables globally!" % count)

if __name__ == '__main__':
    run()
