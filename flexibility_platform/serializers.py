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

import math

from rest_framework import serializers
from datetime import datetime, timedelta

from .models import *


class FlexibilityServiceProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlexibilityServiceProvider
        fields = "__all__"


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class SystemOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemOperator
        fields = "__all__"


class SecondarySystemOperatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondarySystemOperator
        fields = "__all__"


class AggregatorInformationSerializer(serializers.ModelSerializer):
    fsp_name = serializers.ReadOnlyField(source='fsp.identification')

    class Meta:
        model = AggregatorInformation
        fields = "__all__"


class DeliveryPeriodSerializer(serializers.ModelSerializer):
    celeryworker_status = serializers.SerializerMethodField()
    time_left = serializers.SerializerMethodField()
    time_left_minute = serializers.SerializerMethodField()
    time_left_second = serializers.SerializerMethodField()

    def get_celeryworker_status(self, obj):
        ERROR_KEY = "ERROR"
        try:
            from celery.task.control import inspect
            insp = inspect()
            d = insp.stats()
            if not d:
                d = {ERROR_KEY: 'No running Celery workers were found.'}
        except IOError as e:
            from errno import errorcode
            msg = "Error connecting to the backend: " + str(e)
            if len(e.args) > 0 and errorcode.get(e.args[0]) == 'ECONNREFUSED':
                msg += ' Check that the RabbitMQ server is running.'
            d = {ERROR_KEY: msg}
        except ImportError as e:
            d = {ERROR_KEY: str(e)}
        return d

    def get_time_left(self, obj):
        if obj.status:
            if obj.status == "started":
                t1 = obj.starting_date.replace(tzinfo=None) + timedelta(minutes=obj.duration - obj.gct) - datetime.utcnow()
                result = math.ceil(int(t1.seconds) / 60)
            else:
                t1 = obj.ending_date.replace(tzinfo=None) - datetime.utcnow()
                result = math.ceil(int(t1.seconds) / 60)
                if float(result) > float(obj.gct):
                    result = 1
            return result

    def get_time_left_minute(self, obj):
        if obj.status:
            t1 = obj.starting_date.replace(tzinfo=None) + timedelta(minutes=obj.duration - obj.gct) - datetime.utcnow()
            result = math.ceil(int(t1.seconds) / 60)
            return result

    def get_time_left_second(self, obj):
        if obj.status:
            t1 = obj.ending_date.replace(tzinfo=None) - datetime.utcnow()
            result = abs(int(t1.seconds) - (math.ceil(int(t1.seconds) / 60) * 60) + 60)
            return result

    class Meta:
        model = DeliveryPeriod
        fields = "__all__"
