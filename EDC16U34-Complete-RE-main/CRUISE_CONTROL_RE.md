# Bosch EDC16U34 — Cruise Control (FGR / GRA) Reverse Engineering

Target: VAG `03G906021KH`, SW `1037382083`, 2006 Golf Mk5 1.9 TDI BXE, DSG.
Binary: 2 MB external flash, MPC562 (PowerPC big-endian).

Everything below was extracted from the binary itself. Each claim carries the
address it came from. Items that are inference are marked **[inferred]**;
items still unresolved are listed at the end.

SDA base: `r13 = 0x7FFFF0`. All RAM addresses are `r13 + signed_disp`.

---

## 1. Layer model

Cruise control is not one module. Five layers, and only two of them are
application code:

```
J527 steering column
   |  CAN 0x360, 8 bytes
   v
[1] CAN RX           descriptor table 0x41408, buffers 0x7FF024 + 12*i
   v
[2] signal accessor  0x0FC25C, table 0x40A3C  (id -> frame, bit, length)
   v
[3] switch decoder   debounce 0x0F813C -> flags 0x7FD53A / 0x7FD53C / 0x7FD53E
   v
[4] FGR core         0x0F42xx - 0x0F72xx  (state, inhibit, speed loop)
   v
[5] torque demand    0x7FD5AA -> driver-demand path -> DW maps -> IQ
```

---

## 2. Input layer

### 2.1 CAN frames

The RX descriptor table is at `0x41408`: 40 records of 20 bytes,
`{buffer_ptr, index, 0, cfg1, cfg2}`. The config record (`cfg2 & 0xFFFFFF`)
begins with the 11-bit CAN identifier.

```
rec 20   buffer 0x7FF114   id 0x38A     <- GRA_Neu (not consumed by FGR code)
rec 21   buffer 0x7FF120   id 0x7D0
rec  0   buffer 0x7FF024   id 0x360     <- the frame the FGR actually reads
```

Buffers are 12 bytes apart, 8 data bytes + 4 bytes status. Payload is
big-endian.

**Correction to earlier notes:** the multimap build read `0x7FF122`, which is
byte 2 of the `0x7D0` frame. No stock code references it, and it is not the
cruise frame. Do not use it.

### 2.2 Signal accessor

```
0x0FC25C  undefined1 accessor(int id, uint *out)

  entry = *(r14 - 0x62D8) + id*6      ; r14 = 0x46D14 -> table base 0x40A3C
  len   = entry[5]
  frame = entry[2] * 0x14             ; index into the 0x41408 descriptor table
  byte  = entry[4] >> 3
  word  = byteswap(*(uint *)(framedata[frame] + byte))     ; type 2 = swap
  *out  = (word >> (entry[4] & 7)) & ((1 << len) - 1)
```

Entry layout: `{id_hi, id_lo, frame_idx, type, bit_offset, bit_length}`.

### 2.3 FGR signals (decoded)

```
sig 0xC2   frame 0 (CAN 0x360)   bit 2    -> buffer 0x7FF024 bit 2
sig 0xC3   frame 0               bit 3
sig 0xC4   frame 0               bit 4
sig 0xC5   frame 0               bit 11   -> buffer 0x7FF025 bit 3
sig 0x15C  frame 0               bit 45   -> buffer 0x7FF029 bit 5
sig 0x15E  frame 0               bit 47   -> buffer 0x7FF029 bit 7
```

### 2.3.1 Which function actually decodes them

A from-scratch sweep (start at the accessor, follow every caller) shows **14
functions** read frame 0, and the signal-ID space on that frame runs from `0x60`
to `0x187` - roughly 200 signals. Frame 0 (`0x360`) is a large multiplexed
status frame, not a cruise-only message.

The stalk decoder is:

```
FUN_000a984c @ 0x0A984C
  sigs: 0xC0..0xCA, 0xCD..0xD0, 0x156..0x161, 0x166..0x168
  bits: 0,1,2,3,4,11,..,40,45,46,47,48,56,58,60,62
```

Layering:

```
CAN 0x360 -> FUN_000a984c   decode ~30 signals incl. all stalk bits
          -> FUN_0000f4210  FGR core: debounce, state machine, speed loop
```

`0x0F4210` is **not** the decoder - it consumes what `0x0A984C` produced. Other
consumers of the same frame (for reference): `0x0A601C`, `0x0A7F64`, `0x0A8470`,
`0x0A8D84`, `0x0A91C8`, `0x0AA6CC`, `0x0AAF34`, `0x0AB2BC`, `0x0AB794`,
`0x0AC20C`, `0x0AC5E8`, `0x0AC958`, `0x0AD030`.

### 2.3.2 The signal table is an alias layer

Signal IDs are not unique references to physical bits. Many IDs resolve to the
same `(frame, bit, length)`, so "~200 signals" on frame 0 is really a much
smaller set of physical bits with several names each:

```
bit 3 len 1  ->  0x03, 0x4D, 0xC3, 0xE3, 0xFF, 0x107, 0x11D, 0x136
bit 2 len 1  ->  0x02, 0x1E, 0x4C, 0xC2, 0xD2, 0xFE, 0x106, 0x115, 0x11C
bit 4 len 1  ->  0x04, 0x20, 0x4E, 0xC4, 0x108, 0x10F, 0x11E, 0x12D
bit 0 len 8  ->  0x3F, 0x5F, 0x90, 0x98, 0xA0, 0xA3, 0xAD, 0xEB, 0x14B, ...
```

Consequence for tracing: two different functions reading "different" signal IDs
may be reading the **same contact**. Do not assume disjoint inputs.

Worked example: the hold detector's input `0x7F9410` is signal **`0xFF`**, which
is frame 0 bit 3 len 1 - **the same bit as `0xC3`**, i.e. bit 2 of `0x7F93FD`
and flag `0x7FD53E`. So the hold timer watches a contact the stalk decoder also
uses; there is no separate hold input.

### 2.4 Debounce and button flags

```
0x0F4444: uVar7 = debounce(state=0x7FD53A-1, in=(0x7F93FD >> 0) & 1, cal=0x1C18F9)
          store 0x7FD53A
0x0F4478: uVar7 = debounce(state=0x7FD53C-1, in=(0x7F93FD >> 1) & 1, cal=0x1C18F9)
          store 0x7FD53C
0x0F44AC: uVar7 = debounce(state=0x7FD53E-1, in=(0x7F93FD >> 2) & 1, cal=0x1C18F9)
          store 0x7FD53E
```

`0x0F813C` is a debounce/edge primitive: `(state_ptr, input_bit, cal)`.
The three outputs are the clean button states:

| Flag | Source |
|---|---|
| `0x7FD53A` | CAN 0x360 bit 2 |
| `0x7FD53C` | CAN 0x360 bit 4 |
| `0x7FD53E` | CAN 0x360 bit 3 |

`0x7F93FD` is the assembled switch byte (bits 0..2 = the three signals,
bit 3 = sig 0xC5).

### 2.4.1 What the stalk actually provides

The physical stalk carries **five functions**, not three buttons:

```
rocker:  ON | CANCEL | OFF
tip:     RES/+  (pull)      SET/-  (push)
```

but the FGR reads only **four** signals (`0xC2`, `0xC3`, `0xC4`, `0xC5`), and
debounces three of them. That means the inputs are **encoded**, not one-bit-per-
button. The consistent reading:

- two of the signals encode the rocker **position** (ON / CANCEL / OFF is three
  states, so two bits),
- the remaining signal(s) carry the **tip** direction (RES/+ versus SET/−),
- `0xC5` (bit 3 of `0x7F93FD`) is used outside the debounce group.

**[confirmed] The inputs are a one-hot bitfield, not a binary code.** The
decoder `FUN_000a984c` builds `0x7F93FD` bit by bit:

```
0A9B80: li r3, 0xC2 ; bl 0xFC25C ; r27 = (val != 0) ? 1 : 0        -> bit 0
0A9BA4: li r3, 0xC4 ; bl 0xFC25C ; if set: ori r25,r27,2
                                   else:    rlwinm r25,r27,0,0x1f,0x1d  -> bit 1
0A9BC8: li r3, 0xC3 ; bl 0xFC25C ; if set: ori r27,r25,4
                                   else:    rlwinm r27,r25,0,0x1e,0x1c  -> bit 2
0A9BE8: stb r27, 0x7F93FD
```

