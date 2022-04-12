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

from activation.data_management import Activation
from activation.models import FlexibilityActivationOrder
from estfeed_adapter.process.request import EstfeedRequest
from flexibility_platform.process.fsp import FSP
from miscellaneous.misc import Miscellaneous
import xml.etree.ElementTree as ET


class SendActivationOrderEstfeed:

    @staticmethod
    def request_estfeed(order_id):
        # generate random boundary key
        boundary = Miscellaneous.random_string(32)
        string_xml_boundary_infos_start = "--{}\n".format(boundary)
        string_xml_boundary_infos_start += "Content-Type: text/xml; charset=UTF-8\n\n\n"

        string_xml_metadata = '<estfeed:request xmlns:estfeed="http://estfeed.ee/xsd/estfeed-1.0.xsd">'
        string_xml_metadata += "<transactionId>fp-sao</transactionId>"
        string_xml_metadata += "<service>"
        string_xml_metadata += "<code>SendActivationOrder</code>"
        string_xml_metadata += "<version>v1</version>"
        string_xml_metadata += "<kind>SendActivationOrder.v1</kind>"
        string_xml_metadata += "</service>"
        string_xml_metadata += "</estfeed:request>"

        string_xml_boundary_infos_middle = "\n\n--{}\n".format(boundary)
        string_xml_boundary_infos_middle += "Content-Type: text/xml; charset=UTF-8\n\n\n"

        ao_object = FlexibilityActivationOrder.objects.get(id=order_id)

        string_xml_payload = '<ActivationOrder xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" ' \
                             'xsi:noNamespaceSchemaLocation="SendActivationOrder.v1.xsd">'
        string_xml_payload += '<flexibility_service_provider>{}</flexibility_service_provider>'.format(FSP.get_fsp_identification_by_id(ao_object.flexibility_service_provider))
        string_xml_payload += '<order_id>{}</order_id>'.format(order_id)
        string_xml_payload += '<product_id>{}</product_id>'.format(ao_object.product_id)
        string_xml_payload += '<quantity>{}</quantity>'.format(ao_object.quantity)
        string_xml_payload += '<localization_factor>{}</localization_factor>'.format(ao_object.localization_factor)
        string_xml_payload += '<start_of_delivery>{}</start_of_delivery>'.format(str(Miscellaneous.date_output_estfeed_format(ao_object.start_of_delivery)))
        string_xml_payload += '</ActivationOrder>'

        string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

        final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                           string_xml_boundary_infos_middle + string_xml_payload + \
                           string_xml_boundary_infos_end

        response = EstfeedRequest.send_request(boundary, final_string_xml)

        return response



    @staticmethod
    def data_activation_order_response_process(payload):
        dictionnary = {}
        if payload:

            payload_xml = ET.fromstring(payload.group(1))
            for child in payload_xml:
                if child.tag == "ActivationOrderConfirmation":
                    for childchild in child:
                        if childchild.tag == "flexibility_service_provider":
                            dictionnary["fsp_id"] = FSP.get_fsp_id_by_identification(childchild.text)
                        if childchild.tag == "order_id":
                            dictionnary["order_id"] = childchild.text
                        if childchild.tag == "confirmation":
                            dictionnary["confirmation"] = childchild.text
        
        Activation.flexibility_activation_confirmation_process(dictionnary.get("fsp_id"),
                                                               dictionnary.get("order_id"),
                                                               dictionnary.get("confirmation"))

