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


class ActivationAvailableForVerifSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    system_operator_name = serializers.ReadOnlyField(source='system_operator.identification')
    status = serializers.SerializerMethodField()

    @staticmethod
    def get_product_name(obj):
        return obj.product.product_name

    def get_status(self, obj):
        return obj.get_status_display()

    class Meta:
        model = FlexibilityActivationRequest
        fields = "__all__"


class MeteringDataSerializer(serializers.ModelSerializer):
    fsp_name = serializers.ReadOnlyField(source='fsp.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')

    class Meta:
        model = MeteringData
        fields = "__all__"


class ScheduleSerializer(serializers.ModelSerializer):
    fsp_name = serializers.ReadOnlyField(source='fsp.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')

    class Meta:
        model = Schedule
        fields = "__all__"


class VerificationSerializer(serializers.ModelSerializer):
    fsp_name = serializers.ReadOnlyField(source='flexibility_service_provider.identification')
    so_name = serializers.ReadOnlyField(source='system_operator.identification')

    class Meta:
        model = Verification
        fields = "__all__"
