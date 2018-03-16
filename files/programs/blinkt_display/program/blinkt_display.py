from blinkt import set_pixel, set_brightness, show, clear
import yaml
import json
import time
import paho.mqtt.client as mqtt
import signal


class Pixel:
    def __init__(self, colours, index=0):
        self._id = index
        self._brightness = 0
        self._colours = colours
        self.status = {'building': False, 'result': None}

    def show(self):
        if self.status.get('building', False) or self._brightness:
            self._brightness = (self._brightness + 1) % 19
        else:
            self._brightness = 0
        brightness = abs(10 - self._brightness)

        try:
            colour = self._colours[self.status['result']]
        except KeyError:
            colour = (0, 0, 0)

        set_pixel(self._id, *colour, brightness / 10)


pixels = dict()
loop = True


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc) + " " + str(flags) + " " + str(userdata) + " " + repr(client))
    for job in pixels.keys():
        client.subscribe(job)


def on_message(client, userdata, msg):
    try:
        pixel = pixels[msg.topic]
        pixel.status = json.loads(str(msg.payload, 'utf-8'))
    except KeyError:
        pass


def stop_now():
    global loop
    loop = False


def main(yaml_file="../config/blinkt_display.yml"):
    with open(yaml_file) as fp:
        config = yaml.load(fp)

    global pixels
    pixels = dict([(job, Pixel(config['colours'], index)) for index, job in enumerate(config['jobs'][::-1])])
    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config.get('mq', 'localhost'), config.get('mq_port', 1883), 60)

    signal.signal(signal.SIGTERM, stop_now)
    try:
        client.loop_start()

        while loop:
            for pixel in pixels.values():
                pixel.show()
            show()
            time.sleep(0.1)
    finally:
        clear()
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
