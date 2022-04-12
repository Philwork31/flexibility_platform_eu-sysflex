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

from estfeed_adapter.process.request import EstfeedRequest
from flexibility_platform.process.fsp import FSP
from miscellaneous.misc import Miscellaneous
from prequalification.models import FlexibilityPotential
import xml.etree.ElementTree as ET


class PotentialPreqStatusEstfeed:

    @staticmethod
    def response(payload_xml, infos):

        # Get needed info from payload
        dictionnary = {}
        payload_xml = ET.fromstring(payload_xml.group(1))
        for child in payload_xml:
            if child.tag == "flexibility_service_provider":
                dictionnary["fsp_id"] = FSP.get_fsp_id_by_identification(child.text)
                dictionnary["fsp_identification"] = child.text
            if child.tag == "potential_id":
                dictionnary["potential_id"] = child.text

        potential_object = FlexibilityPotential.objects.filter(id=dictionnary.get("potential_id")).latest('id')

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
        string_xml_payload = '<GetPotentialPrequalificationStatus xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" ' \
                             'xsi:noNamespaceSchemaLocation="GetPotentialPrequalificationStatus.v1.xsd">'
        string_xml_payload += '<flexibility_service_provider>{}</flexibility_service_provider>'.format(dictionnary.get("fsp_identification"))
        string_xml_payload += "<potential_id>{}</potential_id>".format(dictionnary.get("potential_id"))
        if potential_object.is_prequalified:
            string_xml_payload += "<status>Prequalified</status>"
        else:
            string_xml_payload += "<status>Not prequalified</status>"

        string_xml_payload += '</GetPotentialPrequalificationStatus>'

        string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

        final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                           string_xml_boundary_infos_middle + string_xml_payload + \
                           string_xml_boundary_infos_end

        response = [boundary, final_string_xml]

        return response

