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

from bidding.models import CallForTenders
from estfeed_adapter.process.request import EstfeedRequest
from flexibility_platform.process.fsp import FSP
from miscellaneous.misc import Miscellaneous
from prequalification.models import FlexibilityPotential
import xml.etree.ElementTree as ET


class GetCallForTendersEstfeed:

    @staticmethod
    def response(payload_xml, infos):

        # Get needed info from payload
        dictionnary = {}
        payload_xml = ET.fromstring(payload_xml.group(1))
        for child in payload_xml:
            if child.tag == "flexibility_service_provider":
                dictionnary["fsp_id"] = FSP.get_fsp_id_by_identification(child.text)
                dictionnary["fsp_identification"] = child.text
            if child.tag == "product_id":
                dictionnary["product_id"] = child.text

        cft_queryset = CallForTenders.objects.filter(product__id=dictionnary.get("product_id"))

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
        string_xml_payload = '<GetCallsForTenders xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" ' \
                             'xsi:noNamespaceSchemaLocation="GetCallsForTenders.v1.xsd">'
        for cft_object in cft_queryset:
            string_xml_payload += '<CallForTenders>'
            string_xml_payload += "<system_operator>{}</system_operator>".format(str(cft_object.system_operator.identification))
            string_xml_payload += "<product_id>{}</product_id>".format(str(cft_object.product.id))
            string_xml_payload += "<total_power_needed>{}</total_power_needed>".format(str(cft_object.total_power_needed))
            string_xml_payload += "<linking_of_bids>{}</linking_of_bids>".format(str(cft_object.linking_of_bids))
            string_xml_payload += "<localization_factor>{}</localization_factor>".format(str(cft_object.localization_factor))
            string_xml_payload += "<opening_date>{}</opening_date>".format(str(Miscellaneous.date_output_estfeed_format(cft_object.opening_date)))
            string_xml_payload += "<closing_date>{}</closing_date>".format(str(Miscellaneous.date_output_estfeed_format(cft_object.closing_date)))
            string_xml_payload += "<start_service_date>{}</start_service_date>".format(str(Miscellaneous.date_output_estfeed_format(cft_object.start_service_date)))
            string_xml_payload += "<end_service_date>{}</end_service_date>".format(str(Miscellaneous.date_output_estfeed_format(cft_object.end_service_date)))
            string_xml_payload += '</CallForTenders>'
        string_xml_payload += '</GetCallsForTenders>'

        string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

        final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                           string_xml_boundary_infos_middle + string_xml_payload + \
                           string_xml_boundary_infos_end

        response = [boundary, final_string_xml]

        return response
