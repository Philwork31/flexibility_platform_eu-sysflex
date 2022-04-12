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

from django.shortcuts import render
from django.http import HttpResponse
import requests
from django.views.decorators.csrf import csrf_exempt

def response_access_control_headers(content, status):
    response = HttpResponse(content, status=status)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "PORT, GET, OPTIONS"
    response["Access-Control-Max-Age"] = "1000"
    response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response

@csrf_exempt
def data_content_test(request):
    """
    Test method to check if others are working
    @TODO : dev only, remove it on final product
    :param request: request from the view with data test
    :return: status 200
    """

    post_data = request.POST
    print(post_data)
    """
    req = requests.post(request.build_absolute_uri('/api/v1/needs/'), data=post_data)
    print(req.content)
    """
    response = response_access_control_headers()
    return response


@csrf_exempt
def register_flexibility_need(request):
    """
    Method who simulate DEP comportment and send post to flexibility platform to inform that a flexibility need has
    been registered.
    :param request: request from the view with flexibility need post data
    :return: status 200
    """
    post_data = request.POST
    req = requests.post(request.build_absolute_uri('/api/v1/need_register/'), data=post_data)
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def register_product_proposition(request):
    """
    Method who simulate DEP comportment and send post to flexibility platform to inform that a flexibility need has
    been registered.
    :param request: request from the view with flexibility need post data
    :return: status 200
    """
    post_data = request.POST
    req = requests.post(request.build_absolute_uri('/api/v1/product/'), data=post_data)
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def register_flexibility_potential(request):
    """
    Method who simulate DEP comportment and send post to flexibility platform to inform that a flexibility potential
    has been registered.
    :param request: request from the view with flexibility potential post data
    :return: status 200
    """
    post_data = request.POST
    req = requests.post(request.build_absolute_uri('/api/v1/potential_register/'), data=post_data)
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def open_call_for_tenders(request):
    """
    Method who simulate DEP comportment and send post to flexibility platform to inform that an auction has been
    opened.
    :param request: request from the view with auction opening post data
    :return: status 200
    """
    post_data = request.POST
    req = requests.post(request.build_absolute_uri('/api/v1/registercallfortenders/'), data=post_data)
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def close_call_for_tenders(request):
    """
    Method who simulate DEP comportment and send post to flexibility platform to inform that an auction has been
    closed.
    :param request: request from the view with auction closing post data
    :return: status 200
    """
    post_data = request.POST
    req = requests.post(request.build_absolute_uri('/api/v1/cancelcallfortenders/'), data=post_data)
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_auction_list(request):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the auction list
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/auctions/'))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_product_list(request):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the product list
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/product/'))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_product_with_need_list(request):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the product list
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/productwithneed/'))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_so_list(request):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the so list
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/so/'))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_fsp_list(request):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the fsp list
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/fsp/'))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_active_product_list(request):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the active product list
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/activeproduct/'))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_cancellable_product_list(request):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the active product list
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/cancellableproduct/'))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_bids_by_fsp_and_product(request, fsp_id, product_id):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the active product list
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/bidsbyfspandproduct/' + fsp_id + '/' + product_id))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_cft_by_so_list(request, so_id):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the cft list by so
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/callfortendersbyso/' + so_id))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_need_by_so_list(request, so_id):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the cft list by so
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/needsbyso/' + so_id))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def get_potential_by_fsp_list(request, fsp_id):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the cft list by so
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/potentialsbyfsp/' + fsp_id))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def cancel_flexibility_need(request, need_id):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the cft list by so
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/cancelflexibilityneed/' + need_id))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def cancel_flexibility_potential(request, potential_id):
    """
    Method who simulate DEP comportment and ask the flexibility platform for the cft list by so
    :return: status 200
    """
    req = requests.get(request.build_absolute_uri('/api/v1/cancelflexibilitypotential/' + potential_id))
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def register_congestion_matrix(request):
    """
    Method who simulate DEP comportment and send post to flexibility platform to inform that a congestion matrix
    has been registered.
    :param request: request from the view with congestion matrix post data
    :return: status 200
    """
    post_data = request.POST
    req = requests.post(request.build_absolute_uri('/api/v1/cmatrices/'), data=post_data)
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def submit_flexibility_bid(request):
    """
    Method who simulate DEP comportment and send post to flexibility platform to inform that a flexibility bid has been
    registered.
    :param request: request from the view with flexibility bid post data
    :return: status 200
    """
    post_data = request.POST
    req = requests.post(request.build_absolute_uri('/api/v1/registerbid/'), data=post_data)
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def update_flexibility_bid(request):
    """
    Method who simulate DEP comportment and send post to flexibility platform to inform that a flexibility bid has been
    registered.
    :param request: request from the view with flexibility bid post data
    :return: status 200
    """
    post_data = request.POST
    req = requests.post(request.build_absolute_uri('/api/v1/updatebid/'), data=post_data)
    response = response_access_control_headers(req.content, req.status_code)
    return response


@csrf_exempt
def inform_winning_bid(request):
    """
    Method who simulate DEP comportment and send post to FSP to inform them about a winning bid.
    @TODO : Need completion.
    :param request: request from the view with winning bid data
    :return: status 200
    """
    return HttpResponse('')
