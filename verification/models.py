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

from djongo import models

from activation.models import FlexibilityActivationRequest, FlexibilityActivationOrder
from flexibility_platform.models import FlexibilityServiceProvider, Product, SystemOperator


class RequestForMeteringData(models.Model):
    fsp = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    meter_point_id = models.TextField()
    start_of_delivery_period = models.DateTimeField()

    objects = models.DjongoManager()


class MeteringData(models.Model):
    # request_for_metering_data = models.ForeignKey(RequestForMeteringData, on_delete=models.CASCADE)
    fsp = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    energy = models.TextField()
    metering_point_id = models.TextField()
    start_of_delivery_period = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class Schedule(models.Model):
    fsp = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    energy = models.TextField()
    metering_point_id = models.TextField()
    start_of_delivery_period = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class Verification(models.Model):
    system_operator = models.ForeignKey(SystemOperator, on_delete=models.CASCADE)
    flexibility_service_provider = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE)
    flexibility_activation_request = models.ForeignKey(FlexibilityActivationRequest, on_delete=models.CASCADE)
    flexibility_activation_order = models.ForeignKey(FlexibilityActivationOrder, on_delete=models.CASCADE)
    metering_point_id = models.TextField()
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()
