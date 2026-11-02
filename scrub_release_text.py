import os

REL = r"C:\Users\user\Documents\Complete ECU Disassembly\Release_Package"

REPLACEMENTS = [
    ("WVWZZZ1KZ6W165917", "00000000000000000"),
    ("VWZBZ0F0361686", "00000000000000"),
    ("4441 (0x1159)", "0000 (0x0000)"),
    ('"4441"', '"0000"'),
    ("Login PIN 4441", "Login PIN 0000"),
    ("PIN (`4441`)", "PIN (`0000`)"),
    ("PIN 4441", "PIN 0000"),
]

TARGETS = [
    "README.md",
    "EDC16U34_Reference.md",
    "EDC16U34_Reference.json",
]

for name in TARGETS:
    p = os.path.join(REL, name)
    if not os.path.exists(p):
        print("[-] missing:", name)
        continue
    txt = open(p, "r", encoding="utf-8").read()
    orig = txt
    for a, b in REPLACEMENTS:
        txt = txt.replace(a, b)
    if txt != orig:
        open(p, "w", encoding="utf-8", newline="\n").write(txt)
        print("[+] scrubbed:", name)
    else:
        print("[=] no change:", name)