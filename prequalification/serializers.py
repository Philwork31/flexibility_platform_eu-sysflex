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
from rest_framework.relations import PrimaryKeyRelatedField

from .models import *


class FlexibilityPotentialNeedSerializer(serializers.ModelSerializer):
    potential_name = serializers.SerializerMethodField()

    def get_potential_name(self, obj):
        return "potential_{}_{}_{}".format(obj.flexibility_potential.fsp.identification,
                                           obj.flexibility_potential.product.product_name,
                                           obj.flexibility_potential.id)

    class Meta:
        model = PrequalificationInformation
        fields = ('potential_name', 'status')


class FlexibilityNeedAvailabilityProcessSerializer(PrimaryKeyRelatedField, serializers.ModelSerializer):

    class Meta:
        model = FlexibilityNeedAvailability
        fields = "__all__"


class FlexibilityNeedProcessSerializer(serializers.ModelSerializer):
    # Ensure that availability is a valid JSON encoded string
    need_availabilitys = FlexibilityNeedAvailabilityProcessSerializer(many=True, queryset=FlexibilityNeedAvailability.objects.all())
    system_operator_name = serializers.ReadOnlyField(source='system_operator.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    need_name = serializers.SerializerMethodField()
    # potential_prequalified = serializers.ReadOnlyField(source='preqinfoneed.flexibility_potential')
    need_potential_prequalified = FlexibilityPotentialNeedSerializer(read_only=True, many=True, allow_null=True)

    def get_need_name(self, obj):
        return "need_{}_{}_{}".format(obj.system_operator.identification, obj.product.product_name, obj.id)

    class Meta:
        model = FlexibilityNeed
        fields = "__all__"


class FlexibilityNeedAvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = FlexibilityNeedAvailability
        fields = "__all__"


class FlexibilityNeedSerializer(serializers.ModelSerializer):
    need_availabilitys = FlexibilityNeedAvailabilitySerializer(read_only=True, many=True)
    system_operator_name = serializers.ReadOnlyField(source='system_operator.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    need_name = serializers.SerializerMethodField()
    # potential_prequalified = serializers.ReadOnlyField(source='preqinfoneed.flexibility_potential')
    need_potential_prequalified = FlexibilityPotentialNeedSerializer(read_only=True, many=True, allow_null=True)

    def get_need_name(self, obj):
        return "need_{}_{}_{}".format(obj.system_operator.identification, obj.product.product_name, obj.id)

    class Meta:
        model = FlexibilityNeed
        fields = "__all__"


class FlexibilityPotentialAvailabilityProcessSerializer(PrimaryKeyRelatedField, serializers.ModelSerializer):

    class Meta:
        model = FlexibilityPotentialAvailability
        fields = "__all__"


class FlexibilityPotentialProcessSerializer(serializers.ModelSerializer):
    # Ensure that availability is a valid JSON encoded string
    need_availabilitys = FlexibilityPotentialAvailabilityProcessSerializer(many=True,
                                                                           queryset=FlexibilityPotentialAvailability.objects.all())
    fsp_name = serializers.ReadOnlyField(source='fsp.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    potential_name = serializers.SerializerMethodField()

    def get_potential_name(self, obj):
        return "potential_{}_{}_{}".format(obj.fsp.identification, obj.product.product_name,
                                           obj.id)

    class Meta:
        model = FlexibilityNeed
        fields = "__all__"


class FlexibilityPotentialAvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = FlexibilityPotentialAvailability
        fields = "__all__"


class FlexibilityPotentialSerializer(serializers.ModelSerializer):
    potential_availabilitys = FlexibilityPotentialAvailabilitySerializer(read_only=True, many=True)
    fsp_name = serializers.ReadOnlyField(source='fsp.identification')
    product_name = serializers.ReadOnlyField(source='product.product_name')
    potential_name = serializers.SerializerMethodField()

    def get_potential_name(self, obj):
        return "potential_{}_{}_{}".format(obj.fsp.identification, obj.product.product_name,
                                           obj.id)

    class Meta:
        model = FlexibilityPotential
        fields = "__all__"

    def create(self, validated_data):
        try:
            potential, created = FlexibilityPotential.objects.update_or_create(
                fsp_id=validated_data.get('fsp_id', None),
                product_id=validated_data.get('product_id', None),
                defaults=validated_data,
            )
        except Exception:
            raise(serializers.ValidationError("Something went wrong while prequalificate."))
        return potential


class PotentialGridImpactAssessmentResultSerializer(serializers.ModelSerializer):
    system_operator_name = serializers.ReadOnlyField(source='system_operator.identification')
    potential_name = serializers.SerializerMethodField()

    def get_potential_name(self, obj):
        return "potential_{}_{}_{}".format(obj.potential.fsp.identification, obj.potential.product.product_name, obj.potential.id)

    class Meta:
        model = GridImpactAssessmentResult
        fields = "__all__"


"""" Old data model sample
class FlexibilityPotentialPowerOnlySerializer(serializers.ModelSerializer):

    class Meta:
        model = FlexibilityPotential
        fields = ('power_min', 'power_max')


class FlexibilityServiceProviderPotentialSerializer(serializers.ModelSerializer):
    flexibilitypotential_set = FlexibilityPotentialPowerOnlySerializer(read_only=True, many=True)

    class Meta:
        model = FlexibilityServiceProvider
        fields = ('id', 'identification', 'prequalified', 'flexibilitypotential_set')

    def to_representation(self, instance):
        data = super(FlexibilityServiceProviderPotentialSerializer, self).to_representation(instance)
        power_min = 0
        power_max = 0
        for flexpot in data.get('flexibilitypotential_set'):
            power_min += float(flexpot.get('power_min'))
            power_max += float(flexpot.get('power_max'))
        if data.get('prequalified'):
            data.update({'prequalified': 'yes'})
        else:
            data.update({'prequalified': 'no'})
        data.pop('flexibilitypotential_set')
        data.update({'flexibilitypotential_min': power_min})
        data.update({'flexibilitypotential_max': power_max})
        return data
"""
