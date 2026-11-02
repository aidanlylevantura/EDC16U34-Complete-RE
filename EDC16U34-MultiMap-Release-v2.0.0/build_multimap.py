import os
import struct
import zlib

BASE_DIR = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34-MultiMap-Release-v2.0.0"
INPUT_BIN = os.path.join(BASE_DIR, "Flash.bin")
OUTPUT_BIN = os.path.join(BASE_DIR, "03G906021KH_MultiMap.bin")

TRAMPOLINE_ADDR = 0x1C8000
TABLE_ADDR = 0x1C8100
MAP_2D_READER = 0x0F94DC

# =========================================================================
# CHANGE THIS TO YOUR PREVIOUS WORKING CAN SWITCH RAM ADDRESS (e.g., 0x8000E0)
# =========================================================================
CAN_SWITCH_RAM = 0x800000 

CHECKSUM_OFFSET_CRC = 0x1FFFFA 
CHECKSUM_OFFSET_SUM = 0x1FFFFE

MAPS = [
    0x1D16F6, 0x1D15C6, 0x1D1584, 0x1D17FC, 0x1D15B2, 0x1D16E2,
    0x1D2F06, 0x1D307E, 0x1D333C, 0x1D3658, 0x1D3836, 0x1D3A14, 0x1D3298, 0x1D351A,
    0x1D360E, 0x1D3C00, 0x1D3D0A, 0x1D3E44, 0x1D3F1A, 0x1D3F3C,
    0x1D3DDE, 0x1D5F50, 0x1D5D64, 0x1D5B44,
    0x1D1584, 0x1D18B8, 0x1D556C, 0x1D5C64, 0x1D146C, 0x1D1BE4
]

def generate_safe_trampoline():
    asm = []
    asm.append(0x3D80001D) # lis r12, 0x001D
    asm.append(0x618C16F6) # ori r12, r12, 0x16F6
    asm.append(0x7C056000) # cmpw r5, r12
    asm.append(0x40820028) # bne +40 (FIXED: Jump straight to stwu if not DW01)
    
    asm.append(0x3D600000 | ((CAN_SWITCH_RAM >> 16) & 0xFFFF)) # lis r11
    asm.append(0x896B0000 | (CAN_SWITCH_RAM & 0xFFFF))         # lbz r11
    asm.append(0x2C0B001D) # cmpwi r11, 29
    asm.append(0x40810008) # ble +8
    asm.append(0x39600000) # li r11, 0
    
    asm.append(0x3D80001C) # lis r12, 0x001C
    asm.append(0x618C8100) # ori r12, r12, 0x8100
    asm.append(0x556B103A) # slwi r11, r11, 2
    asm.append(0x7CAC582E) # lwzx r5, r12, r11
    
    asm.append(0x9421FFE8) # stwu r1, -0x18(r1)
    asm.append(0x3D80000F) # lis r12, 0x000F
    asm.append(0x618C94E0) # ori r12, r12, 0x94E0
    asm.append(0x7D8903A6) # mtctr r12
    asm.append(0x4E800420) # bctr
    return b"".join(struct.pack(">I", inst) for inst in asm)

def patch_flash(buf):
    table_bytes = b"".join(struct.pack(">I", addr) for addr in MAPS)
    buf[TABLE_ADDR : TABLE_ADDR + len(table_bytes)] = table_bytes
    
    tramp_bytes = generate_safe_trampoline()
    buf[TRAMPOLINE_ADDR : TRAMPOLINE_ADDR + len(tramp_bytes)] = tramp_bytes
    
    branch_offset = (TRAMPOLINE_ADDR - MAP_2D_READER) & 0x03FFFFFC
    branch_inst = 0x48000000 | branch_offset
    struct.pack_into(">I", buf, MAP_2D_READER, branch_inst)
    return buf

def fix_checksums(buf):
    buf[CHECKSUM_OFFSET_CRC:CHECKSUM_OFFSET_CRC+4] = b"\x00\x00\x00\x00"
    buf[CHECKSUM_OFFSET_SUM:CHECKSUM_OFFSET_SUM+2] = b"\x00\x00"
    crc_val = zlib.crc32(buf[0:CHECKSUM_OFFSET_CRC]) & 0xFFFFFFFF
    sum_val = sum(buf[0:CHECKSUM_OFFSET_SUM]) & 0xFFFF
    sum_val = (0x10000 - sum_val) & 0xFFFF
    struct.pack_into(">I", buf, CHECKSUM_OFFSET_CRC, crc_val)
    struct.pack_into(">H", buf, CHECKSUM_OFFSET_SUM, sum_val)
    return buf

def main():
    if not os.path.exists(INPUT_BIN):
        print(f"Error: Could not find {INPUT_BIN}")
        return
    with open(INPUT_BIN, "rb") as f:
        buf = bytearray(f.read())
    print(f"[+] Patching maps (CAN RAM: 0x{CAN_SWITCH_RAM:06X})...")
    buf = patch_flash(buf)
    buf = fix_checksums(buf)
    with open(OUTPUT_BIN, "wb") as f:
        f.write(buf)
    print(f"[+] SUCCESS: Saved {OUTPUT_BIN}")

if __name__ == "__main__":
    main()
