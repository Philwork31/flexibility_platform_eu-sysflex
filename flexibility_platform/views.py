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

from datetime import datetime
from itertools import chain
from time import strftime, gmtime

from rest_framework import viewsets, generics
from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import render

from activation.models import FlexibilityActivationRequest
from bidding.models import CallForTenders, FlexibilityBid
from grid_impact.data_management import GridImpact
from miscellaneous.misc import Miscellaneous
from prequalification.models import FlexibilityPotential, FlexibilityNeed
from .serializers import *
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.generics import RetrieveAPIView
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from event_recorder.models import EventRecorder
from . import consumers
import logging
import lxml.etree
import saxonc
from lxml import etree

logger = logging.getLogger('flexibility_platform')

'''These viewsets automatically provide `list`, `create`, `retrieve`, `update`
and `destroy` actions for the corresponding model.

    Example for FlexibilityNeed ("needs" here is defined when the route is
    registered at url.py)
        list – list all elements, serves GET to /needs/
        create – create a new element, serves POST to /needs/
        retrieve – retrieves one element, serves GET to /needs/<id>
        update – updates single element, handles PUT/PATCH to /needs/<id>
        destroy – deletes single element, handles DELETE to /needs/<id>
    '''


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening


class FlexibilityServiceProviderViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = FlexibilityServiceProvider.objects.all()
    serializer_class = FlexibilityServiceProviderSerializer


class SystemOperatorViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = SystemOperator.objects.all()
    serializer_class = SystemOperatorSerializer


class SecondarySystemOperatorViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = SecondarySystemOperator.objects.all()
    serializer_class = SecondarySystemOperatorSerializer


class AggregatorInformationViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = AggregatorInformation.objects.all()
    serializer_class = AggregatorInformationSerializer


class ProductViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = Product.objects.filter(validated_by_fpo=True)
    serializer_class = ProductSerializer


