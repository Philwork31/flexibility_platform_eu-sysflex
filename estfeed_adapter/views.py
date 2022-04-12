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

import xml.etree.ElementTree as ET
import re

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from miscellaneous.misc import Miscellaneous
from .process.acknowledgement import AcknowledgementEstfeed
from .process.activationorder import SendActivationOrderEstfeed
from .process.bid import SubmitBid, GetFlexibilityBids
from .process.callfortenders import GetCallForTendersEstfeed
from .process.potential import PotentialEstfeed
from .process.potentialpreqstatus import PotentialPreqStatusEstfeed
from .process.product import ProductEstfeed
from .process.request import EstfeedRequest
from .process.schedule import SubmitSchedule
from .process.verification import GetVerificationResults


class EstfeedResponse(HttpResponse):
    def __init__(self, data, then_callback):
        # acknowledgement sending (contained in data[1]) with adapted boundary (data[0])
        super().__init__(data[1], content_type="multipart/related;boundary=" + data[0] + "; charset=utf-8")
        self.then_callback = then_callback

    def close(self, ):
        # callback sending (contained in self.then_callback[1]) with boundary (self.then_callback[0])
        super().close()
        EstfeedRequest.send_request_as_datasource(self.then_callback[0], self.then_callback[1])


def format_message_no_data(infos, boundary):
    string_xml_boundary_infos_start = "--{}\n".format(boundary)
    string_xml_boundary_infos_start += "Content-Type: text/xml; charset=UTF-8\n\n\n"

    string_xml_metadata = '<estfeed:request xmlns:estfeed="http://estfeed.ee/xsd/estfeed-1.0.xsd">'
    string_xml_metadata += "<transactionId>{}</transactionId>".format(infos.get("transactionId"))
    string_xml_metadata += "<service>"
    string_xml_metadata += "<code>{}</code>".format(infos.get("code"))
    string_xml_metadata += "<version>{}</version>".format(infos.get("version"))
    string_xml_metadata += "<kind>{}</kind>".format(infos.get("kind"))
    string_xml_metadata += "</service>"
    string_xml_metadata += "</estfeed:request>"

    string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

    final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                       string_xml_boundary_infos_end

    return final_string_xml


def send_request_estfeed_no_data(infos):
    # generate random boundary key
    boundary = Miscellaneous.random_string(32)

    # format message
    format_message = format_message_no_data(infos, boundary)

    return [format_message, boundary]


@csrf_exempt
def get_estfeed_request(request):

    estfeed_request = request.body.decode("utf-8")

    # We get boundary here.
    data_r_boundary = re.search("--(.*)--", estfeed_request)
    boundary = data_r_boundary.group(1)

    # Request type
    request_type = re.search("<estfeed:(.*) [\\s\\S]*<\\/estfeed:(.*)>", estfeed_request).group(1)

    # We get "code" from Estfeed XML here.
    data_r_metadata = re.search("<estfeed[\\s\\S]*<\\/estfeed:(.*)>", estfeed_request)
    root = ET.fromstring(data_r_metadata.group(0))
    transaction_id_metadata = root[0].text
    code_metadata = root[1][0].text
    version_metadata = root[1][1].text
    kind_metadata = root[1][2].text

    infos_metadata = {"transactionId": transaction_id_metadata, "code": code_metadata,
                      "version": version_metadata, "kind": kind_metadata}

    # We check if there is a payload here (.format() doesn't work here)
    data_r_payload = re.search("<estfeed[\\s\\S]*<\/estfeed:.*>[\\s\\S]*?(<[\\s\\S]*>)", estfeed_request)

    # List service
    if code_metadata == "SubmitFlexibilityPotential":
        queryset_and_message = PotentialEstfeed.data_flexibility_potential_process(data_r_payload)
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = PotentialEstfeed.response(queryset_and_message[0], queryset_and_message[1], data_r_payload, infos_metadata)
    if code_metadata == "GetProducts":
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = ProductEstfeed.response(infos_metadata)
    if code_metadata == "GetPotentialPrequalificationStatus":
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = PotentialPreqStatusEstfeed.response(data_r_payload, infos_metadata)
    if code_metadata == "GetCallsForTenders":
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = GetCallForTendersEstfeed.response(data_r_payload, infos_metadata)
    if code_metadata == "SubmitFlexibilityBid":
        queryset_and_message = SubmitBid.data_flexibility_bid_process(data_r_payload)
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = SubmitBid.response(queryset_and_message[0], queryset_and_message[1], data_r_payload, infos_metadata)
    if code_metadata == "CIMSubmitFlexibilityBid":
        queryset_and_message = SubmitBid.cim_data_flexibility_bid_process(data_r_payload)
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = SubmitBid.response(queryset_and_message[0], queryset_and_message[1], data_r_payload, infos_metadata)
    if code_metadata == "GetFlexibilityBids":
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = GetFlexibilityBids.response(data_r_payload, infos_metadata)
    if code_metadata == "SendActivationOrder":
        response = AcknowledgementEstfeed.response(infos_metadata)
        SendActivationOrderEstfeed.data_activation_order_response_process(data_r_payload)
        return HttpResponse(response[1], content_type="multipart/related;boundary=" + response[0] + "; charset=utf-8")
    if code_metadata == "GetVerificationResults":
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = GetVerificationResults.response(data_r_payload, infos_metadata)
    if code_metadata == "SubmitSchedule":
        queryset_and_message = SubmitSchedule.data_schedule_process(data_r_payload)
        response = AcknowledgementEstfeed.response(infos_metadata)
        callback = SubmitSchedule.response(queryset_and_message[0], queryset_and_message[1], data_r_payload, infos_metadata)

    return EstfeedResponse(response, callback)
