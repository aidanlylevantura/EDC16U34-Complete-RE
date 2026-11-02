# @runtime Jython
# EDC16U34 Deep Analysis & EGT Trace
# @author Assistant
# @category Automotive

import ghidra.app.cmd.disassemble.DisassembleCommand as DisassembleCommand
import ghidra.app.plugin.core.analysis.AutoAnalysisManager as AutoAnalysisManager
import ghidra.program.model.address.AddressSet as AddressSet
import ghidra.program.model.symbol.RefType as RefType

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    # =================================================================
    # TASK 1: Disassemble Reset Vectors
    # =================================================================
    print("\n--- Task 1: Disassembling Reset Vectors (0x0, 0x100) ---")
    addr0 = space.getAddress(0x0)
    addr100 = space.getAddress(0x100)
    
    # Create a set to disassemble the first 0x1000 bytes
    addrSet = AddressSet(addr0, space.getAddress(0x1000))
    
    cmd = DisassembleCommand(addrSet, None, True)
    cmd.applyTo(currentProgram, monitor)
    print("Disassembly command applied to 0x00000000 - 0x00001000.")

    # =================================================================
    # TASK 2: Run Auto-Analysis
    # =================================================================
    print("\n--- Task 2: Triggering Auto-Analysis ---")
    # Note: Depending on Ghidra version, this might run in the background
    analysisMgr = AutoAnalysisManager.getAnalysisManager(currentProgram)
    analysisMgr.startAnalysis(monitor)
    print("Auto-Analysis triggered. Ghidra is now tracing functions in the background.")

    # =================================================================
    # TASK 3: Find SDA Pointers (r2 and r13)
    # =================================================================
    print("\n--- Task 3: Scanning for SDA Pointers (r2 and r13) ---")
    inst_iter = listing.getInstructions(addrSet, True)
    
    r13_found = False
    r2_found = False
    
    while inst_iter.hasNext():
        inst = inst_iter.next()
        mnemonic = inst.getMnemonicString()
        
        if mnemonic == "lis":
            ops = inst.getOpObjects(0)
            if len(ops) > 0 and "r13" in ops[0].toString():
                val = inst.getOpObjects(1)[0].getValue()
                print("[SDA Found] r13 (Read-Only Globals) initialized at %s with upper half 0x%04X0000" % (inst.getAddress(), val))
                r13_found = True
            elif len(ops) > 0 and "r2" in ops[0].toString():
                val = inst.getOpObjects(1)[0].getValue()
                print("[SDA Found] r2 (Read-Write RAM) initialized at %s with upper half 0x%04X0000" % (inst.getAddress(), val))
                r2_found = True
                
        if r13_found and r2_found:
            break

    # =================================================================
    # TASK 4: Trace EGT Diagnostic Logic
    # =================================================================
    print("\n--- Task 4: Tracing EGT Switch (0x001D1240) ---")
    egt_addr = space.getAddress(0x001D1240)
    
    # Ensure the label exists (in case the CSV script wasn't run)
    if getSymbolAt(egt_addr) is None:
        createLabel(egt_addr, "EGT_swtEGTActv_C", True)
        
    refs = getReferencesTo(egt_addr)
    
    if refs is None or len(refs) == 0:
        print("No direct cross-references found to 0x001D1240.")
        print("This usually means the variable is accessed via a pointer table (GOT) rather than directly.")
    else:
        print("Found %d cross-reference(s) to EGT_swtEGTActv_C:" % len(refs))
        for ref in refs:
            from_addr = ref.getFromAddress()
            print("\n=======================================================")
            print("X-REF at %s (Type: %s)" % (from_addr, ref.getReferenceType()))
            print("=======================================================")
            
            # Print the 10 instructions starting from the reference
            inst_iter = listing.getInstructions(from_addr, True)
            count = 0
            while inst_iter.hasNext() and count < 10:
                inst = inst_iter.next()
                print("  %s : %s" % (inst.getAddress(), inst.toString()))
                count += 1

# =====================================================================
# MAIN EXECUTION BLOCK
# =====================================================================
transaction_id = currentProgram.startTransaction("EDC16 Deep Analysis")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)
print("\n>>> Script Complete. <<<")