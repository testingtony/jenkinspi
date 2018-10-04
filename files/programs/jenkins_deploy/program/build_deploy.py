import json
import time

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
        self._deployed_build_status = None
        self._first_id = None

    def on_build_message(self, message):
        # print("build_message {} {} {!r}".format(self, self._config['deploy'], message))
        self._build_status = json.loads(message)

    def on_deploy_message(self, message):
        # print("deploy_message {} {} {!r}".format(self, self._config['deploy'], message))
        self._deploy_status = json.loads(message)
        if float(self._build_status.get('timestamp', 3145219200)) < float(self._deploy_status.get('timestamp', 0)):
            self._deployed_build_status = self._build_status

    @property
    def topic(self):
        return self._config['publish']

    @property
    def status(self):
        #        print(self._build_status)
        if self._deployed_build_status is None:
            return None

        build = self._deployed_build_status
        deploy = self._deploy_status

        publish = dict()

        build_result = build['result']
        deploy_result = deploy['result']
        publish['result'] = deploy_result if results.get(build_result, 0) > results.get(deploy_result, 0) else build_result

        publish['building'] = build['building'] or deploy['building']

        timestamp = build.get('timestamp', 0)
        now = time.time()
        if now - timestamp > 24 * 60 * 60:
            build_id = ".".join(time.strftime("%H%M", time.localtime(timestamp))) + "."
        else:
            build_id = time.strftime("%H.%M", time.localtime(timestamp))

        publish['buildid'] = build_id
        publish['time'] = deploy['time']
        publish['timestamp'] = deploy['timestamp']
        publish['deploy_timestamp'] = deploy['timestamp']
        publish['build_timestamp'] = build['timestamp']

        return publish