Each rocker position therefore has its **own dedicated bit**, set when that
position is active and cleared when it is not - three independent one-hot flags
packed into one byte:

```
0x7F93FD bit 0  = sig 0xC2  (frame bit 2)
0x7F93FD bit 1  = sig 0xC4  (frame bit 4)
0x7F93FD bit 2  = sig 0xC3  (frame bit 3)
0x7F93FD bit 3  = sig 0xC5  (frame bit 11)   set elsewhere in the same function
```

`FUN_0000f4210` then debounces bits 0-2 into `0x7FD53A`, `0x7FD53C`,
`0x7FD53E` - one clean flag per stalk position. The physical mapping is
ON / CANCEL / OFF across those three, with the tip (SET / RES) carried by the
`0x15C` / `0x15E` signals.

**Those three flags are diagnostic mirrors only.** A whole-image scan shows each
is written twice (`0x0F4444`/`0x0F4C84`, `0x0F4478`/`0x0F4CA0`,
`0x0F44AC`/`0x0F4CBC`) and **read nowhere**. The value the FGR actually uses is
the debounce return in `r3`, which is folded straight into a condition word:

```
0F444C: ori    r31, r31, 0x800    bit 11  <- sig 0xC2   (cleared by rlwinm 0x15,0x13)
0F4480: ori    r31, r31, 0x1000   bit 12  <- sig 0xC4   (cleared by rlwinm 0x14,0x12)
0F44B4: ori    r31, r31, 0x2000   bit 13  <- sig 0xC3   (cleared by rlwinm 0x13,0x11)
```

The same three bits are set from a second condition set at `0x0F70D4`,
`0x0F70F0`, `0x0F7108`, so the stalk state reaches the state machine through the
condition word, not through the published byte.

Reading `0x7FD53A/3C/3E` from a hook is still valid - they are refreshed every
cycle - but they are copies, and the logic path is the condition word.

What is still not pinned is which of the three positions is ON and which is
OFF; that needs one observation of `0x7F93FD` per stalk position, because the
CAN encoding itself (bit 2 / 3 / 4 of frame `0x360`) is only defined by J527.

`0x15C` (bit 45) and `0x15E` (bit 47) are two further signals from the same
frame, most consistent with the brake and clutch/ESP shut-off paths.

**Not established:** which of the three is SET, RESUME or CANCEL. They are
written here and consumed by address from another routine, so the offsets do
not reappear. The multimap trigger does not need the distinction (see §9).

### 2.5 Main switch

```
0x7F953A   bit 0 = FGR enabled     written 0x0E67F8, read 0x0ACCCC, 0x0B1B24
0x7FD538   published copy
```

---

## 3. Inhibit / condition word - `FUN_000f4210`

The FGR builds a **32-bit condition word** in which *each set bit is one blocking
or status condition*. Everything downstream reads it by bit index, so the code
is not a private enumeration - it is simply "which condition fired first".

```
0x7FD52C   condition word, built here            (writer 0x0F4B08)
0x7FD530   = 0x7FD52C & cal(0x1C18F0)            (mask: which conditions block)
0x7FD528   nonzero => force the word to 0xFFFFFFFF
0x7FD537   code = index of lowest set bit in 0x7FD530, or 0xFF
0x7FD536   same, computed over the unmasked word 0x7FD52C
```

**Code = bit index.** The encoder is a plain priority chain: bit 0 gives code 0,
bit 1 gives code 1, ... bit 31 gives 31. `0xFF` means "no condition". My earlier note that codes
ran 2..12 from bits 29..26 and 25..19 was wrong - that mapping does not exist in
this function; the code is simply the lowest set bit index, 0..31.

Note: the *setpoint supervisor* section 5.7 quotes codes 2..12 for a different
byte. That one is `0x7FD537` read as a value - which, per this section, is a bit
index, so those "codes" are condition numbers, not a separate enumeration.

### 3.1 Bit map, regenerated from the instruction stream

Every row below was produced by extracting all 76 `r13`-relative accesses in
`0x0F4210-0x0F4BFF` and matching each to the bit it sets. The instruction
address is given so the claim can be re-checked in one disassembly.

| Bit | Set at | Source | Condition |
|---|---|---|---|
| 0 | `0F4274` | `0x7F9359` | stalk position == 1 |
| 1 | `0F4290` | `0x7F935E` | nonzero |
| 2 | `0F42B4` | `0x7F931C` | `< cal 0x1C1902`, debounced by `0x1C18FA` |
| 3 | `0F42F4` | `0x7F9704` | bit 0 clear |
| 4 | `0F430C` | `0x7F9412` | **any stalk contact active** |
| 5 | `0F4338` | `0x7F9362` | `& cal 0x1C18F6`, gated by `0x1C1477` bit 1 |
| 6 | `0F435C` | `0x7F92BE` | in {0, 3}, rising edge |
| 7 | `0F440C` | `0x7F9704` | bit 10 clear, debounced by `0x1C1900` |
| 10 | `0F4400` | `0x7F942B` | bit 1 clear **and** `0x7F9704` bit 1 set (`0F440C`) |
| 11 | `0F442C` | `0x7F93FD` | bit 0 - rocker contact (sig `0xC2`) |
| 12 | `0F4460` | `0x7F93FD` | bit 1 - rocker contact (sig `0xC4`) |
| 13 | `0F4494` | `0x7F93FD` | bit 2 - rocker contact (sig `0xC3`) |
| 14 | `0F44C0` | `0x7F9359` | stalk position == 2 |
| 15 | `0F44D8` | `0x7F9316` | nonzero |
| 16 | `0F44F0` | `0x7F947C` | bit 0 clear, together with `0x7F934A` bits 4/5 (`0F44FC`) |
| 17 | `0F4538` | `0x7F9998` | in {1, 0x80, 0x200}; a second source `0x7F947D` is read at `0F4558` |
| 18 | `0F45BC` | `0x7F9700` | `< cal vAlwMin (0x1C146A / 0x1C146C)` **or** `> 0x7FD55E`; the units bit `0x7F946F` is read at `0F4598` |
| 19 | `0F45E0` | `0x7F96FE` | `< cal 0x1C18E4`, debounced by `0x1C18FC` |
| 20 | `0F4664` | `0x7FD59A` | setpoint `+ cal 0x1C18EE` vs `0x7F9700` (`0F466C`), gated by state `0x7FD5A5` (`0F45F8`) |
| 21 | `0F46C0` | `0x7F9704` | bit 2 clear |
| 22 | `0F46C0` | `0x7F9704` | bit 3 clear |
| 23 | `0F46EC` | `0x7F96FA` | `> cal 0x1C18E6` |
| 24 | `0F46EC` | `0x7F96FA` | `< cal 0x1C18E8` |
| 28 | `0F4734` | `0x7F9702` | tracking error vs `0x7FD586` (`0F4730`) `> cal 0x1C18EA` |
| 30 | `0F4794` | `0x7F99A0` | bit 5, debounced by `0x1C1901` |
| 31 | `0F47C8` | `0x7F9992` | bit 5, debounced by `0x1C18FB` |

Bits 8, 9, 25, 26, 27 and 29 are never set by this function - there is no
instruction that touches those mask positions.

### 3.1.1 The second, byte-wide status word

After the 32-bit word is published (`0F4814` -> `0x7FD52C`,
`0F4824` -> `0x7FD530`), the same function builds a byte status from a
different source set and publishes it to `0x7FD534` / `0x7FD535`:

```
0F4828  0x7F9409      0F483C / 0F4848  0x7FD534      0F4850  0x7F9704
0F4870  0x7F942E      0F4888  0x7F9990 (raw switch word)  0F488C  0x7F935B
0F4904  0x7F936E      0F4944 / 0F4958  0x7FD534 / 0x7FD535
0F48BC  -> 0x7FD538  (the published switch byte)
```

This is the word masked by `cal(0x1C18F5)` in 3.3, and it is a *different*
quantity from the 32-bit condition word above - do not conflate the two.

