import re

CFILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_MASTER_v7.c"

def main():
    print("=== Scanning for Checksum Algorithms ===")
    with open(CFILE, encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        
    # Look for patterns like: for (i = 0; i < 0x1C0000; i = i + 1)
    # Or while loops that increment and XOR/ADD a checksum variable
    loop_pattern = re.compile(r'for\s*\(\s*\w+\s*=\s*0\s*;\s*\w+\s*<\s*(0x[0-9A-Fa-f]+)')
    xor_pattern = re.compile(r'\^=')
    add_pattern = re.compile(r'\+=')
    
    in_func = None
    func_name = "UNKNOWN"
    
    for i, line in enumerate(lines):
        # Track the current function header
        if "// Function:" in line:
            func_name = line.split("// Function: ")[1].strip()
            
        # If we see a loop and an XOR/ADD in the same function, it's likely a checksum
        if loop_pattern.search(line):
            # Look ahead 10 lines for checksum math
            for j in range(i, min(i+15, len(lines))):
                if xor_pattern.search(lines[j]) or (add_pattern.search(lines[j]) and "sum" in lines[j].lower()):
                    print(f"Potential Checksum Loop in {func_name} at line {i+1}")
                    print(f"  {line.strip()}")
                    print(f"  {lines[j].strip()}\n")
                    break
                    
if __name__ == '__main__':
    main()