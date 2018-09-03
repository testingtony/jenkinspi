from oled import OLED, OLEDMonitor


class MUX_OLED(OLED):
    def __init__(self, name, config):
        super().__init__(name, config)
        self.mux_addr = config.get('mux_address', 0x70)

    def monitor(self, config):
        monitor = MUX_OLEDMonitor(self, config)
        self._monitors.append(monitor)
        return monitor


class MUX_OLEDMonitor(OLEDMonitor):
    def __init__(self, parent, config):
        super().__init__(parent, config)
        self._id = config.get('id', 0)

    @property
    def status(self):
        return super().status

    @status.setter
    def status(self, instruction):
        a = bytearray(1)
        a[0] = 1 << self._id
        self.parent.i2c.writeto(self.parent.mux_addr, a)
        #super(MUX_OLEDMonitor, self.__class__).status.__set__(self, instruction)
        super().set_status(instruction)

