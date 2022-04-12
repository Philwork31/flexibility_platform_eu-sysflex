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
router.register(r'callfortenders', views.CallForTendersViewSet)
router.register(r'callfortendersbyproduct', views.CallForTendersByProductViewSet)
router.register(r'activeproduct', views.ActiveProductViewSet)
router.register(r'cancellableproduct', views.CancellableProductViewSet)
router.register(r'bids', views.FlexibilityBidsViewSet)
router.register(r'meritorderlist', views.MeritOrderListViewSet)


urlpatterns = [
    path('bidsbyproduct/<str:product_id>', views.BidsByProductListApi.as_view()),
    path('bidsbyfspandproduct/<str:fsp_id>/<str:product_id>', views.BidsByFspAndProductListApi.as_view()),
    path('callfortendersbysoid/<str:so_id>', views.CallForTendersBySoIdListApi.as_view()),
    path('callfortendersbysoname/<str:so_name>/', views.CallForTendersBySoNameListApi.as_view()),
    path('callfortendersbyso/<str:so_name>', views.CallForTendersBySoListApi.as_view()),
    path('registercallfortenders/', views.call_for_tenders_register),
    path('cancelcallfortenders/', views.call_for_tenders_cancel),
    path('registerbid/', views.bid_register),
    path('updatebid/', views.bid_update),
    path('resetcft/', views.reset_cft),
    path('activateserviceperiod/', views.activate_service_period),
    path('deactivateserviceperiod/', views.deactivate_service_period),
    path('generatemoltest/', views.generate_mol_test),
]

urlpatterns += router.urls