### 3.2 Two encoders

```c
// masked - this is the published inhibit code
if (applicable) {
    w = *(uint *)(0x7FD530);
    for (bit = 0; bit < 32; bit++)
        if (w & (1u << bit)) { *(u8*)0x7FD537 = bit; break; }
}

// unmasked - diagnostic copy
w = *(uint *)(0x7FD52C);
... -> 0x7FD536
```

`0x7FD537` and `0x7FD536` are set to `0xFF` first and only overwritten when the
encoder runs, which is the source of the "0xFF = none" behaviour.

### 3.3 Masking

`0x7FD530 = 0x7FD52C & cal(0x1C18F0)` selects which of the 32 conditions actually
block engagement on this variant. `0x1C18F5` does the same job for the byte-sized
status word at `0x7FD54A` (`0x7FD54A = status & cal 0x1C18F5`).

## 3.4 Where the stalk position comes from - `FUN_0007e3f8`

The one-hot contacts of 2.3.1 are **not** what drives the CC state machine. A
separate decoder derives a position code from a different CAN buffer.

```
0x07E3F8   FUN_0007e3f8, the position decoder
  puVar12 = *(ushort **)(r15 + 0x1F8)      a CAN buffer, NOT 0x7FF024
  gate    : if (*(u8*)(puVar12 + 0x25) == 0) -> position = 0 (OFF)
  input   : 0x7F9990   switch word from that buffer
  field   : 0x7F9990 & 0x4300              bits 8, 9, 14
```

Field decoding into the mode byte `0x7F935D`:

```
0x0100 -> 3      0x0300 -> 7      0x4100 -> 2      0x4300 -> 5      else -> 1
```

Position code `0x7F9359`, derived from the 16-bit state word `0x7FB5DC`, which
holds values `0x100, 0x103, 0x105, 0x109, 0x115, 0x129, 0x141, 0x181, 0x405,
0x809`:

```
0x100 -> 1    0x103 -> 2    0x105 -> 4    0x109 -> 7    0x115 -> 5
0x129 -> 8    0x141 -> 3    0x181 -> 6    0x405 -> 4    0x809 -> 7
0,1,2 -> 1    3,5,9 -> 0    default -> 1
```

### 3.5 Tip direction, confirmed from `FUN_000f6cdc`

The condition-word bits are rising edges of the position code, not raw contacts:

```
position 4  ->  bit 0x20      (decrease / decelerate)
position 7  ->  bit 0x400     (increase / accelerate)
position 5  ->  bit 0x80
position 6  ->  bit 0x100
position 8  ->  bit 0x1000
position 1  ->  bit 0x1
```

So SET/RES are **not** separate contacts in frame `0x360` - they are position
codes 7 and 4 of a field carried in a different frame, decoded here.

Still open: the identity of the frame at `r15+0x1F8`, and which physical detent
produces field values `0x0100 / 0x0300 / 0x4100 / 0x4300`.

### 3.6 The rocker is a 3-bit code, not one-hot

The switch word `0x7F9990` is the assembled 16-bit payload of frame `0x360`
(written at `0x0A64F0` as `sth r31`, with a `0x0101` fallback at `0x0A656C`).
The field `0x4300` is therefore three individual CAN bits:

```
bit 8   = signal 0x60
bit 9   = signal 0x61
bit 14  = signal 0x66
```

Decoded to the mode byte `0x7F935D`:

```
bit8 bit9 bit14   field     mode
 1    0    0      0x0100     3
 1    1    0      0x0300     7
 1    0    1      0x4100     2
 1    1    1      0x4300     5
 0    -    -      else       1      <- rest / no position
```

**Bit 8 is a validity bit** - it is set in every observed combination. Bits 9
and 14 form a 2-bit selector giving four states:

```
(9,14) = (0,0) -> 3      (1,0) -> 7      (0,1) -> 2      (1,1) -> 5
```

Mode 1 (bit 8 clear) is the rest position. Modes 0..7 are consumed by
`FUN_0007e3f8`; it treats `0, 1, 4` as "not engaged" and the rest as active
positions.

So the physical ON / OFF / CANCEL detents are four codes in `0x7F935D`, selected
by two CAN bits. Which detent produces which pair is still a bench or DBC
question - the ECU itself only ever compares them numerically.

## 4. State machine

```
0x7FD5A5   mode/state byte       write 0x0F6CCC, read 0x0F4238, 0x0F45F8,
                                 0x0F4648, 0x0F4770, 0x0F55EC, 0x0F71C8,
                                 0x075EF4, 0x0768BC, 0x0769F8
            compared against 0, 1, 9 at 0x0F423C..0x0F4250
0x7FD588   published copy of the state  (written 0x0F643C)
0x7FD5B8   scaled demand = value/100, clamped 0xFF  (0x0F6CC8)
0x7FD5CC   per-state timer, loaded from cal table 0x1C190C indexed by state
0x7FD576   referenced in the OFF/standby branch (bit 1) - no direct writer found;
            treat as [unverified]
0x7FD56B   debounced enable input; sole writer 0x0F4DB8, debounce state 0x7FD56C,
            parameter table 0x1C147C indexed by r31
0x7FD56B   enable flag used in the same decision
0x7FD5A6   companion byte        write 0x0F5DF0
0x7FD528..0x7FD5C4   block of 70+ state variables written by the FGR core
```

**State codes produced** (from `li r31, X` sites in `0x0F6000`-`0x0F6CCC`):

```
0, 1, 4, 6, 7, 8, 11, 12, 13
```

OFF/standby decision at `0x0F6400`:

```
0F6408: lbz   r12, 0x7FD56B   ; enable flag
0F6414: lhz   r12, 0x7FD5CC   ; timer
0F6420: lbz   r12, 0x7FD576
0F6424: rlwinm r12, r12, 30, 31, 31   ; bit 1 of 0x7FD576
0F642C: li    r31, 0          ; -> OFF
0F6434: li    r31, 1          ; -> standby
0F6438: stb   r31, 0x7FD588
0F6440: lis 0x1C / addi 0x190C        ; cal table, indexed by state
0F6448: lhzx  r12, r12, r27           ; per-state timer value
0F6450: sth   r12, 0x7FD5CC
```

Prologue at `0x0F4210`:

```
0F4218: lbz  r12, -27350(r13)    ; 0x7F951A
0F4220: rlwinm r29, r12, 0, 31, 31   ; bit 0 = enable
0F422C: stb  r29, -10952(r13)    ; 0x7FD528 published
0F4238: lbz  r29, -10827(r13)    ; 0x7FD5A5 state
0F423C: cmpwi r29, 1 / 0 / 9     ; state dispatch
0F4258: li   r11, 255            ; idle inhibit code
0F425C: stb  r11, -10937(r13)    ; 0x7FD537
```

**[open]** The exact meaning of states 0/1/9 is not established; 9 appears in
the "not blocked" path, 1 and 0 in the idle paths.

---

## 5. Speed chain and control law

### 5.1 Speed inputs

```
0x7F96FC  lhz   speed input A
0x7F9700  lhz   speed input B
0x0F4FD0: subf r8, r9, r11     ; B - A
```

`0x7F959A` is a *selected* vehicle speed (one writer at `0x05BFB4`, 25 reads),
chosen between a cal constant, a RAM value and a stack copy based on validity
flags at `0x7080F0`. It is sanity-clamped to 30000 at `0x0906A4`
(`cmpwi r10, 0x7530` / `li r9, 30000`).

### 5.2 The loop variables (verified against decompiled C)

The clamp at `0x0F8318` is `clamp(value, min, max)`, and the sites that use it
fix the roles. Terms follow the A2L:

| Address | Role | Value |
|---|---|---|
| `0x7FD560` | **vAlwMin** - allowed minimum set speed | 2414 metric / 2000 imperial = 24.14 / 20.00 km/h |
| `0x7FD55E` | **vAlwMax** - allowed maximum set speed | 255.00 km/h |
| `0x7FD562` | **computed actual speed** | from `0x7F9700`, or the PT1 output |
| `0x7FD59A` | **setpoint** - post-clamp, used by the torque path | |
| `0x7FD564` | setpoint shadow / display | |
| `0x7FD566` | mode byte; bit 3 = resume-eligible | enabled by `0x1C1477` bit 3 |
| `0x7FD570` | PT1 filter state (16.16) | filtered `0x7F96FC` |
| `0x7FD5C4` | 32-bit condition word | single writer `0x0F71A8` |
| `0x7FD554`..`0x7FD55B` | eight speed-window flags | |

