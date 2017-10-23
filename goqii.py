import bluepy.btle as btle
import struct
import time
from datetime import datetime


def bcd(i):
    r = 0
    m = 1
    while i > 0:
        r += m * (i % 10)
        m *= 16
        i //= 10
    return r


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
    return r

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
    0x2C: UNKNOWN, 0x2D: UNKNOWN, 0x2E: REBOOT_, 0x2F: UNKNOWN,

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

get_time = [0x41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x41]
def set_time(t):
    data = [0] * 16
    data[0] = 0x01
    data[1] = bcd(t.year % 100)
    data[2] = bcd(t.month)
    data[3] = bcd(t.day)
    data[4] = bcd(t.hour)
    data[5] = bcd(t.minute)
    data[6] = bcd(t.second)
    data[-1] = sum(data) % 256
    return data

get_display            = [0x31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x31]
set_display_horizontal = [0x30, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x31]
set_display_vertical   = [0x30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x30]

get_clock     = [0x38, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x38]
set_clock_12h = [0x37, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x37]
set_clock_24h = [0x37, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x38]

get_distance            = [0x4f, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x4f]
set_distance_kilometers = [0x0f, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x0f]
set_distance_miles      = [0x0f, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x10]

get_activity_day_0     = [0x43, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x43]
get_activity_day_1     = [0x43, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x44]
get_activity_day_2     = [0x43, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x45]
get_activity_day_3     = [0x43, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x46]
get_activity_today     = get_activity_day_0
get_activity_yesterday = get_activity_day_1

get_steps_target = [0x4b, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x4b]
def set_steps_target(n):
    data = [0] * 16
    data[0] = 0x0b
    data[1] = (n // 65536) % 256
    data[2] = (n // 256) % 256
    data[3] = n % 256
    data[-1] = sum(data) % 256
    return data

reboot = [0x2e, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x2e]
disable = [0x12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x12]

unknown_00 = [0x07, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x07]
unknown_01 = [0x58, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x58]
unknown_02 = [0x2f, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0x2f]


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
