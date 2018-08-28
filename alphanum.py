from machine import I2C
from machine import Pin
import ht16k33_seg


class AlphaNum:
    def __init__(self, name, config):
        self.name = name
        self.i2c = I2C(scl=Pin(config['clock']), sda=Pin(config['data']))
        self.texts = config.get('texts', dict())
        self._monitors = list()
        self._config = config

    def tick(self):
        pass

    def monitor(self, config):
        monitor = AlphaNumMonitor(self, config)
        self._monitors.append(monitor)
        return monitor


class AlphaNumMonitor:
    def __init__(self, parent, config):
        self._parent = parent
        self._config = config
        self._status = None
        self._flash = False
        self._address = config['address']
        self._texts = config.get('texts', self._parent.texts)

        self._seg = ht16k33_seg.Seg14x4(parent.i2c, self._address)
        self._seg.brightness(1)
        self._seg.text('    ')
        self._seg.show()

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        self._status = status
        try:
            result = status['result']
            if result == 'SUCCESS':
                result = status['buildid']
            else:
                result = self._texts[result]
            self._seg.text(result)
            self._seg.blink_rate(1 if status['building'] else 0)
        except KeyError as err:
            print("Error {}".format(err))
            self._seg.text('????')
            self._seg.blink_rate(0)
        finally:
            self._seg.show()
