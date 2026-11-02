import time

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

N = int.from_bytes(d[0x3FBBC:0x3FBBC+128], "big")
e = 3

print(f"N = 0x{N:0256X}")
print("Scanning 0x0-0x40000 for RSA private exponent d...")

start = time.time()
found = False
for off in range(0, 0x40000 - 128, 4):
    cand = int.from_bytes(d[off:off+128], "big")
    if cand == 0 or cand >= N:
        continue
    if pow(pow(2, e, N), cand, N) == 2:
        print(f"[+] Candidate d at 0x{off:06X}: 0x{cand:0256X}")
        found = True
        break

if not found:
    print("[-] No d candidate found in bootloader region.")
print(f"Elapsed: {time.time()-start:.1f}s")