# @runtime Jython
# Automatically resolve r13 offsets to Damos labels in Ghidra
# @category Automotive

from java.math import BigInteger
from ghidra.program.model.lang import RegisterValue

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    mem = currentProgram.getMemory()
    
    # r13 base address
    r13_base = 0x007FFFF0
    
    print("\n--- Resolving r13 Offsets to Damos Labels ---")
    
    code_set = ghidra.program.model.address.AddressSet(space.getAddress(0x00000000), space.getAddress(0x00180000))
    inst_iter = listing.getInstructions(code_set, True)
    
    count = 0
    while inst_iter.hasNext():
        inst = inst_iter.next()
        
        # Look for instructions using r13 (e.g., lwz r3, 0x1234(r13) or -0x640c(r13))
        for i in range(inst.getNumOperands()):
            op_str = inst.getDefaultOperandRepresentation(i).lower()
            if "(r13)" in op_str:
                try:
                    # Extract the offset (e.g., "-0x640c" or "0x1234")
                    offset_str = op_str.split('(')[0].strip()
                    offset = int(offset_str, 16)
                    
                    # Calculate the RAM address
                    ram_addr = (r13_base + offset) & 0xFFFFFFFF
                    ram_addr_ghidra = space.getAddress(ram_addr)
                    
                    # Check if there is already a symbol there
                    sym = getSymbolAt(ram_addr_ghidra)
                    if sym is None:
                        # If no symbol, we can create a generic one based on the offset
                        # Since we don't have a direct map of RAM to Damos in this script,
                        # we will label it as "RAM_Offset_XXXX" to make the C-file readable.
                        createLabel(ram_addr_ghidra, "RAM_r13_%X" % (offset & 0xFFFF), True)
                        count += 1
                except:
                    pass
                    
    print("Labeled %d r13 RAM offsets." % count)
    print(">>> Re-export your C-file to see 'RAM_r13_640C' instead of 'unaff_r13 - 0x640c'! <<<")

transaction_id = currentProgram.startTransaction("Fix RAM")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)