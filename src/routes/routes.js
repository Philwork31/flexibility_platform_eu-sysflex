import DashBoardLayout from "../views/Layouts/DashboardLayout.vue";
import Welcome from "../views/Layouts/Welcome.vue";
import Needs from "../views/Layouts/Needs.vue";
import Potentials from "../views/Layouts/Potentials.vue";
import PotentialsGridImpactAssessment from "../views/Layouts/PotentialsGridImpactAssessmentResult.vue";
import CallForTenders from "../views/Layouts/CallForTenders.vue";
import Bids from "../views/Layouts/Bids.vue";
import BidsGridImpactAssessment from "../views/Layouts/BidsGridImpactAssessmentResult.vue";
import RegisterProduct from "../views/Layouts/RegisterProduct.vue";
import Product from "../views/Layouts/Product.vue";
import BidsOrder from "../views/Layouts/BidsOrder.vue";
import ProductsToValidate from "../views/Layouts/ProductsToValidate.vue";
import Notification from "../views/Layouts/Notification.vue";
import RegisterPotentialDemo from "../views/Layouts/RegisterPotentialDemo.vue";
import RegisterBidDemo from "../views/Layouts/RegisterBidDemo.vue";
import RegisterMeteringDataDemo from "../views/Layouts/RegisterMeteringDataDemo.vue";
import RegisterScheduleDemo from "../views/Layouts/RegisterScheduleDemo.vue";
import ActivationRequests from "../views/Layouts/ActivationRequests.vue";
import ActivationOrder from "../views/Layouts/ActivationOrder.vue";
import Schedules from "../views/Layouts/Schedules.vue";
import MeteringDatas from "../views/Layouts/MeteringDatas.vue";
import RegisterVerification from "../views/Layouts/RegisterVerification.vue";
import Verification from "../views/Layouts/Verification.vue";
import AggregatorInformation from "../views/Layouts/AggregatorInformation.vue";


const routes = [{
    path: '/',
    component: DashBoardLayout,
    redirect: "/l",
    children: [{
            path: '/:theme/',
            searchbar: false,
            component: Welcome
        },
        {
            path: '/:theme/home/',
            searchbar: false,
            component: Welcome
        },

        {
            path: '/:theme/needs/',
            name: 'Needs',
            searchbar: true,
            component: Needs
        },

        {
            path: '/:theme/potentials/',
            name: 'Potentials',
            searchbar: true,
            component: Potentials
        },

        {
            path: '/:theme/potentialsgridimpactassessmentresult/',
            name: 'Potentials Grid Impact Assessment Result',
            searchbar: true,
            component: PotentialsGridImpactAssessment
        },

        {
            path: '/:theme/callfortenders/',
            name: 'Call for tenders',
            searchbar: true,
            component: CallForTenders
        },

        {
            path: '/:theme/bids/',
            name: 'Bids',
            searchbar: true,
            component: Bids
        },

        {
            path: '/:theme/bidsgridimpactassessmentresult/',
            name: 'Bids Grid Impact Assessment Result',
            searchbar: true,
            component: BidsGridImpactAssessment
        },

        {
            path: '/:theme/register_product/',
            name: 'Register product',
            searchbar: true,
            component: RegisterProduct
        },

        {
            path: '/:theme/product/',
            name: 'Product',
            searchbar: true,
            component: Product
        },
        {
            path: '/:theme/bids-order/',
            name: 'Bids Order',
            searchbar: true,
            component: BidsOrder
        },
        {
            path: '/:theme/products-to-validate/',
            name: 'Products to validate',
            searchbar: true,
            component: ProductsToValidate
        },
        {
            path: '/:theme/notifications/',
            name: 'Notification',
            searchbar: false,
            component: Notification
        },
        {
            path: '/:theme/potential-register-demo/',
            name: 'Potential register (demo)',
            searchbar: false,
            component: RegisterPotentialDemo
        },
        {
            path: '/:theme/bid-register-demo/',
            name: 'Potential register (demo)',
            searchbar: false,
            component: RegisterBidDemo
        },
        {
            path: '/:theme/metering-data-register-demo/',
            name: 'Metering data register (demo)',
            searchbar: false,
            component: RegisterMeteringDataDemo
        },
        {
            path: '/:theme/schedule-register-demo/',
            name: 'Schedule register (demo)',
            searchbar: false,
            component: RegisterScheduleDemo
        },
        {
            path: '/:theme/activation-requests/',
            name: 'Activation requests',
            searchbar: false,
            component: ActivationRequests
        },
        {
            path: '/:theme/activation-order/',
            name: 'Activation order',
            searchbar: false,
            component: ActivationOrder
        },
        {
            path: '/:theme/schedules/',
            name: 'Schedules',
            searchbar: false,
            component: Schedules
        },
        {
            path: '/:theme/meteringdatas/',
            name: 'Metering Datas',
            searchbar: false,
            component: MeteringDatas
        },
        {
            path: '/:theme/register-verification/',
            name: 'Register Verification',
            searchbar: false,
            component: RegisterVerification
        },
        {
            path: '/:theme/verification/',
            name: 'Verification',
            searchbar: false,
            component: Verification
        },
        {
            path: '/:theme/aggregatorinformation/',
            name: 'Aggregator Information',
            searchbar: false,
            component: AggregatorInformation
        },

    ]
}];

export default routes;