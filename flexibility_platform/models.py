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
from django.core.validators import MinValueValidator, MaxValueValidator


SERVICE_PERIOD_CHOICES = (
    ('started', 'STARTED'),
    ('gct', 'GCT'),
    ('waiting', 'WAITING'),
    ('ended', 'ENDED'),
)


UP = '+'
DOWN = '-'
UP_DOWN_CHOICES = (
    (UP, 'Up'),
    (DOWN, 'Down'),
)


class SystemOperator(models.Model):
    eic_code = models.TextField()
    identification = models.TextField(unique=True)
    url = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.DjongoManager()

    def __str__(self):
        return self.identification


class Product(models.Model):
    system_operator = models.ForeignKey(SystemOperator, null=True, blank=True, on_delete=models.SET_NULL)
    eic_code = models.TextField()
    product_name = models.TextField()
    price_conditions = models.DecimalField(max_digits=10, decimal_places=3,
                                           validators=[MinValueValidator(0.01), MaxValueValidator(5000)])
    resolution = models.DecimalField(max_digits=10, decimal_places=3,
                                     validators=[MinValueValidator(0.01)])
    divisibility = models.BooleanField()
    ramping_period = models.PositiveIntegerField()
    delivery_period = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(60)])
    validity = models.PositiveIntegerField()
    pricing_method = models.TextField()
    gate_closure_time = models.PositiveIntegerField()
    direction = models.CharField(max_length=5, choices=UP_DOWN_CHOICES)
    validated_by_fpo = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()

    def __str__(self):
        return self.product_name


class SecondarySystemOperator(models.Model):
    original = models.ForeignKey(SystemOperator, on_delete=models.CASCADE, related_name="original_id")
    is_secondary_of_id = models.ForeignKey(SystemOperator, on_delete=models.CASCADE, related_name="is_secondary_of_id")

    objects = models.DjongoManager()

    def __str__(self):
        return "%s secondary of %s" % (self.original.identification, self.is_secondary_of_id.identification)


class FlexibilityServiceProvider(models.Model):
    eic_code = models.TextField()
    identification = models.TextField(unique=True)
    baseline_scenario = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    objects = models.DjongoManager()

    def __str__(self):
        return self.identification


class AggregatorInformation(models.Model):
    identification = models.TextField()
    name = models.TextField()
    contact = models.TextField()
    fsp = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE)

    objects = models.DjongoManager()

    def __str__(self):
        return self.identification


class DeliveryPeriod(models.Model):
    starting_date = models.DateTimeField()
    ending_date = models.DateTimeField()
    gct = models.PositiveIntegerField()
    duration = models.PositiveIntegerField()
    status = models.CharField(max_length=10, choices=SERVICE_PERIOD_CHOICES, default='started')

    objects = models.DjongoManager()


# Reset Delivery Period on server start - Model side (very experimental, i hope it never repeat after server start)
DeliveryPeriod.objects.filter(status="started").update(status="ended")
DeliveryPeriod.objects.filter(status="gct").update(status="ended")
DeliveryPeriod.objects.filter(status="waiting").update(status="ended")
