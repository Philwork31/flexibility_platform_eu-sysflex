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
from . import views

urlpatterns = [
    path('test/', views.data_content_test, name='Test view'),
    path('register-flexibility-need/', views.register_flexibility_need, name='Register flexibility need'),
    path('register-product-proposition/', views.register_product_proposition, name='Register product proposition'),
    path('open-call-for-tenders/', views.open_call_for_tenders, name='Open call for tenders'),
    path('close-call-for-tenders/', views.close_call_for_tenders, name='Close call for tenders'),
    path('register-congestion-matrix/', views.register_congestion_matrix, name='Register congestion matrix'),
    path('submit-flexibility-bid/', views.submit_flexibility_bid, name='Submit flexibility bid'),
    path('update-flexibility-bid/', views.update_flexibility_bid, name='Update flexibility bid'),
    path('register-flexibility-potential/', views.register_flexibility_potential,
         name='Register flexibility potential'),
    path('get-auction-list/', views.get_auction_list, name='Get auction list'),
    path('get-product-list/', views.get_product_list, name='Get product list'),
    path('get-product-with-need-list/', views.get_product_list, name='Get auction list'),
    path('get-so-list/', views.get_so_list, name='Get so list'),
    path('get-fsp-list/', views.get_fsp_list, name='Get fsp list'),
    path('get-active-product-list/', views.get_active_product_list, name='Get active product list'),
    path('get-cancellable-product-list/', views.get_cancellable_product_list, name='Get cancellable product list'),
    path('get-bids-by-fsp-and-product/<str:fsp_id>/<str:product_id>', views.get_bids_by_fsp_and_product,
         name='Get bids list by fsp and product'),
    path('get-cft-by-so-list/<str:so_id>', views.get_cft_by_so_list, name='Get cft by so list'),
    path('get-need-by-so-list/<str:so_id>', views.get_need_by_so_list, name='Get need by so list'),
    path('get-potential-by-fsp-list/<str:fsp_id>', views.get_potential_by_fsp_list, name='Get potential by fsp list'),
    path('cancel-flexibility-need/<str:need_id>', views.cancel_flexibility_need, name='Cancel flexibility need'),
    path('cancel-flexibility-potential/<str:potential_id>', views.cancel_flexibility_potential, name='Cancel flexibility potential'),
]
