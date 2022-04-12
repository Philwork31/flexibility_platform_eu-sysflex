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

import isodate

from estfeed_adapter.process.request import EstfeedRequest
from flexibility_platform.models import Product
from miscellaneous.misc import Miscellaneous


class ProductEstfeed:

    @staticmethod
    def response(infos):
        product_queryset = Product.objects.all()

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
        string_xml_payload = '<GetProducts xmlns:xsi="http://www.w3.org/2001/XMLSchemainstance" ' \
                             'xsi:noNamespaceSchemaLocation="GetProducts.v1.xsd">'
        for product_object in product_queryset:
            string_xml_payload += '<Product>'
            string_xml_payload += "<id>{}</id>".format(str(product_object.id))
            string_xml_payload += "<eic_code>{}</eic_code>".format(str(product_object.eic_code))
            string_xml_payload += "<product_name>{}</product_name>".format(str(product_object.product_name))
            string_xml_payload += "<price_conditions>{}</price_conditions>".format(str(product_object.price_conditions))
            string_xml_payload += "<resolution>{}</resolution>".format(str(product_object.resolution))
            string_xml_payload += "<divisibility>{}</divisibility>".format(str(product_object.divisibility))
            string_xml_payload += "<direction>{}</direction>".format(str(product_object.direction))
            string_xml_payload += "<ramping_period>{}</ramping_period>".format(isodate.duration_isoformat(timedelta(product_object.ramping_period)))
            string_xml_payload += "<delivery_period>{}</delivery_period>".format(isodate.duration_isoformat(timedelta(product_object.delivery_period)))
            string_xml_payload += "<validity>{}</validity>".format(isodate.duration_isoformat(timedelta(product_object.validity)))
            string_xml_payload += "<pricing_method>{}</pricing_method>".format(str(product_object.pricing_method))
            string_xml_payload += "<gate_closure_time>{}</gate_closure_time>".format(isodate.duration_isoformat(timedelta(product_object.gate_closure_time)))
            string_xml_payload += '</Product>'

        string_xml_payload += '</GetProducts>'

        string_xml_boundary_infos_end = "\n\n--{}--\n".format(boundary)

        final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + \
                           string_xml_boundary_infos_middle + string_xml_payload + \
                           string_xml_boundary_infos_end

        response = [boundary, final_string_xml]

        return response
