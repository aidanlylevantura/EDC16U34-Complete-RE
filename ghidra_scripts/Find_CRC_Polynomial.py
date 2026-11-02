# @category ECU
# @runtime PyGhidra
# @description Search the binary for known CRC polynomials and tables.

def run():
    prog = currentProgram
    mem = prog.getMemory()
    space = prog.getAddressFactory().getDefaultAddressSpace()
    
    print("=== Searching for CRC Polynomials / Tables ===")
    
    # Common CRC32 polynomials
    polynomials = [0xEDB88320, 0x04C11DB7, 0x1EDC6F41]
    
    for poly in polynomials:
        # Convert to Big Endian byte array
        b = [(poly >> 24) & 0xFF, (poly >> 16) & 0xFF, (poly >> 8) & 0xFF, poly & 0xFF]
        print("  Searching for polynomial 0x%08X..." % poly)
        
        addr = space.getAddress(0x00000000)
        end_addr = space.getAddress(0x00200000) # 2MB Flash
        
        hits = 0
        while addr < end_addr:
            found = mem.findBytes(addr, end_addr, b, None, True, None)
            if found is None: break
            print("    Found at: %s" % found)
            hits += 1
            addr = found.add(1)
            
        if hits == 0:
            print("    Not found.")

if __name__ == '__main__':
    run()