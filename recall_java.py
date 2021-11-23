

import json
import requests
import sys

java_host_train = "http://172.17.231.59:30069/warnRecord/diagnosisCall"

diagnose_id = sys.argv[1]

header = {'Content-Type': 'application/json','Accept': 'application/json'}
message = {
    "id": diagnose_id
    }
requests.get(java_host_train, params = message,headers= header)
#requests.get(java_host_train, params = json.dumps(message),headers= header)