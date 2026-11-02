# @category ECU
# @runtime PyGhidra
# @description Map Hardware I/O and Interrupt vectors automatically.

from ghidra.program.model.symbol import SourceType

def run():
    prog = currentProgram
    st = prog.getSymbolTable()
    listing = prog.getListing()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    print("=== 1. Mapping Hardware Registers (HAL) ===")
    tx = prog.startTransaction("GodMode HAL")
    hw_count = 0
    
    for inst in listing.getInstructions(True):
        mnem = inst.getMnemonicString().lower()
        if mnem in ['lis', 'lwz', 'stw', 'lhz', 'sth']:
            for i in range(inst.getNumOperands()):
                for obj in inst.getOpObjects(i):
                    if hasattr(obj, 'getUnsignedValue'):
                        val = obj.getUnsignedValue()
                        # Hardware Register ranges on EDC16 MCU
                        if 0xF0000000 <= val <= 0xF0FFFFFF or 0xC0000000 <= val <= 0xC0FFFFFF:
                            addr = space.getAddress(val)
                            try:
                                st.createLabel(addr, "HW_REG_%08X" % val, SourceType.USER_DEFINED)
                                hw_count += 1
                            except:
                                pass
    print("  Mapped %d HW Registers." % hw_count)

    print("\n=== 2. Mapping Interrupt Vector Table (OS) ===")
    # The IVT on PowerPC is usually the first 0x3000 bytes of Flash
    ivt_count = 0
    for addr_val in range(0x0000, 0x3000, 4):
        addr = space.getAddress(addr_val)
        try:
            # Read the pointer value at this address
            ptr_val = prog.getMemory().getInt(addr) & 0xFFFFFFFF
            # If it points to valid Flash code (0x00000000 - 0x001FFFFF)
            if 0x1000 <= ptr_val <= 0x1FFFFF:
                target = space.getAddress(ptr_val)
                func = prog.getFunctionManager().getFunctionAt(target)
                if func:
                    try:
                        st.createLabel(addr, "IVT_IRQ_%s" % func.getName(), SourceType.USER_DEFINED)
                        ivt_count += 1
                    except:
                        pass
        except:
            pass
    print("  Mapped %d IVT Interrupt pointers." % ivt_count)
    prog.endTransaction(tx, True)

if __name__ == '__main__':
    run()