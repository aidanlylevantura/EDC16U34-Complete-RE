/* ============================================================================
 *  MEASURING_BLOCKS.c  -  Bosch EDC16U34 KWP2000 measuring blocks (service 0x21)
 *
 *  Target : VAG 03G 906 021 KH  /  HW 03G 906 021 AN  /  SW 1037382083
 *           R4 1,9L EDC G000AG  9245   (Golf Mk5 1.9 TDI BXE)
 *
 *  A measuring block is a TABLE LOOKUP, not computed logic.  Group + block
 *  selects a signal number; the signal number selects a formula, a
 *  normalisation constant and a name; the name's category supplies scale and
 *  offset.  Everything except the name table lives in calibration.
 *
 *  Companion document: MEASURING_BLOCKS_RE.md
 *
 *  Confidence markers are the same as the cruise reconstruction:
 *    PROVEN   read out of the image, or the layout is arithmetic-verified
 *    INFERRED recovered by content shape, not by following the code
 *    UNKNOWN  not established in this build
 * ==========================================================================*/

#include <stdint.h>

typedef uint8_t  u8;
typedef uint16_t u16;
typedef int16_t  s16;
typedef uint32_t u32;

/* ---------------------------------------------------------------- tables -- */

/* PROVEN. UACC_RSigBlkGrp_MAP, two byte-identical copies.
 *
 *   header  u16 nx = 4, u16 ny = 255
 *   X axis  1,2,3,4          (block 1..4)
 *   Y axis  1,2,...255       (group number)
 *   data    1020 u16
 *
 * Blob length 0xA02 = 4 + 8 + 510 + 2040, which verifies the layout.
 * Storage is Y-major, like every other map in this firmware.              */
#define MB_MAP_CAL2        0x1E9A8A
#define MB_MAP_CAL1        0x190CC2
#define MB_DATA_CAL2       0x1E9C94
#define MB_DATA_CAL1       0x190ECC
#define MB_NX              4
#define MB_NY              255
#define MB_MARK_EMPTY      255      /* slot carries nothing */
#define MB_MARK_UNUSED     0        /* signal 0 is "Sig_unused" as well */

/* PROVEN. Pointer structs that are the only route to the tables. No
 * instruction forms these addresses directly.                              */
#define MB_PTR_STRUCT_OS   0x04CE9C
#define MB_PTR_STRUCT_C1A  0x180680
#define MB_PTR_STRUCT_C1B  0x180CA4
#define MB_PTR_STRUCT_C1C  0x1812C8
/*   +0x00  0x1E90DC   +0x04  0x1E9A80
 *   +0x08  block map (variant)   +0x0C  0x1EA48C   +0x10  0x1EA4B4        */
#define MB_SIDE_A          0x1E90DC
#define MB_SIDE_B          0x1E9A80
#define MB_SIDE_C          0x1EA48C
#define MB_SIDE_D          0x1EA4B4

/* INFERRED by content shape:
 *   MB_SIDE_A  u8 array, max 115, 39 distinct  -> UACC_ESBFormular_C
 *   MB_SIDE_B  u8 array, max 255               -> UACC_ESBNormVal_C
 *   MB_SIDE_C  mixed u8/u16 with 0xFFF0        -> format table
 *   MB_SIDE_D  u16 0A10 0001 0203 0405 ...     -> small conversion table  */

/* UNKNOWN. UACC_ESBSigNr_C is NOT present in this calibration: neither a
 * 561- nor a 582-entry array of any shape tested exists in Cal1/Cal2, and the
 * signal numbers are not r13 displacements.                                */

/* ------------------------------------------------------------ response ---- */

/* PROVEN. The service 0x21 branch of the dispatcher FUN_000971DC.
 *   reached from the dispatch table at 0x972BC, entry 0x21 -> 0x97340
 *   writes response length 13 at 0x9869C  (li r11,13)
 *
 * 13 = 0x61 + group_hi + group_lo + 4 * {value_hi, value_lo, formula_id}  */
#define MB_RESP_SERVICE    0x61
#define MB_RESP_LEN        13
#define MB_FIELDS          4

struct mb_field {
    u8 hi;          /* value, scaled to 8 bits */
    u8 lo;          /* value, scaled to 8 bits */
    u8 formula;     /* formula ID - tells the tester how to parse hi/lo */
};

struct mb_response {
    u8 service;     /* 0x61 */
    u8 group_hi;
    u8 group_lo;
    struct mb_field f[MB_FIELDS];
};

/* ------------------------------------------------------------- lookup ----- */

/* PROVEN ordering. Returns the signal number for (group, block), or one of the
 * two markers. Both 0 and 255 mean "nothing to display". */