Chain:

```
computed actual 0x7FD562
   -> clamp(vAlwMin 0x7FD560, vAlwMax 0x7FD55E)  at 0x0F5B9C
   -> setpoint 0x7FD59A                          stored 0x0F5BA0
```

Earlier notes called `0x7FD560` the target and `0x7FD562` the actual. The first
was wrong: `0x7FD560` is a bound, not a target. The setpoint is `0x7FD59A`.

### 5.3 The controller call

```
0F5B90: lhz r3, 0x7FD560     ; vMin
0F5B94: lhz r4, 0x7FD562     ; setpoint
0F5B98: lhz r5, 0x7FD55E     ; vMax
0F5B9C: bl  0x0F8318
0F5BA0: sth r3, 0x7FD5AA     ; demand out
0F5BA8: sth r30, 0x7FD596    ; filtered demand
```

### 5.4 What `0x0F8318` actually is

Not a PID. Two routines:

```
0F8318: cmpl r4, r5 ; if (in >= limit) return limit
0F8328: cmpl r4, r3 ; if (in <= min)   return in
0F8334: return r4                     ; clamp / median

0F8360: lwz   r6, 0(r3)               ; 16.16 accumulator
        srawi r11, r6, 16
        subf  r11, r11, r4
        mullw r11, r11, r5            ; gain in r5
        add   r6, r6, r11
        stw   r6, 0(r3)               ; integrating element
```

So the loop is a **clamp plus a saturating integral**, with rate shaping from
calibration rather than Kp/Ki/Kd gain maps. `0x7FD596` is the filtered demand
written back each cycle.

The integral's rate is set by the PT1 constants in §6:

- **holding SET** ramps the target up through `CrCtl_tiPT1Accel_C`
- **holding RES** ramps it down through `CrCtl_tiPT1Decel_C`

which is why the loop is an integrator rather than a proportional gain stage:
the button hold duration *is* the setpoint change, and the time constant is the
slope. A tap produces a step (`vTipStepBig/Small_C`), a hold produces a ramp.

### 5.5 Operating behaviour [SUPERSEDED - see 5.6 and 5.10]

**The "hold to ramp" model below is wrong.** There is no ramp: tip presses are
one-shot pulses from the position code `0x7F9359` (bits 0x400 / 0x20 of
`0x7FD5C4`), and `0x0F84C0` only smooths the step. Kept for traceability.



```
press SET              store current speed as target, then step  (vTipStep*_C)
hold  SET              ramp target up   at tiPT1Accel_C
press RES              recall stored target
hold  RES              ramp target down at tiPT1Decel_C
brake / clutch / ESP   shutoff, target retained for the next RES
```

The target variable `0x7FD560` is therefore written by two different paths: a
step on a button edge and a ramp while a button is held. That is why it has a
single writer with a clamp to `0xFFFF` at `0x0F4FA4` - both paths converge there.

### 5.6 What `0x7F946F` and the two cal constants really are

There is **no ramp-rate pair** in this calibration. `0x7F946F` bit 0 is a
**units selector** (metric vs imperial), and it chooses between two complete
constant sets:

```
0x7F946F bit 0 = 0  (metric)           bit 0 = 1  (imperial)
  vAlwMax  = 0x1C1468                   vAlwMax = 0x1C1466
  vAlwMin  = 0x1C146C = 1700            vAlwMin = 0x1C146A = 2114
  vAlwMin + 0x1C146E(300) = 2000        vAlwMin + 0x1C146E = 2414
                                         = 20.00 km/h           = 24.14 km/h

Units polarity is proven by the tip-step constants (see 5.10): the imperial pair
is 161 and 805, which are exactly 1 mph and 5 mph expressed in 0.01 km/h
(1.609 and 8.045). That puts bit 0 = 1 on the imperial side.
```

The A2L confirms this naming: it carries `CrCtl_vAlwMaxMPH_C` next to
`CrCtl_vAlwMax_C`, so an MPH twin for vAlwMin is exactly what the scheme needs.

`0x7F946F` itself is a derived flag written once at `0x0B5028` from three byte
conditions - it is not a stalk button and not an accel/decel direction.

### 5.7 The setpoint supervisor - `FUN_000f4f24`

This single function contains the engagement window, the setpoint selection, the
resume gating and the hold detector. Range `0x0F4F24`-`0x0F5423`.

**Engagement window** - one bit selects between two complete (vMin, vMax) pairs:

```c
if ((0x7F946F & 1) == 0) { calMin = 0x1C146C; calMax = 0x1C1468; }
else                     { calMin = 0x1C146A; calMax = 0x1C1466; }

vMin = min(calMin + cal(0x1C146E), 0xFFFF)   -> 0x7FD560   // 24.14 or 20.00 km/h
vMax = calMax                                 -> 0x7FD55E   // 255.00 km/h
```

So `0x7F946F` bit 0 is a **variant selector** (two speed windows), not an
accel/decel direction.

**PT1 filter** - `FUN_000f84c0(&0x7FD570, speedA, 0x1C1464)`:

```c
target_fx = speed << 16;
if (target_fx != state) {
    step = |target_fx - state| / tc;     // tc = cal 0x1C1464 = 10
    if (step == 0) step = 1;
    state += (state < target_fx) ? step : -step;
}
return state >> 16;
```

That is exponential approach, 1/tc of the gap per call. `0x7FD570` is the
filter state, **not** a target accumulator.

**Resume gating** - bit 3 of the mode byte `0x7FD566`:

```c
if (hold_active && ((cal(0x1C1477) >> 3) & 1)) mode |= 8;

setpoint = (mode & 8) && (rawSpeed <= (0x7FD570 >> 16))
           ? (0x7FD570 >> 16)
           : rawSpeed;                        // -> 0x7FD562
```

The stored target wins only when it is at or above current speed - you cannot
resume downward into a brake event.

**Inhibit mask** - `(flags & cal(0x1C1478)) == 0` decides `0x7FD552`, i.e. which
blocking conditions apply on this variant.

### 5.8 The hold detector - `FUN_000f4dec`

A four-state machine with two thresholds, both = **25 ticks** (`0x1C147A` and
`0x1C147B` are both 25). State `0x7FD567`, counter `0x7FD568`.

```
state 0  idle   : input==1 -> counter=0, state=1                    out 0
state 1  arming : input==1 -> counter++ (cap 255)
                   counter <  25 -> out 0
                   counter >= 25 -> state=3, out 1
                  input==0  -> state=0, out 0        <-- SHORT PRESS DISCARDED
state 3  held   : input==0 -> counter=0, state=2
                  otherwise -> out 1
state 2  decay  : input!=0 -> state=3, out 1
                  input==0 -> counter++ (cap 255)
                   counter <  25 -> out 1
                   counter >= 25 -> state=0, out 0
default         : FUN_000f4d4c(input)  - forces state 3 if input, else 0
```

Consequences:

- **Taps are rejected outright.** Releasing before 25 ticks returns to idle with
  no output and no latch. This is a hold-gesture recogniser, not a debounce.
  SET/RES taps are handled elsewhere, by the edge bits in `0x0F6CDC`.
- **The output decays for 25 ticks after release**, so the falling edge that
  `FUN_000f4f24` latches (`0x7FD569`, `0x7FD551`) occurs 25 ticks after the
  physical release.

**Scope of the state.** `0x7FD567` has 6 accesses and `0x7FD568` has 7, all
inside `0x0F4D4C`/`0x0F4DEC`. No other function in the image touches either.
The counter is private state and cannot drive the setpoint.

**Input.** `(0x7F9410 & 1) || (cal 0x1C1479 & 1)`; the override is 0 in this
file. `0x7F9410` is written at `0x0AAC44` and `0x0AAE50`, inside the decoder for
signals `0xF1`..`0x103` - a **different payload group** from the stalk contacts
`0x156`..`0x161`. Its physical identity is still open.

