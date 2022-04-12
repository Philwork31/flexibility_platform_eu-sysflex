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

import json
from datetime import datetime, timedelta
from itertools import chain

from activation.models import FlexibilityActivationRequest, FlexibilityActivationOrder, \
    FlexibilityActivationConfirmation
from bidding.models import CallForTenders, MeritOrderList, FlexibilityBid
from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from flexibility_platform.models import Product, DeliveryPeriod
from miscellaneous.misc import Miscellaneous


class Activation:

    @staticmethod
    def check_validity_request(new_activation_request):
        start_of_delivery = Miscellaneous.format_date_with_seconds(new_activation_request.get('start_of_delivery'))
        product_id = new_activation_request.get('product_id')
        so_name = new_activation_request.get('so_name')
        quantity = new_activation_request.get('quantity')
        localization_factor = new_activation_request.get('localization_factor')

        result = "No valid call for tenders detected on this product for those parameter."
        # check if the product given is "actif", else we get out

        selected_product = Product.objects.filter(id=product_id)
        queryset_active_cft = selected_product.filter(callfortendersproduct__status="open",
                                                      callfortendersproduct__start_service_date__lte=start_of_delivery,
                                                      callfortendersproduct__end_service_date__gte=start_of_delivery,
                                                      validated_by_fpo=True)
        if queryset_active_cft.exists():
            # check for each call for tenders on this product for this SO
            queryset_cft = CallForTenders.objects.filter(product_id=product_id,
                                                         system_operator__identification=so_name,
                                                         status="open",
                                                         start_service_date__lte=start_of_delivery,
                                                         end_service_date__gte=start_of_delivery)
            for cft in queryset_cft:
                if float(cft.total_power_needed) >= float(quantity) and \
                        (cft.localization_factor == localization_factor or not cft.localization_factor):
                    result = "valid"
                    break
        return result

    @staticmethod
    def flexibility_activation_waiting_launch_process():
        cdp = DeliveryPeriod.objects.filter(status="waiting").latest("starting_date")
        queryset_ar_loc = FlexibilityActivationRequest.objects.filter(start_of_delivery__range=
                                                                  (cdp.starting_date - timedelta(minutes=1),
                                                                   cdp.starting_date + timedelta(minutes=1)),
                                                                  status="waiting",
                                                                  ).exclude(localization_factor="")
        queryset_ar_no_loc = FlexibilityActivationRequest.objects.filter(start_of_delivery__range=
                                                                  (cdp.starting_date - timedelta(minutes=1),
                                                                   cdp.starting_date + timedelta(minutes=1)),
                                                                  status="waiting",
                                                                  localization_factor="")
        queryset_ar = list(chain(queryset_ar_loc, queryset_ar_no_loc))
        Activation.flexibility_activation_process(cdp, queryset_ar)

    @staticmethod
    def flexibility_activation_process(cdp, queryset_ar):
        # PENSER A AJOUTER LE STATUS AU FILTER A LA FIN
        list_bid_affected = []
        for activation_request in queryset_ar:
            mol_object = MeritOrderList.objects.get(service_product=cdp,
                                                    product=activation_request.product)
            if mol_object.list_json == "[]":
                FlexibilityActivationRequest.objects.filter(id=activation_request.id).update(status="no_mol")


                # NOTIFICATION
                consumers.SocketConsumer.notification_trigger("Activation request processed for product {} by SO {}." 
                                                              "".format(activation_request.product.product_name,
                                                                        activation_request.system_operator.identification))
                event_to_record = EventRecorder(text="%1 processed for product %2 by SO %3.",
                                                business_object_info='[{{"order" : 1, "type": "activation_request", "id": "{}",'
                                                                    ' "text": "Activation request"}}, '
                                                                    '{{"order" : 2, "type": "product", '
                                                                     '"id": "{}", "text": "{}"}}, '
                                                                     '{{"order" : 3, "type": '
                                                                     '"fsp", "id": "{}", "text": "{}"}}]'.
                                                format(activation_request.id,
                                                       activation_request.product.id,
                                                       activation_request.product.product_name,
                                                       activation_request.system_operator.id,
                                                       activation_request.system_operator.identification),
                                                types="activation_request")
                event_to_record.save()
            else:
                mol_json = json.loads(mol_object.list_json.replace("'", "\""))
                quantity_ar = activation_request.quantity

                # Check if we already have order on this location
                if list_bid_affected:
                    for bid in list_bid_affected:
                        if ((activation_request.localization_factor and \
                                bid.localization_factor == activation_request.localization_factor)\
                                or not activation_request.localization_factor)\
                                and activation_request.status != "treated"\
                                and activation_request.product.id == bid.product.id:
                            # check power
                            if (float(bid.power_constraint_by_grid) - float(bid.power_left_after_activation)) >= float(quantity_ar):
                                # there is already a bid affected who treat this request
                                activation_request.bid_affected.add(bid)
                                activation_request.status = "treated"
                                FlexibilityActivationRequest.objects.filter(id=activation_request.id).update(
                                    status="treated")

                                # NOTIFICATION
                                consumers.SocketConsumer.notification_trigger("Activation request processed for product {} by SO {}." 
                                                                              "".format(activation_request.product.product_name,
                                                                                        activation_request.system_operator.identification))
                                event_to_record = EventRecorder(text="%1 processed for product %2 by SO %3.",
                                                                business_object_info='[{{"order" : 1, "type": "activation_request", "id": "{}",'
                                                                                    ' "text": "Activation request"}}, '
                                                                                    '{{"order" : 2, "type": "product", '
                                                                                     '"id": "{}", "text": "{}"}}, '
                                                                                     '{{"order" : 3, "type": '
                                                                                     '"fsp", "id": "{}", "text": "{}"}}]'.
                                                                format(activation_request.id,
                                                                       activation_request.product.id,
                                                                       activation_request.product.product_name,
                                                                       activation_request.system_operator.id,
                                                                       activation_request.system_operator.identification),
                                                                       types="activation_request")
                                event_to_record.save()
                            else:
                                activation_request.bid_affected.add(bid)
                                quantity_ar = float(quantity_ar) - (float(bid.power_constraint_by_grid) - float(bid.power_left_after_activation))
                                if quantity_ar <= 0:
                                    quantity_ar = 0
                                    break
                            """
                            elif float(bid.power_left_after_activation) > 0:
                                print("coucou2")
                                if float(activation_request.quantity) >= (float(bid.power_constraint_by_grid) - float(bid.power_left_after_activation)):
                                    print("coucou3")
                                    activation_request.bid_affected.add(bid_affected)
                                    quantity_ar = float(activation_request.quantity) - (float(bid.power_constraint_by_grid) - float(bid.power_left_after_activation))
                                    bid.power_left_after_activation = 0
                                    FlexibilityBid.objects.filter(id=bid.id).update(power_left_after_activation=0)
                                    for bid_of_mol in mol_json:
                                        if bid_of_mol["id"] == bid.id:
                                            bid_of_mol["power_left_after_activation"] = bid.power_left_after_activation
                                else:
                                    print("coucou4")
                                    bid.power_left_after_activation = (float(bid.power_constraint_by_grid) - bid.power_left_after_activation) - activation_request.quantity
                                    FlexibilityBid.objects.filter(id=bid.id).update(power_left_after_activation=bid.power_left_after_activation)
                                    quantity_ar = 0
                                    for bid_of_mol in mol_json:
                                        if bid_of_mol["id"] == bid.id:
                                            bid_of_mol["power_left_after_activation"] = bid.power_left_after_activation
                            """

                ##########################
                if activation_request.status != "treated":
                    maximum_price_ar = activation_request.maximum_price
                    for bid in mol_json:
                        bid_should_be_added = True
                        # Those with localization_factor first
                        if activation_request.localization_factor and \
                                bid.get("localization_factor") == activation_request.localization_factor:
                            if float(quantity_ar) >= float(bid.get("power_left_after_activation")) and \
                                    float(maximum_price_ar) >= float(bid.get("price")) and quantity_ar != 0:
                                bid_power_left_after_activation = bid.get("power_left_after_activation")
                                quantity_ar = float(quantity_ar) - float(bid.get("power_left_after_activation"))
                                bid["power_left_after_activation"] = 0
                                FlexibilityBid.objects.filter(id=bid.get("id")).update(power_left_after_activation=0)
                                bid_affected = FlexibilityBid.objects.get(id=bid.get("id"))
                                activation_request.bid_affected.add(bid_affected)
                                for b in list_bid_affected:
                                    if b.id == bid_affected.id:
                                        b.power_left_after_activation = 0
                                        bid_should_be_added = False
                                if bid_should_be_added:
                                    list_bid_affected.append(bid_affected)
                            elif float(maximum_price_ar) >= float(bid.get("price")) and quantity_ar != 0:
                                bid["power_left_after_activation"] = float(bid.get("power_left_after_activation")) - float(quantity_ar)
                                quantity_ordered = quantity_ar
                                quantity_ar = 0
                                FlexibilityBid.objects.filter(id=bid.get("id")).update(power_left_after_activation=bid.get("power_left_after_activation"))
                                bid_affected = FlexibilityBid.objects.get(id=bid.get("id"))
                                activation_request.bid_affected.add(bid_affected)
                                for b in list_bid_affected:
                                    if b.id == bid_affected.id:
                                        b.power_left_after_activation = bid.get("power_left_after_activation")
                                        bid_should_be_added = False
                                if bid_should_be_added:
                                    list_bid_affected.append(bid_affected)

                            if quantity_ar == 0:
                                break
                    for bid in mol_json:
                        bid_should_be_added = True
                        # Those without localization_factor second
                        if not activation_request.localization_factor:
                            if float(quantity_ar) >= float(bid.get("power_left_after_activation")) and \
                                    float(maximum_price_ar) >= float(bid.get("price")) and quantity_ar != 0:
                                bid_power_left_after_activation = bid.get("power_left_after_activation")
                                quantity_ar = float(quantity_ar) - float(bid.get("power_left_after_activation"))
                                bid["power_left_after_activation"] = 0
                                FlexibilityBid.objects.filter(id=bid.get("id")).update(power_left_after_activation=0)
                                bid_affected = FlexibilityBid.objects.get(id=bid.get("id"))
                                activation_request.bid_affected.add(bid_affected)
                                for b in list_bid_affected:
                                    if b.id == bid_affected.id:
                                        b.power_left_after_activation = 0
                                        bid_should_be_added = False
                                if bid_should_be_added:
                                    list_bid_affected.append(bid_affected)
                            elif float(maximum_price_ar) >= float(bid.get("price")) and quantity_ar != 0:
                                bid["power_left_after_activation"] = float(bid.get("power_left_after_activation")) - float(quantity_ar)
                                quantity_ordered = quantity_ar
                                quantity_ar = 0
                                FlexibilityBid.objects.filter(id=bid.get("id")).update(power_left_after_activation=bid.get("power_left_after_activation"))
                                bid_affected = FlexibilityBid.objects.get(id=bid.get("id"))
                                activation_request.bid_affected.add(bid_affected)
                                for b in list_bid_affected:
                                    if b.id == bid_affected.id:
                                        b.power_left_after_activation = bid.get("power_left_after_activation")
                                        bid_should_be_added = False
                                if bid_should_be_added:
                                    list_bid_affected.append(bid_affected)

                            if quantity_ar == 0:
                                break
                    MeritOrderList.objects.filter(service_product=cdp, product=activation_request.product)\
                        .update(list_json=mol_json)
                    FlexibilityActivationRequest.objects.filter(id=activation_request.id).update(status="treated")


                    # NOTIFICATION
                    consumers.SocketConsumer.notification_trigger("Activation request processed for product {} by SO {}." 
                                                                  "".format(activation_request.product.product_name,
                                                                            activation_request.system_operator.identification))
                    event_to_record = EventRecorder(text="%1 processed for product %2 by SO %3.",
                                                    business_object_info='[{{"order" : 1, "type": "activation_request", "id": "{}",'
                                                                        ' "text": "Activation request"}}, '
                                                                        '{{"order" : 2, "type": "product", '
                                                                         '"id": "{}", "text": "{}"}}, '
                                                                         '{{"order" : 3, "type": '
                                                                         '"fsp", "id": "{}", "text": "{}"}}]'.
                                                    format(activation_request.id,
                                                           activation_request.product.id,
                                                           activation_request.product.product_name,
                                                           activation_request.system_operator.id,
                                                           activation_request.system_operator.identification),
                                                    types="activation_request")
                    event_to_record.save()

        # creation des orders / confirmation
        for bid in list_bid_affected:
            order = Activation.create_flexibility_activation_order(bid)
            Activation.create_flexibility_activation_confirmation(bid.flexibility_service_provider,
                                                                      order.id)
            
            for activation_request in queryset_ar:
                queryset_ar_bid = activation_request.bid_affected.all()
                for bid in queryset_ar_bid:
                    if bid.id == order.bid.id:
                        activation_request.flexibility_activation_order.add(order)


    @staticmethod
    def create_flexibility_activation_order(bid):
        # Creating activation order for FSP
        order_to_create = FlexibilityActivationOrder(product_id=bid.product.id,
                                                     flexibility_service_provider_id=bid.flexibility_service_provider.id,
                                                     bid_id=bid.id,
                                                     quantity=float(bid.power_constraint_by_grid) - float(bid.power_left_after_activation),
                                                     localization_factor=bid.localization_factor,
                                                     start_of_delivery=bid.start_of_delivery,
                                                     )
        order_to_create.save()
        return order_to_create

    # So we're using this for now, but in future it should only be used for FSP simulator. Enoco should be able to
    # confirm his own order with flexibility_activation_confirmation_process function. Confirmation should be false then.
    @staticmethod
    def create_flexibility_activation_confirmation(fsp, fao):
        # Creating activation order for FSP
        confirmation_to_create = FlexibilityActivationConfirmation(flexibility_service_provider_id=fsp.id,
                                                                   flexibility_activation_order_id=fao,
                                                                   confirmation=True,
                                                                   )
        confirmation_to_create.save()

    @staticmethod
    def flexibility_activation_confirmation_process(fsp_id, order_id, confirm):
        confirmation_to_update = FlexibilityActivationConfirmation.objects.get(flexibility_service_provider_id=fsp_id,
                                                                               flexibility_activation_order_id=order_id
                                                                              )
        # Updating activation order for FSP
        if confirm == "accepted":
            confirmation_to_update.confirmation = True
        else:
            confirmation_to_update.confirmation = False
        confirmation_to_update.save()

    @staticmethod
    def format_date_with_seconds(non_format_date):
        if "am" in non_format_date or "pm" in non_format_date or "AM" in non_format_date or \
                "PM" in non_format_date:
            formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %I:%M:%S %p')
        else:
            formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %H:%M:%S')
        return formatted_date

    @staticmethod
    def format_date_without_seconds(non_format_date):
        if "am" in non_format_date or "pm" in non_format_date or "AM" in non_format_date or \
                "PM" in non_format_date:
            formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %I:%M %p')
        else:
            formatted_date = datetime.strptime(non_format_date, '%Y-%m-%d %H:%M')
        return formatted_date
