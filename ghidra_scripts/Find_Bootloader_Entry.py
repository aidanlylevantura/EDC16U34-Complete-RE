# @runtime Jython
# Inspect the Bootloader Region (0x0000 - 0xFFFF)
# @category Automotive

import ghidra.app.cmd.disassemble.DisassembleCommand as DisassembleCommand
import ghidra.program.model.address.AddressSet as AddressSet

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    boot_start = 0x00000000
    boot_end = 0x0000FFFF
    
    print("\n--- Analyzing Bootloader Region (0x0000 - 0xFFFF) ---")
    
    # Force disassembly of the boot block
    addr_set = AddressSet(space.getAddress(boot_start), space.getAddress(boot_end))
    cmd = DisassembleCommand(addr_set, None, True)
    cmd.applyTo(currentProgram, monitor)
    
    # Print instructions starting from the reset vector
    print("\n[Reset Vector at 0x100]")
    inst_iter = listing.getInstructions(space.getAddress(0x100), True)
    count = 0
    while inst_iter.hasNext() and count < 15:
        inst = inst_iter.next()
        print("  %s : %s" % (inst.getAddress(), inst.toString()))
        count += 1

transaction_id = currentProgram.startTransaction("Bootloader")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)