u16 mb_signal_number(u16 data_base, u8 group, u8 block)
{
    u32 index;
    if (group == 0 || group > MB_NY)   return MB_MARK_EMPTY;
    if (block == 0 || block  > MB_NX)  return MB_MARK_EMPTY;
    index = (u32)(group - 1) + (u32)MB_NY * (u32)(block - 1);
    return *(volatile u16 *)(data_base + 2u * index);
}

/* INFERRED. Formula ID and normalisation constant for a signal number. Both
 * companion tables are addressed by the signal number directly; the array
 * lengths are unconfirmed, so bounds are the caller's problem. */
u8  mb_formula_id(u16 side_a_base, u16 signal)
{
    return *(volatile u8 *)(side_a_base + signal);
}

u8  mb_norm_constant(u16 side_b_base, u16 signal)
{
    return *(volatile u8 *)(side_b_base + signal);
}

/* UNKNOWN. Signal number -> name. The name table is NOT in the ECU: it is a
 * COMPU_VTAB called SigName in the A2L (582 entries in the neighbouring build
 * 03G997022F). The firmware never needs names, so there is nothing to read
 * here. Filled in below only for documentation. */
const char *mb_signal_name(u16 signal);

/* --------------------------------------------------------- scaling -------- */

/* PROVEN from the reference Damos, INFERRED for this build.
 *
 * A displayed value is (hi*256 + lo) pushed through the formula selected by
 * formula_id, with the normalisation constant as the "A" term, then scaled by
 * the category implied by the signal's name suffix. Two examples from the
 * reference A2L, both confirmed present there:
 *
 *   signal 222  InjCtl_qCurr__q_DLen1   formula 39, A = 70,  scale q
 *               display = (B/255)*A          -> 0..70 mg/stroke
 *   signal 304  BPSCD_pFltVal__p_DLen1  formula 18, A = 255, scale p
 *               display = 0.04*A*B           -> 0..2601 mbar
 *
 * The 8-bit split is the reason a display limit is set by A and the category
 * scale rather than by anything in RAM: only 0..255 can be sent per field.  */
u16 mb_display_value(const struct mb_field *f, u8 norm_A)
{
    u16 raw = ((u16)f->hi << 8) | f->lo;

    switch (f->formula) {
    case 18:  return (u16)((raw * norm_A) / 25u);        /* 0.04 * A * B   */
    case 39:  return (u16)(((raw & 0xFF) * norm_A) / 255u); /* (B/255)*A   */
    default:  return raw;   /* formula table incomplete for this build */
    }
}

/* ------------------------------------------------------------ builder ----- */

/* PROVEN shape, INFERRED internals. Assembles one group response.
 *
 * Note what this does NOT do: it never converts a RAM value. It fetches the
 * signal number for each of the four slots, looks up that signal's formula and
 * normalisation, and the *tester* applies the arithmetic. The ECU only ships
 * two bytes plus a format byte per field. */
void mb_build_group(u8 group, struct mb_response *out)
{
    u8 block;

    out->service  = MB_RESP_SERVICE;
    out->group_hi = 0;
    out->group_lo = group;

    for (block = 1; block <= MB_FIELDS; block++) {
        u16 sig = mb_signal_number(MB_DATA_CAL2, group, block);
        if (sig == MB_MARK_EMPTY || sig == MB_MARK_UNUSED) {
            out->f[block - 1].hi = 0;
            out->f[block - 1].lo = 0;
            out->f[block - 1].formula = 0;      /* 0 = nothing to show */
            continue;
        }
        out->f[block - 1].formula = mb_formula_id(MB_SIDE_A, sig);
        /* value bytes come from the signal's own RAM location, which is the
         * piece this build does not let us resolve - see below */
        out->f[block - 1].hi = 0;
        out->f[block - 1].lo = 0;
    }
}

/* ============================================================================
 *  How to repoint a block (no code change, calibration only)
 *
 *    1. choose a group; 152 of 255 are entirely 0xFF and free
 *    2. write four signal numbers at
 *          0x1E9C94 + 2 * ((group-1) + 255*(block-1))
 *       and the same into the Cal1 copy at 0x190ECC
 *    3. ensure the formula (0x1E90DC) and normalisation (0x1E9A80) entries for
 *       those signals match the units, or VCDS prints confident nonsense
 *    4. recompute the Cal2 additive sum at 0x1FDFFC
 *
 *  0x1E9A8A sits below FREE_LO = 0x1EA7C8, so the multimap build never disturbs
 *  these tables.
 *
 *  The blocker is step 2: in this build the mapping from signal number to
 *  variable is unlabelled, because the name table belongs to the A2L of a
 *  different software number. The practical route is empirical - change one
 *  index in a group whose VCDS reading you know and see what moves.
 * ==========================================================================*/
