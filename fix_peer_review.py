import os
import json
import re

BASE = r"C:\Users\user\Documents\Complete ECU Disassembly\Release_Package"

print("=== Applying Peer Review Fixes ===")

# 1. Fix Auto_Name_By_Data.py dead branch
py_path = os.path.join(BASE, "Auto_Name_By_Data.py")
if os.path.exists(py_path):
    with open(py_path, "r", encoding="utf-8") as f:
        code = f.read()
    
    # The old broken block
    old_block = 'if "0x6fc" in s:\n                        peripheral_pfx = "CAN_HAL"\n                    elif "0x6f8" in s:\n                        peripheral_pfx = "ADC_HAL"\n                    elif "0x6f80" in s:\n                        peripheral_pfx = "eTPU_HAL"'
    # The new fixed block (checks eTPU before ADC)
    new_block = 'if "0x6fc" in s:\n                        peripheral_pfx = "CAN_HAL"\n                    elif "0x6f80" in s:\n                        peripheral_pfx = "eTPU_HAL"\n                    elif "0x6f8" in s:\n                        peripheral_pfx = "ADC_HAL"'
    
    if old_block in code:
        code = code.replace(old_block, new_block)
        with open(py_path, "w", encoding="utf-8") as f:
            f.write(code)
        print("[+] Fixed Auto_Name_By_Data.py (eTPU dead branch)")
    else:
        print("[!] Auto_Name_By_Data.py already fixed or text mismatch")

# 2. Add Inner Checksum warning to README.md
readme_path = os.path.join(BASE, "README.md")
if os.path.exists(readme_path):
    warning = """
### ⚠️ CRITICAL WARNING: Inner Block Checksums
While `edc16_fix_checksum.py` fixes the outer FADECAFE additive checksum (`0xD01FE500`), there is an **inner checksum** (avalanche-type/CRC32) located at `0x1BFF74` and `0x1FDF78`. 

If you modify a calibration map inside these regions, correcting only the outer additive sum is **not enough**. The inner checksum will fail, and the ECU will refuse to boot. You must use a professional tool (like WinOLS or ECM Titanium) to recalculate both the inner and outer checksums before flashing a modified map.
"""
    with open(readme_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "Inner Block Checksums" not in content:
        with open(readme_path, "a", encoding="utf-8") as f:
            f.write(warning)
        print("[+] Added inner checksum warning to README.md")
    else:
        print("[!] README.md already contains inner checksum warning")

# 3. Fix JSON Metadata
json_path = os.path.join(BASE, "EDC16U34_Reference.json")
if os.path.exists(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if "meta" in data:
        data["meta"]["vehicle"] = "VW Golf 5 1.9 TDI PD 105 hp (2006)"
        data["meta"]["vag_part"] = "03G906021KH"
        data["meta"]["function_source"] = "Golf_KH_MASTER.c"
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("[+] Fixed metadata in EDC16U34_Reference.json")
    else:
        print("[!] No 'meta' block found in JSON")

# 4. Overwrite Linker Script with accurate memory map
ld_path = os.path.join(BASE, "EDC16U34_KH.ld")
ld_content = """/* EDC16U34 (MPC563) Custom OS Linker Script */
MEMORY
{
    flash (rx)  : ORIGIN = 0x00000000, LENGTH = 2M
    sram  (rwx) : ORIGIN = 0x003F8000, LENGTH = 32K
    immr  (rw)  : ORIGIN = 0x006FC000, LENGTH = 32K
}

SECTIONS
{
    .text : {
        *(.text.startup)
        *(.text)
        *(.rodata)
    } > flash

    .data : {
        *(.data)
    } > sram AT > flash

    .bss : {
        *(.bss)
    } > sram
}
"""
with open(ld_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(ld_content)
print("[+] Overwrote EDC16U34_KH.ld with accurate MPC563 memory map")

print("\n=== All fixes applied successfully ===")