import paho.mqtt.client as mqtt
import yaml
import json
import socket


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc) + " " + str(flags) + " " + str(userdata) + " " + repr(client))
    client.subscribe("config/request/#")


def on_message(client, userdata, msg):
    print("Message {!r}".format(msg))
    client_id = msg.topic.split('/')[2]
    config = get_config(client_id)
    if config is not None:
        topic = 'config/reply/{}'.format(client_id)
        client.publish(topic, config)


def get_config(client_id):
    try:
        file = "../config/micro_{}.yml".format(client_id)
        with open(file) as f:
            obj = yaml.load(f)
            print("Serving config file {}".format(file))
        js = json.dumps(obj)
        return js
    except FileNotFoundError as err:
        print("No config file {}".format(err.filename))
        return None


def main(yaml_file="../config/board_config.yml"):
    try:
        with open(yaml_file) as fp:
            config = yaml.load(fp)
    except FileNotFoundError:
        config = dict()

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(config.get('mq', 'localhost'), config.get('mq_port', 1883), 60)

    udp_listen = config.get('broadcast_address', "0.0.0.0")
    udp_port = int(config.get('broadcast_port', '5005'))

    sock = socket.socket(socket.AF_INET,  # Internet
                         socket.SOCK_DGRAM)  # UDP
    sock.bind((udp_listen, udp_port))

    try:
        client.loop_start()
        while True:
            try:
                data, addr = sock.recvfrom(1024)  # buffer size is 1024 bytes
                config = get_config(str(data, 'utf-8'))
                if config is not None:
                    sock.sendto(bytes(config, 'utf-8'), (addr[0], udp_port))
            except socket.timeout:
                pass
    finally:
        client.loop_stop()
        client.disconnect()
        sock.close()


if __name__ == '__main__':
    main()
