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

from datetime import timedelta

import saxonc

from bidding.models import FlexibilityBid
from bidding.process.bid import BidProcess
from estfeed_adapter.process.error import EstfeedError
from estfeed_adapter.process.request import EstfeedRequest
from flexibility_platform.models import DeliveryPeriod
from flexibility_platform.process.fsp import FSP
from miscellaneous.misc import Miscellaneous
import xml.etree.ElementTree as ET
import isodate
import distutils.util


class SubmitBid:

    @staticmethod
    def data_flexibility_bid_process(payload):
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
                if child.tag == "price":
                    dictionnary["price"] = child.text
                if child.tag == "power":
                    dictionnary["power"] = child.text
                if child.tag == "direction":
                    dictionnary["direction"] = child.text
                if child.tag == "linking_of_bids":
                    dictionnary["linking_of_bids"] = bool(distutils.util.strtobool(child.text))
                if child.tag == "localization_factor":
                    dictionnary["localization_factor"] = child.text
                if child.tag == "localization_factor":
                    dictionnary["localization_factor"] = child.text
                if child.tag == "start_of_delivery":
                    dictionnary["start_of_delivery"] = child.text
                dictionnary["fuseau"] = 0
                dp = DeliveryPeriod.objects.all().latest("id")
                dictionnary["interval_duration"] = dp.duration
                dictionnary["gct"] = dp.gct

            queryset_and_message = BidProcess.bid_process(dictionnary, dictionnary.get("flexibility_service_provider_id"),
                                                          dictionnary.get("product_id"))
        return queryset_and_message

    @staticmethod
    def cim_data_flexibility_bid_process(payload):
        dictionnary = {}
        if payload:

            ### SAXONC PROCESS
            SAXONC_PROC = saxonc.PySaxonProcessor(license=False)
            xml_bid = SAXONC_PROC.parse_xml(xml_text=payload.group(1))
            #  xslt30_processor = TEST_SAXONC.new_xslt30_processor()
            xslt30_processor = SAXONC_PROC.new_xslt30_processor()
            xslt30_processor.set_cwd(".")
            result_saxonc = xslt30_processor.transform_to_string(xdm_node=xml_bid,
                                                          stylesheet_file="FlexibilityBid CIM2Sys.xslt")
            ###

            print("RESULT SAXONC")
            print(result_saxonc)

            payload_xml = ET.fromstring(result_saxonc)

            for child in payload_xml:
                if child.tag == "flexibility_service_provider":
                    dictionnary["flexibility_service_provider_id"] = FSP.get_fsp_id_by_identification(child.text)
                if child.tag == "product_id":
                    dictionnary["product_id"] = child.text
                if child.tag == "metering_point_id":
                    dictionnary["metering_point_id"] = child.text
                if child.tag == "price":
                    dictionnary["price"] = child.text
                if child.tag == "power":
                    dictionnary["power"] = child.text
                if child.tag == "direction":
                    dictionnary["direction"] = child.text
                if child.tag == "linking_of_bids":
                    dictionnary["linking_of_bids"] = bool(distutils.util.strtobool(child.text))
                if child.tag == "localization_factor":
                    dictionnary["localization_factor"] = child.text
                if child.tag == "localization_factor":
                    dictionnary["localization_factor"] = child.text
                if child.tag == "start_of_delivery":
                    dictionnary["start_of_delivery"] = child.text
                dictionnary["fuseau"] = 0
                dp = DeliveryPeriod.objects.all().latest("id")
                dictionnary["interval_duration"] = dp.duration
                dictionnary["gct"] = dp.gct

            queryset_and_message = BidProcess.bid_process(dictionnary, dictionnary.get("flexibility_service_provider_id"),
                                                          dictionnary.get("product_id"))
            print(queryset_and_message)
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
        string_xml_payload = '<SubmitFlexibilityBid xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" ' \
                              'xsi:noNamespaceSchemaLocation="CIMFlexibilityBid.v1.xsd">'
        if queryset:
            string_xml_payload += '<flexibility_service_provider>{}</flexibility_service_provider>'.format(FSP.get_fsp_identification_by_id(queryset.flexibility_service_provider_id))
            string_xml_payload += '<status>success</status>'
            string_xml_payload += '<bid_id>{}</bid_id>'.format(queryset.id)
        else:
            string_xml_payload += '<status>failure</status>'
        string_xml_payload += '<message>{}</message>'.format(message)
        string_xml_payload += '</SubmitFlexibilityBid>'

        string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

        final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                           string_xml_boundary_infos_middle + string_xml_payload + \
                           string_xml_boundary_infos_end

        response = [boundary, final_string_xml]

        return response


