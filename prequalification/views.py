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

import os
import sys

from rest_framework import viewsets, generics
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from bidding.models import CallForTenders
from .process.need import NeedProcess
from .process.potential import PotentialProcess

from .serializers import *
from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from datetime import datetime

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


class FlexibilityNeedToRegisterViewSet(viewsets.ModelViewSet):
    queryset = FlexibilityNeed.objects.order_by("-id")
    serializer_class = FlexibilityNeedProcessSerializer


class FlexibilityNeedViewSet(viewsets.ModelViewSet):
    queryset = FlexibilityNeed.objects.order_by("-id")
    serializer_class = FlexibilityNeedSerializer


class FlexibilityNeedBySOViewSet(generics.ListAPIView):
    serializer_class = FlexibilityNeedSerializer

    def get_queryset(self):
        so_name = self.kwargs['so_name']
        queryset = FlexibilityNeed.objects.filter(system_operator__identification=so_name).order_by("-id")
        return queryset


class FlexibilityPotentialToRegisterViewSet(viewsets.ModelViewSet):
    queryset = FlexibilityPotential.objects.order_by("-id")
    serializer_class = FlexibilityPotentialProcessSerializer


class FlexibilityPotentialViewSet(viewsets.ModelViewSet):
    queryset = FlexibilityPotential.objects.order_by("-id")
    serializer_class = FlexibilityPotentialSerializer


class PotentialGridImpactAssessmentResult(viewsets.ModelViewSet):
    queryset = GridImpactAssessmentResult.objects.order_by("-id")
    serializer_class = PotentialGridImpactAssessmentResultSerializer


""" Old data model sample
class FlexibilityServiceProviderPotentialViewSet(viewsets.ModelViewSet):
    queryset = FlexibilityServiceProvider.objects.order_by("-id")
    serializer_class = FlexibilityServiceProviderPotentialSerializer
"""


@csrf_exempt
def potential_register(request):
    new_potential = request.POST
    id_and_message = PotentialProcess.complete_process(new_potential)

    return HttpResponse(id_and_message[1])


@csrf_exempt
def potential_cancel(request, potential_id):
    try:
        # Check which product is this potential on and check if we can modify it
        product_id = Product.objects.filter(potentialproduct__id=potential_id).values_list('id', flat=True).get()
        if PotentialProcess.check_potential_update_state(product_id):
            potential_to_delete = FlexibilityPotential.objects.filter(id=potential_id).get()
            FlexibilityPotential.objects.filter(id=potential_id).delete()

            # NOTIFICATION
            name_potential = "potential_{}_{}_{}".format(potential_to_delete.fsp.identification,
                                                         potential_to_delete.product.product_name,
                                                         potential_to_delete.id)
            consumers.SocketConsumer.notification_trigger("Potential deleted for product {} "
                                                          ": {} "
                                                          "(made by : {})".format(
                                                            potential_to_delete.product.product_name,
                                                            name_potential,
                                                            potential_to_delete.fsp.identification))
            event_to_record = EventRecorder(text="Potential deleted for product %1 : %2 (made by : %3)",
                                            business_object_info='[{{"order" : 1, "type": "product", "id": "{}",'
                                                                 ' "text": "{}"}}, {{"order" : 2, "type": "potential", '
                                                                 '"id": "{}", "text": "{}"}}, {{"order" : 3, "type": '
                                                                 '"fsp", "id": "{}", "text": "{}"}}]'.
                                            format(potential_to_delete.product.id,
                                                   potential_to_delete.product.product_name,
                                                   potential_to_delete.id, name_potential,
                                                   potential_to_delete.fsp.id,
                                                   potential_to_delete.fsp.identification),
                                            types="potential")
            event_to_record.save()

            message = "Potential removed with success."
        else:
            message = "Product deletion failed: you can only delete the product you created."
    except Exception as e:
        message = "Error while trying to remove this potential : {}".format(e)
    return HttpResponse(message)


@csrf_exempt
def need_register(request):
    try:
        new_need = request.POST
        message = NeedProcess.complete_process(new_need)
    except Exception as err:
        message = "An error occured: {}".format(err)

    return HttpResponse(message)


@csrf_exempt
def need_cancel(request, need_id):
    try:
        # Check which product is this need on and check if we can modify it
        product_id = Product.objects.filter(needproduct__id=need_id).values_list('id', flat=True).get()
        print(product_id)
        cft_queryset = CallForTenders.objects.filter(product__id=product_id, start_service_date__lte=datetime.now(),
                                                     end_service_date__gte=datetime.now(), status="open")
        print(cft_queryset)
        if not cft_queryset.exists():
            product_check_prequalification = Product.objects.get(needproduct=need_id)
            need_to_delete = FlexibilityNeed.objects.filter(id=need_id).get()
            FlexibilityNeed.objects.filter(id=need_id).delete()

            # NOTIFICATION
            need_name = "need_{}_{}_{}".format(need_to_delete.system_operator.identification,
                                               need_to_delete.product.product_name, need_to_delete.id)
            consumers.SocketConsumer.notification_trigger("Need delete for product {} "
                                                          ": {} (made by : {})".
                                                          format(need_to_delete.product.product_name, need_name,
                                                                 need_to_delete.system_operator.identification))
            event_to_record = EventRecorder(text="Need deleted for product %1 : %2 (made by : %3)",
                                            business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": "{}"'
                                                                 '}}, '
                                                                 '{{"order" : 2, "type": "need", "id": "{}", "text": "{}"}}, '
                                                                 '{{"order" : 3, "type": "so", "id": "{}", "text": "{}"}}]'.
                                            format(need_to_delete.product.id, need_to_delete.product.product_name,
                                                   need_to_delete.id, need_name, need_to_delete.system_operator.id,
                                                   need_to_delete.system_operator.identification),
                                            types="need, product, so")
            event_to_record.save()

            message = "Need removed with success."
        else:
            message = "Need deletion failed: ongoing call for tenders for the same product."
    except Exception as e:
        message = "Error while trying to cancel this need : {}".format(e)
    return HttpResponse(message)


class NeedsBySoAndProductListApi(generics.ListAPIView):
    serializer_class = FlexibilityNeedSerializer

    def get_queryset(self):
        so_id = self.kwargs['so_id']
        product_id = self.kwargs['product_id']
        queryset = FlexibilityNeed.objects.filter(system_operator_id=so_id, product_id=product_id)
        return queryset


class NeedsBySoListApi(generics.ListAPIView):
    serializer_class = FlexibilityNeedSerializer

    def get_queryset(self):
        so_id = self.kwargs['so_id']
        queryset = FlexibilityNeed.objects.filter(system_operator_id=so_id)
        return queryset


class PotentialsByFspListApi(generics.ListAPIView):
    serializer_class = FlexibilityPotentialSerializer

    def get_queryset(self):
        fsp_id = self.kwargs['fsp_id']
        queryset = FlexibilityPotential.objects.filter(fsp_id=fsp_id)
        return queryset