**No firmware latch records which button was pressed.** The latches `0x7FD550`,
`0x7FD551` are diagnostic: `0x7FD551` escapes through a KWP frame and `0x7FD550`
is mirrored to `0x7F9368`. Control decisions use the position code `0x7F9359`,
not a remembered button.

### 5.9 Calibration constants in this block

```
0x1C1464 = 10        PT1 time constant for 0x7FD570
0x1C1466 / 0x1C1468  vMax pair (1468 = 25500 = 255.00 km/h)
0x1C146A / 0x1C146C  vMin pair (2114 = 21.14, 1700 = 17.00)
0x1C146E = 300       vMin offset (+3.00 km/h)
0x1C1470 = 30000     allowed-speed array base
0x1C1472             setpoint-vs-reference tolerance
0x1C1474             window width
0x1C1476             speed-change test scaling
0x1C1477             feature bits, bit 3 = resume enable
0x1C1478             inhibit mask
0x1C1479             forced-trigger bit
0x1C147A / 0x1C147B  hold thresholds
0x1C147C             debounce time for the change flag
0x1C1918             hysteresis width around 0x7FD59A
```

### 5.10 The tip-step machine - `FUN_000f55d4` (the core state machine)

`0x0F55D4` is the centrepiece: it holds the CC state variable `0x7FD5A5` (codes
0 up to 0x21), applies the SET/RES tip steps, and consumes every cruise map.
The condition word it reads is `0x7FD5C4`.

**Tip step - this is the accelerate / decelerate logic:**

```c
uVar31 = *(uint *)(r13 + -0x2a2c);        // 0x7FD5C4

if (bVar1) {                               // set when (uVar31 & 0x400)  TIP UP
    step = cal[0x1C1918 | 0x1C1916 | 0x1C1914 | 0x1C1912];
    v = *(ushort *)(r13 + -0x2a8c) + step;         // 0x7FD564 shadow + step
    v = FUN_000f8318(vAlwMin, v, vAlwMax);         // clamp
    *(ushort *)(r13 + -0x2a56) = v;                // 0x7FD59A setpoint
    state = 5;
}
if (bVar14) {                              // set when (uVar31 & 0x20)   TIP DOWN
    v = *(ushort *)(r13 + -0x2a8c) - step;         // shadow - step
    v = FUN_000f8318(vAlwMin, v, vAlwMax);
    state = 3;
}
```

| Condition word bit | Direction | State |
|---|---|---|
| `0x400` (bit 10) | **increase / accelerate** | **5** |
| `0x20` (bit 5) | **decrease / decelerate** | **3** |

**Step sizes** (selected by `0x7FD566` bit 2 = big/small, `0x7F946F` bit 0 = units):

```
0x1C1912 =  805  =  8.05 km/h = 5 mph    imperial, big
0x1C1914 = 1000  = 10.00 km/h            metric,   big
0x1C1916 =  161  =  1.61 km/h = 1 mph    imperial, small
0x1C1918 =  150  =  1.50 km/h            metric,   small
```

**Chain, end to end:**

```
tip pressed on the stalk
  -> position code 0x7F9359 (7 = up, 4 = down)
  -> one-shot pulses in 0x7FD5C4: bit 0x400 (up) / 0x20 (down)   built in 0x0F6CDC
  -> FUN_000f55d4: shadow 0x7FD564 +/- step
  -> clamp to [vAlwMin 0x7FD560, vAlwMax 0x7FD55E]
  -> setpoint 0x7FD59A, state 0x7FD5A5 = 5 (up) or 3 (down)
```

**How a tap captures the current speed.** There is no explicit "store" event.
The shadow `0x7FD564` has exactly one writer, at `0x0F5284` inside `FUN_000f4f24`:

```c
0F526C: lhz  r9, 0x7FD59A          // current setpoint
0F5270: if (!resume_bit) r6 = speed (0x7F9700); else r6 = 0x7FD59A
0F5284: sth  r6, 0x7FD564          // shadow
```

where `resume_bit` is `(0x7FD566 >> 3) & 1`. And the tip machine then does
`shadow +/- step`. So the behaviour falls out of the ordering:

```
not resuming (cruise idle)   -> shadow := current speed each cycle
                                tap -> current speed +/- step      = "set to now"
resuming (cruise active)     -> shadow := current setpoint each cycle
                                tap -> setpoint +/- step           = "adjust"
```

That is the whole "SET stores the speed it was pressed at" mechanism: the shadow
is continuously refreshed from the live speed, so a tap simply adds its step to
whatever the car was doing at that instant. There is no separate latch to find,
and `0x7FD5A5` is written only at `0x0F6CCC` (one writer, nine readers).

**Maps consumed by state, all inside this function:**

```
0x1C16CE + 0x1C162A   normal drive        (branch bVar7)
0x1C1772              branch bVar19
0x1C1794              branch bVar11
0x1C147E              branch bVar18
0x1C1586, 0x1C14E2    slope / correction lookups
0x1C182E, 0x1C1848    additional step/limit curves
0x1C1862, 0x1C1874, 0x1C1886, 0x1C1898, 0x1C18AA, 0x1C18BC, 0x1C18DA
                      correction curves
0x1C17D0, 0x1C17EA, 0x1C180C   demand shaping
```

That resolves the map-naming question structurally: they are not one family -
each branch of the state machine calls a different map, which is why their axes
did not match a single A2L entry.

### 5.11 Rate limiters and unit conversion (`0x0F5424` family)

Five tiny accessors around two state words:

```
0x7FD5B4   acceleration request, slew-limited
0x7FD5B6   second slew-limited value (limit/display)
```

**`FUN_000f5424(up, down, target)` - asymmetric slew limiter on `0x7FD5B4`:**

```c
cur = *(short*)(0x7FD5B4);
if (target < cur) {
    cur -= (down * 2000000) / 0x34C7D;      // 0x34C7D = 216189
    if (cur <= target) cur = target;
} else {
    cur += (up * 2000000) / 0x34C7D;
    if (target <= cur) cur = target;
}
*(short*)(0x7FD5B4) = cur;
```

The scale factor `2000000 / 216189` is **9.2512 per unit of rate, per cycle**.

In `FUN_000f55d4` the two rates are computed as:

```c
up   = (cal(0x1C1925) * cal(0x1C1927) * 0x33) / 400;   // 32 * 1 * 51 / 400 = 4
down = (cal(0x1C1927) * cal(0x1C1924) * 0x33) / 400;   // 1 * 150 * 51 / 400 = 19
```

so deceleration is allowed roughly **4.75x** harder than acceleration - a
deliberate asymmetry.

**`FUN_000f549c(up, down, x)`** does the same job without rounding for
`0x7FD5B6`, clamping `x` into `[prev - down, prev + up]`.

**Simple accessors:** `0x0F548C` / `0x0F54D8` write the two words, `0x0F5494` /
`0x0F553C` read them.

**`FUN_000f5544(x)` - proves the speed unit.**

```c
v1 = x / 100;
v2 = x / 25;                       // = 4x/100
if ((v2 - 4*v1) < 2) result = v1 * 100;      // remainder < 0.50 -> round down
else                 result = v1 * 100 + 100; // >= 0.50      -> round up
```

That is "round to the nearest whole km/h, returned in the same unit". It only
makes sense if the unit is **0.01 km/h**, which independently confirms the tip
steps (150 = 1.50 km/h, 161 = 1.61 km/h = 1 mph, 805 = 8.05 km/h = 5 mph).

## 6. Calibration block - layout proven by the evaluators

The evaluator signatures give the exact table formats (`FUN_000f7ec4`,
`FUN_000f731c`, `FUN_000f72a0`, `FUN_000f7bcc`):

```
1-D curve :  u16 n,  u16 axis[n],  u16 data[n]
2-D map   :  u16 nx, u16 ny, u16 axisX[nx], u16 axisY[ny], u16 data[nx*ny]
```

Curves have **no** second dimension word - the u16 after the count is
`axis[0]`. An earlier parse in this document treated it as a zero `ny` and was
therefore off by one element; the tables below are the corrected versions.

