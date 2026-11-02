import os, csv, json, re
from datetime import datetime
from collections import Counter

BASE = r"C:\Users\user\Documents\Complete ECU Disassembly"

def path(name):
    return os.path.join(BASE, name)

def read(name, default=""):
    p = path(name)
    if not os.path.exists(p):
        return default
    try:
        return open(p, "r", encoding="utf-8", errors="replace").read()
    except Exception as e:
        print("[!] %s: %s" % (name, e))
        return default

def read_csv(name):
    p = path(name)
    if not os.path.exists(p):
        return []
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            first = fh.readline()
            fh.seek(0)
            delim = ';' if ';' in first else ','
            return list(csv.reader(fh, delimiter=delim))
    except Exception as e:
        print("[!] %s: %s" % (name, e))
        return []

def norm_addr(v):
    if v is None: return ""
    s = str(v).strip().strip('"').strip("'").replace("_", "")
    if s.lower().startswith("0x"): s = s[2:]
    try:
        return "0x%08X" % int(s, 16)
    except:
        return str(v)

# ---- Load inputs ----
polys            = read("_POLYS.txt")
fadecafe         = read("_FADECAFE_BRANCHES.txt")
maps_csv         = read_csv("WinOLS (VW (Original) - 380437).csv")
dtc_table        = read("DTC_Table.txt")
c_file_path      = path("Golf_KH_MASTER.c")

# ---- Parse maps (WinOLS Semicolon Format) ----
maps = []
if maps_csv and len(maps_csv) > 1:
    for row in maps_csv:
        if len(row) < 2: continue
        name = row[1].strip()
        if not name: continue
        # Find the $XXXXXX address anywhere in the row
        m = re.search(r'\$([0-9A-Fa-f]{4,8})', ",".join(row))
        if not m: continue
        addr = m.group(1)
        dims = "Unknown"
        for c in row:
            if "x" in c.lower() and len(c) < 10:
                dims = c
                break
        maps.append({
            "addr": norm_addr(addr),
            "name": name,
            "dims": dims,
        })
print("[+] maps: %d" % len(maps))

# ---- Parse function names ----
funcs = []
if os.path.exists(c_file_path):
    FUNC_RE = re.compile(
        r'^(?:void|int|uint|undefined\d*|char|byte|short|ushort|bool|long|ulong|float|double|code)\s+'
        r'(\w+)\s*\(([^)]*)\)',
        re.MULTILINE,
    )
    text = open(c_file_path, "r", encoding="utf-8", errors="replace").read()
    for m in FUNC_RE.finditer(text):
        funcs.append({"name": m.group(1), "args": m.group(2).strip()[:80]})
print("[+] functions: %d" % len(funcs))

# ---- Parse LFSR poly table ----
poly_list = []
for line in polys.split("\n"):
    m = re.search(r'\[\s*(\d+)\]\s*0x([0-9a-fA-F]{8})', line)
    if m:
        poly_list.append({"index": int(m.group(1)), "poly": "0x" + m.group(2).upper()})
print("[+] polys: %d" % len(poly_list))

# ---- Parse FADECAFE branches ----
COND_OPS = {"beq","bne","bge","bgt","ble","blt","bso","bns","bdnz","bdz","bdnzt","bdnzf","bc","bclr"}
CALL_OPS = {"bl","bcl"}
UNCOND_OPS = {"b","ba"}
fade_branches = []
for line in fadecafe.split("\n"):
    m = re.search(r'\[\s*(\d+)\]\s*0x([0-9a-fA-F]+)\s+(\w+)\s+0x([0-9a-fA-F]+)', line)
    if m:
        op = m.group(3).lower()
        kind = ("conditional" if op in COND_OPS
                else "call" if op in CALL_OPS
                else "unconditional" if op in UNCOND_OPS
                else "other")
        fade_branches.append({
            "n": int(m.group(1)),
            "addr": norm_addr(m.group(2)),
            "op": op,
            "target": norm_addr(m.group(4)),
            "kind": kind,
        })
kind_counts = Counter(b["kind"] for b in fade_branches)
print("[+] FADECAFE branches: %d" % len(fade_branches))

