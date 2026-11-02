import os

BASE = r"C:\Users\user\Documents\Complete ECU Disassembly"
REL = os.path.join(BASE, "Release_Package")
README = os.path.join(REL, "README.md")
BIN = os.path.join(REL, "Golf_KH_Flash_Patched.bin")
LICENSE = os.path.join(REL, "LICENSE")
GITIGNORE = os.path.join(REL, ".gitignore")

print("=== Finalizing release package ===")

# 1. Verify patched binary
d = open(BIN, "rb").read()
patch = d[0x486C:0x4874].hex().upper()
print("[+] binary size:", len(d))
print("[+] bytes at 0x486C:", patch)
if patch != "386000014E800020":
    print("[-] RSA PATCH MISSING. Stop. Re-run Patch_RSA.py and re-export.")
    raise SystemExit(1)
print("[+] RSA patch verified")

# 2. Fix README function count
if os.path.exists(README):
    txt = open(README, "r", encoding="utf-8").read()
    txt2 = txt.replace("2,366", "2,382")
    if txt2 != txt:
        open(README, "w", encoding="utf-8").write(txt2)
        print("[+] README updated: 2,366 -> 2,382 functions")
    else:
        print("[+] README already has correct count or no 2,366 found")

# 3. Write LICENSE
license_text = """MIT License

Copyright (c) 2026 Aidan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
open(LICENSE, "w", encoding="utf-8", newline="\n").write(license_text)
print("[+] wrote LICENSE")

# 4. Write .gitignore
gitignore_text = """# Commercial/copyrighted Damos files - do not upload
*.csv
*.ols

# Original personal EEPROM - do not upload
Eeprom.bin
*Original_Eeprom*

# Windows junk
Thumbs.db
desktop.ini
"""
open(GITIGNORE, "w", encoding="utf-8", newline="\n").write(gitignore_text)
print("[+] wrote .gitignore")

print("\n=== Release package contents ===")
for f in sorted(os.listdir(REL)):
    p = os.path.join(REL, f)
    if os.path.isfile(p):
        print("  %10d  %s" % (os.path.getsize(p), f))
