import os
import struct
import zlib
import time
import sys

BASE_DIR = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34-MultiMap-Release-v2.0.0"
INPUT_BIN = os.path.join(BASE_DIR, "03G906021KH_MultiMap.bin")

TRAMPOLINE_ADDR = 0x1C8000
TABLE_ADDR = 0x1C8100
MAP_2D_READER = 0x0F94DC
CAN_SWITCH_RAM = 0x800000 

CHECKSUM_OFFSET_CRC = 0x1FFFFA 
CHECKSUM_OFFSET_SUM = 0x1FFFFE

MAP_TYPES = [
    '2D', '2D', '2D', '2D', '2D', '2D', 
    '2D', '2D', '2D', '2D', '2D', '2D', '2D', '2D',
    '1D', '2D', '1D', '2D', '1D', '1D',
    '1D', '2D', '2D', '2D', 
    '2D', '1D', '2D', '2D', '2D', '2D'
]

EXPECTED_MAPS = [
    0x1D16F6, 0x1D15C6, 0x1D1584, 0x1D17FC, 0x1D15B2, 0x1D16E2,
    0x1D2F06, 0x1D307E, 0x1D333C, 0x1D3658, 0x1D3836, 0x1D3A14, 0x1D3298, 0x1D351A,
    0x1D360E, 0x1D3C00, 0x1D3D0A, 0x1D3E44, 0x1D3F1A, 0x1D3F3C,
    0x1D3DDE, 0x1D5F50, 0x1D5D64, 0x1D5B44,
    0x1D1584, 0x1D18B8, 0x1D556C, 0x1D5C64, 0x1D146C, 0x1D1BE4
]

def s16(buf, off):
    if off < 0 or off + 2 > len(buf):
        return None
    v = (buf[off] << 8) | buf[off + 1]
    return v - 0x10000 if v & 0x8000 else v

def get_expected_trampoline():
    asm = []
    asm.append(0x3D80001D)
    asm.append(0x618C16F6)
    asm.append(0x7C056000)
    asm.append(0x40820028) # Corrected bne +40
    asm.append(0x3D600000 | ((CAN_SWITCH_RAM >> 16) & 0xFFFF))
    asm.append(0x896B0000 | (CAN_SWITCH_RAM & 0xFFFF))
    asm.append(0x2C0B001D)
    asm.append(0x40810008)
    asm.append(0x39600000)
    asm.append(0x3D80001C)
    asm.append(0x618C8100)
    asm.append(0x556B103A)
    asm.append(0x7CAC582E)
    asm.append(0x9421FFE8)
    asm.append(0x3D80000F)
    asm.append(0x618C94E0)
    asm.append(0x7D8903A6)
    asm.append(0x4E800420)
    return b"".join(struct.pack(">I", inst) for inst in asm)

