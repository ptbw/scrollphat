import time

from machine import Pin, I2C
from font import font


print("const")
I2C_ADDR = 0x60
CMD_SET_MODE = 0x00
CMD_SET_BRIGHTNESS = 0x19
MODE_5X11 = 0b00000011

print("init")
_rotate = False
buffer = [0] * 11
offset = 0
error_count = 0

print("i2c bus {0}".format(buffer))
bus = I2C(0, scl=Pin(21), sda=Pin(20), freq=100000)

def write_i2c_block_data(addr, register, data):
    """ Write multiple bytes of data to register of device at addr
        Returns None """
    # writeto_mem() expects something it can treat as a buffer    
    buff = bytearray(data)    
    print("values {0} {1} {2}".format(addr, register, buff))
    return bus.writeto_mem(addr, register, buff)

def set_brightness(brightness):    
    write_i2c_block_data(I2C_ADDR, CMD_SET_BRIGHTNESS, [brightness])


def update():
    global buffer
    if offset + 11 <= len(buffer):
        window = buffer[offset:offset + 11]
    else:
        window = buffer[offset:]
        window += buffer[:11 - len(window)]

    if _rotate:
        window.reverse()
        for i in range(len(window)):
            window[i] = rotate5bits(window[i])

    window.append(0xff)
    write_i2c_block_data(I2C_ADDR, 0x01, window)
    
def set_col(x, value):
    global buffer
    print("set col {0}".format(buffer))
    if len(buffer) <= x:
        buffer += [0] * (x - len(buffer) + 1)

    buffer[x] = value    
    
def write_string(chars, x = 0):
    for char in chars:
        if ord(char) == 0x20 or ord(char) not in font:
            set_col(x, 0)
            x += 1
            set_col(x, 0)
            x += 1
            set_col(x, 0)
            x += 1
        else:
            font_char = font[ord(char)]
            for i in range(0, len(font_char)):
                set_col(x, font_char[i])
                x += 1

            set_col(x, 0)
            x += 1 # space between chars
    update()    


def set_mode(mode=MODE_5X11):
    write_i2c_block_data(I2C_ADDR, CMD_SET_MODE, [MODE_5X11])
    
def set_rotate(value):
    _rotate = value

def rotate5bits(x):
    r = 0
    if x & 16:
        r = r | 1
    if x & 8:
        r = r | 2
    if x & 4:
        r = r | 4
    if x & 2:
        r = r | 8
    if x & 1:
        r = r | 16
    return r

set_mode(MODE_5X11)
print("starting")

print("main {0}".format(buffer))
set_brightness(0x01)
while True:
    for x in range(1, 1000):
        write_string("{0:03d}".format(x))
        time.sleep(1)
        
print("done")