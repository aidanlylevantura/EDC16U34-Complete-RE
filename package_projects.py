import os
import shutil

BASE = r"C:\Users\user\Documents\Complete ECU Disassembly"

PROJECTS = {
    "EDC16U34-Multimap-Release": {
        "files": [
            "build_multimap.py",
            "edc16_fix_checksum.py",
            "sanity_check_build.py",
            "03G906021KH_382083_MULTIMAP_v3_R1_CANSTALK_CANDIDATE.bin",
        ],
        "readme": """# EDC16U34 Multimap Release

Multimap tooling and candidate binary for Bosch EDC16U34 (VW Golf 5 / Seat Leon, VAG 03G906021KH, SW 382083).

## Contents

- build_multimap.py - builds a multimap candidate from a stock 2MB flash image.
- edc16_fix_checksum.py - fixes the three FADECAFE additive checksum regions (target 0xD01FE500).
- sanity_check_build.py - verifies region sums and inner checksum locations.
- 03G906021KH_382083_MULTIMAP_v3_R1_CANSTALK_CANDIDATE.bin - candidate multimap binary.

## Required local files

You must supply your own stock 2MB flash image and your own thunk hex. Do not upload Bosch/VAG proprietary stock firmware, WinOLS CSV files, original EEPROM dumps, or personal IMMO/VIN data.

## Checksums

- Region 0x040000-0x17FFFF, checksum at 0x17FFFC
- Region 0x180000-0x1BFFFF, checksum at 0x1BFFFC
- Region 0x1C0000-0x1FDFFF, checksum at 0x1FDFFC

All three must sum to 0xD01FE500.

## Status

Software build and checksum validation are complete. Bench testing is pending. Do not flash a daily-driven ECU without a BDM recovery backup.
""",
    },
    "EDC16U34-ReadWrite-Tool": {
        "files": [
            "bench_test.py",
            "unlock_ecu_can.py",
            "full_flash_writer.py",
            "receive_flash_stream.py",
            "build_033_payload.py",
            "compute_key.py",
            "bdm_extract_key.py",
            "replay_capture.py",
            "edc16_fix_checksum.py",
        ],
        "readme": """# EDC16U34 Read/Write Tool

Experimental CAN read/write tooling for Bosch EDC16U34.

## Contents

- bench_test.py - Phase 1 safe bench validation: TesterPresent, session, single Seed/Key attempt, 0x30 handshake only. No 0x31/0x32/0x33.
- unlock_ecu_can.py - Seed/Key unlock over CAN.
- full_flash_writer.py - 2MB flash writer using 0x30/0x31/0x32/0x33. The 0x33 finish requires a valid RSA-1024 signature.
- receive_flash_stream.py - receiver for a future RAM-injection read stream. Not validated on hardware.
- build_033_payload.py - builds a 50-byte 0x33 bench-test payload with confirmed constants.
- compute_key.py - LFSR Seed/Key implementation.
- bdm_extract_key.py - scans a BDM internal-memory dump for the RSA private exponent.
- replay_capture.py - parses a savvyCAN capture and replays tester messages.
- edc16_fix_checksum.py - FADECAFE checksum fixer.

## Important limits

- The 0x33 finish is protected by RSA-1024 with e=3. The private key was not found in the external 2MB flash after a full scan. Do not expect full_flash_writer.py to complete a write without a valid signature.
- The CAN read path is not validated. Do not run RAM injection read shellcode on a live ECU without a BDM recovery backup.
- Bench-test only. Do not use on a daily-driven vehicle.

## Safe first test

Run only:

```cmd
python bench_test.py --port COMx