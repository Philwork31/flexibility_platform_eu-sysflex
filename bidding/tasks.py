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

from activation.data_management import Activation
from flexibility_platform.celery import app
from grid_impact.data_management import GridImpact
from .globals import MFRR_TIME, GATE_CLOSURE_TIME
from .models import CallForTenders, DeliveryPeriod
from datetime import datetime, timedelta
from django.utils import timezone

# We should remove all cft celery task and base ourselve only on date and "cancelled" status to know the true status
from .process.mol import MeritOrderListProcess


@app.task(bind=True)
def cft_closure_planification(id):
    cft_queryset = CallForTenders.objects.filter(id=id, status="open")
    if cft_queryset.exists():
        CallForTenders.objects.filter(id=id).update(status="close")
        cft_opening_planification.apply_async([id], eta=datetime.now() + timedelta(minutes=MFRR_TIME-GATE_CLOSURE_TIME))


@app.task(bind=True)
def cft_opening_planification(id):
    cft_queryset = CallForTenders.objects.filter(id=id, status__in=["waiting", "close"])
    if cft_queryset.exists():
        CallForTenders.objects.filter(id=id).update(status="open")
        cft_closure_planification.apply_async([id], eta=datetime.now() + timedelta(minutes=GATE_CLOSURE_TIME))


@app.task(bind=True)
def cft_cancelling_planification(id):
    cft_queryset = CallForTenders.objects.filter(id=id, status__in=["open", "close", "waiting"])
    if cft_queryset.exists():
        CallForTenders.objects.filter(id=id).update(status="cancelled")


@app.task(bind=True)
def routine_service_period_start(self, service_period_duration, service_period_gct):
    delivery_period_started = DeliveryPeriod(starting_date=datetime.now(),
                                     ending_date=datetime.now() + timedelta(minutes=service_period_duration),
                                     gct=service_period_gct,
                                     duration=service_period_duration,
                                     status='started')
    delivery_period_started.save()
    delivery_period_waiting = DeliveryPeriod(starting_date=datetime.now() + timedelta(minutes=service_period_duration),
                                     ending_date=datetime.now() + timedelta(minutes=service_period_duration*2),
                                     gct=service_period_gct,
                                     duration=service_period_duration,
                                     status='waiting')
    delivery_period_waiting.save()
    eta_fix = timezone.localtime(timezone.now()).replace(second=0, microsecond=0) + \
              timedelta(minutes=service_period_duration - service_period_gct)
    routine_service_period_gct.apply_async([service_period_duration, service_period_gct], eta=eta_fix)


@app.task(bind=True)
def routine_service_period_gct(self, service_period_duration, service_period_gct):
    delivery_period_to_update = DeliveryPeriod.objects.filter(status="started").latest("starting_date")
    next_service_period = DeliveryPeriod.objects.filter(status="waiting").latest("starting_date")
    delivery_period_to_update.status = "gct"
    delivery_period_to_update.save()
    eta_fix = timezone.localtime(timezone.now()).replace(second=0, microsecond=0) + \
              timedelta(minutes=service_period_gct)
    routine_service_period_end.apply_async([service_period_duration, service_period_gct],
                                           eta=eta_fix)
    # launch data management function here
    GridImpact.bidding_grid_impact_assessment(next_service_period, False)
    MeritOrderListProcess.generate_mol()
    Activation.flexibility_activation_waiting_launch_process()


@app.task(bind=True)
def routine_service_period_end(self, service_period_duration, service_period_gct):
    delivery_period_to_update = DeliveryPeriod.objects.filter(status="gct").latest("starting_date")
    delivery_period_to_update.status = "ended"
    delivery_period_to_update.save()
    delivery_period_to_update = DeliveryPeriod.objects.filter(status="waiting").latest("starting_date")
    delivery_period_to_update.status = "started"
    delivery_period_to_update.save()
    delivery_period = DeliveryPeriod(starting_date=datetime.now() + timedelta(minutes=service_period_duration),
                                     ending_date=datetime.now() + timedelta(minutes=service_period_duration*2),
                                     gct=service_period_gct,
                                     duration=service_period_duration,
                                     status='waiting')
    delivery_period.save()
    eta_fix = timezone.localtime(timezone.now()).replace(second=0, microsecond=0) + \
              timedelta(minutes=service_period_duration - service_period_gct)
    routine_service_period_gct.apply_async([service_period_duration, service_period_gct], eta=eta_fix)
