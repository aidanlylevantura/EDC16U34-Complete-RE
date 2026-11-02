# grep_periph.py
# Run from cmd.exe:
#   cd /d "C:\Users\user\Documents\Complete ECU Disassembly"
#   python grep_periph.py
#
# Reads EDC16U34_FINAL_Annotated.c and finds functions that access
# peripheral registers in the 0x006F0000-0x006FFFFF and 0x007F0000-0x007FFFFF ranges.
# These addresses are resolved by Ghidra's constant propagation, so they
# appear in the .c text even though the raw instructions use lis+ori.

import os, re
from collections import defaultdict

C_FILE = r"C:\Users\user\Documents\Complete ECU Disassembly\EDC16U34_FINAL_Annotated.c"
OUT    = r"C:\Users\user\Documents\Complete ECU Disassembly\_PERIPH_GREP.txt"

if not os.path.exists(C_FILE):
    print("[!] not found: %s" % C_FILE)
    print("    Available .c files in that folder:")
    d = os.path.dirname(C_FILE)
    for f in sorted(os.listdir(d)):
        if f.endswith(".c"):
            print("      %s" % f)
    raise SystemExit(1)

text = open(C_FILE, "r", encoding="utf-8", errors="replace").read()
print("[+] read %d bytes" % len(text))

# Split by function definition (Ghidra style: "void FUN_xxxxxxxx(...)\n{")
# Each function block runs from its signature to the matching closing brace.
FUNC_RE = re.compile(
    r'^(?:void|int|uint|undefined\d*|char|byte|short|ushort|bool|long|ulong|float|double|code)\s+'
    r'(\w+)\s*\([^)]*\)\s*\{',
    re.MULTILINE,
)

# Find all function starts
starts = []
for m in FUNC_RE.finditer(text):
    starts.append((m.start(), m.group(1)))

# Slice into function bodies
blocks = []
for i, (start, name) in enumerate(starts):
    end = starts[i+1][0] if i+1 < len(starts) else len(text)
    blocks.append((name, text[start:end]))

print("[+] found %d function blocks" % len(blocks))

# Peripheral address patterns in decompiled text
# Matches: _DAT_006fc100, DAT_006fc100, _DAT_006F827E, 0x006FC100, etc.
PAT_006F = re.compile(r'(?:_?DAT_|0x)0{0,2}6[fF]([0-9a-fA-F]{4,5})')
PAT_007F = re.compile(r'(?:_?DAT_|0x)0{0,2}7[fF]([0-9a-fA-F]{4,5})')

# IMMR block ranges (correct base from DSM_FUN_000006a0)
BLOCKS = {
    # 0x006F8000 area (from FUN_00050110 reads)
    0x006F8000: "eQADC_or_misc",
    0x006F8800: "eMIOS",
    0x006FC000: "SIU_base",
    0x006FC080: "SIU_GPDI",
    0x006FC100: "SIU_GPDO",
    0x006FC200: "eDMA",
    0x006FC280: "SIU_MCR",
    0x006FC300: "SIU_SYCRA",
    0x006FC380: "SIU_SYCRB",
    0x006FC400: "eSCI_A",
    0x006FC500: "eSCI_B",
    0x006FC600: "DSPI_A",
    0x006FC700: "DSPI_B",
    0x006FC800: "DSPI_C",
    0x006FC900: "DSPI_D",
    0x006FCA00: "FlexCAN_A",
    0x006FCB00: "FlexCAN_B",
    0x006FCC00: "FlexCAN_C",
    0x006FCD00: "FlexCAN_D",
    0x006FD000: "INTC",
    0x007F0000: "RAM_global",
    0x007F8000: "RAM_global_high",
}

def block_of(addr):
    for b in sorted(BLOCKS.keys(), reverse=True):
        if addr >= b:
            return BLOCKS[b]
    return None

# Scan each function
results = []  # (func_name, block_label, hit_count, sample_addresses)
for name, body in blocks:
    per_block = defaultdict(int)
    samples = defaultdict(list)

    for m in PAT_006F.finditer(body):
        try:
            addr = int("0x006f" + m.group(1), 16)
            b = block_of(addr)
            if b:
                per_block[b] += 1
                if len(samples[b]) < 5:
                    samples[b].append(addr)
        except: pass

    for m in PAT_007F.finditer(body):
        try:
            addr = int("0x007f" + m.group(1), 16)
            b = block_of(addr)
            if b:
                per_block[b] += 1
                if len(samples[b]) < 5:
                    samples[b].append(addr)
        except: pass

    for b, count in per_block.items():
        results.append((name, b, count, samples[b]))

# Sort by hit count
results.sort(key=lambda x: -x[2])

# ==== OUTPUT ====
LINES = []
def w(s=""):
    LINES.append(str(s))
    print(s)

w("=" * 78)
w("PERIPHERAL ACCESS GREP — EDC16U34_FINAL_Annotated.c")
w("=" * 78)
w("Correct IMMR base: 0x006FC000 (from DSM_FUN_000006a0)")
w("")
w("Total functions in .c: %d" % len(blocks))
w("Total peripheral references: %d" % len(results))
w("")

# Group by block
by_block = defaultdict(list)
for name, b, count, samples in results:
    by_block[b].append((name, count, samples))

w("--- Peripherals by function ---")
w("")
for b in sorted(by_block.keys()):
    funcs = by_block[b]
    total = sum(c for _, c, _ in funcs)
    w("[%s]  %d functions  %d total accesses" % (b, len(funcs), total))
    for name, count, samples in funcs[:10]:
        sample_str = " ".join("0x%08x" % s for s in samples[:3])
        w("    %-48s %3d hits   %s" % (name, count, sample_str))
    if len(funcs) > 10:
        w("    ... and %d more" % (len(funcs) - 10))
    w("")

# ==== TOP EEPROM / CAN / HAL CANDIDATES ====
w("=" * 78)
w("TOP CANDIDATES BY PERIPHERAL")
w("=" * 78)
w("")

def show_top(label, funcs_list, n=5):
    w("--- %s ---" % label)
    for name, count, samples in funcs_list[:n]:
        w("  %-48s %3d hits" % (name, count))
    w("")

# EEPROM: DSPI or bit-bang
show_top("EEPROM driver (DSPI_A/B or eSCI bit-bang)",
         by_block.get("DSPI_A", []) + by_block.get("DSPI_B", []) +
         by_block.get("eSCI_A", []) + by_block.get("eSCI_B", []))

# CAN: FlexCAN blocks
show_top("CAN driver (FlexCAN_A/B/C/D)",
         by_block.get("FlexCAN_A", []) + by_block.get("FlexCAN_B", []) +
         by_block.get("FlexCAN_C", []) + by_block.get("FlexCAN_D", []))

# HAL: ADC/PWM/timers
show_top("HAL (eQADC/eMIOS/eTPU)",
         by_block.get("eQADC_or_misc", []) + by_block.get("eMIOS", []))

# SIU GPIO (bit-bang source)
show_top("SIU GPIO (potential bit-bang EEPROM)",
         by_block.get("SIU_GPDI", []) + by_block.get("SIU_GPDO", []))

# ==== SAVE ====
with open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(LINES))
print("")
print("[+] wrote %s" % OUT)