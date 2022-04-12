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

import requests
from django.http import HttpResponse
import re

from bidding.models import MeritOrderList, FlexibilityBid, CallForTenders
from flexibility_platform.models import SystemOperator, DeliveryPeriod, Product, SecondarySystemOperator
from grid_impact.models import BiddingGridImpactAssessmentResult
from prequalification.models import GridImpactAssessmentInput, GridImpactAssessmentResult
from prequalification.process.need import NeedProcess


class GridImpact:

    @staticmethod
    def response_access_control_headers(content, status):
        response = HttpResponse(content, status=status)
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "PORT, GET, OPTIONS"
        response["Access-Control-Max-Age"] = "1000"
        response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
        return response

    @staticmethod
    def grid_impact_assessment_structural_and_dynamic(direction, power, localization_factor, so_name):
        post_data = {'direction': direction, 'power': power, 'localization_factor': localization_factor}
        url_so_queryset = SystemOperator.objects.get(identification=so_name)
        req = requests.post(url_so_queryset.url + "gridimpactassessmentstructuralanddynamic/", data=post_data)
        response = GridImpact.response_access_control_headers(req.content, req.status_code)
        return req.content

    @staticmethod
    def grid_impact_assessment_dynamic(direction, power, localization_factor, so_name):
        post_data = {'direction': direction, 'power': power, 'localization_factor': localization_factor}
        url_so_queryset = SystemOperator.objects.get(identification=so_name)
        req = requests.post(url_so_queryset.url + "gridimpactassessmentdynamic/", data=post_data)
        response = GridImpact.response_access_control_headers(req.content, req.status_code)
        return req.content

    @staticmethod
    def grid_impact_assessment_structural(direction, power, localization_factor, so_name):
        post_data = {'direction': direction, 'power': power, 'localization_factor': localization_factor}
        url_so_queryset = SystemOperator.objects.get(identification=so_name)
        req = requests.post(url_so_queryset.url + "gridimpactassessmentstructural/", data=post_data)
        response = GridImpact.response_access_control_headers(req.content, req.status_code)
        return req.content

    @staticmethod
    def get_lowest_result_from_list(list_so_response):
        lowest_power = None
        result = "YES"
        for so_response in list_so_response:
            if so_response != "YES":
                parameter_so_response = GridImpact.get_parameter_from_so_response(so_response)
                if not lowest_power:
                    lowest_power = parameter_so_response.get("power_limit")
                    result = "YES/{}{}{}".format(parameter_so_response.get("location"),
                                                 parameter_so_response.get("direction"),
                                                 parameter_so_response.get("power_limit"))
                elif float(lowest_power) > float(parameter_so_response.get("power_limit")):
                    lowest_power = parameter_so_response.get("power_limit")
                    result = "YES/{}{}{}".format(parameter_so_response.get("location"),
                                                 parameter_so_response.get("direction"),
                                                 parameter_so_response.get("power_limit"))
        return result


    @staticmethod
    def get_parameter_from_so_response(so_response):
        match_obj = re.match(r'YES\/(.)(.)(.*)', so_response)
        return {"location": match_obj.group(1), "direction": match_obj.group(2), "power_limit": match_obj.group(3)}


    @staticmethod
    def bidding_grid_impact_assessment(next_service_period, activation_now):
        all_product = Product.objects.all()
        for product in all_product:
            bid_queryset = FlexibilityBid.objects.filter(product=product,
                                                         start_of_delivery__range=(
                                                             next_service_period.starting_date - timedelta(minutes=1),
                                                             next_service_period.ending_date - timedelta(minutes=1)))
            for bid in bid_queryset:
                if bid.included_in_mol is None or activation_now:
                    list_so_to_contact = []
                    list_giad = []
                    queryset_cft = bid.call_for_tenders.all()
                    for cft in queryset_cft:
                        if bid.localization_factor == cft.localization_factor or (bid.localization_factor and \
                                                                                  not cft.localization_factor):
                            if cft.system_operator.identification not in list_so_to_contact:
                                list_so_to_contact.append(cft.system_operator.identification)
                    # get secondary SO
                    for so_to_contact in list_so_to_contact:
                        queryset_secondary_so = SecondarySystemOperator.objects.filter(is_secondary_of_id__identification=so_to_contact)
                        for secondary_so in queryset_secondary_so:
                            if secondary_so.original.identification not in list_so_to_contact:
                                list_so_to_contact.append(secondary_so.original.identification)
                    # / get secondary SO
                    for so_to_contact in list_so_to_contact:
                        giad_byte = GridImpact.grid_impact_assessment_structural_and_dynamic(bid.product.direction,
                                                                                             bid.power_origin,
                                                                                             bid.localization_factor,
                                                                                             so_to_contact)
                        giad = giad_byte.decode("utf-8")
                        list_giad.append(giad)
                        # save result grid for list #
                        so_selected = SystemOperator.objects.get(identification=so_to_contact)
                        bgiar = BiddingGridImpactAssessmentResult(system_operator=so_selected,
                                                                  bid=bid,
                                                                  result=giad)
                        bgiar.save()
                        #############################
                    lowest_giad = GridImpact.get_lowest_result_from_list(list_giad)
                    if lowest_giad != "YES":
                        parameter_lowest_giad = GridImpact.get_parameter_from_so_response(lowest_giad)
                        if float(parameter_lowest_giad.get("power_limit")) != 0:
                            bid.power_left_after_activation = float(parameter_lowest_giad.get("power_limit"))
                            bid.power_constraint_by_grid = float(parameter_lowest_giad.get("power_limit"))
                            bid.included_in_mol = True
                        else:
                            bid.power_left_after_activation = float(parameter_lowest_giad.get("power_limit"))
                            bid.power_constraint_by_grid = float(parameter_lowest_giad.get("power_limit"))
                            bid.included_in_mol = False
                    else:
                        bid.power_left_after_activation = bid.power_origin
                        bid.power_constraint_by_grid = bid.power_origin
                        bid.included_in_mol = True
                    bid.save()


    @staticmethod
    def potential_grid_prequalification(potential, product):
        need_queryset = NeedProcess.get_needs_for_product(product)
        list_so_to_contact = []
        list_so_response = []
        for need in need_queryset:
            if potential.localization_factor == need.localization_factor or (potential.localization_factor and \
                                                                             not need.localization_factor):
                so = SystemOperator.objects.get(id=need.system_operator.id)
                if so.identification not in list_so_to_contact:
                    list_so_to_contact.append(so.identification)
        # get secondary SO
        for so_to_contact in list_so_to_contact:
            queryset_secondary_so = SecondarySystemOperator.objects.filter(is_secondary_of_id__identification=so_to_contact)
            for secondary_so in queryset_secondary_so:
                if secondary_so.original.identification not in list_so_to_contact:
                    list_so_to_contact.append(secondary_so.original.identification)
        # / get secondary SO
        for so_to_contact in list_so_to_contact:
            response_from_so = GridImpact.grid_impact_assessment_structural(potential.product.direction,
                                                                            potential.power,
                                                                            potential.localization_factor,
                                                                            so_to_contact)
            response_from_so = response_from_so.decode("utf-8")
            so_selected = SystemOperator.objects.get(identification=so_to_contact)
            grid_impact_assessment_result = GridImpactAssessmentResult(system_operator=so_selected,
                                                                       potential=potential,
                                                                       result=response_from_so)
            grid_impact_assessment_result.save()
            list_so_response.append(response_from_so)
        if len(list_so_response) == 1:
            return list_so_response[0]
        else:
            return GridImpact.get_lowest_result_from_list(list_so_response)

    @staticmethod
    def set_grid_input_potential(potential):
        grid_input = GridImpactAssessmentInput(direction=potential.product.direction, quantity=potential.power,
                                               location=potential.localization_factor)
        grid_input.save()
