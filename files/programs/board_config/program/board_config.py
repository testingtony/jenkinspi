import paho.mqtt.client as mqtt
import yaml
import json


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc) + " " + str(flags) + " " + str(userdata) + " " + repr(client))
    client.subscribe("config/request/#")


def on_message(client, userdata, msg):
    client_id = msg.topic.split('/')[2]
    try:
        with open("../config/micro_{}.yml".format(client_id)) as f:
            obj = yaml.load(f)
        js = json.dumps(obj)
        topic = 'config/reply/{}'.format(client_id)
        client.publish(topic, js)
        print("sending a config")
    except FileNotFoundError as err:
        print("No config file {}".format(err.filename))


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

    try:
        client.loop_forever()
    finally:
        client.disconnect()


if __name__ == '__main__':
    main()
