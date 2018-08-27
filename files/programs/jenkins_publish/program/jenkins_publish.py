import paho.mqtt.client as mqtt
import yaml
import json
import time
from jenkins_build import JenkinsBuild
from jenkins_deploy import JenkinsDeploy


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc) + " " + str(flags) + " " + str(userdata) + " " + repr(client))


def main(yaml_file="../config/jenkins_publish.yml"):
    with open(yaml_file) as fp:
        config = yaml.load(fp)

    auth = {'user': config['auth']['user'], 'token': config['auth']['token']}

    client = mqtt.Client()
    client.on_connect = on_connect

    client.connect(config['mq'], config.get('mq_port', 1883), 60)

    for job_config in config.get('build', []):
        job = JenkinsBuild(config['url'] + job_config['job'], auth)
        job_config['jenkins_monitor'] = job

    for job_config in config.get('deploy', []):
        job = JenkinsDeploy(config['url'] + job_config['job'], auth)
        job_config['jenkins_monitor'] = job

    try:
        client.loop_start()

        while True:
            for job_config in config['build'] + config['deploy']:
                status = job_config['jenkins_monitor'].status
                if status:
                    client.publish(job_config['topic'], json.dumps(status), qos=1, retain=True)

            time.sleep(config.get('pause', 30))

    finally:
        client.loop_stop()
        client.disconnect()


if __name__ == '__main__':
    main()
