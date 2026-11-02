# @runtime Jython
# Set r13 base register to 0x007FFFF0 to resolve SDA offsets
# @category Automotive

from java.math import BigInteger
from ghidra.program.model.lang import RegisterValue

def run():
    context = currentProgram.getProgramContext()
    reg_r13 = currentProgram.getRegister("r13")
    
    if reg_r13 is None:
        print("ERROR: Could not find register r13.")
        return
        
    # r13 base address: 0x007FFFF0
    r13_val = BigInteger(str(0x007FFFF0))
    
    # Create the RegisterValue object required by the API
    reg_val = RegisterValue(reg_r13, r13_val)
    
    print("\n--- Setting r13 base to 0x007FFFF0 ---")
    
    func_mgr = currentProgram.getFunctionManager()
    funcs = func_mgr.getFunctions(True)
    
    count = 0
    while funcs.hasNext():
        func = funcs.next()
        body = func.getBody()
        
        # Set the register value for the entire address range of the function
        context.setRegisterValue(body.getMinAddress(), body.getMaxAddress(), reg_val)
        count += 1
        
    print("Applied r13 base to %d functions." % count)
    print(">>> Re-open or refresh the Decompiler window to see the changes! <<<")

transaction_id = currentProgram.startTransaction("Set r13")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)