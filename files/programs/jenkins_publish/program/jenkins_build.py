import requests
import json
import time


class JenkinsBuild:
    def __init__(self, url, auth):
        self.url = url
        self.auth = (auth['user'], auth['token'])
        self.last_run_id = 0
        self.last_result = 'ABORTED'

    @property
    def status(self):
        url = self.url + "/lastBuild/api/json?tree=id,building,result,changeSets[items[commitId]],timestamp"
        try:
            request = requests.get(url, auth=self.auth)

            if request.status_code == 200:
                data = json.loads(request.text)

                # still show a build if the run_id has changed, useful for deploys which are very quick
                run_id = data.get('id', self.last_run_id)
                building = run_id != self.last_run_id or data.get('building', False)
                self.last_run_id = run_id

                result = data.get('result', 'ABORTED')
                if not result:
                    result = self.last_result

                self.last_result = result

                timestamp = data.get('timestamp', 0)/1000
                now = time.time()
                fmtime = time.strftime("%Y/%m/%d %H:%M:%d", time.localtime(timestamp))
                if now - timestamp > 24 * 60 * 60:
                    build_id = ".".join(time.strftime("%H%M", time.localtime(timestamp))) + "."
                else:
                    build_id = time.strftime("%H.%M", time.localtime(timestamp))

                return {'building': building, 'result': result, 'buildid': build_id, 'time': fmtime, 'timestamp': timestamp}
            else:
                print("Status code {} message {}".format(request.status_code, request.text))
        except BaseException as err:
            print("Got an error " + str(err))
            print("URL is {}".format(url))
            return None