def get_all_errors():
    errors = []
    if not os.path.exists(INPUT_BIN):
        return [f"FATAL: File missing: {INPUT_BIN}"]

    try:
        with open(INPUT_BIN, "rb") as f:
            buf = bytearray(f.read())
    except Exception as e:
        return [f"FATAL: File read error: {e}"]

    if len(buf) != 2097152: 
        return [f"FATAL: File size is {len(buf)} (expected 2097152)"]

    # 1. Checksums
    stored_crc = struct.unpack_from(">I", buf, CHECKSUM_OFFSET_CRC)[0]
    stored_sum = struct.unpack_from(">H", buf, CHECKSUM_OFFSET_SUM)[0]
    test_buf = bytearray(buf)
    test_buf[CHECKSUM_OFFSET_CRC:CHECKSUM_OFFSET_CRC+4] = b"\x00\x00\x00\x00"
    test_buf[CHECKSUM_OFFSET_SUM:CHECKSUM_OFFSET_SUM+2] = b"\x00\x00"
    calc_crc = zlib.crc32(test_buf[0:CHECKSUM_OFFSET_CRC]) & 0xFFFFFFFF
    calc_sum = sum(test_buf[0:CHECKSUM_OFFSET_SUM]) & 0xFFFF
    calc_sum = (0x10000 - calc_sum) & 0xFFFF
    if stored_crc != calc_crc:
        errors.append(f"Checksum Error: CRC32 mismatch! Stored: {stored_crc:08X}, Calc: {calc_crc:08X}")
    if stored_sum != calc_sum:
        errors.append(f"Checksum Error: SUM16 mismatch! Stored: {stored_sum:04X}, Calc: {calc_sum:04X}")

    # 2. Trampoline
    expected_tramp = get_expected_trampoline()
    actual_tramp = buf[TRAMPOLINE_ADDR : TRAMPOLINE_ADDR + len(expected_tramp)]
    if actual_tramp != expected_tramp:
        for i in range(0, len(expected_tramp), 4):
            exp_word = expected_tramp[i:i+4]
            act_word = actual_tramp[i:i+4]
            if exp_word != act_word:
                errors.append(f"Trampoline Error: Instruction mismatch at 0x{TRAMPOLINE_ADDR + i:08X}. Expected {exp_word.hex().upper()}, Found {act_word.hex().upper()}")

    # 3. Hook
    expected_branch = 0x48000000 | ((TRAMPOLINE_ADDR - MAP_2D_READER) & 0x03FFFFFC)
    actual_branch = struct.unpack_from(">I", buf, MAP_2D_READER)[0]
    if actual_branch != expected_branch:
        errors.append(f"Hook Error: Instruction at 0x{MAP_2D_READER:08X} is {actual_branch:08X}, expected {expected_branch:08X}")

    # 4. Table
    for i, expected_addr in enumerate(EXPECTED_MAPS):
        val = struct.unpack_from(">I", buf, TABLE_ADDR + (i * 4))[0]
        if val != expected_addr: 
            errors.append(f"Table Error: Index {i} mismatch. Found {val:08X}, expected {expected_addr:08X}")

    # 5. Maps & Overlaps
    allocated_ranges = []
    allocated_ranges.append(("Trampoline", TRAMPOLINE_ADDR, TRAMPOLINE_ADDR + len(expected_tramp)))
    allocated_ranges.append(("MapTable", TABLE_ADDR, TABLE_ADDR + (30 * 4)))
    
    for i, addr in enumerate(EXPECTED_MAPS):
        nx = s16(buf, addr)
        ny = s16(buf, addr + 2)
        if nx is None or ny is None:
            errors.append(f"Map {i} at {addr:08X} read failure.")
            continue
        if nx < 2 or nx > 64:
            errors.append(f"Map {i} at {addr:08X} invalid Nx={nx} (must be 2-64)")
            continue
        if MAP_TYPES[i] == '2D':
            if ny < 2 or ny > 64:
                errors.append(f"Map {i} at {addr:08X} invalid Ny={ny} (must be 2-64 for 2D map)")
                continue
            size = 4 + (2 * nx) + (2 * ny) + (2 * nx * ny)
        else:
            size = 2 + (4 * nx)
            
        map_end = addr + size
        for name, start, end in allocated_ranges:
            if addr == start:
                continue # Allow exact duplicate map pointers
            if addr < end and map_end > start:
                errors.append(f"Overlap Error: Map {i} ({addr:08X}-{map_end:08X}) overlaps with {name} ({start:08X}-{end:08X})")
        allocated_ranges.append((f"Map_{i}", addr, map_end))

    return errors

def main():
    print("=== ULTIMATE CONTINUOUS ERROR AUDIT ===")
    print(f"Target: {INPUT_BIN}")
    print("Checks: CRC32, SUM16, Trampoline Bytes, Hook, Map Pointers, Map Bounds, Memory Overlaps.")
    print("Scanning... The script will only exit after 10 consecutive clean passes.\n")

    consecutive_passes = 0
    unique_errors = set()
    iteration = 0

    try:
        while True:
            iteration += 1
            errors = get_all_errors()
            if errors:
                consecutive_passes = 0
                new_errors_found = False
                print(f"--- Iteration {iteration} --- FAILED ({len(errors)} errors)")
                for err in errors:
                    if err not in unique_errors:
                        print(f"  [NEW ERROR] {err}")
                        unique_errors.add(err)
                        new_errors_found = True
            else:
                consecutive_passes += 1
                print(f"--- Iteration {iteration} --- PASSED ({consecutive_passes}/10)")

            if consecutive_passes >= 10:
                print("\n" + "="*50)
                print("[+] SUCCESS! 10 consecutive deeply validated clean passes achieved.")
                print("="*50)
                print("\nVerified Components:")
                print("  - File Size: 2 MB")
                print("  - CRC32 and SUM16 Checksums mathematically perfect")
                print("  - PowerPC Trampoline machine code is byte-for-byte correct")
                print("  - Hook branch instruction is exactly correct")
                print("  - 30 Map pointers match perfectly")
                print("  - All Map headers (Nx/Ny) are valid")
                print("  - No overlapping map data (duplicates allowed)")
                print("  - CAN Switch RAM address: 0x%06X" % CAN_SWITCH_RAM)
                break
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[!] Interrupted by user. Exiting.")

if __name__ == "__main__":
    main()
