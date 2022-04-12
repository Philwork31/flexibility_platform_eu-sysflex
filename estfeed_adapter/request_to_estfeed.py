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

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from estfeed_adapter.process.request import EstfeedRequest
from miscellaneous.misc import Miscellaneous


def response_access_control_headers(content, status):
    response = HttpResponse(content, status=status, content_type="text/plain")
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "PORT, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response


@csrf_exempt
def test_send_activation_order(request):
    data_text = """--haVcUmJkSGCWyYLYoukNggGGKftWbnXc
Content-Type: text/xml; charset=UTF-8

<estfeed:request xmlns:estfeed="http://estfeed.ee/xsd/estfeed-1.0.xsd">
<transactionId>gp-fp</transactionId>
<service>
<code>SendActivationOrder</code>
<version>v1</version>
<kind>SendActivationOrder.v1</kind>
</service>
</estfeed:request>

--haVcUmJkSGCWyYLYoukNggGGKftWbnXc
Content-Type: text/xml; charset=UTF-8

<ActivationOrder xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="SendActivationOrder.v1.xsd">
<flexibility_service_provider>EnocoFSP</flexibility_service_provider>
<order_id>30</order_id>
<product_id>27</product_id>
<quantity>100.0</quantity>
<direction>+</direction>
<localization_factor>A</localization_factor>
<start_of_delivery>2020-12-01T18:00:00</start_of_delivery>
</ActivationOrder>

--haVcUmJkSGCWyYLYoukNggGGKftWbnXc--
"""
    boundary = Miscellaneous.random_string(32)
    req = EstfeedRequest.send_request_as_application(boundary, data_text)
    response = response_access_control_headers(req.content, req.status_code)

    return response
