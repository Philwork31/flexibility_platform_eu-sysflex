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
import xml.etree.ElementTree as ET

from verification.process.schedule import ScheduleProcess


class SubmitSchedule:

    @staticmethod
    def data_schedule_process(payload):
        energy = None
        array_date = None
        array_hour = None
        dictionnary = {}
        if payload:

            payload_xml = ET.fromstring(payload.group(1))
            for child in payload_xml:
                if child.tag == "flexibility_service_provider":
                    dictionnary["flexibility_service_provider_id"] = FSP.get_fsp_id_by_identification(child.text)
                if child.tag == "product_id":
                    dictionnary["product_id"] = child.text
                if child.tag == "metering_point_id":
                    dictionnary["metering_point_id"] = child.text
                if child.tag == "energy":
                    energy = [child.text]
                if child.tag == "direction":
                    dictionnary["direction"] = child.text
                if child.tag == "start_of_delivery":
                    split_date_hour = child.text.split("T")
                    array_date = [split_date_hour[0]]
                    array_hour = [split_date_hour[1]]

            queryset_and_message = ScheduleProcess.process(dictionnary, array_date, array_hour, energy)

        return queryset_and_message

    @staticmethod
    def response(queryset, message, payload, infos):
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

        # Get potential FSP
        payload_xml = ET.fromstring(payload.group(1))
        for child in payload_xml:
            if child.tag == "flexibility_service_provider":
                flexibility_service_provider = FSP.get_fsp_id_by_identification(child.text)

        string_xml_payload = '<SubmitSchedule xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" ' \
                             'xsi:noNamespaceSchemaLocation="SubmitSchedule.v1.xsd">'
        string_xml_payload += '<flexibility_service_provider>{}</flexibility_service_provider>'.format(flexibility_service_provider)
        if queryset:
            string_xml_payload += '<status>success</status>'
        else:
            string_xml_payload += '<status>failure</status>'
        string_xml_payload += '<message>{}</message>'.format(message)
        string_xml_payload += '</SubmitSchedule>'

        string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

        final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                           string_xml_boundary_infos_middle + string_xml_payload + \
                           string_xml_boundary_infos_end

        response = [boundary, final_string_xml]

        return response
