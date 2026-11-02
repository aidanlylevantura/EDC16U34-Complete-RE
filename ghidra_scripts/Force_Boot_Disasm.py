# @category ECU
# @runtime PyGhidra
# @description Force disassemble the bootblock and create functions at vectors.

from ghidra.app.cmd.disassemble import DisassembleCommand
from ghidra.app.cmd.function import CreateFunctionCmd

def run():
    prog = currentProgram
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    print("=== Forcing Disassembly of Bootblock (0x0 - 0x8000) ===")
    
    # 1. Disassemble the main block
    start = space.getAddress(0x0)
    end = space.getAddress(0x8000)
    disasm = DisassembleCommand(start, end, True)
    disasm.applyTo(prog)
    
    # 2. Create functions at the standard EDC16 vectors
    vectors = [0x100, 0x200, 0x300, 0x400, 0x500, 0x600, 0x700, 0x900, 0xA00, 0xF20]
    for v in vectors:
        addr = space.getAddress(v)
        cmd = CreateFunctionCmd(addr)
        cmd.applyTo(prog)
        
    print("Done! Go to 0x100 in Ghidra to see the reset vector.")