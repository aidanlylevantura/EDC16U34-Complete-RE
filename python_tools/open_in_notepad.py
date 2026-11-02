# open_in_notepad.py
# Usage:
#   python open_in_notepad.py
#   python open_in_notepad.py _INFRA_REPORT.txt
#   python open_in_notepad.py _FINISH_JOB.txt _INFRA_REPORT.txt

import os, sys, subprocess

OUT_DIR = r"C:\Users\user\Documents\Complete ECU Disassembly"

if len(sys.argv) > 1:
    files = sys.argv[1:]
else:
    files = ["_FINISH_JOB.txt"]

opened = 0
for filename in files:
    path = os.path.join(OUT_DIR, filename)
    if not os.path.exists(path):
        print(f"[!] Not found: {path}")
        continue
    size = os.path.getsize(path)
    print(f"[+] {path}  ({size} bytes)")
    subprocess.Popen(["notepad.exe", path])
    opened += 1

if opened == 0:
    print(f"[!] No reports found in {OUT_DIR}")
    print("    Files present:")
    if os.path.isdir(OUT_DIR):
        for f in sorted(os.listdir(OUT_DIR)):
            if f.endswith((".txt", ".json")):
                print(f"      {f}")