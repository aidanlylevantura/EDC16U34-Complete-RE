import zlib
import binascii

# UPDATE THIS PATH IF YOUR BIN FILE IS NAMED DIFFERENTLY
BIN_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"

# Typical Calibration Ranges for EDC16
CAL_START = 0x1C0000
CAL_END   = 0x1E0000

def main():
    print("=== Bosch Checksum Cracker ===")
    try:
        with open(BIN_FILE, 'rb') as f:
            data = f.read()
    except FileNotFoundError:
        print(f"ERROR: Could not find {BIN_FILE}")
        return

    print(f"File Size: {len(data)} bytes")
    
    # 1. Extract the stored checksums at the end of the blocks
    # Checksums are usually the last 4 or 8 bytes of the block
    print("\n--- Stored Checksum Bytes ---")
    print(f"End of CAL block (0x1DFFFC): {data[0x1DFFFC:0x1E0000].hex().upper()}")
    print(f"End of full Flash (0x1FFFFC): {data[0x1FFFFC:0x200000].hex().upper()}")

    # 2. Extract the calibration data block
    cal_data = data[CAL_START:CAL_END]
    
    # 3. Calculate standard checksums
    print("\n--- Calculated Checksums (Over 0x1C0000 - 0x1E0000) ---")
    
    # CRC32 (Standard)
    crc32 = zlib.crc32(cal_data) & 0xFFFFFFFF
    print(f"CRC32 (Standard): {crc32:08X}")
    
    # CRC16 (CCITT)
    crc16 = binascii.crc_hqx(cal_data, 0)
    print(f"CRC16 (CCITT):     {crc16:04X}")
    
    # Additive Sum (16-bit)
    sum16 = sum(int.from_bytes(cal_data[i:i+2], 'big') for i in range(0, len(cal_data), 2)) & 0xFFFF
    print(f"Sum16 (Additive):  {sum16:04X}")
    
    # XOR Sum (16-bit)
    xor16 = 0
    for i in range(0, len(cal_data), 2):
        xor16 ^= int.from_bytes(cal_data[i:i+2], 'big')
    print(f"Xor16 (XOR):       {xor16:04X}")

    print("\n--- Instructions ---")
    print("Look at the 'Stored Checksum Bytes' above. If the last 4 or 2 bytes match")
    print("any of the calculated checksums, you have cracked the algorithm!")
    print("If not, the Bosch algorithm uses a custom polynomial seed, which")
    print("is why WinOLS handles it automatically.")

if __name__ == '__main__':
    main()