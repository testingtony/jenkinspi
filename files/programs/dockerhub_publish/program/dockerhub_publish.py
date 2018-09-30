import paho.mqtt.client as mqtt
import yaml
import json
import time
from dockerhub_build import DockerhubBuild


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc) + " " + str(flags) + " " + str(userdata) + " " + repr(client))


def main(yaml_file="../config/dockerhub_publish.example.yml"):
    with open(yaml_file) as fp:
        config = yaml.load(fp)

    DockerhubBuild.set_auth(config['auth']['username'], config['auth']['password'])

    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect(config['mq'], config.get('mq_port', 1883), 60)

    for job_config in config['dockerhub']:
        job = DockerhubBuild(job_config['repository'], job_config['tag'])
        job_config['dockerhub_monitor'] = job

    try:
        client.loop_start()

        while True:
            for job_config in config['dockerhub']:
                status = job_config['dockerhub_monitor'].status
                if status:
                    client.publish(job_config['topic'], json.dumps(status), qos=1, retain=True)
            time.sleep(config.get('pause', 30))

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
