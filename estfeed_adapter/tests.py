"""
Copyright 2021 AKKA Technologies (philippe.szczech@akka.eu)

Licensed under the EUPL, Version 1.2 or – as soon they will be approved by
the European Commission - subsequent versions of the EUPL (the "Licence");
You may not use this work except in compliance with the Licence.
You may obtain a copy of the Licence at:

https://joinup.ec.europa.eu/software/page/eupl

Unless required by applicable law or agreed to in writing, software
distributed under the Licence is distributed on an "AS IS" basis,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the Licence for the specific language governing permissions and
limitations under the Licence.
"""

import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from estfeed_adapter.globals import APPLICATION_URL
from estfeed_adapter.views import send_request_estfeed_no_data


def response_access_control_headers(content, status):
    response = HttpResponse(content, status=status, content_type="text/plain")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "PORT, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@csrf_exempt
def test_request_hour(request):
    infos = {"transactionId": "fp-req", "code": "GetUTCTimestamp", "version": "v1", "kind": "Timestamp.v1"}

    data = send_request_estfeed_no_data(infos)
    headers = {'content-type': 'multipart/related;boundary=' + data[1] + ';charset=UTF-8'}

    req = requests.post(APPLICATION_URL, data=data[0], headers=headers)
    response = response_access_control_headers(req.content, req.status_code)

    return response
