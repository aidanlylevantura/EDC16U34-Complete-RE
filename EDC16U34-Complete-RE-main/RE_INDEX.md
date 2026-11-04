# EDC16U34 RE — Recall Index

Purpose: a small, stable entry point. Load **this** file first in a new session,
then read only the section you need. Nothing here duplicates the documents; it
points at them.

Last updated: after the 0x0F55D4 tip-step pass.
Context window is 1M tokens - do NOT assume the session is exhausted.

---

## 1. The three things that exist

| What | Where |
|---|---|
| Cruise control write-up (canonical, address-backed) | `CRUISE_CONTROL_RE.md` |
| Original user RE tree (architecture, A2L dumps, decompiled C) | `README.md`, `ARCHITECTURE.md`, `EDC16U34_Reference.md`, `Golf_KH_MASTER.c` |
| Working tree with binaries, builders, tools, scripts | `C:\Users\user\OneDrive\Documents\deepseek-harness\default-workspace\edc16-multimap\` |

Binary under analysis:
`edc16-multimap\out\repo_ready\binaries\Stock_Baseline.bin`
(2 MB, 03G906021KH / 1037382083, MPC562 big-endian)

---

## 2. How to find a topic fast

Do not read the whole document. Grep it:

```
grep -n "0x7F9413" CRUISE_CONTROL_RE.md      # a specific address
grep -n "^## " CRUISE_CONTROL_RE.md          # section list
grep -n "open\]" CRUISE_CONTROL_RE.md        # unresolved items
```

Sections in `CRUISE_CONTROL_RE.md`:

```
1  Layer model              overall dataflow, one diagram
2  Input layer              CAN 0x360, accessor, decoder, debounce, stalk encoding
3  Inhibit / status codes   0x7FD537 and its priority encoder
4  State machine            0x7FD5A5, state codes, per-state timers
5  Speed chain              target/actual/limit, ramp, controller
6  Calibration block        0x1C1464-0x1C199A, maps and curves
7  Vmax                     EEPROM + flash + clamp chain
8  Pedal interface          0x7F95C4 and the shared torque path
9  Multimap consequences    trigger options (9.1 has the final answer)
10 Open items               what is genuinely unknown
11 Method and tooling       which script produced which fact
12 Corrections              earlier wrong claims, superseded
```

---

## 3. Address quick reference

Values are proven from the binary unless marked.

```
CAN / INPUT
0x41408          CAN RX descriptor table, 40 records x 20 bytes
0x7FF024         buffer for CAN 0x360 (frame index 0)
0x7FF114         buffer for CAN 0x38A  (not used by FGR)
0x40A3C          signal table, 6-byte entries; ALIAS layer (many ids -> same bit)
0x0FC25C         signal accessor
0x0A984C         stalk decoder (FUN_000a984c), range to 0x0AA49B
0x7F93FD         rocker byte: bit0=sig0xC2  bit1=sig0xC4  bit2=sig0xC3  bit3=sig0xC5
0x7F9413         switch contact byte, 8 contacts, see §9.1 bit map
0x7F9412         aggregate "any stalk switch active", written 0x0AB1C8
0x0F813C         debounce primitive (state_ptr, input_bit, cal)
0x1C18F9/0x1C18FD/0x1C18FE   per-signal debounce constants

CONTROL
0x0F4210         FGR core (state machine, inhibit, loop)
0x7F953A         main switch bit 0
0x7FD537         inhibit code, 2..12, 0xFF = none; encoder 0x0F49C0
0x7FD5A5         state byte; codes 0/1/4/6/7/8/11/12/13
0x7FD588         published state
0x7FD5CC         per-state timer, table 0x1C190C indexed by state
0x7FD560         vMin bound     (writer 0x0F4FA4) 24.14/20.00 km/h
0x7FD562         SETPOINT v_Soll (writer 0x0F5268)
0x7FD55E         vMax bound     (writer 0x0F4FC4) 255.00 km/h
0x7F946F         variant selector: bit0 picks (vMin,vMax) pair (writer 0x0B5028)
0x0F55D4         CORE STATE MACHINE FUN_000f55d4 - tip steps, all maps, state 0x7FD5A5
0x0F6CDC         builds condition word 0x7FD5C4 (tip pulses 0x400 up / 0x20 down)
0x7FD5C4         condition word; bit 0x400 = accelerate, bit 0x20 = decelerate
0x7FD564         setpoint shadow; sole writer 0x0F5284 (speed when idle, setpoint when resuming)
0x1C1912 = 805   tip step imperial big  (5 mph)
0x1C1914 = 1000  tip step metric big    (10.00 km/h)
0x1C1916 = 161   tip step imperial small (1 mph)
0x1C1918 = 150   tip step metric small  (1.50 km/h)
0x7F9359         stalk position code: 7 = up, 4 = down
0x0F4F24         setpoint supervisor FUN_000f4f24 (window, setpoint, resume)
0x0F84C0         PT1 filter  FUN_000f84c0  state 0x7FD570, tc 0x1C1464=10
0x0F4DEC         hold detector FUN_000f4dec, state 0x7FD567, counter 0x7FD568
0x7FD566         mode byte, bit3 = resume eligible (cal 0x1C1477 bit3)
0x7FD59A         stored setpoint, reference for window tests
0x7FD554-55B     eight speed-window flags

0x0F8318         clamp helper; integrator entry 0x0F8360 has no callers
0x7FD5AA         demand out; 0x7FD596 filtered demand

SPEED / VMAX
0x7F96FC, 0x7F9700   speed inputs A / B
0x7F959A             selected vehicle speed (writer 0x05BFB4), clamped 0x0906A4
0x1C1470             allowed-speed array base, [0] = 30000 = 300.00 km/h
EEPROM 0x048E        0x7530 = 30000 = 300.00 km/h (mirror 0x04CE)
0x1C0CF8             flash default 0x7530
0x7F95C4             pedal, 0..10000 = 0..100.00 %

