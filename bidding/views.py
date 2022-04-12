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

from celery import Celery
from rest_framework import viewsets, generics

from miscellaneous.misc import Miscellaneous
from .process.bid import BidProcess
from .process.cft import CallForTendersProcess
from .process.mol import MeritOrderListProcess
from .serializers import *
from flexibility_platform.serializers import ProductSerializer
from flexibility_platform.models import Product
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from .tasks import routine_service_period_start
from flexibility_platform.celery import app

"""
    These viewsets automatically provide `list`, `create`, `retrieve`, `update`
    and `destroy` actions for the corresponding model.

    Example for FlexibilityNeed ("needs" here is defined when the route is
    registered at url.py)
        list – list all elements, serves GET to /needs/
        create – create a new element, serves POST to /needs/
        retrieve – retrieves one element, serves GET to /needs/<id>
        update – updates single element, handles PUT/PATCH to /needs/<id>
        destroy – deletes single element, handles DELETE to /needs/<id>
"""


class CallForTendersViewSet(viewsets.ModelViewSet):
    """
        Restful service who return a call for tenders list ordered by their Django id.
        Since Django id are incremental, i suppose we can also say it's ordered by creation date.

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
    """
    queryset = CallForTenders.objects.filter(status__in=["open", "waiting"]).order_by("-id")
    serializer_class = CallForTendersSerializer


class CallForTendersByProductViewSet(viewsets.ModelViewSet):
    """
        Restful service who return a call for tenders list.
        Only call for tenders with a product which have associated needs are returned.

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
    """
    queryset = CallForTenders.objects.filter(product__needproduct__isnull=False)
    serializer_class = CallForTendersByProductSerializer


class ActiveProductViewSet(viewsets.ModelViewSet):
    """
        Restful service who return a product list.
        Only return product which are considered as "active" : with at least 1 open call for tenders, and validated by
        FPO.

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
    """
    queryset = Product.objects.filter(callfortendersproduct__status="open", 
                                      callfortendersproduct__start_service_date__lte=datetime.now(), 
                                      callfortendersproduct__end_service_date__gte=datetime.now(), 
                                      validated_by_fpo=True).distinct()
    serializer_class = ProductSerializer


class CancellableProductViewSet(viewsets.ModelViewSet):
    """
        Restful service who return a product list.
        Only return product which are considered as "cancellable" :

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
        .. todo:: I have some doubt, check in specs ("cancellable" is not "close") (12/02/2020)
    """
    queryset = Product.objects.filter(callfortendersproduct__status__in=["open", "waiting"], validated_by_fpo=True).distinct()
    serializer_class = ProductSerializer


class BidsByProductListApi(generics.ListAPIView):
    """
        Restful service who return a bid list.
        Returned bids are associated with given product id.
        Ordered by price.

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
        .. todo:: Probably used only for MOL. Do we change the name ? Need checking.
    """
    serializer_class = FlexibilityBidSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        queryset = FlexibilityBid.objects.filter(product_id=product_id).order_by('-price')
        return queryset


class BidsByFspAndProductListApi(generics.ListAPIView):
    """
        Restful service who return a bid list.
        Returned bids are associated with given product id and given fsp id.
        Also, only returned when associated call for tenders is still open.

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
        .. todo:: Big doubt on logic here. Why only when call for tenders is "open" ? Need checking.
    """
    serializer_class = FlexibilityBidSerializer

    def get_queryset(self):
        fsp_id = self.kwargs['fsp_id']
        product_id = self.kwargs['product_id']
        queryset = FlexibilityBid.objects.filter(flexibility_service_provider_id=fsp_id, product_id=product_id,
                                                 call_for_tenders__status="open")
        return queryset


class CallForTendersBySoIdListApi(generics.ListAPIView):
    """
        Restful service who return a CfT list.
        Returned CfT are associated with given so id.
        Also, only returned when status is open, close or waiting.

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
    """
    serializer_class = CallForTendersReadOnlySerializer

    def get_queryset(self):
        so_id = self.kwargs['so_id']
        queryset = CallForTenders.objects.filter(Q(system_operator_id=so_id, status="open") |
                                                 Q(system_operator_id=so_id, status="close") |
                                                 Q(system_operator_id=so_id, status="waiting"))
        return queryset


