import csv
import os

BIN_CSV = r"C:\Users\user\Documents\Complete ECU Disassembly\Extracted_Maps.csv"
DAMOS_CSV = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv"
OUT_CSV = r"C:\Users\user\Documents\Complete ECU Disassembly\Extracted_Maps_Scaled.csv"
DELIMITER = ';'

def load_damos_factors():
    factors = {}
    with open(DAMOS_CSV, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f, delimiter=DELIMITER)
        headers = next(reader)
        idx_id = headers.index("IdName")
        idx_factor = headers.index("Fieldvalues.Factor")
        idx_offset = headers.index("Fieldvalues.Offset")
        
        for row in reader:
            if len(row) <= max(idx_id, idx_factor, idx_offset):
                continue
            try:
                # European decimals use commas, convert to dots
                factor_str = row[idx_factor].replace(',', '.')
                offset_str = row[idx_offset].replace(',', '.')
                factor = float(factor_str) if factor_str else 1.0
                offset = float(offset_str) if offset_str else 0.0
                factors[row[idx_id]] = (factor, offset)
            except ValueError:
                factors[row[idx_id]] = (1.0, 0.0)
    return factors

def scale_maps():
    print("Loading Damos factors...")
    factors = load_damos_factors()
    
    print("Scaling extracted maps...")
    with open(BIN_CSV, 'r', encoding='utf-8') as f_in, open(OUT_CSV, 'w', newline='', encoding='utf-8') as f_out:
        reader = csv.reader(f_in)
        writer = csv.writer(f_out)
        
        headers = next(reader)
        writer.writerow(headers)
        
        for row in reader:
            if len(row) < 5:
                continue
            
            id_name = row[1]
            factor, offset = factors.get(id_name, (1.0, 0.0))
            
            # Scale the data
            scaled_rows = []
            raw_data_rows = row[4].split(" | ")
            for r in raw_data_rows:
                scaled_vals = []
                for val_str in r.split(","):
                    try:
                        raw_val = int(val_str)
                        scaled_val = (raw_val * factor) + offset
                        # Format to 2 decimal places
                        scaled_vals.append("%.2f" % scaled_val)
                    except ValueError:
                        scaled_vals.append("ERR")
                scaled_rows.append(",".join(scaled_vals))
                
            row[4] = " | ".join(scaled_rows)
            writer.writerow(row)
            
    print("Success! Scaled maps saved to: " + OUT_CSV)

if __name__ == "__main__":
    scale_maps()