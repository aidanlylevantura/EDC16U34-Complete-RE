# EDC16U34 Measuring Blocks - Reverse Engineering

Bosch EDC16U34, VAG `03G 906 021 KH`, SW `1037382083`, component `9245`
(2007 Golf Mk5 1.9 TDI BXE, DSG DQ250).

This document covers the KWP2000 service `0x21` path - how a request for
"group N" turns into the four values VCDS displays. It is separate from
`CRUISE_CONTROL_RE.md` because it is a different subsystem, and because this one
has a documented correction history that deserves its own record.

---

## 1. The mechanism

A measuring block is not computed by firmware logic. It is a **table lookup**
followed by a formula and a scaling, all of it in calibration:

```
UACC_RSigBlkGrp_MAP    group + block  ->  signal number
UACC_ESBFormular_C     signal         ->  formula ID     (how VCDS parses)
UACC_ESBNormVal_C      signal         ->  constant "A"    (in that formula)
UACC_ESBSigNr_C        signal         ->  SigName index
SigName table (A2L)    index          ->  variable name
sig_<cat>DIAScale_C    scale for the name's category
sig_<cat>DIAOffset_C   offset for the name's category
```

The response on the wire is `0x61`, the echoed group number, then four fields of
`{value_hi, value_lo, formula_id}` - 13 bytes total, which is exactly what the
handler at `0x9863C` writes (`li r11,13` at `0x9869C`).

The four values are sent as **8-bit each** after scaling, so the formula's
constant `A` and the category scale together determine both range and resolution.
Raising a display limit means changing `A` and the matching `sig_*DIAScale_C`, not
touching any value in RAM.

---

## 2. The tables in this calibration

### 2.1 UACC_RSigBlkGrp_MAP - located

Two byte-identical copies:

```
0x1E9A8A   Cal2
0x190CC2   Cal1

header    u16 nx = 4, u16 ny = 255
axis X    1, 2, 3, 4              (block 1..4)
axis Y    1, 2, ... 255           (group number)
data      1020 u16 at 0x1E9C94 (Cal2) / 0x190ECC (Cal1)
```

Storage is **Y-major**, the same convention as every other map in this firmware:

```
index = (group - 1) + 255 * (block - 1)
```

Blob length `0xA02` = 2562 bytes = header (4) + X axis (8) + Y axis (510) +
data (2040), which confirms the layout independently.

Content of the Cal2 copy:

```
groups with all 4 blocks filled    45 of 255
groups partially filled           103
completely empty groups           152
distinct signal numbers           157, range 0..437
```

Full decode of all 255 groups: `MEASURING_BLOCKS.csv`.

### 2.2 The companion tables

No instruction addresses these tables directly - zero `lis`+`addi`/`ori`
formations reach the header, the axes or the data. They are reached through
**pointer structs**, which appear at four places:

```
04CE9C   180680   180CA4   1812C8

   +0x00  0x1E90DC
   +0x04  0x1E9A80
   +0x08  0x1E9A8A  (Cal2)  or  0x190CC2  (Cal1)   <- variant selector
   +0x0C  0x1EA48C
   +0x10  0x1EA4B4
```

The third entry switching between the two copies is the calibration variant
selector; the same struct exists once in the OS region and three times in Cal1.

Content shape of the companions:

```
0x1E90DC  u8 array, max 115, 39 distinct     consistent with formula IDs
0x1E9A80  u8 array, max 255                  consistent with normalisation values
0x1EA48C  mixed u8/u16, 0xFFF0 marker        format table, not signal numbers
0x1EA4B4  u16: 0A10 0001 0203 0405 ...       small conversion table
```

None of the four is `UACC_ESBSigNr_C`. That table is **not present** in this
calibration as a 561- or 582-entry array of any shape tested.

### 2.3 What the signal numbers are not

They are **not RAM addresses**. A search for an array of `r13` displacements
(`0x8000..0xFFFE`) of the expected length found nothing in Cal1 or Cal2.

Signal numbers are indices into a **name table that lives in the A2L**, not in
the ECU. The firmware never needs the names; only the diagnostic tool does.

---

## 3. What a signal number means

