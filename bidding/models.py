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
from flexibility_platform.models import SystemOperator, Product, FlexibilityServiceProvider, DeliveryPeriod
from django.core.validators import MinValueValidator

UP = '+'
DOWN = '-'
UP_DOWN_CHOICES = (
    (UP, 'Up'),
    (DOWN, 'Down'),
)

OPEN_CLOSE_CHOICES = (
    ('open', 'OPEN - SUBMISSION OPEN'),
    ('close', 'OPEN - SUBMISSION CLOSED'),
    ('cancelled', 'CLOSED'),
    ('waiting', 'PENDING'),
)


class CallForTenders(models.Model):
    system_operator = models.ForeignKey(SystemOperator, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='callfortendersproduct')
    total_power_needed = models.DecimalField(max_digits=10, decimal_places=3, null=True)
    linking_of_bids = models.BooleanField()
    localization_factor = models.TextField(blank=True, null=True)
    opening_date = models.DateTimeField()
    closing_date = models.DateTimeField(blank=True, null=True)
    start_service_date = models.DateTimeField()
    end_service_date = models.DateTimeField(blank=True, null=True)
    # modified : now used only if CfT cancelled, don't change anymore with Celerry, waiting for a better solution
    status = models.CharField(max_length=10, choices=OPEN_CLOSE_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class FlexibilityBid(models.Model):
    flexibility_service_provider = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    call_for_tenders = models.ManyToManyField(CallForTenders)
    price = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])
    power_origin = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])
    power_left_after_activation = models.DecimalField(max_digits=10, decimal_places=3, validators=[MinValueValidator(0.01)])
    power_constraint_by_grid = models.DecimalField(blank=True, null=True, max_digits=10, decimal_places=3,
                                           validators=[MinValueValidator(0.01)])
    included_in_mol = models.NullBooleanField(blank=True, null=True)
    linking_of_bids = models.BooleanField()
    metering_point_id = models.TextField()
    localization_factor = models.TextField(blank=True, null=True)
    start_of_delivery = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class MeritOrderList(models.Model):
    service_product = models.ForeignKey(DeliveryPeriod, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    list_json = models.TextField()

    objects = models.DjongoManager()