The evaluator chain: `FUN_000f7ec4`/`0F7e7c` call `FUN_000f86b4`/`0F8764`
(axis interpolation) then `FUN_000f8848`/`0F88a4` (store). `FUN_000f731c` /
`0F72a0` interpolate both axes, then call `FUN_000f7a80` / `0F79fc` for the
2-D lookup.

### 6.0 The interpolation kernels - exact numerics

**Axis interpolation** (`FUN_000f86b4` unsigned, `FUN_000f8764` signed) returns a
**16.16 fixed-point index**:

```c
// out-of-range -> 0 (index 0, fraction 0)
binary/linear search for the segment containing x
if (axis[i] != x)
    frac = (x - axis[i]) * 0x10000 / (axis[i+1] - axis[i]);
return i * 0x10000 + frac;        // high half = index, low half = fraction
```

So the low 16 bits are the fraction across the segment, 0xFFFF = the next point.

**1-D lookup** (`FUN_000f8848` signed, `FUN_000f88a4` unsigned):

```c
p = data + (idx >> 16);
return p[0] + ((frac * (p[1] - p[0])) >> 16);
```

Plain linear interpolation in **raw table units** - no scaling is applied here,
so the caller's divisor defines the unit of each table.

**2-D lookup** (`FUN_000f7a80` signed, `FUN_000f79fc` unsigned):

```c
base = data + ((fy >> 16) + ny * (fx >> 16));
v00 = base[0]; v01 = base[1];
v0  = v00 + (frac_y * (v01 - v00) >> 16);
v10 = base[ny]; v11 = base[ny+1];
v1  = v10 + (frac_y * (v11 - v10) >> 16);
return v0 + (frac_x * (v1 - v0) >> 16);
```

**Data is stored Y-major**: `index = y_index + ny * x_index`. Y varies fastest,
X strides by `ny`.

Consequence for reading the tables: the first `ny` data values are the whole
`x = axisX[0]` column, not a row. For `0x1C14E2` that column is
`-2359, -1769, -1180, -590, 0, 590, 1415, 2359` - a straight line through zero
across the Y axis. So that map is essentially **a function of the error (Y)**,
with only mild dependence on speed (X); the correction is symmetric because the
Y axis straddles zero.

### 6.1 One-dimensional curves

```
0x1C1772  n=8  axis   0 .. 16000          data 2359 2359 2359 2359 2123 1769 1213 1127
0x1C1794  n=8  axis   0 .. 16000          data -2123 -2123 -2123 -2123 -1887 -1887 -1887 -1887
0x1C17B6  n=6  axis   2000 .. 12000       data all 0            (unused)
0x1C17D0  n=6  axis  -500 .. 0            data 10 8 6 4 2 0
0x1C182E  n=6  axis   3000 .. 12000       data 0 0 200 300 300 300
0x1C1848  n=6  axis   3000 .. 12000       data all 0            (unused)
0x1C1862  n=4  axis   0 .. 300            data -1200 constant
0x1C1874  n=4  axis   0 1638 3277 4915    data 10 constant
0x1C1886  n=4  axis   0 1638 3277 4915    data 10 constant
0x1C1898  n=4  axis   0 1638 3277 4915    data 10 constant
0x1C18AA  n=4  axis   0 1638 3277 4915    data 10 constant
0x1C18BC  n=7  axis  -2359 .. 3539        data 970 980 990 1000 1005 1020 1030
```

Reading:

- `0x1C1772` is the **acceleration authority** curve: flat 2359 up to 60 km/h
  then falling to 1127 by 160 km/h. Authority must fall as speed rises.
- `0x1C1794` is its **deceleration** twin, negative, flatter (-2123 to -1887).
- `0x1C17D0` maps a small negative error (-5.00 .. 0) to 10..0 - a linear ramp.
- `0x1C1862` constant -1200: a fixed offset.
- `0x1C1874`..`0x1C18AA` are four identical unity-gain curves (axis 0/1638/
  3277/4915 = 0, 0.25, 0.50, 0.75 of 6552; data 10 = gain 1.0). They exist so a
  calibration can be varied per condition; all are neutral in this file.
- `0x1C18BC` is a slope correction around unity (0.970 .. 1.030) versus
  acceleration (-23.59 .. +35.39).

### 6.2 Two-dimensional maps

```
0x1C147E  6x6  X  20 .. 140 km/h   Y  100 .. 700      data -1887 constant
0x1C14E2  8x8  X  20 .. 250 km/h   Y -800 .. 2000     data -2359 .. +2359 symmetric
0x1C1586  8x8  X  20 .. 200 km/h   Y -5000 .. 6000    data all 0   (unused)
0x1C162A  8x8  X  10 .. 200 km/h   Y 200 .. 10000     data 500 .. 5000
0x1C16CE  8x8  X  10 .. 200 km/h   Y 200 .. 10000     data 1000 .. 5000
```

- `0x1C147E` - constant deceleration floor across the whole grid.
- `0x1C14E2` - the only **symmetric** table: -2359..+2359 spanning a Y axis that
  crosses zero. That is the slope / correction map, positive above zero error and
  negative below.
- `0x1C162A` and `0x1C16CE` - identical axes, data saturating at 5000, differing
  only in their low-speed corner (500 vs 1000). The `aDemUnlim` pair, one per
  drive mode.
- `0x1C1586` - disabled in this calibration.

Speed axes are in 0.01 km/h (20..250 km/h for `0x1C14E2`), which matches the tip
steps and the `+200` offset in §5.7.

### 6.3 Arithmetic helpers - no hidden scaling

Four one-liners, and their simplicity is the finding: **all cruise arithmetic is
plain integer with explicit constants**. The only fixed-point anywhere is the
16.16 accumulator pair.

```
FUN_000f8acc(a,b) = a / b            , 0xFFFFFFFF if b == 0
FUN_000f8b10(a,b) = min(a / b, 0xFFFF), 0xFFFF if b == 0 or overflow
FUN_000f833c(a,b,c) = clamp(b, a, c)       (same as the first half of 0x0F8318)
FUN_000f8418(p,target,tc) = 16.16 PT1 accumulator (identical to 0x0F84C0)
```

`FUN_000f8418` and `FUN_000f84C0` are the **same routine implemented twice** -
one works on `0x7FD5AC`, the other on `0x7FD570`. Both move 1/tc of the gap per
call and return the integer part.

### 6.4 The acceleration accumulator

```c
FUN_000f8418(&0x7FD5AC, accel_value, cal(0x1C1930));   // tau = 0x0D = 13
*(short *)(0x7FD572) = *(int *)(0x7FD5AC) >> 16;
```

So:

```
0x7FD5AC   16.16 acceleration accumulator, tau = 13 cycles
0x7FD572   acceleration demand, integer part
0x7FD570   16.16 speed filter,        tau = cal 0x1C1464 = 10
```

Two independent first-order lags, both in 16.16, both rate-limited downstream by
`FUN_000f5424` (scale 9.2512 per unit per cycle, §5.11).

