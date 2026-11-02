# @runtime Jython
# Search for Bootloader ASCII strings
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    mem = currentProgram.getMemory()
    
    print("\n--- Searching for Strings in Bootloader Region (0x0 - 0x20000) ---")
    
    start = 0x00000000
    end = 0x00020000
    
    current_str = ""
    str_start = 0
    
    for i in range(start, end):
        addr = space.getAddress(i)
        try:
            val = mem.getByte(addr) & 0xFF
        except:
            break
            
        # Check if printable ASCII (32 to 126)
        if 32 <= val <= 126:
            if not current_str:
                str_start = i
            current_str += chr(val)
        else:
            if len(current_str) >= 5:
                # Only print strings longer than 5 characters
                print("  0x%06X : %s" % (str_start, current_str))
            current_str = ""

transaction_id = currentProgram.startTransaction("Search Strings")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)