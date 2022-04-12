from datetime import datetime, timedelta

from bidding.models import CallForTenders
from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from flexibility_platform.models import DeliveryPeriod
from miscellaneous.misc import Miscellaneous
from prequalification.process.need import NeedProcess


class CallForTendersProcess:

    @staticmethod
    def call_for_tenders_process(new_call_for_tenders, so_id, product_id):
        """
            Just... redo this.
            ..todo:: separate verification check by method.
            ..todo:: try catch to generate custom message somehow, maybe.
        """
        needs_for_product_and_so = NeedProcess.get_needs_for_product_and_so(product_id, so_id)
        if needs_for_product_and_so.exists():

            # check date here, everything must be in future
            opening_date_datetime = Miscellaneous.format_date_without_seconds(new_call_for_tenders.get('opening_date'))
            closing_date_datetime = Miscellaneous.format_date_without_seconds(new_call_for_tenders.get('closing_date'))
            start_service_datetime = Miscellaneous.format_date_with_seconds(new_call_for_tenders.get('start_service_date'))
            end_service_datetime = Miscellaneous.format_date_with_seconds(new_call_for_tenders.get('end_service_date'))
            if opening_date_datetime < datetime.now() and closing_date_datetime < datetime.now() and \
                start_service_datetime < datetime.now() and end_service_datetime < datetime.now():
                message = "Incorrect date : should be set in future"
                return message
            # validation date
            if opening_date_datetime >= closing_date_datetime:
                message = "Closing date should be after opening date"
                return message
            if start_service_datetime >= end_service_datetime:
                message = "Call for tenders registration failed: the start of the service period must be prior to the end of the service period."
                return message
            if start_service_datetime < datetime.now():
                message = "Call for tenders registration failed: service period cannot be in the past."
                return message
            # specific check date : no cft on same period for same so/product
            queryset_all_cft_by_so_product_covered = CallForTenders.objects.filter(system_operator_id=so_id) \
                .filter(product_id=product_id).filter(start_service_date__lte=start_service_datetime) \
                .filter(end_service_date__gte=end_service_datetime).filter(status="open")
            queryset_all_cft_by_so_product_infromleft = CallForTenders.objects.filter(system_operator_id=so_id) \
                .filter(product_id=product_id).filter(end_service_date__gte=start_service_datetime) \
                .filter(end_service_date__lte=end_service_datetime).filter(status="open")
            queryset_all_cft_by_so_product_infromright = CallForTenders.objects.filter(system_operator_id=so_id) \
                .filter(product_id=product_id).filter(start_service_date__gte=start_service_datetime) \
                .filter(start_service_date__lte=end_service_datetime).filter(status="open")
            if queryset_all_cft_by_so_product_covered.exists() or queryset_all_cft_by_so_product_infromleft.exists() \
                or queryset_all_cft_by_so_product_infromright.exists():
                message = "This time range is already covered totally or partially by another Call for Tenders. You " \
                          "cannot have multiple Call for Tenders on a Delivery Period."
                return message

            # removed for now : an cft is now considered actif regarding start and end of service date, and if his status isn't cancelled
            # cft_opening_planification.apply_async([call_for_tenders_created_id], eta=opening_date_datetime)
            # cft_cancelling_planification.apply_async([call_for_tenders_created_id], eta=closing_date_datetime)

            CallForTendersProcess.register_call_for_tenders(new_call_for_tenders, so_id)
            message = "Call for tenders registered with success."
        else:
            message = "Call for tenders registration failed: no registered flexibility need."
        return message

    @staticmethod
    def register_call_for_tenders(new_call_for_tenders, new_call_for_tenders_so_id):
        # call_for_tenders_to_create = CallForTenders(**new_call_for_tenders.dict())
        call_for_tenders_to_create = CallForTenders(product_id=new_call_for_tenders.get("product_id"),
                                                    system_operator_id=new_call_for_tenders_so_id,
                                                    total_power_needed=new_call_for_tenders.get("total_power_needed"),
                                                    linking_of_bids=new_call_for_tenders.get("linking_of_bids"),
                                                    localization_factor=new_call_for_tenders.get("localization_factor"),
                                                    opening_date=Miscellaneous.format_date_without_seconds(
                                                        new_call_for_tenders.get("opening_date")),
                                                    closing_date=Miscellaneous.format_date_without_seconds(
                                                        new_call_for_tenders.get("closing_date")),
                                                    start_service_date=Miscellaneous.format_date_with_seconds(
                                                        new_call_for_tenders.get("start_service_date")),
                                                    end_service_date=Miscellaneous.format_date_with_seconds(
                                                        new_call_for_tenders.get("end_service_date"))
                                                    )
        call_for_tenders_to_create.save()

        # NOTIFICATION
        name_cft = "cft_{}_{}_{}_{}".format(call_for_tenders_to_create.system_operator.identification,
                                            call_for_tenders_to_create.product.product_name,
                                            call_for_tenders_to_create.id,
                                            call_for_tenders_to_create.status)
        consumers.SocketConsumer. \
            notification_trigger("Call for tenders registered for product {} "
                                 ": {} "
                                 "(made by : {})".format(call_for_tenders_to_create.product.product_name,
                                                         name_cft,
                                                         call_for_tenders_to_create.system_operator.identification))
        event_to_record = EventRecorder(text="Call for tenders registered for product %1 : %2 (made by : %3)",
                                        business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 2, "type": "cft", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 3, "type": "fsp", "id": "{}", '
                                                             '"text": "{}"}}]'.
                                        format(call_for_tenders_to_create.product.id,
                                               call_for_tenders_to_create.product.product_name,
                                               call_for_tenders_to_create.id, name_cft,
                                               call_for_tenders_to_create.system_operator.id,
                                               call_for_tenders_to_create.system_operator.identification),
                                        types="call for tenders, product, so")
        event_to_record.save()

        return call_for_tenders_to_create.id

    @staticmethod
    def get_active_call_for_tenders_for_product(product_id, start_service_datetime, end_service_datetime):
        queryset_all_cft_by_so_product_covered = CallForTenders.objects \
            .filter(product_id=product_id).filter(start_service_date__lte=(start_service_datetime + timedelta(minutes=1))) \
            .filter(end_service_date__gte=(end_service_datetime - timedelta(minutes=1))).filter(status="open")
        return queryset_all_cft_by_so_product_covered

    @staticmethod
    def call_for_tenders_cancel(call_for_tenders_id):
        # doit supprimer les bids qui n'ont QUE ce cft en many to many
        # queryset_bid = FlexibilityBid.object.filter(call_for_tenders__id=new_call_for_tenders_id)
        # modification cft to cancelled
        service_period_gct = DeliveryPeriod.objects.filter(status="gct")
        if not service_period_gct.exists():
            CallForTenders.objects.filter(id=call_for_tenders_id).update(status="cancelled",
                                                                         updated_at=datetime.now())
            call_for_tenders_to_cancel = CallForTenders.objects.filter(id=call_for_tenders_id).get()
            # NOTIFICATION
            name_cft = "cft_{}_{}_{}_{}".format(call_for_tenders_to_cancel.system_operator.identification,
                                                call_for_tenders_to_cancel.product.product_name,
                                                call_for_tenders_to_cancel.id,
                                                call_for_tenders_to_cancel.status)
            consumers.SocketConsumer. \
                notification_trigger("Call for tenders cancelled for product {} "
                                     ": {} "
                                     "(made by : {})".format(call_for_tenders_to_cancel.product.product_name,
                                                             name_cft,
                                                             call_for_tenders_to_cancel.system_operator.identification))
            event_to_record = EventRecorder(text="Call for tenders cancelled for product %1 : %2 (made by : %3)",
                                            business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                                 '"{}"}}, '
                                                                 '{{"order" : 2, "type": "cft", "id": "{}", "text": '
                                                                 '"{}"}}, '
                                                                 '{{"order" : 3, "type": "fsp", "id": "{}", '
                                                                 '"text": "{}"}}]'.
                                            format(call_for_tenders_to_cancel.product.id,
                                                   call_for_tenders_to_cancel.product.product_name,
                                                   call_for_tenders_to_cancel.id, name_cft,
                                                   call_for_tenders_to_cancel.system_operator.id,
                                                   call_for_tenders_to_cancel.system_operator.identification),
                                            types="call for tenders, product, so")
            event_to_record.save()
            return "Call for tenders cancelled with success"
        else:
            return "Call for tenders can only be cancelled on Gate Closure Time"