# ---- File manifest ----
manifest = []
self_names = {"EDC16U34_Reference.md", "EDC16U34_Reference.json", "build_master.py", "build_master_v2.py"}
for f in sorted(os.listdir(BASE)):
    p = os.path.join(BASE, f)
    if not os.path.isfile(p): continue
    if f in self_names: continue
    sz = os.path.getsize(p)
    mt = int(os.path.getmtime(p))
    if sz > 100 or f.endswith((".py", ".md", ".csv", ".txt", ".bin", ".c")):
        manifest.append({"name": f, "size": sz, "mtime": mt})

# ============================================================
# BUILD MARKDOWN
# ============================================================
md = []
def L(s=""): md.append(str(s))

L("# VW Golf 5 EDC16U34 KH Master Reference")
L()
L("**VW Golf 5 1.9 TDI PD 105 hp — EDC16U34 — 03G906021KH / 0281013226 / 380437**")
L()
L("Generated: %s" % datetime.now().strftime("%Y-%m-%d %H:%M"))
L()
L("---")
L()

L("## Platform")
L()
L("| Field | Value |")
L("|---|---|")
L("| ECU | Bosch EDC16U34 |")
L("| Vehicle | VW Golf 5 1.9 TDI PD 105 hp (2006) |")
L("| VAG part no | 03G906021KH |")
L("| Bosch part no | 0281013226 |")
L("| Software version | 380437 |")
L("| CPU | PowerPC MPC563 |")
L("| Flash dump size | 2 MB (0x000000–0x1FFFFF) |")
L("| IMMR base | 0x006FC000 |")
L()

L("## Resolved RE Facts")
L()
L("| Fact | Address / Value |")
L("|---|---|")
L("| Seed LFSR polynomial table | `0x2240` (64 × 32-bit) |")
L("| Seed handler (UDS 0x27) | `DSM_FUN_000017a4 @ 0x17A4` |")
L("| FADECAFE self-check region | `0x4D284–0x52804` |")
L("| Boot verify signature walker | `DSM_auto_00486c @ 0x486C` |")
L("| Warm-start SPRG1 magic | `0x1A` |")
L("| Cruise stalk decoder | `CrCtl_FUN_000db0a0 @ 0xDB0A0` |")
L("| **VIN** | **WVWZZZ1KZ6W165917** (EEPROM @ 0x0145, 0x0165) |")
L("| **IMMO/FIN** | **VWZBZ0F0361686** (EEPROM @ 0x00EC, 0x010C, 0x012C) |")
L("| **Login / PIN** | **4441 (0x1159)** (EEPROM @ 0x00E8) |")
L()

L("## Function Inventory")
L()
named = [f for f in funcs if not f["name"].startswith(("FUN_", "func_"))]
unnamed = [f for f in funcs if f["name"].startswith(("FUN_", "func_"))]
L("- Total functions: **%d**" % len(funcs))
L("- Named (meaningful): **%d**" % len(named))
L("- Unnamed (FUN_/func_): **%d**" % len(unnamed))
L()

L("## Calibration Maps")
L()
L("**%d maps total.**" % len(maps))
L()
L("| Address | Name | Dimensions |")
L("|---|---|---|")
for m in maps[:500]:
    L("| `%s` | `%s` | %s |" % (m["addr"], m["name"], m["dims"]))
L()

L("## Crypto: LFSR Poly Table")
L()
L("**%d 32-bit polynomials** at flash address **`0x2240`**." % len(poly_list))
L()
L("| Index | Poly |")
L("|---:|---|")
for p in poly_list:
    L("| %d | `%s` |" % (p["index"], p["poly"]))
L()

L("## Crypto: FADECAFE Branches")
L()
L("**%d branch sites** in `FUN_0004d714`." % len(fade_branches))
L()
L("| # | Address | Op | Kind | Target |")
L("|---:|---|---|---|---|")
for b in fade_branches:
    L("| %d | `%s` | `%s` | %s | `%s` |" % (b["n"], b["addr"], b["op"], b["kind"], b["target"]))
L()

md_out = "\n".join(md)

# ============================================================
# WRITE
# ============================================================
out_md   = path("EDC16U34_Reference.md")
out_json = path("EDC16U34_Reference.json")

with open(out_md, "w", encoding="utf-8") as fh:
    fh.write(md_out)

print("[+] wrote %s" % out_md)