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

from bidding.models import FlexibilityBid
from flexibility_platform.models import SystemOperator, Product, FlexibilityServiceProvider
from django.core.validators import MinValueValidator

UP = '+'
DOWN = '-'
UP_DOWN_CHOICES = (
    (UP, 'Up'),
    (DOWN, 'Down'),
)

OPEN_CLOSE_CHOICES = (
    ('treated', 'Activation order confirmed by all FSPs'),
    ('no_mol', 'No bids on the MOL'),
    ('waiting', 'Not processed yet'),
)


class FlexibilityActivationOrder(models.Model):
    flexibility_service_provider = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    bid = models.ForeignKey(FlexibilityBid, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])
    localization_factor = models.TextField()
    start_of_delivery = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class FlexibilityActivationRequest(models.Model):
    system_operator = models.ForeignKey(SystemOperator, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])
    localization_factor = models.TextField()
    maximum_price = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])
    start_of_delivery = models.DateTimeField()
    status = models.CharField(max_length=10, choices=OPEN_CLOSE_CHOICES, default='waiting')
    bid_affected = models.ManyToManyField(FlexibilityBid)
    flexibility_activation_order = models.ManyToManyField(FlexibilityActivationOrder)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class FlexibilityActivationConfirmation(models.Model):
    flexibility_service_provider = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE)
    flexibility_activation_order = models.ForeignKey(FlexibilityActivationOrder, on_delete=models.CASCADE)
    confirmation = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()
