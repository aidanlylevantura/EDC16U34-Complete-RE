# @runtime Jython
# Find callers of the CAN polling functions
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    listing = currentProgram.getListing()
    
    # The function addresses we found
    targets = [0x0001f8d4, 0x0001f918, 0x000fbd44]
    
    print("\n--- Tracing callers of CAN polling functions ---")
    
    for target in targets:
        target_addr = space.getAddress(target)
        # Look for the function that starts before this address
        func = getFunctionContaining(target_addr)
        if func:
            entry = func.getEntryPoint()
            print("\n[CAN Function] %s at %s" % (func.getName(), entry))
            
            refs = getReferencesTo(entry)
            if refs is not None:
                for ref in refs:
                    if ref.getReferenceType().isCall():
                        print("  -> Called by: %s" % ref.getFromAddress())
            else:
                print("  -> No direct calls found (might be in a function pointer table).")

transaction_id = currentProgram.startTransaction("Trace CAN Callers")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)