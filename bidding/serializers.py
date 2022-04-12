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

from rest_framework import serializers

from .models import *
from flexibility_platform.serializers import ProductSerializer
from .globals import GATE_CLOSURE_TIME


class CallForTendersSerializer(serializers.ModelSerializer):
    system_operator_name = serializers.ReadOnlyField(source='system_operator_id.identification')
    cft_name = serializers.SerializerMethodField()
    system_operator_name = serializers.ReadOnlyField(source='system_operator.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    gate_closure_time = serializers.SerializerMethodField()
    # status = serializers.CharField(source='get_status_display')

    @staticmethod
    def get_cft_name(obj):
        return "cft_{}_{}_{}".format(obj.system_operator.identification, obj.product.product_name, obj.id)

    @staticmethod
    def get_gate_closure_time(obj):
        return "{}".format(GATE_CLOSURE_TIME)

    class Meta:
        model = CallForTenders
        fields = ("id", "system_operator_name", "cft_name", "system_operator_name", "product_name", "gate_closure_time",
                  "total_power_needed", "linking_of_bids", "localization_factor", "opening_date",
                  "closing_date", "start_service_date", "end_service_date", "created_at", "updated_at")


class CallForTendersReadOnlySerializer(serializers.ModelSerializer):
    system_operator_name = serializers.ReadOnlyField(source='system_operator.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    # status = serializers.CharField(source='get_status_display')

    class Meta:
        model = CallForTenders
        fields = "__all__"


class CallForTendersByProductSerializer(serializers.ModelSerializer):
    """
        Serializer for Call for tenders.
        Product associated content is displayed.
        Statut "string" is displayed instead of database value.

        Author : Romain Kochmanier
        In views : Yes
    """
    product = ProductSerializer()
    # status = serializers.CharField(source='get_status_display')

    class Meta:
        model = CallForTenders
        fields = "__all__"


class FlexibilityBidSerializer(serializers.ModelSerializer):
    fsp_name = serializers.ReadOnlyField(source='flexibility_service_provider.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    bid_name = serializers.SerializerMethodField()

    @staticmethod
    def get_bid_name(obj):
        return "bid_{}_{}".format(obj.product.product_name, obj.id)

    class Meta:
        model = FlexibilityBid
        fields = "__all__"


class MeritOrderListSerializer(serializers.ModelSerializer):
    delivery_period_start = serializers.SerializerMethodField()
    delivery_period_end = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()

    @staticmethod
    def get_delivery_period_start(obj):
        return obj.service_product.starting_date

    @staticmethod
    def get_delivery_period_end(obj):
        return obj.service_product.ending_date

    @staticmethod
    def get_product_name(obj):
        return obj.product.product_name

    class Meta:
        model = MeritOrderList
        fields = "__all__"