class CallForTendersBySoNameListApi(generics.ListAPIView):
    """
        Restful service who return a CfT list.
        Returned CfT are associated with given so id.
        Also, only returned when status is open, close or waiting.

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
    """
    serializer_class = CallForTendersSerializer

    def get_queryset(self):
        so_name = self.kwargs['so_name']
        queryset = CallForTenders.objects.filter(system_operator__identification=so_name).order_by("-id").filter(Q(status="open") |
                                                                                                                 Q(status="close") |
                                                                                                                 Q(status="waiting")).order_by("id")
        return queryset


class CallForTendersBySoListApi(generics.ListAPIView):
    """
        Restful service who return a CfT list.
        Returned CfT are associated with given so id.
        Also, only returned when status is open, close or waiting.

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
    """
    serializer_class = CallForTendersSerializer

    def get_queryset(self):
        so_name = self.kwargs['so_name']
        queryset = CallForTenders.objects.filter(Q(system_operator__identification=so_name, status="open") |
                                                 Q(system_operator__identification=so_name, status="close") |
                                                 Q(system_operator__identification=so_name, status="waiting"))
        return queryset


class FlexibilityBidsViewSet(viewsets.ModelViewSet):
    """
        Restful service who return a bid list.
        Ordered by id (in extension, by creation date).

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
    """
    queryset = FlexibilityBid.objects.order_by('-id')
    serializer_class = FlexibilityBidSerializer


class MeritOrderListViewSet(viewsets.ModelViewSet):
    """
        Restful service who return a bid list.
        Ordered by id (in extension, by creation date).

        Author : Romain Kochmanier
        Used : Unknown (12/02/2020)
        In URLs : Yes (12/02/2020)
        .. todo:: Check if used on frontend
    """
    queryset = MeritOrderList.objects.exclude(list_json="[]").order_by('-id')
    serializer_class = MeritOrderListSerializer


@csrf_exempt
def call_for_tenders_register(request):
    """
        View launching the process to register a call for tenders.
        Call for tenders characteristics, associated product id and so id are received by POST method.
        Process method respond with a status message.

        Author : Romain Kochmanier
        Used : Yes (12/02/2020)
        In URLs : Yes (12/02/2020)
        ..todo:: Sending back a message with the process is quite ugly. Maybe i should not use static.
    """
    new_call_for_tenders = request.POST
    new_call_for_tenders_product_id = new_call_for_tenders.get("product_id")
    new_call_for_tenders_so_id = SystemOperator.objects.values_list('id', flat=True).get(identification=new_call_for_tenders.get("system_operator_id"))

    message =CallForTendersProcess.call_for_tenders_process(new_call_for_tenders, new_call_for_tenders_so_id,
                                               new_call_for_tenders_product_id)

    return HttpResponse(message)


@csrf_exempt
def call_for_tenders_cancel(request):
    """
        View launching the process to cancel a call for tenders.
        Call for tenders characteristics and associated so id are received by POST method.

        Author : Romain Kochmanier
        Used : Yes (12/02/2020)
        In URLs : Yes (12/02/2020)
    """
    new_call_for_tenders = request.POST
    new_call_for_tenders_id = new_call_for_tenders.get("call_for_tenders_id")

    message = CallForTendersProcess.call_for_tenders_cancel(new_call_for_tenders_id)

    return HttpResponse(message)


@csrf_exempt
def bid_register(request):
    """
        View launching the process to register a bid.
        Bid characteristics, associated product id and fsp id are received by POST method.
        Process method respond with a status message.

        Author : Romain Kochmanier
        Used : Yes (12/02/2020)
        In URLs : Yes (12/02/2020)
        ..todo:: Sending back a message with the process is quite ugly. Maybe i should not use static.
    """
    new_bid = request.POST
    new_bid_product_id = new_bid.get("product_id")
    new_bid_fsp_id = new_bid.get("flexibility_service_provider_id")

    queryset_and_message = BidProcess.bid_process(new_bid, new_bid_fsp_id, new_bid_product_id)

    return HttpResponse(queryset_and_message[1])


