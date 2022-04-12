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

from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from flexibility_platform.models import SystemOperator
from miscellaneous.misc import Miscellaneous
from prequalification.models import FlexibilityNeed, FlexibilityNeedAvailability


class NeedProcess:

    @staticmethod
    def complete_process(new_need):
        new_need_so_id = SystemOperator.objects.values_list('id', flat=True).get(identification=new_need.get("so_name"))

        # Check if for this product/SO, a need already exist on those availability
        needs_product_so = FlexibilityNeed.objects.filter(product_id=new_need.get("product_id"),
                                                          system_operator_id=new_need_so_id)
        print(new_need.get("availability_start"))
        list_availability_start = new_need.get("availability_start").split(',')
        list_availability_end = new_need.get("availability_end").split(',')
        for need in needs_product_so:
            for i in range(len(list_availability_start)):
                if list_availability_start[i] and list_availability_end[i]:
                    datetime_availability_start = Miscellaneous.format_date_without_seconds(list_availability_start[i])
                    datetime_availability_end = Miscellaneous.format_date_without_seconds(list_availability_end[i])
                    queryset_all_av_by_need_covered = FlexibilityNeedAvailability.objects \
                        .filter(flexibility_need_id=need.id).filter(availability_start__lte=datetime_availability_start) \
                        .filter(availability_end__gte=datetime_availability_end)
                    queryset_all_av_by_need_infromleft = FlexibilityNeedAvailability.objects \
                        .filter(flexibility_need_id=need.id).filter(availability_end__gte=datetime_availability_start) \
                        .filter(availability_end__lte=datetime_availability_end)
                    queryset_all_av_by_need_infromright = FlexibilityNeedAvailability.objects \
                        .filter(flexibility_need_id=need.id).filter(availability_start__gte=datetime_availability_start) \
                        .filter(availability_start__lte=datetime_availability_end)
                    if queryset_all_av_by_need_covered.exists() or queryset_all_av_by_need_infromleft.exists() \
                        or queryset_all_av_by_need_infromright.exists():
                        message = "This availability range is already covered totally or partially by another Need." \
                                  "You cannot have multiple Need for same availability on the same Product/SO."
                        return message

        # Saving
        need_to_create = FlexibilityNeed(product_id=new_need.get("product_id"),
                                         system_operator_id=new_need_so_id,
                                         total_indicative_power_needed=new_need.get("total_indicative_power"),
                                         preparation_period=new_need.get("preparation_period"),
                                         localization_factor=new_need.get("localization_factor"),
                                         expiration_date=Miscellaneous.format_date_without_seconds(new_need.get("expiration_date")))
        need_to_create.save()

        # Availability part
        list_availability_start = new_need.get("availability_start").split(',')
        list_availability_end = new_need.get("availability_end").split(',')
        for i in range(len(list_availability_start)):
            if list_availability_start[i] and list_availability_end[i]:
                datetime_availability_start = Miscellaneous.format_date_without_seconds(list_availability_start[i])
                datetime_availability_end = Miscellaneous.format_date_without_seconds(list_availability_end[i])
                if datetime_availability_start < datetime_availability_end:
                    availability_to_create = FlexibilityNeedAvailability(flexibility_need_id=need_to_create.id,
                                                                         availability_start=datetime_availability_start,
                                                                         availability_end=datetime_availability_end)
                    availability_to_create.save()
                else:
                    need_to_create.delete()
                    raise Exception("Incorrect availability detected. This need wasn't saved.")

        # NOTIFICATION
        need_name = "need_{}_{}_{}".format(need_to_create.system_operator.identification,
                                           need_to_create.product.product_name, need_to_create.id)
        consumers.SocketConsumer.notification_trigger("New need registered for product {} "
                                                      ": {} (made by : {})".
                                                      format(need_to_create.product.product_name, need_name,
                                                             need_to_create.system_operator.identification))
        event_to_record = EventRecorder(text="New need registered for product %1 : %2 (made by : %3)",
                                        business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": "{}"'
                                                             '}}, '
                                                             '{{"order" : 2, "type": "need", "id": "{}", "text": "{}"}}, '
                                                             '{{"order" : 3, "type": "so", "id": "{}", "text": "{}"}}]'.
                                        format(need_to_create.product.id, need_to_create.product.product_name,
                                               need_to_create.id, need_name, need_to_create.system_operator.id,
                                               need_to_create.system_operator.identification),
                                        types="need, product, so")
        event_to_record.save()
        message = "Need registered with success."

        return message

    @staticmethod
    def get_needs_for_product(product_id):
        queryset_need = FlexibilityNeed.objects.filter(product_id=product_id)
        return queryset_need

    @staticmethod
    def get_needs_for_product_and_so(product_id, so_id):
        queryset_need = FlexibilityNeed.objects.filter(product_id=product_id, system_operator_id=so_id)
        return queryset_need