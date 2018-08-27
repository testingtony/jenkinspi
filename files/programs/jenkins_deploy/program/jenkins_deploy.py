import paho.mqtt.client as mqtt
import yaml
from build_deploy import BuildDeploy


def main(yaml_file="../config/jenkins_deploy.yml", client=mqtt.Client()):
    with open(yaml_file) as fp:
        config = yaml.load(fp)

    build_handlers = dict()
    deploy_handlers = dict()

    def on_message(client, userdata, msg):
        message = str(msg.payload, 'utf-8')
        for handler in build_handlers.get(msg.topic, []):
            handler.on_build_message(client, message)
        for handler in deploy_handlers.get(msg.topic, []):
            handler.on_deploy_message(client, message)

    def on_connect(client, userdata, flags, rc):
        for job in config['jobs']:
            build_topic = job['build']
            deploy_topic = job['deploy']
            handler = BuildDeploy(job)
            build_handlers.setdefault(build_topic, []).append(handler)
            deploy_handlers.setdefault(deploy_topic, []).append(handler)
            client.subscribe(build_topic)
            client.subscribe(deploy_topic)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config['mq'], config.get('mq_port', 1883), 60)

    client.loop_forever(retry_first_connection=False)


if __name__ == '__main__':
    main()
