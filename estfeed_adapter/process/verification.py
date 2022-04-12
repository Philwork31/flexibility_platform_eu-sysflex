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

import re

from activation.models import FlexibilityActivationOrder
from verification.models import Verification
from estfeed_adapter.process.request import EstfeedRequest
from flexibility_platform.process.fsp import FSP
from miscellaneous.misc import Miscellaneous
import xml.etree.ElementTree as ET

class GetVerificationResults:

    @staticmethod
    def response(payload_xml, infos):

        # Get needed info from payload
        dictionnary = {}
        verification_result_list_id = []
        payload_xml = ET.fromstring(payload_xml.group(1))
        for child in payload_xml:
            if child.tag == "flexibility_service_provider":
                dictionnary["fsp_id"] = FSP.get_fsp_id_by_identification(child.text)
                dictionnary["fsp_identification"] = child.text
            if child.tag == "order_ids":
                for c in child:
                    verification_result_list_id.append(c.text)

        order_queryset = FlexibilityActivationOrder.objects.filter(id__in=verification_result_list_id)

        # generate random boundary key
        boundary = Miscellaneous.random_string(32)
        string_xml_boundary_infos_start = "--{}\n".format(boundary)
        string_xml_boundary_infos_start += "Content-Type: text/xml; charset=UTF-8\n\n\n"

        string_xml_metadata = '<estfeed:data xmlns:estfeed="http://estfeed.ee/xsd/estfeed-1.0.xsd">'
        string_xml_metadata += "<transactionId>{}</transactionId>".format(infos.get("transactionId"))
        string_xml_metadata += "<service>"
        string_xml_metadata += "<code>{}</code>".format(infos.get("code"))
        string_xml_metadata += "<version>{}</version>".format(infos.get("version"))
        string_xml_metadata += "<kind>{}</kind>".format(infos.get("kind"))
        string_xml_metadata += "</service>"
        string_xml_metadata += "</estfeed:data>"

        string_xml_boundary_infos_middle = "\n\n--{}\n".format(boundary)
        string_xml_boundary_infos_middle += "Content-Type: text/xml; charset=UTF-8\n\n\n"

        ### payload product list ###
        string_xml_payload = '<GetVerificationResults xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" ' \
                             'xsi:noNamespaceSchemaLocation="GetVerificationResults.v1.xsd">'
        string_xml_payload += '<flexibility_service_provider>{}</flexibility_service_provider>'.format(dictionnary.get("fsp_identification"))
        for order_object in order_queryset:
            string_xml_payload += '<Verification>'
            string_xml_payload += "<order_id>{}</order_id>".format(str(order_object.id))
            verif_queryset = Verification.objects.filter(flexibility_activation_order_id=order_object.id)
            if verif_queryset.exists():
                verif_object = verif_queryset.latest('id')
                verif_result_reg = re.search("Result : (.*)", verif_object.result)
                if verif_result_reg.group(1) == "0.0":
                    string_xml_payload += "<result>0</result>"
                elif float(verif_result_reg.group(1)) > 0:
                    string_xml_payload += "<result>+</result>"
                else:
                    string_xml_payload += "<result>-</result>"
            else:
                string_xml_payload += "<result></result>"
            string_xml_payload += '</Verification>'
        string_xml_payload += '</GetVerificationResults>'

        string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

        final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                           string_xml_boundary_infos_middle + string_xml_payload + \
                           string_xml_boundary_infos_end

        response = [boundary, final_string_xml]

        return response