class ProductBySoListApi(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        so_name = self.kwargs['so_name']
        queryset = Product.objects.filter(system_operator__identification=so_name).order_by('-id')
        return queryset


class ProductNotValidatedViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = Product.objects.filter(validated_by_fpo=False)
    serializer_class = ProductSerializer


class ProductWithNeedViewSet(viewsets.ModelViewSet):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = Product.objects.filter(needproduct__isnull=False, validated_by_fpo=True).distinct()
    serializer_class = ProductSerializer


class CurrentDeliveryPeriodViewSet(RetrieveAPIView):
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    queryset = DeliveryPeriod.objects.all()
    serializer_class = DeliveryPeriodSerializer

    def get_object(self):
        dp = self.queryset.filter(status__in=["started", "gct"])
        if dp.exists():
            last_dp = dp.latest('starting_date')
        else:
            return self.queryset.all().latest('starting_date')
        return last_dp


@csrf_exempt
def product_register(request):
    try:
        new_product = request.POST

        product_to_create = Product(**new_product.dict())
        product_to_create.save()

        consumers.SocketConsumer.notification_trigger("New product registered : {} (made by : FPO)".
                                                      format(new_product['product_name']))
        event_to_record = EventRecorder(text="New product registered : %1 (made by : FPO)".
                                        format(new_product['product_name']),
                                        business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                             '"{}"}}]'.
                                        format(product_to_create.id, new_product['product_name']),
                                        types="product")
        event_to_record.save()
        return HttpResponse('')
    except Exception as e:
        return HttpResponse(e, status=500)


@csrf_exempt
def product_propose(request):
    try:
        new_product = request.POST

        if new_product['divisibility'] == "no":
            divisibility = False
        else:
            divisibility = True

        so = SystemOperator.objects.get(identification=new_product['system_operator'])
        product_to_create = Product(system_operator_id=so.id,
                                    product_name=new_product['product_name'],
                                    eic_code=new_product['eic_code'],
                                    price_conditions=new_product['price_conditions'],
                                    resolution=new_product['resolution'],
                                    divisibility=divisibility,
                                    direction=new_product['direction'],
                                    ramping_period=new_product['ramping_period'],
                                    delivery_period=new_product['delivery_period'],
                                    validity=new_product['validity'],
                                    pricing_method=new_product['pricing_method'],
                                    gate_closure_time=new_product['gate_closure_time'])
        product_to_create.save()

        consumers.SocketConsumer.notification_trigger("New product proposed : {} (made by : {})".
                                                      format(new_product['product_name'],
                                                             new_product['system_operator']))
        event_to_record = EventRecorder(text="New product proposed : %1 (made by : %2)".
                                        format(new_product['product_name'], new_product['system_operator']),
                                        business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 2, "type": "so", "id": "{}", "text": '
                                                             '"{}"}}]'.
                                        format(product_to_create.id, new_product['product_name'],
                                               so.id, new_product['system_operator']),
                                        types="product")
        event_to_record.save()

        return HttpResponse('')
    except Exception as e:
        return HttpResponse(e, status=500)


@csrf_exempt
def product_update(request):
    try:

        new_product = request.POST

        check_potential_queryset = FlexibilityPotential.objects.filter(product_id=new_product['product'])
        check_need_queryset = FlexibilityNeed.objects.filter(product_id=new_product['product'])
        check_cft_queryset = CallForTenders.objects.filter(product_id=new_product['product'])

        if check_potential_queryset.exists() or check_need_queryset.exists() or check_cft_queryset.exists():
            return HttpResponse('Product cannot be updated : it\'s used in a process.')

        if new_product['divisibility'] == "no":
            divisibility = False
        else:
            divisibility = True


        product_to_update = Product.objects.get(id=new_product['product'])
        product_to_update.eic_code = new_product['eic_code']
        product_to_update.price_conditions = new_product['price_conditions']
        product_to_update.resolution = new_product['resolution']
        product_to_update.divisibility = divisibility
        product_to_update.direction = new_product['direction']
        product_to_update.ramping_period = new_product['ramping_period']
        product_to_update.delivery_period = new_product['delivery_period']
        product_to_update.validity = new_product['validity']
        product_to_update.pricing_method = new_product['pricing_method']
        product_to_update.gate_closure_time = new_product['gate_closure_time']
        product_to_update.save()
        so = SystemOperator.objects.get(id=product_to_update.system_operator.id)

        consumers.SocketConsumer.notification_trigger("New product updated : {} (made by : {})".
                                                      format(product_to_update.product_name,
                                                             so.identification))
        event_to_record = EventRecorder(text="New product updated : %1 (made by : %2)",
                                        business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 2, "type": "so", "id": "{}", "text": '
                                                             '"{}"}}]'.
                                        format(product_to_update.id, product_to_update.product_name,
                                               so.id, so.identification),
                                        types="product")
        event_to_record.save()

        return HttpResponse('Product updated with success.')
    except Exception as e:
        return HttpResponse(e, status=500)


@csrf_exempt
def product_validate(request, product_id):
    try:
        Product.objects.filter(id=product_id).update(validated_by_fpo=True)
        message = "Product validated with success."
    except Exception as e:
        message = "Error while trying to validate this product : {}".format(e)
    return HttpResponse(message)


@csrf_exempt
def product_cancel(request, product_id):
    selected_product = Product.objects.filter(id=product_id)
    check_product_owner_queryset = selected_product.filter(system_operator__identification=request.POST.get("system_operator_id"))
    if not check_product_owner_queryset.exists():
        return HttpResponse("You cannot cancel product which you did not create.")
    queryset_active_cft = selected_product.filter(callfortendersproduct__status="open",
                                                  callfortendersproduct__start_service_date__lte=datetime.now(),
                                                  callfortendersproduct__end_service_date__gte=datetime.now(),
                                                  validated_by_fpo=True).distinct()
    if queryset_active_cft.exists():
        message = "Impossible to cancel this product : there is open call for tenders on it."
    else:
        try:
            selected_product.delete()
            message = "Product cancelled with success."
        except Exception as e:
            message = "Error while trying to cancel this product : {}".format(e)
    return HttpResponse(message)


@csrf_exempt
def tests(request):
    # 2020-05-10 22:34:01+00:00
    """
    date_start_delivery_period = format_date_with_seconds("2020-05-10 22:34:01+00:00")
    true_delivery_period_of_spec = DeliveryPeriod.objects.latest("id")
    true_delivery_period_of_spec_start = true_delivery_period_of_spec.starting_date - timedelta(minutes=
                                                                                int(true_delivery_period_of_spec.gct))
    true_delivery_period_of_spec_end = true_delivery_period_of_spec.ending_date - timedelta(minutes=
                                                                                int(true_delivery_period_of_spec.gct))
    print(strftime("%z", gmtime()))
    print(true_delivery_period_of_spec.starting_date)
    print(true_delivery_period_of_spec_start)
    print(date_start_delivery_period)
    print(true_delivery_period_of_spec_end)
    if true_delivery_period_of_spec_start.replace(
        tzinfo=None) >= date_start_delivery_period <= true_delivery_period_of_spec_end.replace(tzinfo=None):
        message = "You can't register new bid on Gate Closure Time."
    else:
        message = "bjikop"
    """
    """
    list_de_truc = []
    list_de_truc.append({"truc": "machin"})
    list_de_truc.append({"truc": "masqsqchin"})
    print(list_de_truc)
    for chose in list_de_truc:
        print(chose.get("truc"))
    """
    """
    queryset_cft = CallForTenders.objects.all()
    for cft in queryset_cft:
        queryset = FlexibilityBid.objects.prefetch_related('call_for_tenderss')
        print(queryset)
    """
    """ QUERYSET IN TESTING
    queryset_request = FlexibilityActivationRequest.objects.filter(id__in=[114, 113, 112, 111, 110, 109, 108, 107, 106])
    for request in queryset_request:
        print(request.localization_factor)
    print("##########################################")
    queryset_request_no_loc = FlexibilityActivationRequest.objects.filter(id__in=[114, 113, 112, 111, 110, 109, 108, 107, 106],
                                                                   localization_factor="")
    queryset_request_loc = FlexibilityActivationRequest.objects.filter(id__in=[114, 113, 112, 111, 110, 109, 108, 107, 106])\
        .exclude(localization_factor="")
    print("queryset_request_no_loc")
    for request in queryset_request_no_loc:
        print(request.localization_factor)
    print("##########################################")
    print("queryset_request_loc")
    for request in queryset_request_loc:
        print(request.localization_factor)
    print("##########################################")
    test = list(chain(queryset_request_no_loc, queryset_request_loc))
    print("test")
    for request in test:
        print(request.localization_factor)
    print("##########################################")
    """
    xml = lxml.etree.XML("""<?xml version="1.0" encoding="UTF-8"?>
    <!--Fichier échantillon XML généré par XMLSpy v2021 (x64) (http://www.altova.com)-->
    <FP:FlexibilityBid_MarketDocument xmlns:FP="CIM/EuSysFlex/FlexibilityBid" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="CIM/EuSysFlex/FlexibilityBid CIM_flexibilityBid.xsd">
        <Bid_TimeSeries>
            <Currency_Unit>
                <name>€/MWh</name>
            </Currency_Unit>
            <Delivery_Period>
                <Point>
                    <position>0</position>
                    <Price>
                        <amount>30</amount>
                    </Price>
                    <quantity>20</quantity>
                </Point>
                <resolution>PT1H</resolution>
                <timeInterval>
                    <end>2001-12-17T09:00:00Z</end>
                    <start>2001-12-17T10:00:00Z</start>
                </timeInterval>
            </Delivery_Period>
            <Linked_BidTimeSeries>
                <mRID>ID of the Linked BID</mRID>
            </Linked_BidTimeSeries>
            <Measure_Unit>
                <name>MW</name>
            </Measure_Unit>
            <Metering_MarketEvaluationPoint>
                <mRID>Id of the Meter or sub meter</mRID>
                <ServiceLocation>
                    <CoordinateSystem>
                        <name>String</name>
                    </CoordinateSystem>
                    <mainAddress>
                        <postalCode>String</postalCode>
                        <streetDetail>
                            <addressGeneral>String</addressGeneral>
                            <buildingName>String</buildingName>
                            <name>String</name>
                            <number>String</number>
                        </streetDetail>
                        <townDetail>
                            <country>String</country>
                            <name>String</name>
                            <stateOrProvince>String</stateOrProvince>
                        </townDetail>
                    </mainAddress>
                    <PositionPoints>
                        <xPosition>String</xPosition>
                        <yPosition>String</yPosition>
                        <zPosition>String</zPosition>
                    </PositionPoints>
                </ServiceLocation>
            </Metering_MarketEvaluationPoint>
            <mRID>id of the BID</mRID>
            <product>iD of the product</product>
        </Bid_TimeSeries>

        <LocalizationFactor_Domain>
            <mRID>Id of the localization Factor</mRID>
        </LocalizationFactor_Domain>
        <mRID>Id of the message wich may contain several Bids</mRID>
        <Period>
            <timeInterval>
                <end>2001-12-17T01:00:00Z</end>
                <start>2001-12-17T23:30:00Z</start>
            </timeInterval>
        </Period>
        <Provider_MarketParticipant>
            <MarketRole>
                <mRID>id of the marketRole valid for this Provider</mRID>
            </MarketRole>
            <mRID>ID of the Provider</mRID>
        </Provider_MarketParticipant>
    </FP:FlexibilityBid_MarketDocument>
    """.encode('UTF-8'))
    transform = lxml.etree.XSLT(lxml.etree.XML("""<?xml version="1.0" encoding="UTF-8"?>
    <!--
    This file was generated by Altova MapForce 2021

    YOU SHOULD NOT MODIFY THIS FILE, BECAUSE IT WILL BE
    OVERWRITTEN WHEN YOU RE-RUN CODE GENERATION.

    Refer to the Altova MapForce Documentation for further details.
    http://www.altova.com/mapforce
    -->
    <xsl:stylesheet version="2.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:ns0="CIM/EuSysFlex/FlexibilityBid" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:fn="http://www.w3.org/2005/xpath-functions" exclude-result-prefixes="ns0 xs fn">
        <xsl:output method="xml" encoding="UTF-8" byte-order-mark="no" indent="yes"/>
        <xsl:template match="/">
            <xsl:variable name="var1_FlexibilityBid_MarketDocument" as="node()?" select="ns0:FlexibilityBid_MarketDocument"/>
            <FlexibilityBid>
                <xsl:attribute name="xsi:noNamespaceSchemaLocation" namespace="http://www.w3.org/2001/XMLSchema-instance" select="'file:///home/rko/git_fp/flexibility_platform/ActualFlexibilityBid.xsd'"/>
                <!-- <flexibility_service_provider><xsl:value-of select="$var1_FlexibilityBid_MarketDocument/Provider_MarketParticipant/mRID"/></flexibility_service_provider> -->
                <xsl:for-each select="$var1_FlexibilityBid_MarketDocument">
                    <flexibility_service_provider>
                        <!-- <xsl:value-of select="string(Provider_MarketParticipant/mRID)"/> -->
                        <xsl:sequence select="string(Provider_MarketParticipant/mRID)"/>
                    </flexibility_service_provider>
                </xsl:for-each>
                <xsl:for-each select="$var1_FlexibilityBid_MarketDocument/Bid_TimeSeries">
                    <product_id>
                        <xsl:sequence select="fn:string(product)"/>
                    </product_id>
                </xsl:for-each>
                <xsl:for-each select="$var1_FlexibilityBid_MarketDocument/Bid_TimeSeries/Metering_MarketEvaluationPoint">
                    <metering_point_id>
                        <xsl:sequence select="fn:string(mRID)"/>
                    </metering_point_id>
                </xsl:for-each>
                <xsl:for-each select="$var1_FlexibilityBid_MarketDocument/Bid_TimeSeries/Delivery_Period/Point">
                    <power>
                        <xsl:sequence select="xs:string(xs:decimal(fn:string(quantity)))"/>
                    </power>
                </xsl:for-each>
                <xsl:for-each select="$var1_FlexibilityBid_MarketDocument/Bid_TimeSeries/Delivery_Period/Point">
                    <price>
                        <xsl:sequence select="xs:string(xs:decimal(fn:string(Price/amount)))"/>
                    </price>
                </xsl:for-each>
                <xsl:for-each select="$var1_FlexibilityBid_MarketDocument/Bid_TimeSeries">
                    <linking_of_bids>
                        <xsl:sequence select="xs:string((fn:count(Linked_BidTimeSeries) &gt; xs:decimal('0')))"/>
                    </linking_of_bids>
                </xsl:for-each>
                <xsl:for-each select="$var1_FlexibilityBid_MarketDocument">
                    <localization_factor>
                        <xsl:sequence select="fn:string(LocalizationFactor_Domain/mRID)"/>
                    </localization_factor>
                </xsl:for-each>
                <xsl:for-each select="$var1_FlexibilityBid_MarketDocument/Bid_TimeSeries/Delivery_Period">
                    <start_of_delivery>
                        <xsl:sequence select="xs:string(xs:dateTime(fn:string(timeInterval/start)))"/>
                    </start_of_delivery>
                </xsl:for-each>
            </FlexibilityBid>
        </xsl:template>
    </xsl:stylesheet>
    """.encode('UTF-8')))
    html = transform(xml)
    print(html)
    print(lxml.etree.tostring(html, pretty_print=True))
    """
    xsl = libxslt.parseStyleSheetDoc(libxml2.parseFile('stylesheet.xml'))
    data =  # your xml here
    result = xsl.applyStylesheet(data)
    response = HttpResponse()
    xsl.saveResultToFile(response, result)
    return response
    """

    return HttpResponse(lxml.etree.tostring(html, pretty_print=True), content_type='text/xml')


@csrf_exempt
def tests2(request):
    """
    result = TEST_SAXONC.transform_to_string(source_file="ActualFlexibilityBid_sample.xml", stylesheet_file="FlexibilityBid Sys2CIM.xslt")
    print("print")
    print(result)
    """
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <FlexibilityBid xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="ActualFlexibilityBid.xsd">
        <flexibility_service_provider>ID of the Provider</flexibility_service_provider>
        <product_id>iD of the product</product_id>
        <metering_point_id>Id of the Meter or sub meter</metering_point_id>
        <power>20</power>
        <price>30</price>
        <linking_of_bids>true</linking_of_bids>
        <localization_factor>Id of the localization Factor</localization_factor>
        <start_of_delivery>2001-12-17T10:00:00Z</start_of_delivery>
    </FlexibilityBid>
    """
    print(xml)
    TEST_SAXONC = saxonc.PySaxonProcessor(license=False)
    print(TEST_SAXONC.version)
    xml_bid = TEST_SAXONC.parse_xml(xml_text=xml)
    # xslt30_processor = TEST_SAXONC.new_xslt30_processor()
    xslt30_processor = TEST_SAXONC.new_xslt30_processor()
    xslt30_processor.set_cwd(".")
    result = xslt30_processor.transform_to_string(xdm_node=xml_bid,
                                                  stylesheet_file="FlexibilityBid Sys2CIM.xslt")
    print(result)
    return HttpResponse("coucou")


@csrf_exempt
def tests3(request):
    """
    result = TEST_SAXONC.transform_to_string(source_file="ActualFlexibilityBid_sample.xml", stylesheet_file="FlexibilityBid Sys2CIM.xslt")
    print("print")
    print(result)
    """
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <!--Fichier échantillon XML généré par XMLSpy v2021 (x64) (http://www.altova.com)-->
    <FP:FlexibilityBid_MarketDocument xmlns:FP="CIM/EuSysFlex/FlexibilityBid" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="CIM/EuSysFlex/FlexibilityBid CIM_flexibilityBid.xsd">
        <Bid_TimeSeries>
            <Currency_Unit>
                <name>€/MWh</name>
            </Currency_Unit>
            <Delivery_Period>
                <Point>
                    <position>0</position>
                    <Price>
                        <amount>30</amount>
                    </Price>
                    <quantity>20</quantity>
                </Point>
                <resolution>PT1H</resolution>
                <timeInterval>
                    <end>2001-12-17T09:00:00Z</end>
                    <start>2001-12-17T10:00:00Z</start>
                </timeInterval>
            </Delivery_Period>
            <Linked_BidTimeSeries>
                <mRID>ID of the Linked BID</mRID>
            </Linked_BidTimeSeries>
            <Measure_Unit>
                <name>MW</name>
            </Measure_Unit>
            <Metering_MarketEvaluationPoint>
                <mRID>Id of the Meter or sub meter</mRID>
                <ServiceLocation>
                    <CoordinateSystem>
                        <name>String</name>
                    </CoordinateSystem>
                    <mainAddress>
                        <postalCode>String</postalCode>
                        <streetDetail>
                            <addressGeneral>String</addressGeneral>
                            <buildingName>String</buildingName>
                            <name>String</name>
                            <number>String</number>
                        </streetDetail>
                        <townDetail>
                            <country>String</country>
                            <name>String</name>
                            <stateOrProvince>String</stateOrProvince>
                        </townDetail>
                    </mainAddress>
                    <PositionPoints>
                        <xPosition>String</xPosition>
                        <yPosition>String</yPosition>
                        <zPosition>String</zPosition>
                    </PositionPoints>
                </ServiceLocation>
            </Metering_MarketEvaluationPoint>
            <mRID>id of the BID</mRID>
            <product>iD of the product</product>
        </Bid_TimeSeries>
        
        <LocalizationFactor_Domain>
            <mRID>Id of the localization Factor</mRID>
        </LocalizationFactor_Domain>
        <mRID>Id of the message wich may contain several Bids</mRID>
        <Period>
            <timeInterval>
                <end>2001-12-17T01:00:00Z</end>
                <start>2001-12-17T23:30:00Z</start>
            </timeInterval>
        </Period>
        <Provider_MarketParticipant>
            <MarketRole>
                <mRID>id of the marketRole valid for this Provider</mRID>
            </MarketRole>
            <mRID>ID of the Provider</mRID>
        </Provider_MarketParticipant>
    </FP:FlexibilityBid_MarketDocument>"""
    print(xml)
    TEST_SAXONC = saxonc.PySaxonProcessor(license=False)
    print(TEST_SAXONC.version)
    xml_bid = TEST_SAXONC.parse_xml(xml_text=xml)
    # xslt30_processor = TEST_SAXONC.new_xslt30_processor()
    xslt30_processor = TEST_SAXONC.new_xslt30_processor()
    xslt30_processor.set_cwd(".")
    result = xslt30_processor.transform_to_string(xdm_node=xml_bid,
                                                  stylesheet_file="FlexibilityBid CIM2Sys.xslt")
    print(result)
    return HttpResponse("coucou")


def format_date_with_seconds(non_format_date):
    if "am" in non_format_date or "pm" in non_format_date or "AM" in non_format_date or \
            "PM" in non_format_date:
        formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %I:%M:%S %p')
    else:
        formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %H:%M:%S%z')
    return formatted_date


def format_date_without_seconds(non_format_date):
    if "am" in non_format_date or "pm" in non_format_date or "AM" in non_format_date or \
            "PM" in non_format_date:
        formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %I:%M %p')
    else:
        formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %H:%M')
    return formatted_date


def index(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    logger.info('IP : {}'.format(ip))
    return render(request, 'index.html')

