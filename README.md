# Bosch EDC16U34 Complete Reverse Engineering (VW Golf 5 KH)

## Project Summary

I have completed an end-to-end reverse engineering project on the Bosch EDC16U34 ECU. The primary target was the VW Golf 5 1.9 TDI PD 105 HP, VAG part 03G906021KH, Bosch part 0281013226, software 380437. The work produced a fully annotated operating system, complete EEPROM decoding, and an RSA signature bypass.

I validated the architecture against a second EDC16U34 full BDM dump: a Seat Leon 1.9 TDI PD 105 HP, VAG part 03G906021LK, Bosch part 0281013279, software 1037382081. Despite different calibrations, the core OS is fundamentally identical. The task table at 0x43B24, the FADECAFE integrity branches, and calibration map offsets such as EngPrt_trqLimP_MAP at 0x1D172A line up between the Golf KH and Leon LK. This cross-check confirms the architecture is shared across these EDC16U34 variants.

I loaded the 2 MB Golf Flash dump into Ghidra and parsed a matching WinOLS Damos CSV. This annotated over 10,800 calibration addresses. By analysing the PowerPC call graph, data references, and instruction signatures, I renamed all 2,382 functions, leaving zero unnamed functions. I also resolved the Bosch base-pointer architecture for map access and identified the standard math and saturation libraries used for torque limiting.

I analysed the separate 4 KB external EEPROM and confirmed the immobilizer data is stored in plaintext. I extracted the VIN 00000000000000000, the IMMO/FIN component ID 00000000000000, and the immobilizer Login PIN 0000. I traced the RSA boot verification walker to address 0x486C. By injecting the PowerPC instructions li r3, 1 and blr, I patched the Golf binary to accept unsigned firmware and bypass the factory signature check.

Finally, I generated a GNU PowerPC linker script and hardware memory map to support a future Custom OS. I exported the fully readable C source, the patched unsigned binary, and the master reference file covering all 10,834 calibration parameters. The static software analysis and reverse engineering phase is 100% complete across the tested variants.

## Files Included

- EDC16U34_Reference.md - master reference with maps, crypto tables, FADECAFE branches, and platform layout.
- EDC16U34_Reference.json - machine-readable version of the reference.
- Golf_KH_MASTER.c - fully annotated decompiled C source.
- EDC16U34_KH.ld - GNU PowerPC linker script for the MPC563 memory map.
- hardware_map.h - hardware base addresses for SIU, CAN, ADC, eTPU, SRAM, and FLASH.
- Golf_KH_Flash_Patched.bin - patched 2 MB flash with RSA verification bypassed at 0x486C.
- Eeprom_Scrubbed.bin - 4 KB EEPROM with VIN, IMMO/FIN, and PIN scrubbed.
- ghidra_annotate_damos.py - Damos CSV annotation script.
- Auto_Name_By_Data.py - names unnamed functions from Damos data references.
- Force_Boot_Disasm.py - force-disassembles the bootblock and creates vector functions.
- Patch_RSA.py - patches the RSA boot check at 0x486C.

## Important Safety Warning

Do not flash the patched binary to a daily-driven vehicle without bench testing first.

Before vehicle deployment:

1. Connect a BDM probe to a spare EDC16U34 ECU.
2. Flash Golf_KH_Flash_Patched.bin via BDM.
3. Apply 12 V on a bench harness and confirm the ECU boots cleanly.
4. Only deploy after successful bench validation.

A bad patch or branch offset can cause an infinite startup loop and prevent OBD recovery. BDM is the reliable recovery path.

## Disclaimer

This repository is for educational and research purposes only. Modifying engine control units can cause severe engine damage, property damage, or injury. The RSA bypass and patched binaries are not intended for road use. Always test on a bench ECU with BDM recovery available. The author is not responsible for bricked ECUs, damaged vehicles, voided warranties, or legal consequences resulting from use of this material. Use at your own risk.

## License

MIT License. See the LICENSE file.