Unit check: the acceleration curve `0x1C1772` peaks at 2359 and reaches the
accumulator unchanged (its caller multiplies by a unity-gain curve and divides
by that curve's own scale of 10). That is consistent with **0.001 m/s2**, i.e.
2.359 m/s2 of authority falling to 1.127 m/s2 at 160 km/h - plausible for a
1.9 TDI in top gear. It is consistent, not proven: nothing in the code names the
unit.

## 7. Vmax

```
EEPROM 0x048E  = 0x7530 = 30000 = 300.00 km/h      (mirror at 0x04CE)
flash  0x1C0CF8 = 0x7530                           (EepInit default block)
code   0x0906A4 = cmpwi 0x7530 / li r9, 30000      (clamp)
code   0x0E0200 = cmpwi 0x7530                     (delta plausibility, fault 53)
```

Vmax is therefore **EEPROM-backed with a flash default**, displayed by
`EDC16Calc` as "V max 300" for this ECU. There is no `cmpwi 0x61A8` anywhere in
the image — a 250 km/h limit would be an axis endpoint (the 8x8 map at
`0x1C14E2` has a speed axis running 20..250 km/h), not a comparison.

**Where the FGR enforces it:**

```
0F500C: lhz   r12, -26864(r13)   ; 0x7F9700  speed input
0F5010: lis   r11, 0x1C
0F5014: addi  r11, r11, 0x1470   ; base of the allowed-speed array
0F5018: lhzx  r11, r11, r30      ; r11 = limit[index]
0F501C: cmp   r12, r11           ; speed vs allowed limit
```

`0x1C1470` is an **indexed array of allowed speeds**, first entry 30000
(300.00 km/h), inside the FGR calibration block - the `CrCtl_vAlwMax` family.
The EEPROM copy at `0x048E` is the persisted value the tool writes.

**[open]** Which routine reads EEPROM `0x048E` and compares it against
`CrCtl_vAlwMax_C` is not yet identified.

---

## 8. Pedal interface (context)

```
0x7F95C4   pedal position, 0..10000 = 0.00..100.00 %
           proven by cmpwi r12, 0x2710 at 0x0AF3D4
           also the y-axis of all eight Driver Wish maps
           axisY = [~100, 400, 1000, 2300, 4500, 6500, 8500, 10000]
```

Cruise does not bypass the torque path: its demand (`0x7FD5AA`) enters the same
driver-demand chain the pedal feeds, ahead of the Driver Wish maps.

---

## 9. Consequences for the multimap build

The multimap trigger previously read `0x7FF122` (byte 2 of CAN `0x7D0`), which
no code touches. The correct input is the debounced button state:

```
0x7FD53A   CAN 0x360 bit 2
0x7FD53C   CAN 0x360 bit 4
0x7FD53E   CAN 0x360 bit 3
```

Because the roles are not individually labelled, the robust trigger is a change
detector on the group rather than a bit test:

```
boot:  idle  = 0x7FD53A | 0x7FD53C | 0x7FD53E
run:   cur   = 0x7FD53A | 0x7FD53C | 0x7FD53E
       if cur != idle and not fired:  advance slot; fired = 1
       if cur == idle:                fired = 0
```

This advances once per press regardless of which button was used, and is
independent of frame layout and polarity.

### 9.1 Better sources, found later

Two firmware-maintained bytes are more direct than the mirrors above.

**`0x7F9413` - the switch contact byte**, assembled by the decoder
`FUN_000a984c` from signals `0x156..0x161` and stored at `0x0AA434`:

```
bit 0  0x01 <- sig 0x160        bit 4  0x10 <- sig 0x15A
bit 1  0x02 <- sig 0x158        bit 5  0x20 <- sig 0x15D
bit 2  0x04 <- sig 0x161        bit 6  0x40 <- sig 0x15E
bit 3  0x08                     bit 7  0x80 <- sig 0x15C
```

Each bit is set and cleared every cycle, so the byte is live state.

**`0x7F9412` - aggregate "any switch active"**, computed at `0x0AB1C8` from
`0x7F9413`, `0x7F9414` and `(0x7F942D & 0x3D)`. The consumer at `0x0AB1A8`
tests the whole byte against zero - the firmware never distinguishes which
contact closed, only whether one did.

Recommended trigger:

```
cur = *(u8*)0x7F9412          ; 1 = any stalk contact closed
if (cur && !prev) advance_slot
prev = cur
```

or, restricted to the two tip contacts only:

```
cur = *(u8*)0x7F9413 & 0xC0   ; bit 7 (0x15C) | bit 6 (0x15E)
```

The first catches every stalk action including the rocker; the second catches
only the tip. Both are single-byte reads with no encoding assumptions.

### 9.1.1 What v2.1.0 actually ships

The release does not hardcode either option. Because the tip polarity cannot be
proven from this binary (section 2.3.2 - all eight contacts collapse into one
flag), the masks are calibration:

```
0x1EA7C8   MAPS_MASK_NEXT   default 0x80    bit of 0x7F9413 that means next
0x1EA7C9   MAPS_MASK_PREV   default 0x40    bit that means previous
0x1EA7CA   MAPS_CFG         default 0x01    bit0 = only while cruise is off
                                            bit1 = disable stalk switching
0x1EA7CB   MAPS_SRC          default 0x00    0 = 0x7F9413, 1 = 0x7F9990 high
                                            byte (rocker bits 8/9/14 as
                                            0x01/0x02/0x40), 2 = 0x7F935D
```

Behaviour in the thunk at `0x1FC000`:

```
if (MAPS_CFG & 0x02)                      -> do nothing
if (MAPS_CFG & 0x01) && (0x7F953A != 0)   -> do nothing   (cruise not OFF)
next = (0x7F9413 & MAPS_MASK_NEXT)        rising edge -> slot = (slot+1) % 3
prev = (0x7F9413 & MAPS_MASK_PREV)        rising edge -> slot = (slot+2) % 3
```

Separate latches at `0x7F9212` (next) and `0x7F9213` (prev) mean holding a
contact produces exactly one step. Diagnostics for the in-car polarity test:

```
0x7F9218  last byte read from the SELECTED source (0x7F9413 by default)
          <- if this never changes, the chosen source/mask is wrong
0x7F9219  last raw 0x7F953A (written only when the gate actually runs)
0x7F921A  trigger counter
0x7F921B  1 = the off-gate ran and passed; 0 = gate disabled or blocked
```

**Never give both masks the same bit.** If `MAPS_MASK_NEXT == MAPS_MASK_PREV`,
both rising edges fire in the same call: the slot advances +1 and then +2, which
is +3 mod 3 - no net change. Harmless, but it looks like a dead trigger while
testing.

Swapping the two mask bytes inverts the polarity with no rebuild. If neither
bit works, any other bit of `0x7F9413` can be supplied instead.

**Offline validation: 71/71 active, 65/65 inert. Not verified on hardware.**
All three `MAPS_SRC` paths are covered: the validator pokes distinct values into
`0x7F9413` / `0x7F9990` / `0x7F935D` and checks the diagnostic mirror `0x7F9218`
equals the configured source's value (0xA1 / 0xB2 / 0xC3). Build variants with
`--src 0|1|2`.

---

## 9.2 Measuring blocks - moved

The measuring-block investigation outgrew this document and has its own file:

- **`MEASURING_BLOCKS_RE.md`** - the mechanism, the tables, their addresses in
  this calibration, what is unresolved, and the four wrong answers this work went
  through on the way.
- **`MEASURING_BLOCKS.c`** - annotated C reconstruction of the service `0x21`
  path with confidence markers.
- **`MEASURING_BLOCKS.csv`** - all 255 groups decoded to signal numbers.

Summary of where it stands: `UACC_RSigBlkGrp_MAP` is located at `0x1E9A8A`
(Cal2) / `0x190CC2` (Cal1), 4 x 255, Y-major, reached only through pointer
structs at `0x04CE9C` / `0x180680` / `0x180CA4` / `0x1812C8`. The four companion
tables are located too. What is missing is the signal-number-to-name mapping,
which lives in an A2L for a different software number and therefore does not
transfer.

The earlier conclusion in this section - that measuring blocks were not
table-driven and could not be repointed by calibration - was **wrong** and is
retracted. See section 4 of the new document for how that happened.

## 10. Open items

1. **Stalk encoding** — five functions (ON, CANCEL, OFF, SET/−, RES/+) reach the
   ECU as four signals (`0xC2`-`0xC5`), so the rocker position is encoded across
   bits rather than one-bit-per-button. The per-position bit pattern needs one
   observation of `0x7F93FD` per stalk position, or a decode of the J527 encoder.
2. **State encoding** — meaning of `0x7FD5A5` values 0, 1, 9.
3. **Inhibit bit meanings** — which physical condition maps to codes 2..12.
4. **Vmax read path** — which routine reads EEPROM `0x048E`.
5. **Target-speed update** — which button edge writes `0x7FD560`, and through
   which cal (`vTipStep*`, `dvInitRamp*`).

---

## 11. Method and tooling

- Signal table recovered by decoding the accessor's `r14 - 0x62D8 + id*6`
  indexing, then reading each 6-byte entry and mapping `entry[2]` through the
  `0x41408` descriptor table.
- Button bits confirmed by disassembling the debounce sites and resolving the
  cal constants (`0x1C18F9`) from the `lis 0x1C` / `addi` pairs.
- Speed variables identified by writer/reader histograms over `r13`-relative
  accesses, then confirmed by the `lhz r3/r4/r5 + bl` call pattern.
- Controller characterised by disassembling `0x0F8318` (clamp + fixed-point
  integrator).
- Vmax located in EEPROM by matching the `EDC16Calc` display against a 16-bit
  scan, then verified against the flash clamp at `0x0906A4`.

Ghidra scripts used (in `edc16-multimap/ghidra/`):
`CanBufAnalysis.py`, `CanCopyTargets.py`, `TraceCanRx2.py`, `DumpFgrCluster.py`,
`FindFgrSpeedConsts.py`, `FgrFinal.py`, `FullScan.py`.

---

## 12. Corrections applied to earlier notes

Added after the final decompile pass:

- `0x7FD560` is **vAlwMin** (a bound), not the target. `0x7FD55E` is vAlwMax.
  `0x7FD562` is the computed actual, and the setpoint is `0x7FD59A`.
- `0x1C146A` = 2114 and `0x1C146C` = 1700 are **vAlwMin in metric and imperial**,
  not ramp rates. `0x7F946F` bit 0 selects units, not accel vs decel.
- There is **no ramp function and no hold-to-accelerate ramp**. Tip steps are
  one-shot pulses (bits 0x400 / 0x20 of `0x7FD5C4`) from the position code
  `0x7F9359`; `0x0F84C0` only smooths the resulting jumps (PT1, tau = 10).
- The hold detector's counter `0x7FD568` is **private** to `0x0F4DEC`; it cannot
  be the setpoint latch.
- `0x7FD570` is a **PT1 filter state**, not a target accumulator.
- The signal table at `0x40A3C` is an **alias layer**: many IDs resolve to the
  same frame bit, so "14 consumers of 200 signals" is far fewer real inputs.
- `0x7F9410` (the hold detector input) is signal `0xFF` = frame `0x360` bit 3,
  the **same contact as `0xC3`** (bit 2 of `0x7F93FD`, flag `0x7FD53E`).
- `0x7F946F` bit 0 = 1 means **imperial**, not metric. Proven by the tip-step
  constants 161 (1 mph) and 805 (5 mph).
- The accelerate / decelerate logic is **`FUN_000f55d4 @ 0x0F55D4`**, driven by
  condition-word bits `0x400` (up, state 5) and `0x20` (down, state 3).
- `0x7FD5A5` carries state codes 0..0x21, not just 0/1/9.
- The cruise maps are consumed **by state branch** inside `0x0F55D4`, not as one
  family with a common axis.



- Cruise is on **CAN `0x360`**, not `0x38A`. `0x38A` exists in the RX table at
  buffer `0x7FF114` but no FGR code reads it.
- `0x7FF122` is byte 2 of frame `0x7D0` and is unused by stock code.
- `0x7F951A` is a single enable bit, not the target speed.
- There is no `cmpwi 0x61A8`; the 250 km/h figure is a map axis endpoint.
- The FGR loop is a **clamp + integrating element**, not a Kp/Ki/Kd PID.
- `0x7FD560` / `0x7FD55E` are **vMin / vMax bounds**, not target and limit.
  The setpoint is `0x7FD562`.
- `0x7FD570` is a **PT1 filter state** (`FUN_000f84c0`, tc `0x1C1464` = 10),
  not a target accumulator.
- `0x7F946F` bit 0 selects a **(vMin, vMax) variant pair**, not accel vs decel.
- There is **no continuous ramp function** in this ECU. "Hold to accelerate" is
  realised by the hold detector `FUN_000f4dec` counting cycles in `0x7FD568`;
  any consumer of that counter steps the target once per cycle.

- The stalk decoder is **`FUN_000a984c @ 0x0A984C`**, not `0x0F4210`. The latter
  debounces and runs the state machine but does not read the CAN signals itself.
- The three debounced flags `0x7FD53A/3C/3E` are **diagnostic mirrors** - written
  twice each, read nowhere. The logic path is the condition word in `r31`
  (bits 11 / 12 / 13).
- `0x1C146A` = 2114 and `0x1C146C` = 1700 are **vAlwMin metric / imperial**, not
  ramp rates, and `0x7F946F` bit 0 is a units selector. An intermediate note in
  this document called them motion rates - that was an over-read and is
  superseded by 5.6.

## 13. Pitfalls when reading this subsystem

Each of these cost real time, so they are listed with the evidence that settles
them. If a future pass contradicts this list, the evidence below is what to
re-check.

### 13.1 `0x7F946F` bit 0 is a units selector, not a direction flag

It looked like "two motion states" because it picks between two complete
`(vMin, vMax)` constant pairs. The proof is in the tip steps: `0x1C1916` = 161
and `0x1C1912` = 805 are exactly 1 mph and 5 mph expressed in 0.01 km/h. The
metric pair is 150 and 1000. See 5.6 and 5.10.

### 13.2 The setpoint shadow is refreshed continuously - there is no latch event

`0x7FD564` has one writer (`0x0F5284`) which copies either the current setpoint
or the current speed, every cycle. A "SET tap stores the current speed" falls
out of that refresh; there is no store-on-edge to find. See 5.10.

### 13.3 `0x7FD568` is private state

Seven accesses, all inside `0x0F4DEC` and its reset helper `0x0F4D4C`. It cannot
drive the setpoint, so "the hold counter ramps the target" is wrong. The hold
detector's *return value* is what escapes. See 5.8.

### 13.4 The debounced flags are mirrors, not logic

`0x7FD53A / 0x7FD53C / 0x7FD53E` are each written twice and read nowhere. The
live path is the condition word bits 11/12/13. Reading the mirrors from a hook
still works (they are refreshed every cycle) but they are copies. See 2.4.

### 13.5 The condition mask excludes exactly one condition

`cal(0x1C18F0)` = `0xFFFFFFDF`, so only bit 5 - the `0x1C18F6`-gated one - can
never block engagement. Everything else is live. See 3.3.

### 13.6 Bits 25..27 and 29 of the condition word are never driven

Verified by reading the whole of `0x0F4210`; they are always clear, so any
inhibit code of 25/26/27/29 would be a symptom of a corrupt word.

### 13.7 The inhibit code is a bit index, not an enumeration

`0x7FD537` is the index of the lowest set bit in the masked word, `0xFF` for
none. Codes 11/12/13 are therefore "a stalk contact is held", which is why the
byte looked like a button enumeration in early notes. See 3.2.

### 13.8 A hold gesture discards taps

`0x0F4DEC` state 1 returns 0 and resets to idle if the input drops before 25
ticks. It is a gesture recogniser, not a debounce: SET/RES *taps* are handled
elsewhere, by the position-code pulses. See 5.8.

### 13.9 Table data is Y-major and out-of-range samples the first point

`index = y_index + ny * x_index`. And `cc_axis_index` returns 0 - index 0,
fraction 0 - for any x outside the axis, so an out-of-range input silently
reads `data[0]` rather than clamping to the nearest end. See 6.0.

### 13.10 The cubic trap: `r13` displacements are signed

`-24248` is `0xA148`, but the address is `0x7FFFF0 - 0x5EB8 = 0x7FA138`, not
`0x7F5EA8`. Subtracting the unsigned hex value gives a plausible-looking wrong
address. Do the arithmetic in a script - this document's addresses came from
scripted scans that sign-extend correctly, and hand-computed ones have been
wrong more than once.

### 13.11 Boot differs between our baseline and public dumps

The `EDC16U34 Map packs` collection ships calibration-only images with the boot
block erased, so nothing matches byte-for-byte. Comparing region by region
shows OS, Cal1 and Cal2 are identical to the `382083 / 7EA1` dump. Do not flash
a map pack.

## 14. Companion C file

`CRUISE_CONTROL.c` in the same folder is an annotated reconstruction of this
subsystem - named functions, real addresses in comments, the RAM map and the
calibration constants as defines, and the open items stated in the header.
It complements this document: the document carries the evidence trails, the C
file carries the shape.
