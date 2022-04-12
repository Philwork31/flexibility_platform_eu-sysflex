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
from flexibility_platform.models import SystemOperator, FlexibilityServiceProvider, Product
from django.core.validators import MinValueValidator

UP = '+'
DOWN = '-'
UP_DOWN_CHOICES = (
    (UP, 'Up'),
    (DOWN, 'Down'),
)


class FlexibilityNeed(models.Model):
    system_operator = models.ForeignKey(SystemOperator, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="needproduct")
    total_indicative_power_needed = models.DecimalField(max_digits=10, decimal_places=3, default='0.1')
    preparation_period = models.PositiveIntegerField()
    localization_factor = models.TextField(blank=True, null=True)
    expiration_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class FlexibilityNeedAvailability(models.Model):
    flexibility_need = models.ForeignKey(FlexibilityNeed, related_name='need_availabilitys', on_delete=models.CASCADE)
    availability_start = models.DateTimeField()
    availability_end = models.DateTimeField()

    objects = models.DjongoManager()

    def __str__(self):
        return "{} to {}".format(str(self.availability_start), str(self.availability_end))


class FlexibilityPotential(models.Model):
    fsp = models.ForeignKey(FlexibilityServiceProvider, on_delete=models.CASCADE,)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="potentialproduct")
    power = models.DecimalField(max_digits=11, decimal_places=3, validators=[MinValueValidator(0.01)])
    power_constraint = models.DecimalField(blank=True, null=True, max_digits=11, decimal_places=3,
                                           validators=[MinValueValidator(0.01)])
    preparation_period = models.PositiveIntegerField()
    compliance_demonstration = models.TextField()
    localization_factor = models.TextField(blank=True, null=True)
    metering_point_id = models.TextField()
    baseline_type = models.TextField()
    expiration_date = models.DateTimeField()
    is_prequalified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class FlexibilityPotentialAvailability(models.Model):
    flexibility_potential = models.ForeignKey(FlexibilityPotential, related_name='potential_availabilitys',
                                              on_delete=models.CASCADE)
    availability_start = models.DateTimeField()
    availability_end = models.DateTimeField()

    objects = models.DjongoManager()


class GridImpactAssessmentResult(models.Model):
    system_operator = models.ForeignKey(SystemOperator, on_delete=models.CASCADE)
    potential = models.ForeignKey(FlexibilityPotential, on_delete=models.CASCADE)
    result = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class GridImpactAssessmentInput(models.Model):
    system_operator = models.ForeignKey(SystemOperator, on_delete=models.CASCADE)
    potential = models.ForeignKey(FlexibilityPotential, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=11, decimal_places=3)
    direction = models.CharField(max_length=1, choices=UP_DOWN_CHOICES)
    location = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()


class PrequalificationInformation(models.Model):
    flexibility_potential = models.ForeignKey(FlexibilityPotential, on_delete=models.CASCADE,
                                              related_name="potential_need_prequalified")
    status_prequalification_product = models.TextField()
    status_grid_impact = models.TextField()
    commentary = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.DjongoManager()
