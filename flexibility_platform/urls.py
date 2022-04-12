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

"""flexibility_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'fsp', views.FlexibilityServiceProviderViewSet)
router.register(r'product', views.ProductViewSet)
router.register(r'productnotvalidated', views.ProductNotValidatedViewSet)
router.register(r'productwithneed', views.ProductWithNeedViewSet)
router.register(r'so', views.SystemOperatorViewSet)
router.register(r'secondaryso', views.SecondarySystemOperatorViewSet)
router.register(r'aggregatorinformation', views.AggregatorInformationViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dep_simulator/', include('dep_simulator.urls')),
    path('api/v1/', include('event_recorder.urls')),
    path('api/v1/', include('prequalification.urls')),
    path('api/v1/', include('bidding.urls')),
    path('api/v1/', include('activation.urls')),
    path('api/v1/', include('grid_impact.urls')),
    path('api/v1/', include('verification.urls')),
    path('estfeed/', include('estfeed_adapter.urls')),
    path('api/v1/', include(router.urls)),
    path('api/v1/register_product/', views.product_register),
    path('api/v1/update_product/', views.product_update),
    path('api/v1/propose_product/', views.product_propose),
    path('test/', views.tests),
    path('test2/', views.tests2),
    path('test3/', views.tests3),
    path('api/v1/validate_product/<str:product_id>', views.product_validate),
    path('api/v1/cancel_product/<str:product_id>', views.product_cancel),
    path('api/v1/productbyso/<str:so_name>', views.ProductBySoListApi.as_view()),
    path('api/v1/lastdeliveryperiod/', views.CurrentDeliveryPeriodViewSet.as_view(), name="lastdeliveryinstance"),
    path('', views.index)
    # path('', TemplateView.as_view(template_name='index.html'), name='EU-SysFlex - Flexibility Platform')
]
