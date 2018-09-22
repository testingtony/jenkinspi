from machine import I2C, Pin
from ssd1306_i2c import Display
from display import error
from uio import BytesIO
from framebuf import FrameBuffer, MONO_HLSB


class OLEDBitmap:
    def __init__(self, name, config):
        self.name = name
        self.i2c = I2C(scl=Pin(config['clock']), sda=Pin(config['data']))
        self._monitors = list()
        self.config = config

    def tick(self):
        pass

    def monitor(self, config):
        monitor = OLEDBitmapMonitor(self, config)
        self._monitors.append(monitor)
        return monitor


class OLEDBitmapMonitor:
    def __init__(self, parent, config):
        self.parent = parent
        self._config = config
        self._status = None
        self._flash = False
        self._w = config.get('width', parent.config.get('width', 128))
        self._h = config.get('height', parent.config.get('height', 64))
        self._display = Display(parent.i2c, width=self._w, height=self._h)
        self._display.fb.fill(0)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, image):
        display = self._display
        self._status = image
        width, framebuffer = get_image(0, image)
        display.fb.blit(framebuffer, 0, 0)
        display.update()


def get_image(x, image):
    try:
        with BytesIO(image) as f:
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
    except OSError as e:
        error("Problem loading bitmap", e)
        w = 0

    return w, fb
