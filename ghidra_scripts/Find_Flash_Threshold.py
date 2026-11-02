# @runtime Jython
# Search for the RAM Init Table entry for 0x007F9BE4
# @category Automotive

from jarray import array

def to_signed_byte(val):
    # Jython requires signed bytes (-128 to 127) for the 'b' array type
    return val - 256 if val > 127 else val

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    mem = currentProgram.getMemory()
    
    ram_addr = 0x007F9BE4
    print("\n--- Searching for RAM Init Table (0x%08X) ---" % ram_addr)
    
    # Convert to signed bytes: [0x00, 0x7F, 0x9B(-101), 0xE4(-28)]
    target_bytes = array([ to_signed_byte(0x00), to_signed_byte(0x7F), to_signed_byte(0x9B), to_signed_byte(0xE4) ], 'b')
    
    start = space.getAddress(0x00000000)
    end = space.getAddress(0x00200000)
    
    iter = mem.findBytes(start, end, target_bytes, None, True, monitor)
    if iter is not None:
        while iter is not None:
            print("\n[FOUND] 32-bit pointer to threshold RAM at: %s" % iter)
            print("  Dumping surrounding 16 bytes (looking for ROM source):")
            for i in range(-8, 8, 4):
                addr = iter.add(i)
                val = mem.getInt(addr) & 0xFFFFFFFF
                print("    %s : 0x%08X" % (addr, val))
            iter = mem.findBytes(iter.next(), end, target_bytes, None, True, monitor)
    else:
        print("  -> No direct 32-bit pointer found in Flash.")
        
    # Search for 16-bit offset (9B E4)
    print("\n--- Searching for 16-bit offset (9B E4) ---")
    target_short = array([ to_signed_byte(0x9B), to_signed_byte(0xE4) ], 'b')
    iter = mem.findBytes(start, end, target_short, None, True, monitor)
    if iter is not None:
        print("  [FOUND] 16-bit offset at: %s" % iter)
        for i in range(-8, 8, 4):
            addr = iter.add(i)
            val = mem.getInt(addr) & 0xFFFFFFFF
            print("    %s : 0x%08X" % (addr, val))
    else:
        print("  -> No 16-bit offset found.")

transaction_id = currentProgram.startTransaction("Find Flash Threshold")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)