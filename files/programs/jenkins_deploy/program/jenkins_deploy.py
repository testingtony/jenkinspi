import paho.mqtt.client as mqtt
import yaml
from build_deploy import BuildDeploy
import time
import json


def main(yaml_file="../config/jenkins_deploy.yml", client=mqtt.Client()):
    with open(yaml_file) as fp:
        config = yaml.load(fp)

    build_handlers = dict()
    deploy_handlers = dict()
    all_deployers = list()
    timeout = int(config.get('pause', '30'))

    def on_message(client, userdata, msg):
        message = str(msg.payload, 'utf-8')

        for handler in build_handlers.get(msg.topic, []):
            handler.on_build_message(message)
        for handler in deploy_handlers.get(msg.topic, []):
            handler.on_deploy_message(message)

    def on_connect(client, userdata, flags, rc):
        for job in config['jobs']:
            build_topic = job['build']
            deploy_topic = job['deploy']
            deployer = BuildDeploy(job)
            all_deployers.append(deployer)
            build_handlers.setdefault(build_topic, []).append(deployer)
            deploy_handlers.setdefault(deploy_topic, []).append(deployer)
            client.subscribe(build_topic)
            client.subscribe(deploy_topic)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config['mq'], config.get('mq_port', 1883), 60)

    try:
        client.loop_start()
        while True:
            for deployer in all_deployers:
                status = deployer.status
                if status is not None:
                    client.publish(deployer.topic, json.dumps(status), qos=1, retain=True)
            time.sleep(timeout)
    finally:
        client.loop_stop()


if __name__ == '__main__':
    main()
