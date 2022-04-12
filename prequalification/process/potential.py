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

from bidding.models import CallForTenders
from event_recorder.models import EventRecorder
from flexibility_platform import consumers
from flexibility_platform.models import Product
from grid_impact.data_management import GridImpact
from miscellaneous.misc import Miscellaneous
from prequalification.models import FlexibilityPotential, FlexibilityPotentialAvailability, FlexibilityNeedAvailability
from prequalification.process.need import NeedProcess
from prequalification.process.preq_infos import PrequalificationInfosProcess


class PotentialProcess:

    @staticmethod
    def complete_process(new_potential):

        new_potential_product_id = new_potential.get("product_id")
        new_potential_fsp_id = new_potential.get("fsp_id")

        new_potential_saved_response = None

        # First, we check if there is needs for this product
        needs_for_product = NeedProcess.get_needs_for_product(new_potential_product_id)
        if needs_for_product.exists():

            # First, we check if there is already potential for this product.
            potential_for_product = PotentialProcess.get_potential_for_product(new_potential_product_id,
                                                                               new_potential_fsp_id)
            if potential_for_product.exists():
                # Second, we check if we can update it (open or close cft on this product)
                if PotentialProcess.check_potential_update_state(new_potential_product_id, new_potential):
                    new_potential_saved = PotentialProcess.update_previous_potential_ok(potential_for_product,
                                                                                        new_potential)
                    new_potential_saved_response = new_potential_saved
                # (Second) if we can't, operation cannot be completed.
                else:
                    message = "Cannot update this potential : there is open call for tenders on it."
                    return [False, message]

            # (First) If there is not, we simply save it and launch prequalification process
            else:
                new_potential_saved = PotentialProcess.save_potential_as_ok(new_potential)
                new_potential_saved_response = new_potential_saved
            GridImpact.set_grid_input_potential(new_potential_saved)
            process_result = PotentialProcess.preq_process(new_potential_saved, new_potential_product_id)
            message = "Potential registered with success. Prequalification process started."

            # (First) If there is no need, failure.
        else:
            # OLD CODE, to remove
            # new_potential_saved = Prequalification.save_potential_as_ok(new_potential)
            message = "No need detected for this product for now."
            process_result = "failure"

        PotentialProcess.contact_fsp_potential(new_potential_fsp_id, message)
        return [new_potential_saved_response, message]

    @staticmethod
    def get_potentials_for_product(product_id):
        queryset_potential = FlexibilityPotential.objects.filter(product_id=product_id)
        return queryset_potential

    @staticmethod
    def get_potential_for_product(product_id, fsp_id):
        queryset_potential = FlexibilityPotential.objects.filter(product_id=product_id, fsp_id=fsp_id)
        return queryset_potential

    @staticmethod
    def get_prequalified_potential_for_product(product_id, fsp_id):
        queryset_potential = FlexibilityPotential.objects.filter(product_id=product_id, fsp_id=fsp_id,
                                                                 is_prequalified=True)
        return queryset_potential

    @staticmethod
    def get_cft_potential(potential_queryset):
        queryset_potential_cft = potential_queryset.filter(update_status__in=["used_in_cft", "waiting_cft"])
        return queryset_potential_cft

    @staticmethod
    def get_cft_potential_waiting(potential_queryset):
        queryset_potential_cft_waiting = potential_queryset.filter(update_status="waiting_cft")
        return queryset_potential_cft_waiting

    @staticmethod
    def update_waiting_cft_potential(potential_queryset):
        potential_to_update = potential_queryset.objects.filter(update_status="waiting_cft")
        potential_to_update.update_status = "to_remove"
        potential_to_update.save()

    @staticmethod
    def save_potential_as_ok(potential_post_data):
        # Saving potential object
        # potential_to_create = FlexibilityPotential(**potential_post_data.dict())
        potential_to_create = FlexibilityPotential(product_id=potential_post_data.get("product_id"),
                                                   fsp_id=potential_post_data.get("fsp_id"),
                                                   power=potential_post_data.get('power'),
                                                   preparation_period=potential_post_data.get("preparation_period"),
                                                   compliance_demonstration=potential_post_data.get("compliance_demonstration"),
                                                   localization_factor=potential_post_data.get("localization_factor"),
                                                   metering_point_id=potential_post_data.get("metering_point_id"),
                                                   baseline_type=potential_post_data.get("baseline_type"),
                                                   expiration_date=Miscellaneous.format_date_with_seconds(potential_post_data.get("expiration_date"))
                                                   )
        potential_to_create.save()

        # Saving associated availabilitys

        list_availability_start = potential_post_data.get("availability_start").split(',')
        list_availability_end = potential_post_data.get("availability_end").split(',')
        for i in range(len(list_availability_start)):
            if list_availability_start[i] and list_availability_end[i]:
                datetime_availability_start = Miscellaneous.format_date_with_seconds(list_availability_start[i])
                datetime_availability_end = Miscellaneous.format_date_with_seconds(list_availability_end[i])
                if datetime_availability_start < datetime_availability_end:
                    availability_to_create = FlexibilityPotentialAvailability(flexibility_potential_id=potential_to_create.id,
                                                                              availability_start=datetime_availability_start,
                                                                              availability_end=datetime_availability_end)
                    availability_to_create.save()
                else:
                    potential_to_create.delete()
                    raise Exception("Incorrect availability detected. This potential wasn't saved.")


        # NOTIFICATION
        name_potential = "potential_{}_{}_{}".format(potential_to_create.fsp.identification,
                                                     potential_to_create.product.product_name,
                                                     potential_to_create.id)
        consumers.SocketConsumer.notification_trigger("New potential registered for product {} "
                                                      ": {} "
                                                      "(made by : {})".format(potential_to_create.product.product_name,
                                                                              name_potential,
                                                                              potential_to_create.fsp.identification))
        event_to_record = EventRecorder(text="New potential registered for product %1 : %2 (made by : %3)",
                                        business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 2, "type": "potential", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 3, "type": "fsp", "id": "{}", "text": "{}"}}]'.
                                        format(potential_to_create.product.id, potential_to_create.product.product_name,
                                               potential_to_create.id, name_potential,
                                               potential_to_create.fsp.id,
                                               potential_to_create.fsp.identification),
                                        types="potential")
        event_to_record.save()
        return potential_to_create

    @staticmethod
    def update_previous_potential_ok(old_potential_queryset, new_potential):

        potential_updated = FlexibilityPotential.objects.get(fsp=new_potential.get("fsp_id"),
                                                             product=new_potential.get("product_id"))



        # Check if potential can change his availability, else abort
        list_availability_start = new_potential.get("availability_start").split(',')
        list_availability_end = new_potential.get("availability_end").split(',')
        # first time to check if we can delete old availability
        for i in range(len(list_availability_start)):
            if list_availability_start[i] and list_availability_end[i]:
                datetime_availability_start = Miscellaneous.format_date_with_seconds(list_availability_start[i])
                datetime_availability_end = Miscellaneous.format_date_with_seconds(list_availability_end[i])
                if datetime_availability_start >= datetime_availability_end:
                    raise Exception("Incorrect availability detected. This potential wasn't updated.")
        # No exception, so we remove old availabilitys
        availability_to_remove = FlexibilityPotentialAvailability.objects.filter(flexibility_potential_id=potential_updated.id)
        availability_to_remove.delete()
        # And add news ones
        for i in range(len(list_availability_start)):
            if list_availability_start[i] and list_availability_end[i]:
                datetime_availability_start = Miscellaneous.format_date_with_seconds(list_availability_start[i])
                datetime_availability_end = Miscellaneous.format_date_with_seconds(list_availability_end[i])
                if datetime_availability_start < datetime_availability_end:
                    availability_to_create = FlexibilityPotentialAvailability(
                        flexibility_potential_id=potential_updated.id,
                        availability_start=datetime_availability_start,
                        availability_end=datetime_availability_end)
                    availability_to_create.save()
                else:
                    raise Exception("Incorrect availability detected. This potential wasn't updated.")

        old_potential_queryset.filter(fsp=new_potential.get("fsp_id"),
                                      product=new_potential.get("product_id")).update(product_id=new_potential.get("product_id"),
                                                                                      fsp_id=new_potential.get("fsp_id"),
                                                                                      power=new_potential.get('power'),
                                                                                      preparation_period=new_potential.get("preparation_period"),
                                                                                      compliance_demonstration=new_potential.get("compliance_demonstration"),
                                                                                      localization_factor=new_potential.get("localization_factor"),
                                                                                      metering_point_id=new_potential.get("metering_point_id"),
                                                                                      baseline_type=new_potential.get("baseline_type"),
                                                                                      expiration_date=Miscellaneous.format_date_with_seconds(new_potential.get("expiration_date")),
                                                                                      updated_at=datetime.now())
        # Check for later : extract from old_potential_queryset instead ?
        potential_updated = FlexibilityPotential.objects.get(fsp=new_potential.get("fsp_id"),
                                                             product=new_potential.get("product_id"))

        # NOTIFICATION
        name_potential = "potential_{}_{}_{}".format(potential_updated.fsp.identification,
                                                     potential_updated.product.product_name,
                                                     potential_updated.id)
        consumers.SocketConsumer.notification_trigger("Potential updated registered for product {} "
                                                      ": {} "
                                                      "(made by : {})".format(potential_updated.product.product_name,
                                                                              name_potential,
                                                                              potential_updated.fsp.identification))
        event_to_record = EventRecorder(text="Potential updated for product %1 : %2 (made by : %3)",
                                        business_object_info='[{{"order" : 1, "type": "product", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 2, "type": "potential", "id": "{}", "text": '
                                                             '"{}"}}, '
                                                             '{{"order" : 3, "type": "fsp", "id": "{}", "text": "{}"}}]'.
                                        format(potential_updated.product.id, potential_updated.product.product_name,
                                               potential_updated.id, name_potential,
                                               potential_updated.fsp.id,
                                               potential_updated.fsp.identification),
                                        types="potential")
        event_to_record.save()
        return potential_updated



    @staticmethod
    def preq_process(potential, new_potential_product_id):
        product = Product.objects.get(id=new_potential_product_id)
        product_prequalification_result = PotentialProcess.product_prequalification(potential, product)
        grid_impact_result = GridImpact.potential_grid_prequalification(potential, product)
        if product_prequalification_result == "Prequalified" and grid_impact_result == "YES":
            potential.is_prequalified = True
            potential.power_constraint = potential.power
            potential.save()
            return "ok"
        else:
            parameter_so_response = GridImpact.get_parameter_from_so_response(grid_impact_result)
            if float(parameter_so_response.get("power_limit")) != 0:
                potential.is_prequalified = True
                potential.power_constraint = float(parameter_so_response.get("power_limit"))
                potential.save()
                return "ok"
        potential.is_prequalified = False
        potential.save()

        # saving info
        PrequalificationInfosProcess.save_result(potential, product_prequalification_result, grid_impact_result)

        return "failure"

    @staticmethod
    def check_potential_update_state(new_potential_product_id, new_potential):
        # If there is CFT on open or close for this product, we send False.
        cft_queryset = CallForTenders.objects.filter(product__id=new_potential_product_id, status__in=["open", "close"])
        potential = FlexibilityPotential.objects.filter(fsp=new_potential.get("fsp_id"),
                                                        product=new_potential.get("product_id")).get()
        if cft_queryset.exists() and potential.is_prequalified:
            result = False
        else:
            result = True
        return result

    @staticmethod
    def check_bidding_potential(product_id, fsp_id, power, localization_factor):
        queryset_potential = FlexibilityPotential.objects.filter(product_id=product_id, fsp_id=fsp_id,
                                                                 localization_factor=localization_factor,
                                                                 is_prequalified=True)
        # Djongo cannot compare Decimal by itself, so workaround here
        if queryset_potential.exists():
            if float(power) > float(queryset_potential[0].power_constraint):
                queryset_potential = FlexibilityPotential.objects.none()
        return queryset_potential

    @staticmethod
    def check_availability(need, potential):
        # Here what's happening
        # For each potential availability, we check each need availability
        # If there is correspondance for even one, we check the next potential availability
        # If one of the potential availability check every need potential but return false, then check_availability
        # return false
        need_availabilitys = FlexibilityNeedAvailability.objects.filter(flexibility_need_id=need.id)
        potential_availabilitys = FlexibilityPotentialAvailability.objects.filter(flexibility_potential_id=potential.id)
        result = True
        for pa in potential_availabilitys:
            if not result:
                break
            for na in need_availabilitys:
                if na.availability_start <= pa.availability_start and na.availability_end >= pa.availability_end:
                    result = True
                    break
                    break
                else:
                    result = False
        return result\


    @staticmethod
    def contact_fsp_potential(potential_fsp_id, message):
        print("coucou")

    @staticmethod
    def product_prequalification(potential, product):
        # All the old complexe process to prequalified is removed on release 3 patch 3.
        # From now on, a potential prequalification supposedly compare some value of his associated product and
        # ... his associated product, the same. So there is no need to match since its necessarily matching.
        prequalified_state = "Prequalified"
        return prequalified_state
