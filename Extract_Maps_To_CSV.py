import csv
import struct
import os

# Paths are pre-set to your folder
BIN_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
CSV_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
OUTPUT_MAPS_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\Extracted_Maps.csv"
DELIMITER = ';'

def extract_maps():
    print("Reading 2MB binary file...")
    if not os.path.exists(BIN_FILE):
        print("ERROR: Binary file not found.")
        return
        
    with open(BIN_FILE, 'rb') as f:
        bin_data = f.read()

    print("Reading Damos CSV...")
    if not os.path.exists(CSV_FILE):
        print("ERROR: CSV file not found.")
        return

    count = 0
    with open(OUTPUT_MAPS_FILE, 'w', newline='', encoding='utf-8') as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Map Name", "IdName", "Address", "Dimensions", "Data (Row by Row)"])

        with open(CSV_FILE, 'r', encoding='utf-8', errors='ignore') as f_in:
            reader = csv.reader(f_in, delimiter=DELIMITER)
            try:
                headers = next(reader)
            except StopIteration:
                print("ERROR: Empty CSV.")
                return
                
            try:
                idx_name = headers.index("Name")
                idx_id = headers.index("IdName")
                idx_addr = headers.index("Fieldvalues.StartAddr")
                idx_cols = headers.index("Columns")
                idx_rows = headers.index("Rows")
                idx_type = headers.index("Type")
            except ValueError:
                print("ERROR: Could not find headers. Check delimiter.")
                return

            for row in reader:
                if len(row) <= max(idx_addr, idx_cols, idx_rows):
                    continue
                
                # Only process 2D maps (eZweiInv)
                if row[idx_type] not in ['eZweiInv', 'eZwei']:
                    continue
                    
                addr_str = row[idx_addr].replace('$', '').strip()
                if not addr_str or addr_str == '0':
                    continue
                    
                try:
                    addr = int(addr_str, 16)
                    cols = int(row[idx_cols])
                    rows = int(row[idx_rows])
                    
                    if cols == 0 or rows == 0:
                        continue
                        
                    map_data = []
                    # Read the map data (16-bit Big Endian)
                    for r in range(rows):
                        row_data = []
                        for c in range(cols):
                            offset = addr + ((r * cols) + c) * 2
                            if offset + 1 < len(bin_data):
                                val = struct.unpack('>H', bin_data[offset:offset+2])[0]
                                row_data.append(str(val))
                            else:
                                row_data.append("0")
                        map_data.append(",".join(row_data))
                        
                    writer.writerow([row[idx_name], row[idx_id], addr_str, "%dx%d" % (cols, rows), " | ".join(map_data)])
                    count += 1
                except Exception as e:
                    pass

    print("\n--- Success! ---")
    print("Extracted %d maps to: %s" % (count, OUTPUT_MAPS_FILE))

if __name__ == "__main__":
    extract_maps()