import json
import time
import datetime
from dateutil.parser import parse
import requests


class DockerhubBuild:
    _payload = None
    _token = None
    base_url = "https://hub.docker.com/v2"

    @classmethod
    def set_auth(cls, username, password):
        cls._payload = {'username': username, 'password': password}

    @classmethod
    def token(cls):
        now = datetime.datetime.now().timestamp()
        if cls._token is not None and now - cls._token['date'] < 30 * 60:
            return cls._token['token']
        cls._token = {"date": now}

        headers = {
            'Content-Type': "application/json",
            'Cache-Control': "no-cache"}
        response = requests.request("POST", cls.base_url + "/users/login/", json=cls._payload, headers=headers)

        if response.status_code != 200:
            raise IOError("could not get a new token")

        body = json.loads(response.text, encoding='utf-8')
        cls._token['token'] = body['token']
        return body['token']

    def __init__(self, repository, tag):
        self.repository = repository
        self.tag = tag
        self.last_run_id = 0
        self.last_result = 'ABORTED'
        self._status = None
        self._building = False
        self._timestamp = None

    @property
    def status(self):
        headers = {
            'Authorization': 'Bearer {}'.format(DockerhubBuild.token()),
            'Content-Type': "application/json",
            'Cache-Control': "no-cache"}

        url = DockerhubBuild.base_url + "/repositories/{}/buildhistory?page_size=10&page=1".format(self.repository)

        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            raise IOError("Could not get repository")

        data = json.loads(response.text, encoding='utf-8')

        first_result = True
        for result in data['results']:
            if result['dockertag_name'] == self.tag:
                status = result['status']
                if first_result:
                    self._building = False
                    if status == 10:
                        self._status = "SUCCESS"
                    elif status == -1:
                        self._status = "FAILURE"
                    elif status == -4:
                        self._status = "ABORTED"
                    else:
                        self._building = True
                    first_result = False

                if status == 10:
                    self._timestamp = parse(result['created_date']).timestamp()
                    break

        now = time.time()
        fmtime = time.strftime("%Y/%m/%d %H:%M:%d", time.localtime())
        if now - self._timestamp > 24 * 60 * 60:
            build_id = ".".join(time.strftime("%H%M", time.localtime(self._timestamp))) + "."
        else:
            build_id = time.strftime("%H.%M", time.localtime(self._timestamp))

        return {"buildid": build_id, "result": self._status, "building": self._building,
                "timestamp": self._timestamp, "time":fmtime}
