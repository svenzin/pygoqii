import bluepy.btle as btle
import struct
import time
from datetime import datetime, timedelta, date

def convert(i, a, b):
    assert(i >= 0)
    assert(a > 0)
    assert(b > 0)
    j = 0
    m = 1
    while i > 0:
        j += m * (i % a)
        m *= b
        i //= a
    return j


def int_to_bcd(i):
    return convert(i, 10, 16)


def bcd_to_int(bcd):
    return convert(bcd, 16, 10)


block = []
class Delegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print('Received from', cHandle, ':', data.hex())
        item = cHandle, data
        block.append(item)

    def handleDiscovery(self, scanEntry, isNewDev, isNewData):
        print('Discovered', scanEntry, isNewDev, isNewData)


SAFE = True
def cmd(data):
    command = commands[data[0]]
    if SAFE and command == DISABLE:
        print(DISABLE, 'is an unsafe command. Aborting.')
        return None

    print('Executing', command)

    step = 0.1

    write.write(bytearray(data), True)

    global block
    r = []
    while True:
        time.sleep(step)
        read.read()
        if len(block) == 0:
            break
        r = r + block
        block = []
    success = (r[0][1][0] & 0x80) == 0
    return success, r

UNKNOWN = 'UNKNOWN'
REBOOT_ = 'REBOOT'
DISABLE = 'DISABLE'
G_TIME_ = 'GET TIME'
S_TIME_ = 'SET TIME'
G_DISPL = 'GET DISPLAY ORIENTATION'
S_DISPL = 'SET DISPLAY_ORIENTATION'
G_CLOCK = 'GET CLOCK FORMAT'
S_CLOCK = 'SET CLOCK FORMAT'
G_DISTF = 'GET DISTANCE FORMAT'
S_DISTF = 'SET DISTANCE FORMAT'
G_TARGT = 'GET STEPS TARGET'
S_TARGT = 'SET STEPS TARGET'
G_ACTIV = 'GET ACTIVITY DETAILS'
G_HR___ = 'GET HEART RATE DETAILS'

commands = {
    0x00: UNKNOWN, 0x01: S_TIME_, 0x02: UNKNOWN, 0x03: UNKNOWN,
    0x04: UNKNOWN, 0x05: UNKNOWN, 0x06: UNKNOWN, 0x07: UNKNOWN,
    0x08: UNKNOWN, 0x09: UNKNOWN, 0x0A: UNKNOWN, 0x0B: S_TARGT,
    0x0C: UNKNOWN, 0x0D: UNKNOWN, 0x0E: UNKNOWN, 0x0F: S_DISTF,

    0x10: UNKNOWN, 0x11: UNKNOWN, 0x12: DISABLE, 0x13: UNKNOWN,
    0x14: UNKNOWN, 0x15: UNKNOWN, 0x16: UNKNOWN, 0x17: UNKNOWN,
    0x18: UNKNOWN, 0x19: UNKNOWN, 0x1A: UNKNOWN, 0x1B: UNKNOWN,
    0x1C: UNKNOWN, 0x1D: UNKNOWN, 0x1E: UNKNOWN, 0x1F: UNKNOWN,

    0x20: UNKNOWN, 0x21: UNKNOWN, 0x22: UNKNOWN, 0x23: UNKNOWN,
    0x24: UNKNOWN, 0x25: UNKNOWN, 0x26: UNKNOWN, 0x27: UNKNOWN,
    0x28: UNKNOWN, 0x29: UNKNOWN, 0x2A: UNKNOWN, 0x2B: UNKNOWN,
    0x2C: UNKNOWN, 0x2D: UNKNOWN, 0x2E: REBOOT_, 0x2F: G_HR___,

    0x30: S_DISPL, 0x31: G_DISPL, 0x32: UNKNOWN, 0x33: UNKNOWN,
    0x34: UNKNOWN, 0x35: UNKNOWN, 0x36: UNKNOWN, 0x37: S_CLOCK,
    0x38: G_CLOCK, 0x39: UNKNOWN, 0x3A: UNKNOWN, 0x3B: UNKNOWN,
    0x3C: UNKNOWN, 0x3D: UNKNOWN, 0x3E: UNKNOWN, 0x3F: UNKNOWN,

    0x40: UNKNOWN, 0x41: G_TIME_, 0x42: UNKNOWN, 0x43: G_ACTIV,
    0x44: UNKNOWN, 0x45: UNKNOWN, 0x46: UNKNOWN, 0x47: UNKNOWN,
    0x48: UNKNOWN, 0x49: UNKNOWN, 0x4A: UNKNOWN, 0x4B: G_TARGT,
    0x4C: UNKNOWN, 0x4D: UNKNOWN, 0x4E: UNKNOWN, 0x4F: G_DISTF,

    0x50: UNKNOWN, 0x51: UNKNOWN, 0x52: UNKNOWN, 0x53: UNKNOWN,
    0x54: UNKNOWN, 0x55: UNKNOWN, 0x56: UNKNOWN, 0x57: UNKNOWN,
    0x58: UNKNOWN, 0x59: UNKNOWN, 0x5A: UNKNOWN, 0x5B: UNKNOWN,
    0x5C: UNKNOWN, 0x5D: UNKNOWN, 0x5E: UNKNOWN, 0x5F: UNKNOWN,

    0x60: UNKNOWN, 0x61: UNKNOWN, 0x62: UNKNOWN, 0x63: UNKNOWN,
    0x64: UNKNOWN, 0x65: UNKNOWN, 0x66: UNKNOWN, 0x67: UNKNOWN,
    0x68: UNKNOWN, 0x69: UNKNOWN, 0x6A: UNKNOWN, 0x6B: UNKNOWN,
    0x6C: UNKNOWN, 0x6D: UNKNOWN, 0x6E: UNKNOWN, 0x6F: UNKNOWN,

    0x70: UNKNOWN, 0x71: UNKNOWN, 0x72: UNKNOWN, 0x73: UNKNOWN,
    0x74: UNKNOWN, 0x75: UNKNOWN, 0x76: UNKNOWN, 0x77: UNKNOWN,
    0x78: UNKNOWN, 0x79: UNKNOWN, 0x7A: UNKNOWN, 0x7B: UNKNOWN,
    0x7C: UNKNOWN, 0x7D: UNKNOWN, 0x7E: UNKNOWN, 0x7F: UNKNOWN,
}


