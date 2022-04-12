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

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, generics

from activation.models import FlexibilityActivationRequest, FlexibilityActivationOrder, \
    FlexibilityActivationConfirmation
from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from miscellaneous.misc import Miscellaneous
from .models import MeteringData, Schedule, Verification
from .process.schedule import ScheduleProcess
from .serializers import ScheduleSerializer, MeteringDataSerializer, ActivationAvailableForVerifSerializer, \
    VerificationSerializer


class MeteringDataViewset(viewsets.ModelViewSet):
    queryset = MeteringData.objects.order_by("-id")
    serializer_class = MeteringDataSerializer


class ScheduleViewset(viewsets.ModelViewSet):
    queryset = Schedule.objects.order_by("-id")
    serializer_class = ScheduleSerializer


class VerificationViewset(viewsets.ModelViewSet):
    queryset = Verification.objects.order_by("-id")
    serializer_class = VerificationSerializer


class ActivationAvailableForVerifViewset(viewsets.ModelViewSet):
    queryset = FlexibilityActivationRequest.objects.filter(status="treated").order_by("-id")
    serializer_class = ActivationAvailableForVerifSerializer


class VerificationBySoListApi(generics.ListAPIView):
    serializer_class = VerificationSerializer

    def get_queryset(self):
        so_name = self.kwargs['so_name']
        queryset = Verification.objects.filter(system_operator__identification=so_name)
        return queryset


@csrf_exempt
def metering_data_register(request):
    try:
        new_metering_data = request.POST
        new_metering_data_dp_time = request.POST.get("start_of_delivery_date").strip('][').split(',')
        new_metering_data_dp_date = request.POST.get("start_of_delivery_time").strip('][').split(',')
        new_metering_dp_datetime = request.POST.get("start_of_delivery_datetime").strip('][').split(',')
        new_metering_data_dp_energy = request.POST.get("energy").strip('][').split(',')

        if len(new_metering_data_dp_time) == 0:
            raise Exception("empty field(s) in the form.")

        for i in range(len(new_metering_data_dp_time)):
            if not new_metering_data_dp_time[i] or not new_metering_data_dp_date[i] or not \
                    new_metering_data_dp_energy[i]:
                raise Exception("empty field(s) in the form.")

        for i in range(len(new_metering_data_dp_time)):
            if new_metering_dp_datetime:
                dp = Miscellaneous.format_date_without_seconds(new_metering_dp_datetime[i])
            else:
                dp = Miscellaneous.format_date_with_seconds(new_metering_data_dp_time[i] + " " + new_metering_data_dp_date[i])

            metering_data_to_create = MeteringData(product_id=new_metering_data.get("product_id"),
                                                   fsp_id=new_metering_data.get("flexibility_service_provider_id"),
                                                   metering_point_id=new_metering_data.get("metering_point_id"),
                                                   start_of_delivery_period=dp,
                                                   energy=new_metering_data_dp_energy[i],
                                                   )
            metering_data_to_create.save()

            # NOTIFICATION
            consumers.SocketConsumer.notification_trigger("Metering data registered for product {} by FSP {}." 
                                                          "".format(metering_data_to_create.product.product_name,
                                                                    metering_data_to_create.fsp.identification))
            event_to_record = EventRecorder(text="%1 registered for product %2 by FSP %3",
                                            business_object_info='[{{"order" : 1, "type": "metering_data", "id": "{}",'
                                                                 ' "text": "Metering data"}}, '
                                                                 '{{"order" : 2, "type": "product", '
                                                                 '"id": "{}", "text": "{}"}}, '
                                                                 '{{"order" : 3, "type": '
                                                                 '"fsp", "id": "{}", "text": "{}"}}]'.
                                            format(metering_data_to_create.id,
                                                   metering_data_to_create.product.id,
                                                   metering_data_to_create.product.product_name,
                                                   metering_data_to_create.fsp.id,
                                                   metering_data_to_create.fsp.identification),
                                            types="metering_data")
            event_to_record.save()

        message = "Metering data registered with success."
    except Exception as e:
        message = "Metering data registration failed : {}".format(e)
    return HttpResponse(message)


