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

from rest_framework import viewsets, generics

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from activation.data_management import Activation
from activation.models import FlexibilityActivationRequest
from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from flexibility_platform.models import SystemOperator, DeliveryPeriod
from datetime import datetime

from grid_impact.data_management import GridImpact
from .serializers import *
from miscellaneous.misc import Miscellaneous


class FlexibilityRequestActivationViewSet(viewsets.ModelViewSet):
    serializer_class = FlexibilityRequestActivationListSerializer
    queryset = FlexibilityActivationRequest.objects.order_by("-id")


class FlexibilityRequestActivationBySoViewSet(generics.ListAPIView):
    serializer_class = FlexibilityRequestActivationListSerializer

    def get_queryset(self):
        so_name = self.kwargs['so_name']
        queryset = FlexibilityActivationRequest.objects.filter(system_operator__identification=so_name).order_by("-id")
        return queryset


class FlexibilityActivationOrderViewSet(generics.ListAPIView):
    serializer_class = FlexibilityActivationOrderListSerializer

    def get_queryset(self):
        queryset = FlexibilityActivationOrder.objects.all().order_by("-id")
        return queryset


class FlexibilityActivationConfirmationViewSet(generics.ListAPIView):
    serializer_class = FlexibilityActivationConfirmationListSerializer

    def get_queryset(self):
        queryset = FlexibilityActivationConfirmation.objects.all().order_by("-id")
        return queryset


@csrf_exempt
def register_flexibility_activation_request(request):
    new_activation_request = request.POST
    check_validity = Activation.check_validity_request(new_activation_request)
    start_delivery = Miscellaneous.format_date_with_seconds(new_activation_request.get("start_of_delivery"))
    if check_validity == "valid":
        so = SystemOperator.objects.get(identification=new_activation_request.get("so_name"))
        request_to_create = FlexibilityActivationRequest(product_id=new_activation_request.get("product_id"),
                                                         system_operator_id=so.id,
                                                         quantity=new_activation_request.get("quantity"),
                                                         localization_factor=new_activation_request.get("localization_factor"),
                                                         maximum_price=new_activation_request.get("maximum_price"),
                                                         start_of_delivery=start_delivery,
                                                         )
        request_to_create.save()



        # NOTIFICATION
        consumers.SocketConsumer.notification_trigger("Activation request registered for product {} by SO {}." 
                                                      "".format(request_to_create.product.product_name,
                                                                request_to_create.system_operator.identification))
        event_to_record = EventRecorder(text="%1 registered for product %2 by SO %3.",
                                        business_object_info='[{{"order" : 1, "type": "activation_request", "id": "{}",'
                                                            ' "text": "Activation request"}}, '
                                                            '{{"order" : 2, "type": "product", '
                                                             '"id": "{}", "text": "{}"}}, '
                                                             '{{"order" : 3, "type": '
                                                             '"fsp", "id": "{}", "text": "{}"}}]'.
                                        format(request_to_create.id,
                                               request_to_create.product.id,
                                               request_to_create.product.product_name,
                                               request_to_create.system_operator.id,
                                               request_to_create.system_operator.identification),
                                        types="activation_request")
        event_to_record.save()

        # check if should be process now or not
        if start_delivery < datetime.now():
            request_to_treat = FlexibilityActivationRequest.objects.filter(id=request_to_create.id)
            cdp = DeliveryPeriod.objects.filter(status__in=["started", "gct"]).latest("starting_date")
            GridImpact.bidding_grid_impact_assessment(cdp, True)
            Activation.flexibility_activation_process(cdp, request_to_treat)
            result = "Flexibility activation request registered with success. Will be processed right away."
        else:
            result = "Flexibility activation request registered with success. " \
                     "Will be processed at the GCT of the targeted delivery period."

    else:
        result = check_validity

    return HttpResponse(result)


@csrf_exempt
def activation_testing(request):
    Activation.flexibility_activation_process()
    return HttpResponse("tu gères ?")


def format_date_with_seconds(non_format_date):
    if "am" in non_format_date or "pm" in non_format_date or "AM" in non_format_date or \
            "PM" in non_format_date:
        formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %I:%M:%S %p')
    else:
        formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %H:%M:%S')
    return formatted_date

def format_date_without_seconds(non_format_date):
    if "am" in non_format_date or "pm" in non_format_date or "AM" in non_format_date or \
            "PM" in non_format_date:
        formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %I:%M %p')
    else:
        formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %H:%M')
    return formatted_date
