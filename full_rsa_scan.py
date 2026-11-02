import time
import math
import random

path = r"C:\Users\user\Documents\Complete ECU Disassembly\Seat Leon 1.9 TDI 105 hp 2006 EDC16U34 03G906021LK 0281013279 1037382081 bdm.bin"
d = open(path, "rb").read()

N = int.from_bytes(d[0x3FBBC:0x3FBBC+128], "big")
e = 3

print(f"Modulus N = 0x{N:0256X}")
print(f"Public exponent e = {e}")
print(f"File size: {len(d):,} bytes")

# ---- Part 1: Full 2MB scan for private key ----
print("\n=== Part 1: Full 2MB scan for RSA private exponent d ===")
start = time.time()
found = False
target = 2
mod_exp = pow(2, e, N)  # = 8

for off in range(0, len(d) - 128, 4):
    cand = int.from_bytes(d[off:off+128], "big")
    if 0 < cand < N:
        if pow(mod_exp, cand, N) == target:
            print(f"[+] Big-endian d at 0x{off:06X}: 0x{cand:0256X}")
            found = True
            break
    cand_sw = int.from_bytes(d[off:off+128], "little")
    if 0 < cand_sw < N:
        if pow(mod_exp, cand_sw, N) == target:
            print(f"[+] Byte-swapped d at 0x{off:06X}: 0x{cand_sw:0256X}")
            found = True
            break

    if off % 0x40000 == 0 and off > 0:
        elapsed = time.time() - start
        pct = off / len(d) * 100
        eta = elapsed / off * (len(d) - off)
        print(f"  ... 0x{off:06X} ({pct:.1f}%), {elapsed:.1f}s elapsed, ETA {eta:.1f}s")

if not found:
    print("[-] No private key candidate found (4-byte aligned).")
print(f"Elapsed: {time.time()-start:.1f}s")

# ---- Part 2: CRT factor search ----
print("\n=== Part 2: CRT factor search (64-byte p, q) ===")
start = time.time()
found = False
for off in range(0, len(d) - 64, 4):
    p = int.from_bytes(d[off:off+64], "big")
    if p < 2:
        continue
    if N % p == 0:
        q = N // p
        print(f"[+] CRT factor p at 0x{off:06X}: 0x{p:0128X}")
        print(f"    q = 0x{q:0128X}")
        phi = (p - 1) * (q - 1)
        d_priv = pow(e, -1, phi)
        print(f"[+] Private exponent d = 0x{d_priv:0256X}")
        found = True
        break
if not found:
    print("[-] No CRT factor found.")
print(f"Elapsed: {time.time()-start:.1f}s")

# ---- Part 3: Pollard rho factoring ----
print("\n=== Part 3: Pollard rho factoring (30s timeout) ===")

def pollard_rho(n, timeout=30):
    if n % 2 == 0:
        return 2
    start = time.time()
    while time.time() - start < timeout:
        c = random.randint(1, n-1)
        x = random.randint(2, n-1)
        y = x
        d = 1
        while d == 1:
            x = (x*x + c) % n
            y = (y*y + c) % n
            y = (y*y + c) % n
            d = math.gcd(abs(x-y), n)
            if time.time() - start > timeout:
                return None
        if d != n:
            return d
    return None

factor = pollard_rho(N, timeout=30)
if factor:
    print(f"[+] Found factor! p = {factor}")
    q = N // factor
    phi = (factor - 1) * (q - 1)
    d_priv = pow(e, -1, phi)
    print(f"[+] q = {q}")
    print(f"[+] Private exponent d = 0x{d_priv:0256X}")
else:
    print("[-] No factor found in 30s (expected for 1024-bit RSA).")

print("\nDone.")