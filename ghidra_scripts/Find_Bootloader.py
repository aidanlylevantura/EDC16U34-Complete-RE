# @runtime Jython
# Disassemble and inspect the Bootloader
# @category Automotive

import ghidra.app.cmd.disassemble.DisassembleCommand as DisassembleCommand
import ghidra.program.model.address.AddressSet as AddressSet

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    # Bootloader start address (typical for EDC16 2MB flash)
    boot_start = 0x001F0000
    boot_end = 0x001FFFFF
    
    print("\n--- Analyzing Bootloader Region (0x%08X - 0x%08X) ---" % (boot_start, boot_end))
    
    addr_set = AddressSet(space.getAddress(boot_start), space.getAddress(boot_end))
    
    # Force disassembly
    cmd = DisassembleCommand(addr_set, None, True)
    cmd.applyTo(currentProgram, monitor)
    
    # Print the first 20 instructions
    inst_iter = listing.getInstructions(space.getAddress(boot_start), True)
    count = 0
    while inst_iter.hasNext() and count < 20:
        inst = inst_iter.next()
        print("  %s : %s" % (inst.getAddress(), inst.toString()))
        count += 1

transaction_id = currentProgram.startTransaction("Bootloader")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)