@csrf_exempt
def schedule_register(request):
    new_schedule = request.POST
    new_schedule_dp_date = request.POST.get("start_of_delivery_date").strip('][').split(',')
    new_schedule_dp_time = request.POST.get("start_of_delivery_time").strip('][').split(',')
    new_schedule_dp_datetime = request.POST.get("start_of_delivery_datetime").strip('][').split(',')
    new_schedule_dp_energy = request.POST.get("energy").strip('][').split(',')
    queryset_and_message = ScheduleProcess.process(new_schedule, new_schedule_dp_date, new_schedule_dp_time,
                                                   new_schedule_dp_energy, new_schedule_dp_datetime)
    return HttpResponse(queryset_and_message[1])


@csrf_exempt
def verification_process(request):
    activation_request = FlexibilityActivationRequest.objects.get(id=request.POST.get("activation_request_id"))
    activation_order_queryset = activation_request.flexibility_activation_order.all()
    if not activation_order_queryset.exists():
        return HttpResponse("No activation order confirmed for this activation request.")
    for activation_order in activation_order_queryset:
        activation_order_start_dp = activation_order.start_of_delivery - timedelta(minutes=1)
        activation_order_end_dp = activation_order.start_of_delivery + timedelta(minutes=1)
        activation_confirmation = FlexibilityActivationConfirmation.objects.get(flexibility_activation_order_id=activation_order.id)
        if activation_confirmation.confirmation:
            schedule_queryset = Schedule.objects.filter(fsp_id=activation_order.flexibility_service_provider,
                                                        product_id=activation_request.product.id,
                                                        start_of_delivery_period__range=(activation_order_start_dp,
                                                                                         activation_order_end_dp))
            if not schedule_queryset.exists():
                return HttpResponse("Verification process failed: no baseline for this delivery period.")

            metering_data_queryset = MeteringData.objects.filter(fsp_id=activation_order.flexibility_service_provider,
                                                                 product_id=activation_request.product.id,
                                                        start_of_delivery_period__range=(activation_order_start_dp,
                                                                                         activation_order_end_dp))
            if not metering_data_queryset.exists():
                return HttpResponse("Verification process failed: no metering data for this delivery period.")
            schedule = schedule_queryset.latest("id")
            metering_data = metering_data_queryset.latest("id")
            message = ""
            delivered = float(metering_data.energy) - float(schedule.energy)
            ordered = float("{}{}".format(activation_order.product.direction, activation_order.quantity))
            message += "Baseline : {} | ".format(schedule.energy)
            message += "Meter data : {} | ".format(metering_data.energy)
            message += "Delivered : {} | ".format(delivered)
            message += "Ordered : {} | ".format(ordered)
            message += "Result : {}".format(float(delivered) - float(ordered))
            verification_to_create = Verification(system_operator_id=activation_request.system_operator.id,
                                                  flexibility_service_provider_id=activation_order.flexibility_service_provider.id,
                                                  flexibility_activation_request_id=activation_request.id,
                                                  flexibility_activation_order_id=activation_order.id,
                                                  metering_point_id=schedule.metering_point_id,
                                                  result=message)
            verification_to_create.save()

            # NOTIFICATION
            consumers.SocketConsumer.notification_trigger("Verification process launched for activation request {}." 
                                                          "".format(activation_request.id))
            event_to_record = EventRecorder(text="%1 process launched for activation request %2.",
                                            business_object_info='[{{"order" : 1, "type": "verification", "id": "{}",'
                                                                 ' "text": "Verification"}}, '
                                                                 '{{"order" : 2, "type": "activation_request", '
                                                                 '"id": "{}", "text": "{}"}}] '.
                                            format(verification_to_create.id,
                                                   activation_request.id,
                                                   activation_request.id),
                                            types="verification")
            event_to_record.save()
    return HttpResponse("Verification process completed. See the results in Verification > Results.")





