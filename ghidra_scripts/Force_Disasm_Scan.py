# @runtime Jython
# Force Disassembly and Scan for GOT/EGT Addresses
# @category Automotive

import ghidra.app.cmd.disassemble.DisassembleCommand as DisassembleCommand
import ghidra.program.model.address.AddressSet as AddressSet

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    # Force disassembly of the entire code section (First 1.5MB)
    start = space.getAddress(0x00000000)
    end = space.getAddress(0x00180000) 
    addrSet = AddressSet(start, end)
    
    print("\n--- Forcing disassembly of 0x0 - 0x180000 (This may take a minute) ---")
    cmd = DisassembleCommand(addrSet, None, True)
    cmd.applyTo(currentProgram, monitor)
    print("Disassembly command finished.")
    
    print("\n--- Scanning for instructions referencing 0x4CB70 or 0x1D1240 ---")
    
    inst_iter = listing.getInstructions(addrSet, True)
    found = False
    
    while inst_iter.hasNext():
        inst = inst_iter.next()
        for i in range(inst.getNumOperands()):
            op_str = inst.getDefaultOperandRepresentation(i).lower()
            
            # Look for the GOT pointer (0x4CB70) or the EGT address (0x1D1240)
            # Also check for the 16-bit offset versions (0xCB70 or -0x3490)
            if "0x4cb70" in op_str or "0x1d1240" in op_str or "0xcb70" in op_str or "-0x3490" in op_str:
                found = True
                print("\n[FOUND] at %s : %s" % (inst.getAddress(), inst.toString()))
                
                # Print 15 instructions
                sub_iter = listing.getInstructions(inst.getAddress(), True)
                cnt = 0
                while sub_iter.hasNext() and cnt < 15:
                    sub = sub_iter.next()
                    print("   %s : %s" % (sub.getAddress(), sub.toString()))
                    cnt += 1
                print("--------------------------------------------------")
                
    if not found:
        print("\nNo direct instruction matches found even after forced disassembly.")
        print("This strongly suggests the code is compressed (MPC562 feature).")
        print("Ghidra cannot analyze the logic if the code is compressed. You must use the Freescale decompressor first.")

transaction_id = currentProgram.startTransaction("Force Disasm Scan")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)
print("\n>>> Script Complete. <<<")