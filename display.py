from machine import Pin, I2C
import ht16k33_seg
from neopixel import NeoPixel
from umqtt.simple import MQTTClient
import ujson
from pause import Pause
import ubinascii
import machine
import gc

CLIENT_ID = ubinascii.hexlify(machine.unique_id())

colours = None
connection = None
subscriptions = list()


class Pixel:
    def __init__(self, neopixel, index=0):
        self._id = index
        self._neopixel = neopixel
        self._brightness = 0
        self.status = {'building': False, 'result': None}

    def tick(self):
        if self.status.get('building', False):
            self._brightness = (self._brightness + 1) % 19
        else:
            self._brightness = 0
        brightness = abs(10 - self._brightness)

        try:
            colour = colours[self.status['result']]
        except KeyError:
            colour = (0, 0, 0)

        self._neopixel[self._id] = [int(rgb * brightness / 10) for rgb in (colour[1], colour[0], colour[2])]

    def __str__(self):
        return "[Pixel neopixel {!s}, id {!s}, status {!r}]".format(self._neopixel, self._id, self.status)

    __repr__ = __str__


class Alpha:
    def __init__(self, i2c, address=0x70, texts=None):
        self.address = address
        self._seg = ht16k33_seg.Seg14x4(i2c, address)
        self._seg.brightness(1)
        self._seg.text('    ')
        self._seg.show()
        if texts:
            self._texts = texts
        else:
            self._texts = dict()

    def tick(self):
        pass

    @property
    def status(self):
        return

    @status.setter
    def status(self, status):
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

    def __str__(self):
        return "[Alpha {!s}, id {!s}]".format(self._seg, self.address)

    __repr__ = __str__


pixels = dict()
monitors = list()
jobs = dict()


def message_callback(topic, msg):
    instruction = ujson.loads(str(msg, 'utf-8'))
    topic = str(topic, 'utf-8')
    if topic.startswith('config/reply'):
        apply_config(instruction)
        return

    for monitor in jobs.get(topic, list()):
        monitor.status = instruction


def apply_config(config):
    global pixels
    global monitors
    global jobs
    global colours
    global subscriptions

    colours = config['colours']
    pixels = dict()
    monitors = list()
    jobs = dict()
    i2cs = dict()
    for (name, setting) in config['devices'].items():
        if name.startswith("Pixel"):
            pixels[name] = NeoPixel(Pin(setting['pin']), setting['size'])
        elif name.startswith("Alpha"):
            i2cs[name] = I2C(scl=Pin(setting['clock']), sda=Pin(setting['data']))
        else:
            print("Unknown configuration Type '{}'".format(name))
            pass

    for monitor in config['monitors']:
        output = monitor['output']
        topic = monitor['topic']
        address = monitor['address']
        job = jobs.setdefault(topic, list())
        if output.startswith('Pixel'):
            mon = Pixel(pixels[output], address)
        elif output.startswith('Alpha'):
            mon = Alpha(i2cs[output], address, texts=config['texts'])
        monitors.append(mon)
        job.append(mon)
        subscriptions.append(topic)
        connection.subscribe(topic)

    gc.collect()


def subscribe():
    global subscriptions
    global connection
    for topic in subscriptions:
        connection.subscribe(topic)


def main(server="raspberrypi"):
    global connection
    no_connection_count = 0

    import network
    sta_if = network.WLAN(network.STA_IF)
    while not sta_if.isconnected():
        pass
    print('network config:{!r} clientid:{}'.format(sta_if.ifconfig(), CLIENT_ID))

    try:
        connection = MQTTClient(CLIENT_ID, server)
        connection.set_callback(message_callback)
        connection.connect()
        connected = True
        print("Connected to MQ")
        connection.subscribe(b"config/reply/" + CLIENT_ID)
        connection.publish(b'config/request/' + CLIENT_ID, CLIENT_ID)
    except OSError:
        pin = Pin(2, Pin.OUT)
        pin.off()
        raise

    while True:
        try:
            if not connected:
                connection.connect()
                subscribe()

            connection.check_msg()

            for monitor in monitors:
                monitor.tick()

            for pixel in pixels.values():
                pixel.write()

            gc.collect()
            Pause.pause(100)
            no_connection_count = 0

        except (IndexError, OSError) as e:
            print("exception {!r} {}".format(e, no_connection_count))
            Pause.pause(1000)
            connected = False
            no_connection_count += 1
            if no_connection_count > 100:
                import machine
                machine.reset()
        except BaseException as e:
            print("Other exception {!r}".format(e))
            connection.disconnect()
            connection = None
            break


if __name__ == '__main__':
    main()
