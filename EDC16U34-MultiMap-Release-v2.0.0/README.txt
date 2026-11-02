EDC16U34 MultiMap Release v2.0.0 
 
This folder contains the verified scripts and data for the 30-Map MultiMap build. 
 
INCLUDED FILES: 
- Flash.bin (Original unmodified BDM read) 
- build_safe_30map_fixed.py (Injects 30 maps and PPC trampoline) 
- validate_10x.py (10-loop structural and checksum validator) 
- maps_per_block.txt (Full r15 block table analysis) 
 
INSTRUCTIONS: 
1. Run build_safe_30map_fixed.py to generate the binary. 
2. Run validate_10x.py to confirm checksums. 
