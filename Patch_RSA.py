# @category ECU
# @runtime PyGhidra
# @description Clear existing code, patch RSA check, and disassemble the new bytes.

from ghidra.app.cmd.disassemble import DisassembleCommand
from ghidra.program.model.address import AddressSet

def run():
    prog = currentProgram
    mem = prog.getMemory()
    listing = prog.getListing()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    print("=== Patching RSA Boot Check ===")
    
    start_addr = space.getAddress(0x486C)
    end_addr = space.getAddress(0x4873)
    
    tx = prog.startTransaction("Patch RSA")
    try:
        # 1. Clear the existing instructions so we don't get an overlap error
        listing.clearCodeUnits(start_addr, end_addr, False)
        
        # 2. Write the new PowerPC instructions
        # 0x38600001 = li r3, 1
        # 0x4E800020 = blr
        patch_bytes = b"\x38\x60\x00\x01\x4E\x80\x00\x20"
        mem.setBytes(start_addr, patch_bytes)
        
        # 3. Force Ghidra to disassemble the new bytes using AddressSet
        addr_set = AddressSet(start_addr, end_addr)
        cmd = DisassembleCommand(addr_set, None, True)
        cmd.applyTo(prog)
        
        print("[+] SUCCESS: Patched DSM_auto_00486c @ 0x486C.")
        print("[+] The RSA boot check now simply returns '1' (Success).")
    except Exception as e:
        print("[-] Patch failed:", e)
    finally:
        prog.endTransaction(tx, True)

if __name__ == '__main__':
    run()