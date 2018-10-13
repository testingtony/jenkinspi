from machine import I2C, Pin
from framebuf import FrameBuffer, MONO_HLSB
import ujson
from display import error


class OLEDText:
    def __init__(self, name, config):
        self.name = name
        self.i2c = I2C(scl=Pin(config['clock']), sda=Pin(config['data']))
        self.images = config.get('images', dict())
        self._monitors = list()
        self.config = config

    def tick(self):
        pass

    def monitor(self, config):
        monitor = OLEDTextMonitor(self, config)
        self._monitors.append(monitor)
        return monitor


class OLEDTextMonitor:
    def __init__(self, parent, config):
        self.parent = parent
        self._config = config
        self._status = None
        self._flash = False
        self._images = config.get('images', parent.images)
        self._w = config.get('width', parent.config.get('width', 128))
        self._h = config.get('height', parent.config.get('height', 64))
        self._last = None
        display = config.get('type', parent.config.get('type', 'sh1106'))
        if display == 'sh1106':
            import sh1106_i2c
            self._display = sh1106_i2c.Display(parent.i2c, width=self._w, height=self._h)
        elif display == 'ssd1306':
            import ssd1306_i2c
            self._display = ssd1306_i2c.Display(parent.i2c, width=self._w, height=self._h)
        else:
            error("Unknown OLED type")
        self._display.fb.fill(0)
        self._display.update()
        self._format = config.get('format', '{buildid}')

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, msg):
        s = str(msg, 'utf-8')
        instruction = ujson.loads(s)
        self._status = instruction
        images = ("failed",)
        try:
            result = instruction['result']
            building = instruction['building']
            if building:
                images = ('building',)
            elif result == 'SUCCESS':
                images = self._format.format(**instruction)
            elif result == 'ABORTED':
                images = ('aborted',)
            elif result == 'FAILURE':
                images = ('failure',)
            elif result == 'UNSTABLE':
                images = ('unstable',)
            else:
                images = (self._images[result],)
        except KeyError as err:
            error("Key Error in OLED.status {}".format(err))
        finally:
            if self._last is None or self._last != images:
                self._last = images
                self.show(images)

    def show(self, images):
        display = self._display
        display.fb.fill(0)
        x = 0
        for img in images:
            x = x + 1 + add_image(display.fb, x, img)
        display.update()


def add_image(display, x, image):
    if image == ':':
        image = 'colon'
    elif image == '/':
        image = 'slash'
    try:
        with open("fonts/{}.pbm".format(image), "rb") as f:
            pbm_format = f.readline().strip()
            size = f.readline().strip()
            if size.startswith(b'#'):
                size = f.readline().strip()
            assert(pbm_format == b'P4')
            w, h = size.split()
            w = int(w)
            h = int(h)
            bar = bytearray(f.read())
            fb = FrameBuffer(bar, w, h, MONO_HLSB)
            display.blit(fb, x, 0)
    except OSError as e:
        error("Problem loading bitmap '{}'".format(image), e)
        w = 0

    return w
