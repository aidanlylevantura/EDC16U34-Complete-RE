\# EDC16U34 Complete Reverse Engineering Notes



This document contains the raw architectural findings for the Bosch EDC16U34 (VAG 03G906021KH / SW 382083).



\## 1. The ROMless MPC562 Discovery

Early attempts to reverse-engineer this ECU assumed the bootloader and master descriptor tables were hidden in an "internal flash" (the Micro) on the MPC562 processor. 



\*\*Correction:\*\* The Motorola/Freescale MPC562MZP56 is completely \*\*ROMless\*\*. It contains no internal program flash. 

\- The entire bootloader, the Reset Vector, and the Master Map Descriptor Table live in the \*\*first 256 KB of the External 2MB Flash\*\* (`0x000000` to `0x03FFFF`).

\- Many "stock" or "tune" files found online are actually partial reads that have blanked out this boot sector (`FF`). Flashing those files directly will brick the ECU. Always verify the boot sector is populated.



\## 2. The Master Descriptor Table (0x4400)

The bootloader initializes the map descriptors by reading a table located at Flash address `0x4400`.

\- The table holds RAM pointers (starting at `0x00704000`).

\- The bootloader uses a loop to read `lwzx r27, r26, r12` (where `r26` is the base `0x4400`).

\- The OS relies on this RAM table to locate the calibration maps. Hooking `r15` blindly will crash the ECU because `r15` points to this dynamic RAM structure.



\## 3. The Map Readers (Hooking Points)

To switch maps safely without patching 377 absolute references, we intercept the OS at the reader functions:

1\. \*\*Main 2D Reader (`0x0F94DC`)\*\*: The primary interpolation function for 2D maps. It expects the map header address in register `r5`.

2\. \*\*SOI Block Pointer (`0x000C0454`)\*\*: The Start of Injection maps are not individual maps; they are a shared 7.8 KB block loaded via `lwz r31, 0x428(r15)`.



\## 4. The RSA 0x33 Security Check

The ECU uses an RSA-1024 signature check on the `0x33` (Finish Flash) diagnostic service.

\- \*\*Dispatcher:\*\* The `0x33` handler is at `FUN\_000151d0`.

\- \*\*Verifier:\*\* The RSA math and signature check happen inside `FUN\_00023fe4` (called from `0x151d0`).

\- \*\*Success Token:\*\* If the signature is valid, `FUN\_00023fe4` outputs the status `10` (`0xA`) and the magic token `0x61af3c8e`.

\- \*\*Vulnerability:\*\* The verification function does not rely on a hardware secure element. It can be patched by overwriting the start of `FUN\_00023fe4` to immediately return the success token, completely bypassing the RSA check. (See `EDC16U34-ReadWrite-Tool` for the bypass script).



\## 5. Memory Layout (External Flash)

\- `0x000000` - `0x03FFFF`: Bootloader / OS Security / Master Tables (ROMless init).

\- `0x040000` - `0x17FFFF`: OS Code (Application).

\- `0x180000` - `0x1BFFFF`: Calibration 1 (Dormant).

\- `0x1C0000` - `0x1FDFFF`: Calibration 2 (Active Maps).

\- `0x1FE000` - `0x1FFFFF`: Empty Flash Tail (Used for custom hooks/thunks).



\## 6. Checksum Regions

The OS validates three FADECAFE regions using a 32-bit additive sum with balance words.

\- OS: `0x040000` - `0x17FFFF` (Balance at `0x17FFFC`)

\- Cal 1: `0x180000` - `0x1BFFFF` (Balance at `0x1BFFFC`)

\- Cal 2: `0x1C0000` - `0x1FDFFF` (Balance at `0x1FDFFC`)

All three sums must equal `0xD01FE500`. Any custom code injected outside these regions (like at `0x1FE000` or in the bootloader) requires no checksum adjustment.

