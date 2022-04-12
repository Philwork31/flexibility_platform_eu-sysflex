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

from django.urls import path
from . import views, request_to_estfeed
from . import tests

urlpatterns = [
    path('test_request_hour_estfeed/', tests.test_request_hour, name='Test view hour'),
    path('estfeed_request/', views.get_estfeed_request, name='Get Estfeed Request'),
    path('test_send_activation_order/', request_to_estfeed.test_send_activation_order, name='Test send activation order')
]
