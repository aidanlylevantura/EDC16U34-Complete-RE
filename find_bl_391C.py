import struct

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

target = 0x391C
print(f"Searching for 'bl 0x{target:04X}' in the Leon bootloader...")

for i in range(0, 0x40000, 4): # Only search the bootloader
    w = struct.unpack(">I", d[i:i+4])[0]
    op = (w >> 26) & 0x3F
    
    # Check if it's a branch instruction (opcode 18)
    if op == 18:
        li = w & 0x03FFFFFC
        if li & 0x02000000:
            li -= 0x04000000
            
        aa = (w >> 1) & 1
        lk = w & 1
        
        # We want a 'bl' (Link=1, Absolute=0)
        if lk and not aa:
            tgt = i + li
            if tgt == target:
                print(f"[+] Found 'bl 0x391C' at address 0x{i:06X}")
                # Print the 5 instructions before it for context
                for j in range(max(0, i-20), i+4, 4):
                    w2 = struct.unpack(">I", d[j:j+4])[0]
                    print(f"    0x{j:06X}: {w2:08X}")

print("Done.")