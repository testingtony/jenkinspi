Jenkins  Deploy
===============

Deploy job monitoring. Also needs to track the builds and reports that when the deploy occurs.

Each job publishes
* topic
* deploy date time
* status
* build_id


### Steps
1. subscribe to existing deploy topics and get the initial build ids
1. unsubscribe
1. subscribe to build topics
1. enter the main loop
   1. update ids from success build topics
   1. check for new deploys
   1. publish new releases



Config
------
Linking the deploy to the build

```yaml
---
url: 'https://jenkins.hostname/job/'
auth:
  user: user.name
  token: user.token
mq: localhost
pause: 10 # seconds between polling jenkins
jobs:
  - job: path/to/jenkins/job1
    build_topic: jenkins/job/topic1
    topic: jenkins/job/deploy1
  - job: path/to/jenkins/job2
    build_topic: jenkins/job/topic2
    topic: jenkins/job/deploy2
...

```

