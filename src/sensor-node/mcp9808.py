from machine import I2C, Pin
import struct

class MCP9808:

    def __init__(self, scl_pin=5, sda_pin=4, baudrate=100000, address=0x18):
        self._i2c = I2C(scl=Pin(scl_pin), sda=Pin(sda_pin), freq=baudrate)
        self._address = address

    def get_temp(self):

        # read from temp register (0x05, from datasheet)
        temp = self._i2c.readfrom_mem(self._address, 0x05, 2)
        # read temperature as 16-bit word
        temp_raw = struct.unpack('>H', temp)[0]

        # mask first 4 bits
        temp = temp_raw & 0x0fff

        # divide by 16, convert to floating point
        temp /= 16.0

        # check sign bit (4th bit of the raw word)
        sign = temp_raw & 0x1000

        if sign:
            # if sign bit is high, it's a negative number, remove 256
            temp -= 0xff

        # return temperature in degrees C
        return temp