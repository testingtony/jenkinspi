from neopixel import NeoPixel
from machine import Pin
import ujson


class Pixel:
    def __init__(self, name, config):
        self.name = name
        self.pixel = NeoPixel(Pin(config['pin']), config['size'])
        self.colours = config.get('colours', dict())
        self._monitors = list()
        self._config = config

    def tick(self):
        for monitor in self._monitors:
            monitor.tick()
        self.pixel.write()

    def monitor(self, config):
        monitor = PixelMonitor(self, config)
        self._monitors.append(monitor)
        return monitor


class PixelMonitor:
    def __init__(self, parent, config):
        self._parent = parent
        self._config = config
        self._status = None
        self._flash = False
        self._brightness = 0
        self._address = config['address']
        self._colours = config.get('colours', self._parent.colours)
        self._colour = [0, 0, 0]

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, msg):
        status = ujson.loads(str(msg, 'utf-8'))
        self._status = status
        self._flash = status.get('building', False)
        result = status['result']
        self._colour = self._colours.get(result, [0, 0, 0])

    def tick(self):
        if self._flash:
            self._brightness = (self._brightness + 1) % 20
            brightness = abs(self._brightness - 10)
        else:
            brightness = 10

        colour = [int(component * brightness / 10) for component in self._colour]
        self._parent.pixel[self._address] = [colour[1], colour[0], colour[2]]
