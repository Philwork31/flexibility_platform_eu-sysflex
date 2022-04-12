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

from miscellaneous.misc import Miscellaneous


class AcknowledgementEstfeed:

    @staticmethod
    def response(infos_metadata):
        """
         <estfeed:acknowledgement xmlns:estfeed=”http://estfeed.ee/xsd/estfeed-1.0.xsd”>
             <transactionId>...</transactionId>
             <service>
                 <code>...</code>
                 <version>...</version>
                 <kind>...</kind>
             </service>
             <responders>
                 <sourceId>...</sourceId>
             </responders>
         </estfeed:acknowledgement>
        """
        # generate random boundary key
        boundary = Miscellaneous.random_string(32)

        string_xml_boundary_infos_start = "--{}\n".format(boundary)
        string_xml_boundary_infos_start += "Content-Type: text/xml; charset=UTF-8\n\n\n"

        string_xml_metadata = '<estfeed:acknowledgement xmlns:estfeed="http://estfeed.ee/xsd/estfeed-1.0.xsd">'
        string_xml_metadata += "<transactionId>{}</transactionId>".format(infos_metadata.get("transactionId"))
        string_xml_metadata += "<service>"
        string_xml_metadata += "<code>{}</code>".format(infos_metadata.get("code"))
        string_xml_metadata += "<version>{}</version>".format(infos_metadata.get("version"))
        string_xml_metadata += "<kind>{}</kind>".format(infos_metadata.get("kind"))
        string_xml_metadata += "</service>"
        string_xml_metadata += "</estfeed:acknowledgement>"

        string_xml_boundary_infos_end = "\n\n--{}--".format(boundary)

        final_string_xml = string_xml_boundary_infos_start + string_xml_metadata + string_xml_boundary_infos_end

        response = [boundary, final_string_xml]

        return response
