# @runtime Jython
# EDC16U34 Initial Setup Script for Ghidra (WinOLS CSV Parser)
# @author Assistant
# @category Automotive

import os
import csv
from ghidra.program.model.data import ArrayDataType, WordDataType, ByteDataType
from ghidra.program.model.symbol import SourceType

# =====================================================================
# CONFIGURATION
# =====================================================================
DAMOS_FILE_PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\WinOLS (VW (Original) - 380437).csv" 
DELIMITER = ';'  # WinOLS usually uses semicolons. If this fails, try ','
# =====================================================================

def setup_memory_map():
    print("--- Setting up Memory Map ---")
    mem = currentProgram.getMemory()
    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    
    # 1. RAM Block (CALRAM / DECRAM)
    try:
        ram_start = space.getAddress(0x003F8000)
        if mem.getBlock(ram_start) is None:
            mem.createUninitializedBlock("RAM", ram_start, 0x8000, False)
            print("Created RAM block at 0x003F8000")
    except Exception as e:
        pass 

    # 2. Peripherals Block (USIU, CAN, TPU, etc.)
    try:
        periph_start = space.getAddress(0x002FC000)
        if mem.getBlock(periph_start) is None:
            mem.createUninitializedBlock("Peripherals", periph_start, 0x14000, False)
            print("Created Peripherals block at 0x002FC000")
    except Exception as e:
        pass 

def parse_damos_csv(file_path, delimiter):
    print("--- Parsing Damos CSV ---")
    if not os.path.exists(file_path):
        print("ERROR: File not found at " + file_path)
        return

    space = currentProgram.getAddressFactory().getDefaultAddressSpace()
    
    with open(file_path, 'r') as f:
        reader = csv.reader(f, delimiter=delimiter)
        
        try:
            headers = next(reader)
        except StopIteration:
            print("Error: Empty file.")
            return
            
        # Dynamically find the column indices based on the header names
        try:
            idx_id = headers.index("IdName")
            idx_org = headers.index("DataOrg")
            idx_cols = headers.index("Columns")
            idx_rows = headers.index("Rows")
            idx_addr = headers.index("Fieldvalues.StartAddr")
        except ValueError as e:
            print("ERROR: Could not find required headers in CSV. Make sure you selected the right delimiter. " + str(e))
            return

        count = 0
        for row in reader:
            if len(row) <= idx_addr:
                continue
                
            id_name = row[idx_id]
            if not id_name or id_name == "-":
                continue
                
            data_org = row[idx_org]
            addr_str = row[idx_addr]
            
            if not addr_str or addr_str == "$0" or addr_str == "-" or addr_str.strip() == "":
                continue
                
            try:
                cols = int(row[idx_cols])
                rows = int(row[idx_rows])
            except ValueError:
                cols = 1
                rows = 1
                
            # Clean address string (e.g., "$1DF09A" -> "0x1DF09A")
            clean_addr = addr_str.replace('$', '0x').strip()
            
            try:
                addr_val = int(clean_addr, 16)
                address = space.getAddress(addr_val)
                
                # Ensure we only label inside the Flash block (0x0 - 0x200000)
                if addr_val > 0x200000:
                    continue
                
                # 1. Create Label
                createLabel(address, id_name, True, SourceType.USER_DEFINED)
                
                # 2. Create Data Type (Array or Scalar)
                if data_org == 'eByte':
                    dt = ByteDataType()
                else:
                    dt = WordDataType()
                    
                if cols > 1 or rows > 1:
                    total_elements = cols * rows
                    array_dt = ArrayDataType(dt, total_elements, dt.getLength())
                    createData(address, array_dt)
                else:
                    createData(address, dt)
                
                count += 1
            except Exception as e:
                pass # Ignore overlaps or invalid memory addresses
                
    print("--- Finished Parsing. Applied %d labels/data structures. ---" % count)

def find_sda_pointers():
    print("--- Scanning for SDA Pointers (r2 and r13) ---")
    listing = currentProgram.getListing()
    inst_iter = listing.getInstructions(True)
    
    r13_base = None
    r2_base = None
    count = 0
    
    # Scan the first 50,000 instructions to find the boot initialization
    while inst_iter.hasNext() and count < 50000:
        inst = inst_iter.next()
        count += 1
        
        mnemonic = inst.getMnemonicString()
        if mnemonic == "lis":
            reg = inst.getOpObjects(0)[0]
            if reg.toString() == "r13":
                val = inst.getOpObjects(1)[0].getValue()
                if not r13_base:
                    r13_base = val << 16
                    print("Found 'lis r13, 0x%04X' at %s. (Upper half of r13)" % (val, inst.getAddress()))
            elif reg.toString() == "r2":
                val = inst.getOpObjects(1)[0].getValue()
                if not r2_base:
                    r2_base = val << 16
                    print("Found 'lis r2, 0x%04X' at %s. (Upper half of r2)" % (val, inst.getAddress()))
                    
        if r13_base and r2_base:
            break

# =====================================================================
# EXECUTION
# =====================================================================
transaction_id = currentProgram.startTransaction("EDC16 Setup")
try:
    setup_memory_map()
    parse_damos_csv(DAMOS_FILE_PATH, DELIMITER)
    find_sda_pointers()
finally:
    currentProgram.endTransaction(transaction_id, True)

print(">>> Setup Complete. <<<")