CALIBRATION
0x1C1464-0x1C199A    FGR calibration block
0x1C146A = 2114      ramp rate A
0x1C146C = 1700      ramp rate B
0x1C146E = 300       ramp offset
0x1C1470 = 30000     Vmax array
0x1C190C             per-state timer table
0x1C15B6 etc.        reference A2L names, see document §6
```

---

## 4. Ghidra scripts

All in `edc16-multimap\ghidra\`. Output goes to `edc16-multimap\out\`.

| Script | Purpose | Output |
|---|---|---|
| `FgrFromScratch2.py` | independent sweep from the accessor outward; lists all frame-0 consumers | `edc16_fgr_fromscratch2.txt` |
| `StalkDecode.py` | stores + cal refs + C of the decoder `0x0A984C` | `edc16_stalk_decode.txt` |
| `StalkBits.py` | how `0x7F93FD` is assembled | `edc16_stalk_bits.txt` |
| `StalkRoles2.py` | condition-word bits 11/12/13 usage | `edc16_stalk_roles2.txt` |
| `AccelDecel.py` | writer of target speed, ramp arithmetic | `edc16_accel_decel.txt` |
| `TipMap.py` | full bit map of `0x7F9413` | `edc16_tipmap.txt` |
| `TipUse.py` | every access to `0x7F9413` / `0x7F93FB` / `0x7F93FC` | `edc16_tipuse.txt` |
| `TipConsumer.py` | the single consumer at `0x0AB1A8` | `edc16_tipconsumer.txt` |
| `DumpFgrCluster.py`, `FindFgrSpeedConsts.py`, `FgrFinal.py`, `FullScan.py` | earlier passes | `edc16_fgr_*.txt` |

Notes for whoever runs them:

- Ghidra "Go To" cannot resolve RAM (`0x7xxxxx`) unless a memory block is added;
  the scripts compute addresses from displacements instead.
- Do not iterate the whole image calling `getMnemonicString` per instruction — that
  is what caused two `OutOfMemoryError`s. Read raw words with `getInt` and decode
  the opcode fields, as `TipUse.py` does.
- `DecompileResults` has no `dispose()`; only `DecompileFunction` does.

---

## 5. Multimap build tree

```
edc16-multimap\out\repo_ready\
  binaries\    Stock_Baseline.bin, 03G906021KH_MultiMap_v2.0.1.bin, ..._INERT.bin
  builders\    build_multimap.py
  tools\       validate_build.py, ppc.py, ppcasm.py, kwp_ram.py, ...
  mappack\     ..._maps.csv
  docs\        RE_Notes.txt
```

Verified at last build: 12 reader maps, SOI block, DOI block with 18 hooks, slot
table `0x1F3F00 = {0x1DF02E, 0x1F4000, 0x1F6000, 0x1DF02E}`, 69/69 active,
71/71 active, 65/65 inert, 51/51 DOI path, reproducible; all three MAPS_SRC paths covered.

Trigger source to use: see document §9.1 (`0x7F9412`, or `0x7F9413 & 0xC0`).

---

## 6. Open items (do not re-derive)

1. **SET vs RES polarity** — not recoverable. The firmware ORs all eight switch
   contacts into `0x7F9412` and never distinguishes which one closed.
   Requires a J527/`0x360` DBC entry or one bus observation per stalk position.
2. **Meaning of state codes 4/6/7/8/11/12/13** — transitions visible, names not.
3. **Matching the seven calibration maps to A2L names** — dimensions and axes known.
4. **Which routine reads EEPROM `0x048E`**.

---

## 7. Known-bad claims (superseded — do not repeat)

- Cruise is on CAN **`0x360`**, not `0x38A`.
- `0x7FF122` is byte 2 of frame `0x7D0` and is used by no code.
- The decoder is `0x0A984C`, not `0x0F4210`.
- `0x7FD53A/3C/3E` are write-only diagnostic mirrors; logic path is `r31` bits 11/12/13.
- `0x7F951A` is an enable bit, not a target speed.
- There is no `cmpwi 0x61A8`; 250 km/h is a map axis endpoint.
- The FGR loop is a clamp + integrator, not a Kp/Ki/Kd PID.
- Ramp constants `0x1C146A`/`0x1C146C` are motion rates, not SET/RES constants.
- Several `r13` offsets quoted verbally earlier were computed by hand and are wrong
  (`-10842` is `0x7FD596`, not `0x7FD5A6`; tip bits are 7 and 6, not 6 and 2).
  Every address in `CRUISE_CONTROL_RE.md` was computed by script — trust it.

## Measuring blocks (separate subsystem)

- `MEASURING_BLOCKS_RE.md` - KWP 0x21 mechanism, UACC tables, addresses, open items
- `MEASURING_BLOCKS.c`      - C reconstruction with PROVEN / INFERRED / UNKNOWN markers
- `MEASURING_BLOCKS.csv`    - all 255 groups decoded to signal numbers

```
0x1E9A8A / 0x190CC2   UACC_RSigBlkGrp_MAP, 4 x 255, Y-major
0x1E9C94 / 0x190ECC   data (1020 u16), index = (group-1) + 255*(block-1)
0x1E90DC              formula table      (inferred)
0x1E9A80              normalisation       (inferred)
0x1EA48C / 0x1EA4B4   format tables       (inferred)
04CE9C 180680 180CA4 1812C8   pointer structs, +0x08 = variant selector
```

Unresolved: signal number -> variable name. The name table is an A2L COMPU_VTAB
(`SigName`, 582 entries) for software `03G997022F`, not ours; signal numbering
differs between builds.
