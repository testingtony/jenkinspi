from machine import I2C, Pin
from ssd1306 import SSD1306_I2C
from math import ceil
from display import error
import ujson


class OLED:
    def __init__(self, name, config):
        self.name = name
        self.i2c = I2C(scl=Pin(config['clock']), sda=Pin(config['data']))
        self.images = config.get('images', dict())
        self._monitors = list()
        self.config = config

    def tick(self):
        pass

    def monitor(self, config):
        monitor = OLEDMonitor(self, config)
        self._monitors.append(monitor)
        return monitor


class OLEDMonitor:
    def __init__(self, parent, config):
        self.parent = parent
        self._config = config
        self._status = None
        self._flash = False
        self._images = config.get('images', parent.images)
        self._w = config.get('width', parent.config.get('width', 128))
        self._h = config.get('height', parent.config.get('height', 64))

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, msg):
        instruction = ujson.loads(str(msg, 'utf-8'))
        self.set_status(instruction)

    def set_status(self, instruction):
        self._status = instruction
        images = ("fail",)
        try:
            result = instruction['result']
            if result == 'SUCCESS':
                images = instruction['buildid']
            else:
                images = (self._images[result],)
        except KeyError as err:
            error("Key Error in AlphaNum.status {}".format(err))
        finally:
            self.show(images)

    def show(self, images):
        display = SSD1306_I2C(self._w, self._h, self.parent.i2c)
        display.fill(0)
        x = 0
        for img in images:
            x = x + 1 + add_image(display, x, img)
        display.show()
        display = None


def add_image(display, x, image):
    if image == ':' or image == '.':
        image = 'colon'
    try:
        with open("fonts/{}.pbm".format(image), "rb") as f:
            pbm_format = f.readline().strip()
            f.readline()
            size = f.readline().strip()
            assert(pbm_format == b'P4')
            w, h = size.split()
            byte_count = int(ceil(int(w) / 8.0))
            for line_no in range(int(h)):
                line = f.read(byte_count)
                bits = bitz(line)
                for bit_no in range(int(w)):
                    display.pixel(x + bit_no, line_no, 1 if next(bits) else 0)
    except OSError as e:
        error("Problem loading bitmap", e)
        w = 0

    return int(w)


def bitz(string):
    for byte in string:
        for bit_no in range(8):
            bit = byte & 0x80
            byte <<= 1
            yield bit != 0x80
