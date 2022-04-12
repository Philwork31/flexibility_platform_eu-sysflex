from datetime import timedelta

from bidding.models import MeritOrderList, FlexibilityBid
from flexibility_platform.models import DeliveryPeriod, Product


class MeritOrderListProcess:

    @staticmethod
    def generate_mol():
        next_service_period = DeliveryPeriod.objects.filter(status="waiting").latest("starting_date")
        all_product = Product.objects.all()
        for product in all_product:
            list_bid_by_product = MeritOrderListProcess.mol_bidlist_by_product(product, next_service_period)
            mol = MeritOrderList(service_product=next_service_period, product=product, list_json=list_bid_by_product)
            mol.save()

    @staticmethod
    def mol_bidlist_by_product(product, next_service_period):
        bids_by_product_ordered = list(FlexibilityBid.objects.filter(product=product,
                                                                     start_of_delivery__range=(
                                                                     next_service_period.starting_date - timedelta(
                                                                         minutes=1),
                                                                     next_service_period.ending_date - timedelta(
                                                                         minutes=1))).values(
            'flexibility_service_provider',
            'product',
            'price',
            'power_constraint_by_grid',
            'power_left_after_activation',
            'localization_factor',
            'id'))
        bids_by_product_ordered = sorted(bids_by_product_ordered, key=lambda i: float(i['price']))
        return bids_by_product_ordered
