from umqtt.simple import MQTTClient
import ujson
import ubinascii
import machine
from machine import Pin
import gc
from pause import pause


CLIENT_ID = ubinascii.hexlify(machine.unique_id())

topic_monitors = dict()
name_device = dict()
connection = None


def message_callback(topic, msg):
    try:
        topic = str(topic, 'utf-8')
        if topic.startswith('config/reply'):
            instruction = ujson.loads(str(msg, 'utf-8'))
            apply_config(instruction)
            return

        for monitor in topic_monitors.get(topic, list()):
            monitor.status = msg
    except Exception as e:
        error("Config failed", e)


def apply_config(config):
    global name_device
    global topic_monitors

    name_device = dict()
    for name, cfg in config['devices'].items():
        if name.startswith("Alpha"):
            from alphanum import AlphaNum
            name_device[name] = AlphaNum(name, cfg)
        elif name.startswith("Pixel"):
            from pixel import Pixel
            name_device[name] = Pixel(name, cfg)
        elif name.startswith("OLED"):
            print("0.1")
            from oled import OLED
            name_device[name] = OLED(name, cfg)
            print("0.2")
        else:
            error("I don't know what sort of device a {} is".format(name))

        if 'mux_address' in cfg:
            print("wrapping {!r}".format(cfg))
            from mux import MUX
            to_wrap = name_device[name]
            name_device[name] = MUX(name, cfg, to_wrap)

    topic_monitors = dict()
    for monitor_config in config['monitors']:
        try:
            device = name_device[monitor_config['output']]
            monitor = device.monitor(monitor_config)
            topic_monitors.setdefault(monitor_config['topic'], list()).append(monitor)
        except KeyError as e:
            error("Problem with the config {!r}".format(monitor_config), e)

    subscribe()
    gc.collect()


def subscribe():
    global topic_monitors
    global connection
    for topic, monitor in topic_monitors.items():
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

            for name, device in name_device.items():
                device.tick()

            gc.collect()
            pause(100)
            no_connection_count = 0

        except (IndexError, OSError) as e:
            print("exception {!r} {}".format(e, no_connection_count))
            pause(1000)
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


def log(level, message, exception=None):
    global connection
    if connection is not None:
        bmessage = message
        if exception is not None:
            bmessage += ' '
            bmessage += str(exception)
#        bmessage += traceback.format_exc(limit=4, chain=True)
        connection.publish(b'status/' + CLIENT_ID + b'/' + bytes(level, 'utf-8'), bytes(bmessage, 'utf-8'))


def error(message, exception=None):
    log("ERROR", message, exception)


def warn(message, exception=None):
    log("WARN", message, exception)


if __name__ == '__main__':
    main()