From the reference A2L (`03G997022F`, a neighbouring EDC16U34 build), `SigName`
is a `COMPU_VTAB` with 582 entries:

```
0    "Sig_unused"
13   "VSSCD_vCarb1__Carb_v_DLen1"
16   "AFSCD_dmAirRawPerTime__Carb_mAirTim_DLen2"
31   "VehDa_tiCarbEngOn__OneToOne_DLen2"
222  "InjCtl_qCurr__q_DLen1"
```

Name format is `<Module>_<variable>__<scale>_<length>`, and the scale character
selects `sig_<scale>DIAScale_C` and `sig_<scale>DIAOffset_C`.

**`0` means unused, exactly like `255`.** Both markers appear in the block table
and neither displays a value.

---

## 4. Corrections to earlier conclusions

This subsystem produced three wrong answers before the right one. They are
recorded because the reasoning errors are reusable lessons.

### 4.1 "Measuring blocks are not table-driven" - WRONG

Concluded from a search for `Messwert`, `MWB` and `DIUMPR` across the A2L, all of
which came up empty or irrelevant. The Bosch identifiers are `UACC_*` and
`ESB*`, and both A2Ls contain all four tables. Searching for the German word
instead of the Bosch acronym produced a confident negative.

### 4.2 "The tables are at 0x1F1BC4 / 0x1F2026 / 0x1F25BA" - WRONG for our SW

Those are the reference build's addresses. In `1037382083` that whole region is
`0xFF`. The tables exist, at different addresses, found by structure.

### 4.3 "The 0x21 handler reads no per-group table" - WRONG

The Ghidra walk of `FUN_000971DC` and 30 callees found only the identification
block (`0x1C0C92`, `0x1C0D00`) as calibration references. That is correct as far
as it goes - the handler reaches the block table through a pointer struct, which
a direct-reference scan cannot see.

### 4.4 Group-major vs Y-major

First decode assumed the 4 blocks of a group were consecutive u16. That produced
`group 1 = [0,0,0,0]` and 152 fully-empty groups, which is implausible for an ECU
that answers VCDS. Y-major gives every low group four populated slots and matches
the map convention used everywhere else in this firmware.

---

## 5. Open items

**Our signal names.** The reference SigName table belongs to `03G997022F`, not to
`1037382083`. Signal numbering differs between builds - group 1's indices do not
resolve to sensible names in the reference table - so the names cannot be
transferred. Recovering them needs the A2L for `1037382083`, which is not
available here.

**Which copy is live.** The variant selector suggests one of `0x1E9A8A` /
`0x190CC2`, but nothing establishes which the running software picks. Editing
both is the safe course.

**Formula and normalisation assignment.** `0x1E90DC` and `0x1E9A80` are identified
by content shape only, not by following the code that consumes them.

---

## 6. How to add or repoint a block

No code change is required. The tables are calibration.

1. Pick a group. 152 are entirely `255` and free; group 14 and group 30 are
   examples.
2. Write four signal numbers into that group's slots:
   `data + 2 * ((group-1) + 255*(block-1))`.
3. Make sure the formula (`0x1E90DC`) and normalisation (`0x1E9A80`) entries for
   those signal numbers match the value's units, or VCDS will render nonsense
   with confident digits.
4. Edit **both** copies if the variant selector is unknown.
5. Checksums: the tables sit in Cal2, so the additive sum at `0x1FDFFC` must be
   recomputed. `0x1E9A8A` is below `FREE_LO = 0x1EA7C8`, so the multimap build
   never touches it.

**Caveat that matters:** step 2 is only useful once you know which signal number
carries what. In this build, you do not. The practical route is empirical - pick
a group whose VCDS reading you know, change one index, and observe what moves.
Group 1 block 2 = signal 1 is a single-word experiment.

---

## 7. Method notes

What worked:

- searching for a **shape** (map header `{nx=4, ny=255}` with axes `1..4` and
  `1..255`) rather than a name;
- confirming the layout arithmetically from the blob length and the reference
  table offsets;
- finding the pointer structs, which is where a direct-reference scan fails.

What did not:

- name-based searches using German terminology;
- assuming reference addresses transfer between software builds;
- loose "looks like a displacement array" scans, which flooded on repeated
  fill values and produced thousands of false positives.