@csrf_exempt
def bid_update(request):
    """
        View updating a bid.
        Bid characteristics, associated product id and fsp id are received by POST method.
        Process method respond with a status message.

        Author : Romain Kochmanier
        Used : Yes (12/02/2020)
        In URLs : Yes (12/02/2020)
        ..todo:: Custom response needed if it fail.
        ..todo:: Why is this outside data_management ?
    """
    new_bid = request.POST
    new_bid_fsp_id = new_bid.get("flexibility_service_provider_id")
    new_bid_product_id = new_bid.get("product_id")

    FlexibilityBid.objects.filter(flexibility_service_provider_id=new_bid_fsp_id,
                                  product_id=new_bid_product_id).update(**new_bid.dict(),
                                                                        updated_at=datetime.now())
    bid_to_update = FlexibilityBid.objects.filter(flexibility_service_provider_id=new_bid_fsp_id,
                                                  product_id=new_bid_product_id).get()

    # NOTIFICATION
    name_bid = "bid_{}_{}_{}".format(bid_to_update.flexibility_service_provider.identification,
                                     bid_to_update.product.product_name,
                                     bid_to_update.id)
    consumers.SocketConsumer. \
        notification_trigger("Bid updated for product {} "
                             ": {} "
                             "(made by : {})".format(bid_to_update.product.product_name,
                                                     name_bid,
                                                     bid_to_update.flexibility_service_provider.identification))
    event_to_record = EventRecorder(text="Bid updated for product %1 : %2 (made by : %3)",
                                    business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                         '"{}"}}, '
                                                         '{{"order" : 2, "type": "bid", "id": "{}", "text": '
                                                         '"{}"}}, '
                                                         '{{"order" : 3, "type": "fsp", "id": "{}", '
                                                         '"text": "{}"}}]'.
                                    format(bid_to_update.product.id,
                                           bid_to_update.product.product_name,
                                           bid_to_update.id, name_bid,
                                           bid_to_update.flexibility_service_provider.id,
                                           bid_to_update.flexibility_service_provider.identification),
                                    types="bid, product, fsp")
    event_to_record.save()

    return HttpResponse('Bid was successfully updated.')


@csrf_exempt
def reset_cft(request):
    """
        View updating all CFT.

        Author : Romain Kochmanier
        Used : Yes (04/03/2020)
        In URLs : Yes (04/03/2020)
    """
    # Doesn't work for some "djongo" reason.
    # CallForTenders.objects.all().update(status='CLOSED')
    CallForTenders.objects.filter(total_power_needed__isnull=False).update(status='cancelled')
    return HttpResponse('CFTs were successfully reset.')


@csrf_exempt
def activate_service_period(request):
    """
        View activating service period.

        Author : Romain Kochmanier
        Used : Yes (05/03/2020)
        In URLs : Yes (05/03/2020)
    """
    # Getting the right time UTC+0
    # service_period_start_time = datetime.strptime(request.POST.get('service_period_start_time'), '%I:%M:%p')
    service_period_start_time = Miscellaneous.format_date_without_seconds(request.POST.get('service_period_start_time'))
    print(request.POST.get('service_period_start_time'))
    print(service_period_start_time)
    service_period_start_time_only = service_period_start_time.time()

    # checking if launched today or tomorrow, setting date right
    if timezone.localtime(timezone.now()).time() > service_period_start_time_only:
        # for tomorrow
        date_start = timezone.localtime(timezone.now()) + timedelta(days=1)
    else:
        # for today
        date_start = timezone.localtime(timezone.now())

    # set result
    final_spst = date_start.replace(hour=service_period_start_time.hour,
                                    minute=service_period_start_time.minute,
                                    second=0, microsecond=0)

    # Launch routine
    service_period_duration = int(request.POST.get('service_period_duration'))
    service_period_gct = int(request.POST.get('service_period_gct'))
    routine_service_period_start.apply_async((service_period_duration,
                                              service_period_gct), eta=final_spst)

    return HttpResponse('Service period routine was successfully activated.')


@csrf_exempt
def deactivate_service_period(request):
    DeliveryPeriod.objects.filter(status="started").update(status="ended")
    DeliveryPeriod.objects.filter(status="gct").update(status="ended")
    DeliveryPeriod.objects.filter(status="waiting").update(status="ended")
    app.control.purge()

    return HttpResponse('Service period routine was successfully deactivated.')


def get_celery_worker_status():
    ERROR_KEY = "ERROR"
    try:
        from celery.task.control import inspect
        insp = inspect()
        d = insp.stats()
        if not d:
            d = { ERROR_KEY: 'No running Celery workers were found.' }
    except IOError as e:
        from errno import errorcode
        msg = "Error connecting to the backend: " + str(e)
        if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
            msg += ' Check that the RabbitMQ server is running.'
        d = { ERROR_KEY: msg }
    except ImportError as e:
        d = { ERROR_KEY: str(e)}
    return d


def generate_mol_test(request):
    # launch data management function here
    MeritOrderListProcess.generate_mol()
    return HttpResponse("Mol generated")
