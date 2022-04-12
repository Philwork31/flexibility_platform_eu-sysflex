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

from rest_framework import viewsets

from .serializers import *
from .models import EventRecorder

'''These viewsets automatically provide `list`, `create`, `retrieve`, `update`
and `destroy` actions for the corresponding model.

    Example for FlexibilityNeed ("needs" here is defined when the route is
    registered at url.py)
        list – list all elements, serves GET to /needs/
        create – create a new element, serves POST to /needs/
        retrieve – retrieves one element, serves GET to /needs/<id>
        update – updates single element, handles PUT/PATCH to /needs/<id>
        destroy – deletes single element, handles DELETE to /needs/<id>
    '''


class EventRecorderViewSet(viewsets.ModelViewSet):
    queryset = EventRecorder.objects.all().order_by('-id')
    serializer_class = EventRecorderSerializer


class EventRecorderLimitedViewSet(viewsets.ModelViewSet):
    queryset = EventRecorder.objects.all().order_by('-id')[:100]
    serializer_class = EventRecorderSerializer
