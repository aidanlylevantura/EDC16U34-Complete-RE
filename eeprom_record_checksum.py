import struct

PATH = r"C:\Users\user\Documents\Complete ECU Disassembly\Golf_KH_BDM\Eeprom.bin"
d = open(PATH, "rb").read()

def crc16_ccitt(b, init=0xFFFF, poly=0x1021):
    crc = init
    for v in b:
        crc ^= v << 8
        for _ in range(8):
            crc = ((crc << 1) ^ poly) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return crc

def crc16_xmodem(b):
    return crc16_ccitt(b, 0x0000, 0x1021)

def crc16_modbus(b):
    crc = 0xFFFF
    for v in b:
        crc ^= v
        for _ in range(8):
            crc = ((crc >> 1) ^ 0xA001) & 0xFFFF if crc & 1 else (crc >> 1) & 0xFFFF
    return crc

def sum16be(b):
    return sum(int.from_bytes(b[i:i+2], "big") for i in range(0, len(b)-1, 2)) & 0xFFFF

def sum16le(b):
    return sum(int.from_bytes(b[i:i+2], "little") for i in range(0, len(b)-1, 2)) & 0xFFFF

def xor8(b):
    x = 0
    for v in b: x ^= v
    return x & 0xFF

def sum8(b):
    return sum(b) & 0xFF

records = [
    ("IMMO rec1", 0x00E0),
    ("IMMO rec2", 0x0100),
    ("IMMO rec3", 0x0120),
    ("VIN rec1",  0x0140),
    ("VIN rec2",  0x0160),
]

print("=== 32-byte record checksum tests ===")
for name, off in records:
    rec = d[off:off+32]
    body = rec[:30]
    tail_be = int.from_bytes(rec[30:32], "big")
    tail_le = int.from_bytes(rec[30:32], "little")
    print("\n%s @ 0x%04X" % (name, off))
    print("  record:", rec.hex())
    print("  body  :", body.hex())
    print("  tail  : %s  BE=0x%04X  LE=0x%04X" % (rec[30:32].hex(), tail_be, tail_le))
    print("  xor8      = 0x%02X" % xor8(body))
    print("  sum8      = 0x%02X" % sum8(body))
    print("  sum16be   = 0x%04X  matchBE=%s matchLE=%s" % (sum16be(body), sum16be(body)==tail_be, sum16be(body)==tail_le))
    print("  sum16le   = 0x%04X  matchBE=%s matchLE=%s" % (sum16le(body), sum16le(body)==tail_be, sum16le(body)==tail_le))
    print("  crc16ccitt= 0x%04X  matchBE=%s matchLE=%s" % (crc16_ccitt(body), crc16_ccitt(body)==tail_be, crc16_ccitt(body)==tail_le))
    print("  crc16xmod = 0x%04X  matchBE=%s matchLE=%s" % (crc16_xmodem(body), crc16_xmodem(body)==tail_be, crc16_xmodem(body)==tail_le))
    print("  crc16modb = 0x%04X  matchBE=%s matchLE=%s" % (crc16_modbus(body), crc16_modbus(body)==tail_be, crc16_modbus(body)==tail_le))

print("\n=== Test same algorithms over first 31 bytes, compare last byte ===")
for name, off in records:
    rec = d[off:off+32]
    body = rec[:31]
    tail = rec[31]
    print("\n%s @ 0x%04X tail byte=0x%02X" % (name, off, tail))
    print("  xor8=0x%02X match=%s" % (xor8(body), xor8(body)==tail))
    print("  sum8=0x%02X match=%s" % (sum8(body), sum8(body)==tail))
    print("  crc16ccitt low=0x%02X high=0x%02X" % (crc16_ccitt(body)&0xFF, (crc16_ccitt(body)>>8)&0xFF))