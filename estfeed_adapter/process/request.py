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

from estfeed_adapter.globals import DATA_SOURCE_URL, APPLICATION_URL


class EstfeedRequest:

    @staticmethod
    def response_access_control_headers(content, boundary):
        response = HttpResponse(content, content_type='multipart/relate')
        response["boundary"] = boundary
        return response

    @staticmethod
    def send_request_as_datasource(boundary, string_xml):
        headers = {'content-type': 'multipart/related;boundary=' + boundary + ';charset=UTF-8'}
        req = requests.post(DATA_SOURCE_URL, data=string_xml, headers=headers)
        return req.content

    @staticmethod
    def send_request_as_application(boundary, string_xml):
        headers = {'content-type': 'multipart/related;boundary=' + boundary + ';charset=UTF-8'}
        req = requests.post(APPLICATION_URL, data=string_xml, headers=headers)
        return req
