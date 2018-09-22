from machine import I2C, Pin


class MUX:
    def __init__(self, name, config, to_wrap):
        self.mux_addr = config.get('mux_address', 0x70)
        self._wrapped = to_wrap
        self._monitors = list()
        self.i2c = I2C(scl=Pin(config['clock']), sda=Pin(config['data']))

    def monitor(self, config):
        monitor = MUXMonitor(self, config)
        monitor.select()
        monitor.wrap(self._wrapped.monitor(config))
        self._monitors.append(monitor)
        return monitor

    def tick(self):
        for monitor in self._monitors:
            monitor.tick()


class MUXMonitor:
    def __init__(self, parent, config):
        self._id = config.get('id', 0)
        self.parent = parent
        self._wrapped = None

    def wrap(self, to_wrap):
        self._wrapped = to_wrap

    @property
    def status(self):
        return self._wrapped.status

    @status.setter
    def status(self, msg):
        self.select()
        self._wrapped.status = msg

    def tick(self):
        tick_op = getattr(self._wrapped, "tick", None)
        if callable(tick_op):
            tick_op()

    def select(self):
        byte_message = bytearray(1)
        byte_message[0] = 1 << self._id
        self.parent.i2c.writeto(self.parent.mux_addr, byte_message)

