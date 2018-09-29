import json

results = {
    'SUCCESS': 50,
    'UNSTABLE': 30,
    'ABORTED': 10,
    'FAILURE': 10
}


class BuildDeploy:
    def __init__(self, config):
        self._config = config
        self._build_status = None
        self._deploy_status = None
        self._first_id = None

    def on_build_message(self, client, message):
#        print("build_message {} {} {!r}".format(self, self._config['deploy'], message))
        self._build_status = json.loads(message)

    def on_deploy_message(self, client, message):
#        print("deploy_message {} {} {!r}".format(self, self._config['deploy'], message))
        self._deploy_status = json.loads(message)

#        print(self._build_status)
        if self._build_status is not None:
            build = self._build_status
            deploy = self._deploy_status

            publish = dict()

            build_result = build['result']
            deploy_result = deploy['result']
            publish['result'] = deploy_result if results[build_result] > results[deploy_result] else build_result

            publish['building'] = build['building'] or deploy['building']

            publish['buildid'] = build['buildid']
            publish['time'] = deploy['time']
            publish['timestamp'] = deploy['timestamp']

#            print("build {}, deploy {}".format( build['timestamp'], deploy['timestamp']))
            if build['timestamp'] < deploy['timestamp']:
                client.publish(self._config['publish'], json.dumps(publish), qos=1, retain=True)
