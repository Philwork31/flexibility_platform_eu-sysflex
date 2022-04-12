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

from rest_framework.routers import DefaultRouter
from django.urls import path

from . import views

router = DefaultRouter()

# Register the routes for the viewsets
router.register(r'needs', views.FlexibilityNeedViewSet)
router.register(r'needs_to_register', views.FlexibilityNeedToRegisterViewSet)
router.register(r'potentials', views.FlexibilityPotentialViewSet)
router.register(r'potentials_to_register', views.FlexibilityPotentialToRegisterViewSet)
router.register(r'potentialgridimpactassessmentresults', views.PotentialGridImpactAssessmentResult)

urlpatterns = [
    path('needsbysoandproduct/<str:so_id>/<str:product_id>', views.NeedsBySoAndProductListApi.as_view()),
    path('needsbysoid/<str:so_id>', views.NeedsBySoListApi.as_view()),
    path('potentialsbyfsp/<str:fsp_id>', views.PotentialsByFspListApi.as_view()),
    path('potential_register/', views.potential_register),
    path('need_register/', views.need_register),
    path('cancelflexibilityneed/<str:need_id>', views.need_cancel),
    path('cancelflexibilitypotential/<str:potential_id>', views.potential_cancel),
    path('needsbyso/<str:so_name>', views.FlexibilityNeedBySOViewSet.as_view()),
    path('needsbyso/<str:so_name>/', views.FlexibilityNeedBySOViewSet.as_view()),
]

urlpatterns += router.urls