def packet(command, payload=None):
    assert(0 <= command < 0x80)
    assert(payload is None or len(payload) <= 14)
    block = 16 * [0]
    block[0] = command
    if payload is not None:
        for i, x in enumerate(payload):
            block[i + 1] = x
    block[-1] = sum(block) % 256
    return block


def unpacket(packet):
    assert(len(packet) > 1)
    packet_sum = sum(packet[:-1]) % 256
    checksum = packet[-1]
    assert(packet_sum == checksum)
    command = packet[0]
    payload = packet[1:-1]
    return command, payload, checksum


def decode_heart_rate(data):
    def decode_block(block):
        id = block[0]
        seconds = int.from_bytes(block[1:5], byteorder='big')
        t = datetime(2000, 1, 1) + timedelta(seconds=seconds)
        hr = [i for i in block[5:8]]
        return id, t, hr

    command, payload, _ = unpacket(data)
    assert(command == 0x2F)
    assert(len(payload) == 18)

    measures = []

    id1, t1, hr1 = decode_block(payload[0:8])
    if id1 not in [0x00, 0xff]:
        measures.append((t1, hr1))

    id2, t2, hr2 = decode_block(payload[8:16])
    if id2 not in [0x00, 0xff]:
        measures.append((t2, hr2))

    return measures

def decode_daily_summary(data):
    command, payload, _ = unpacket(data)
    assert(command == 0x07)
    assert(len(payload) == 14)
    type = payload[0]
    assert(type in [0x00, 0x01])
    index_of_day = payload[1]
    year = bcd_to_int(payload[2])
    month = bcd_to_int(payload[3])
    day = bcd_to_int(payload[4])
    t = date(year, month, day)
    if type == 0x00:
        assert(payload[5] == 0x00)
        steps = 256 * payload[6] + payload[7]
        assert(payload[8] == 0x00)
        assert(payload[9] == 0x00)
        assert(payload[10] == 0x00)
        assert(payload[11] == 0x00)
        unknown = [payload[12], payload[13]]
        return type, t, steps, unknown
    elif type == 0x01:
        assert(payload[5] == 0x00)
        distance = (256 * payload[6] + payload[7]) / 100
        active_distance = (256 * payload[8] + payload[9]) / 100
        assert(payload[10] == 0x00)
        assert(payload[11] == 0x00)
        assert(payload[12] == 0x00)
        assert(payload[13] == 0x00)
        return type, t, distance, active_distance


get_time = packet(0x41)
def set_time(t):
    y = int_to_bcd(t.year % 100)
    m = int_to_bcd(t.month)
    d = int_to_bcd(t.day)
    hh = int_to_bcd(t.hour)
    mm = int_to_bcd(t.minute)
    ss = int_to_bcd(t.second)
    return packet(0x01, [y, m, d, hh, mm, ss])

get_display            = packet(0x31)
set_display_horizontal = packet(0x30, [1])
set_display_vertical   = packet(0x30, [0])

get_clock     = packet(0x38)
set_clock_12h = packet(0x37, [0])
set_clock_24h = packet(0x37, [1])

get_distance            = packet(0x4f)
set_distance_kilometers = packet(0x0f, [0])
set_distance_miles      = packet(0x0f, [1])

get_activity_day_0     = packet(0x43, [0])
get_activity_day_1     = packet(0x43, [1])
get_activity_day_2     = packet(0x43, [2])
get_activity_day_3     = packet(0x43, [3])
get_activity_today     = get_activity_day_0
get_activity_yesterday = get_activity_day_1

get_steps_target = packet(0x4b)
def set_steps_target(n):
    h = (n // 65536) % 256
    m = (n // 256) % 256
    l = n % 256
    return packet(0x0b, [h, m, l])

get_heart_rate = packet(0x2f)

reboot = packet(0x2e)
disable = packet(0x12)

unknown_00 = packet(0x07)
unknown_01 = packet(0x58)


try:
    addr = 'FF:17:B2:A3:BB:22'
    print('Connecting to', addr, '...')
    goqii = btle.Peripheral(addr)
    goqii.setDelegate(Delegate())

    read = goqii.getCharacteristics(uuid='0000fff7-0000-1000-8000-00805f9b34fb')[0]
    goqii.writeCharacteristic(read.getHandle() + 1, struct.pack('<bb', 0x01, 0x00))
    write = goqii.getCharacteristics(uuid='0000fff6-0000-1000-8000-00805f9b34fb')[0]

    import code
    code.interact(local=locals())
except Exception:
    print('disconnecting...')
    goqii.disconnect()
print('disconnecting...')
goqii.disconnect()
