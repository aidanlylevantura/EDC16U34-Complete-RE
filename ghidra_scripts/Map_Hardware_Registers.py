# @runtime Jython
# Map MPC5xx Hardware Registers
# @category Automotive

def run():
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    
    print("\n--- Labeling Hardware Registers ---")
    
    # Key hardware modules from MPC561RM.pdf
    modules = {
        "USIU": 0x002FC000,
        "TPU_A": 0x00304000,
        "TPU_B": 0x00304400,
        "QADC_A": 0x00304800,
        "QADC_B": 0x00304C00,
        "QSMCM": 0x00305000,
        "MIOS14": 0x00306000,
        "TouCAN_A": 0x00307080,
        "TouCAN_B": 0x00307480,
        "TouCAN_C": 0x00307880,
        "UIMB": 0x00307F80
    }
    
    for name, base in modules.items():
        try:
            addr = space.getAddress(base)
            createLabel(addr, name + "_BASE", True)
            print("Labeled %s at 0x%08X" % (name, base))
        except Exception as e:
            pass
            
    # Specific TouCAN A registers
    can_a_regs = {
        0x00: "MCR", 0x02: "TEST", 0x04: "ICR", 0x06: "CTRL0",
        0x08: "PRESDIV_CTRL1", 0x0A: "TIMER", 0x10: "RXGMSKHI",
        0x12: "RXGMSKLO", 0x20: "ESTAT", 0x22: "IMASK", 0x24: "IFLAG"
    }
    for offset, reg_name in can_a_regs.items():
        addr = space.getAddress(0x00307080 + offset)
        try:
            createLabel(addr, "TouCAN_A_" + reg_name, True)
        except:
            pass

transaction_id = currentProgram.startTransaction("Map Hardware")
try:
    run()
finally:
    currentProgram.endTransaction(transaction_id, True)