class GetFlexibilityBids:

    @staticmethod
    def response(payload_xml, infos):

        try:
            # Get needed info from payload
            dictionnary = {}
            payload_xml = ET.fromstring(payload_xml.group(1))
            for child in payload_xml:
                if child.tag == "flexibility_service_provider":
                    dictionnary["fsp_id"] = FSP.get_fsp_id_by_identification(child.text)
                    dictionnary["fsp_identification"] = child.text
                if child.tag == "product_id":
                    dictionnary["product_id"] = child.text
                if child.tag == "start_of_delivery":
                    dictionnary["start_of_delivery"] = child.text.replace("T", " ")

            # Datetime format
            date_start_delivery_period = Miscellaneous.format_date_with_seconds(dictionnary.get('start_of_delivery'))
            date_start_delivery_period_minus_one = date_start_delivery_period - timedelta(minutes=1)
            date_start_delivery_period_plus_one = date_start_delivery_period + timedelta(minutes=1)

            bid_queryset = FlexibilityBid.objects.filter(product_id=dictionnary.get("product_id"),
                                                         flexibility_service_provider_id=dictionnary.get("fsp_id"),
                                                         start_of_delivery__range=(date_start_delivery_period_minus_one,
                                                                                   date_start_delivery_period_plus_one))

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
            string_xml_payload = '<GetFlexibilityBids xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" ' \
                                 'xsi:noNamespaceSchemaLocation="GetFlexibilityBids.v1.xsd">'
            for bid_object in bid_queryset:
                string_xml_payload += '<FlexibilityBid>'
                string_xml_payload += "<flexibility_service_provider>{}</flexibility_service_provider>".format(str(dictionnary.get("fsp_identification")))
                string_xml_payload += "<product_id>{}</product_id>".format(str(bid_object.product_id))
                string_xml_payload += "<metering_point_id>{}</metering_point_id>".format(str(bid_object.metering_point_id))
                string_xml_payload += "<price>{}</price>".format(str(bid_object.price))
                string_xml_payload += "<linkings_of_bids>{}</linkings_of_bids>".format(str(bid_object.linking_of_bids))
                string_xml_payload += "<localization_factor>{}</localization_factor>".format(str(bid_object.localization_factor))
                string_xml_payload += "<start_of_delivery>{}</start_of_delivery>".format(str(Miscellaneous.date_output_estfeed_format(bid_object.start_of_delivery)))
                string_xml_payload += '</FlexibilityBid>'

            string_xml_payload += '</GetFlexibilityBids>'

            string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

            final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                               string_xml_boundary_infos_middle + string_xml_payload + \
                               string_xml_boundary_infos_end

            response = [boundary, final_string_xml]

        except Exception as e:
            print("exception time !")
            print(e)

            boundary = Miscellaneous.random_string(32)
            string_xml_boundary_infos_start = "--{}\n".format(boundary)
            string_xml_boundary_infos_start += "Content-Type: text/xml; charset=UTF-8\n\n\n"

            string_xml_metadata = '<estfeed:error xmlns:estfeed="http://estfeed.ee/xsd/estfeed-1.0.xsd">'
            string_xml_metadata += "<message>{}</message>".format(str(e))
            string_xml_metadata += "</estfeed:error>"

            string_xml_boundary_infos_end = "\n\n--{}--\n".format(boundary)
            
            response = string_xml_boundary_infos_start + string_xml_metadata + string_xml_boundary_infos_end


        return response
