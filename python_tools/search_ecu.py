import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cfile', required=True, help="Path to exported C file")
    ap.add_argument('--term', required=True, help="Variable or Map name to search for")
    ap.add_argument('--addr', required=False, help="Hex address (e.g., 007f9be2) to search for")
    a = ap.parse_args()

    print(f"=== Searching for '{a.term}' in {a.cfile} ===\n")
    
    # Create a list of search terms
    terms = [a.term]
    if not a.term.startswith("_"):
        terms.append("_" + a.term) # Check for underscore prefix
    
    if a.addr:
        # Add hex address variations
        terms.append(f"0x{a.addr}")
        terms.append(f"DAT_{a.addr}")
        terms.append(f"_DAT_{a.addr}")

    found = False
    try:
        with open(a.cfile, encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            
        for i, line in enumerate(lines, 1):
            if any(term in line for term in terms):
                clean_line = line.strip()
                print(f"L{i}: {clean_line}")
                found = True
                
        if not found:
            print("No references found for any variations.")
    except FileNotFoundError:
        print(f"Error: Could not find file '{a.cfile}'.")

if __name__ == '__main__':
    main()