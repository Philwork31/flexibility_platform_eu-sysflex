import copy
from datetime import timedelta, datetime

from bidding.models import FlexibilityBid
from bidding.process.cft import CallForTendersProcess
from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from flexibility_platform.models import DeliveryPeriod
from miscellaneous.misc import Miscellaneous
from prequalification.process.potential import PotentialProcess
from verification.models import Schedule


class BidProcess:

    @staticmethod
    def bid_process(new_bid, fsp_id, product_id):
        bid_created = None

        date_start_delivery_period = Miscellaneous.format_date_with_seconds(new_bid.get('start_of_delivery'))
        date_start_delivery_period_copy = date_start_delivery_period - timedelta(minutes=1)
        date_end_delivery_period = date_start_delivery_period + timedelta(minutes=
                                                                          int(new_bid.get('interval_duration')))
        date_end_delivery_period_copy = date_end_delivery_period + timedelta(minutes=1)
        date_end_delivery_period_check = date_start_delivery_period + timedelta(minutes=
                                                                                int(new_bid.get('interval_duration')) -
                                                                                int(new_bid.get('gct')))
        queryset_bid = FlexibilityBid.objects.filter(product_id=product_id, flexibility_service_provider_id=fsp_id,
                                                     start_of_delivery__range=(date_start_delivery_period,
                                                                               date_end_delivery_period))
        if date_end_delivery_period_check < datetime.now():
            message = "Bid registration failed: submission closed after Gate Closure Time. Please check the Start of delivery parameter."
            return [bid_created, message]
        delivery_period_gct = DeliveryPeriod.objects.filter(status="gct")
        if delivery_period_gct.exists():
            true_delivery_period_of_spec = DeliveryPeriod.objects.get(status="waiting")
            true_delivery_period_of_spec_start = true_delivery_period_of_spec.starting_date - timedelta(minutes=
            int(
                true_delivery_period_of_spec.gct))
            true_delivery_period_of_spec_end = true_delivery_period_of_spec.ending_date - timedelta(minutes=
            int(
                true_delivery_period_of_spec.gct))
            if true_delivery_period_of_spec_start.replace(
                tzinfo=None) <= date_start_delivery_period <= true_delivery_period_of_spec_end.replace(
                tzinfo=None):
                message = "You can't register new bid on Gate Closure Time."
                return [bid_created, message]
        queryset_schedule = Schedule.objects.filter(fsp_id=fsp_id,
                                                    start_of_delivery_period__range=(date_start_delivery_period_copy,
                                                                                     date_end_delivery_period_copy))
        schedule_test = Schedule.objects.all().latest("id")
        if not queryset_schedule.exists():
            message = "Bid registration failed: no schedule for the targeted delivery period. "
            return [bid_created, message]
        if not queryset_bid.exists():
            potential_for_product = PotentialProcess.get_prequalified_potential_for_product(product_id, fsp_id)
            if potential_for_product.exists():
                potential_for_product = PotentialProcess.check_bidding_potential(product_id, fsp_id,
                                                                                 new_bid.get("power"),
                                                                                 new_bid.get("localization_factor"))
                if potential_for_product.exists():
                    open_cft_product = CallForTendersProcess.get_active_call_for_tenders_for_product(product_id,
                                                                                       date_start_delivery_period,
                                                                                       date_end_delivery_period)
                    if open_cft_product.exists():
                        bid_created = BidProcess.bid_register(new_bid, product_id, open_cft_product)
                        message = "Bid registered with success."
                    else:
                        message = "No open call for tenders for this product."
                else:
                    message = "Bid registration failed: doesn't match the potential. Please check the Power, " \
                              "the Direction and/or the Localization factor parameters."
            else:
                message = "Bid registration failed: no prequalified potential."
        else:
            message = "Bid already existing at this delivery period for this product and FSP. Bid wasn't saved."
        return [bid_created, message]

    @staticmethod
    def bid_register(new_bid, product_id, call_for_tenders_for_product):
        # bid_to_create = FlexibilityBid(**new_bid.dict())
        bid_to_create = FlexibilityBid(product_id=new_bid.get("product_id"),
                                       flexibility_service_provider_id=new_bid.get("flexibility_service_provider_id"),
                                       price=new_bid.get("price"),
                                       power_origin=new_bid.get("power"),
                                       power_left_after_activation=new_bid.get("power"),
                                       power_constraint_by_grid=new_bid.get("power"),
                                       linking_of_bids=new_bid.get("linking_of_bids"),
                                       metering_point_id=new_bid.get("metering_point_id"),
                                       localization_factor=new_bid.get("localization_factor"),
                                       start_of_delivery=Miscellaneous.format_date_with_seconds(
                                           new_bid.get("start_of_delivery")),
                                       )
        bid_to_create.save()

        # NOTIFICATION
        name_bid = "bid_{}_{}_{}".format(bid_to_create.flexibility_service_provider.identification,
                                         bid_to_create.product.product_name,
                                         bid_to_create.id)
        consumers.SocketConsumer. \
            notification_trigger("Bid registered for product {} "
                                 ": {} "
                                 "(made by : {})".format(bid_to_create.product.product_name,
                                                         name_bid,
                                                         bid_to_create.flexibility_service_provider.identification))
        event_to_record = EventRecorder(text="Bid registered for product %1 : %2 (made by : %3)",
                                        business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 2, "type": "bid", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 3, "type": "fsp", "id": "{}", '
                                                             '"text": "{}"}}]'.
                                        format(bid_to_create.product.id,
                                               bid_to_create.product.product_name,
                                               bid_to_create.id, name_bid,
                                               bid_to_create.flexibility_service_provider.id,
                                               bid_to_create.flexibility_service_provider.identification),
                                        types="bid, product, fsp")
        event_to_record.save()

        for call_for_tenders in call_for_tenders_for_product:
            bid_to_create.call_for_tenders.add(call_for_tenders)

        return bid_to_create

    @staticmethod
    def remove_obsolete_bid(call_for_tenders_id):
        # Get bid to remove
        bids_to_remove = BidProcess.get_removable_bids(call_for_tenders_id)

        # Delete others
        FlexibilityBid.objects.filter(call_for_tenders__id__in=bids_to_remove).delete()

    @staticmethod
    def get_removable_bids(call_for_tenders_id):
        # Djongo is fucked up on some method for many-to-many, especially exclude, so this is the only (bad) way i
        # found to do this.
        # Check bidding for this CFT
        list_bid = list(FlexibilityBid.objects.filter(call_for_tenders__id=call_for_tenders_id).
                        values_list('id', flat=True))

        # I wanted to get only the open one for this CFT, but Djongo give me empty list... so i call everything.
        bids_to_not_remove = list(
            FlexibilityBid.objects.filter(call_for_tenders__status__in=["open", "close"]).distinct().
                values_list('id', flat=True))

        # I suppose there is a bug on index when i remove things before i finish, so i duplicate the list. Sigh.
        list_bid_final = copy.deepcopy(list_bid)
        for id_bid in list_bid:
            if id_bid in bids_to_not_remove:
                list_bid_final.remove(id_bid)

        return list_bid_final
