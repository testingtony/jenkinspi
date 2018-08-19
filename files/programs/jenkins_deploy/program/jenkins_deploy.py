import paho.mqtt.client as mqtt
import yaml
import json
import time
from jenkins_build import JenkinsBuild
from copy import deepcopy


def main(yaml_file="../config/jenkins_deploy.yml", client=mqtt.Client(), status_class=JenkinsBuild):
    with open(yaml_file) as fp:
        config = yaml.load(fp)

    auth = {'user': config['auth']['user'], 'token': config['auth']['token']}

    for job_config in config['jobs']:
        job = status_class(config['url'] + job_config['job'], auth)
        job_config['jenkins_monitor'] = job
        job_config['build_status'] = None
        job_config['deploy_status'] = None

    def on_message(client, userdata, msg):
        for job_config in config['jobs']:
            if job_config['build_topic'] == msg.topic:
                job_config['build_status'] = str(msg.payload, 'utf-8')

    def on_connect(client, userdata, flags, rc):
        print("Connected with result code " + str(rc) + " " + str(flags) + " " + str(userdata) + " " + repr(client))
        for job_config in config['jobs']:
            client.subscribe(job_config['build_topic'])

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(config['mq'], config.get('mq_port', 1883), 60)

    try:
        client.loop_start()
        while True:
            for job_config in config['jobs']:
                new_status = job_config['jenkins_monitor'].status
                old_status = job_config['deploy_status']
                build_status = job_config['build_status']
                if new_status != old_status:
                    job_config['deploy_status'] = new_status
                    if old_status is not None:
                        message = deepcopy(new_status)
                        message['build_status'] = dict() if build_status is None else json.loads(build_status)
                        client.publish(job_config['topic'], json.dumps(message), qos=1, retain=True)
            time.sleep(config.get('pause', 30))
    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
