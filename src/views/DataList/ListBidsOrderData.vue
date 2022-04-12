<template>
    <div class="view-content">
        <transition name="modal">
            <modal v-if="showModal">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                        <div class="modalActive">
                            <div class="modal-container" v-if="bid_serializer != ''">
                                <div class="modal-header">
                                    <slot name="header">
                                        Selected bid : bid_{{ bid_serializer.product_name }}_{{ bid_serializer.id }}
                                    </slot>
                                </div>
                                <div class="modal-body">
                                    <table class="table table-striped" id="tblGrid">
                                        <thead>
                                          <tr>
                                            <th>Field</th>
                                            <th>Value</th>
                                          </tr>
                                        </thead>
                                        <tbody>
                                          <tr v-for="val, key in bid_serializer">
                                            <td>{{ key }}</td>
                                            <td>{{ val }}</td>
                                          </tr>
                                        </tbody>
                                      </table>
                                </div>
                                <div class="modal-footer">
                                    <slot name="footer">
                                        <button class="btn btn-primary" @click="showModal = false">
                                        OK
                                        </button>
                                    </slot>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </modal>
        </transition>
        <div class="listing-content">
            <div class="filter-wrapper">
                <div class="product-filter">
                    <select v-model="product_name">
                        <option value="" disabled selected>Product Name</option>
                        <option value="">No filter</option>
                        <option v-for="option in product_list" v-bind:value="option">{{ option }}</option>
                    </select>
                </div>
                <div class="delivery_period-filter">
                    <select v-model="service_product_id">
                        <option value="" disabled selected>Delivery period</option>
                        <option value="">No filter</option>
                        <option v-for="option in delivery_period_list" v-bind:value="option.id">{{ option.display }}</option>
                    </select>
                </div>
            </div>
            <div class="warningselect" style="text-align: center;" v-if="warningselect">You need to select a product then a delivery period to display a MOL</div>
            <div class="tablewrapper" v-for="bid in mol" @click="showModal=true; objectSelectedId=bid.id">
                <div>
                    <div class="tablerowwrapper">
                        <div class="tablerowwrapper-left">
                            <div class="tablerowwrappername">
                                <div>Identifier : bid_{{ bid.product_name }}_{{ bid.id }}</div>
                            </div>
                            <div class="tablerowwrapperdetails" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
                                <div>Details : Price {{ bid.price }}, Power {{ bid.power_constraint_by_grid }} ...</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "ListBidsMeritOrderData",
    data() {
        return {
            bid_list: null,
            showModal: false,
            objectSelectedId: null,
            product_list: null,
            product_name: "",
            delivery_period_list: null,
            service_product_id: "",
            serializer_date: null,
            mol: null,
            bid_serializer: "",
            warningselect: true
        }
    },
    mounted() {
        var self = this;
        this.$axios
            .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/meritorderlist/')
            .then(function (response) {
                self.serializer_date = response.data;
                self.product_list = self.getDistinctProduct(response.data);
            })
    },
    methods: {
        getDistinctProduct(json){
            var lookup = {};
            var items = json;
            var result = [];

            for (var item, i = 0; item = items[i++];) {
              var name = item.product_name;

              if (!(name in lookup)) {
                lookup[name] = 1;
                result.push(name);
              }
            }
            return result.sort();
        },
        getDistinctDeliveryPeriod(json, product_name){
            var lookup = {};
            var items = json;
            var result = [];

            for (var item, i = 0; item = items[i++];) {
              var delivery_period_start_date = item.delivery_period_start.slice(0, 10);
              var delivery_period_end_date = item.delivery_period_end.slice(0, 10);
              var delivery_period_start_time = new Date(item.delivery_period_start).toLocaleTimeString();
              var delivery_period_end_time = new Date(item.delivery_period_end).toLocaleTimeString();
              var name = delivery_period_start_date + " " + delivery_period_start_time + " to " + delivery_period_end_date + " " + delivery_period_end_time;

              if (!(name in lookup) && item.product_name == product_name) {
                lookup[name] = 1;
                result.push({"display": name, "id": item.service_product});
              }
            }
            return result.sort();
        },
        getMol(json, product_name, service_product_id){
            var lookup = {};
            var items = json;
            var result = [];

            for (var item, i = 0; item = items[i++];) {
              if (item.product_name == product_name && item.service_product == service_product_id) {
                var mol = JSON.parse(item.list_json.replace(/'/g, "\""));
              }
            }

            for (var item, i = 0; item = mol[i++];) {
                item["product_name"] = product_name;
            }

            return mol;
        }
    },
  watch: {
    product_name: function(){
        if(this.product_name != ""){
            this.delivery_period_list = this.getDistinctDeliveryPeriod(this.serializer_date, this.product_name);
        } else {
            this.mol = "";
            this.service_product_id = "";
        }
    },
    service_product_id: function(){
        if(this.service_product_id != ""){
            this.mol = this.getMol(this.serializer_date, this.product_name, this.service_product_id);
            this.warningselect = false;
        } else {
            this.mol = "";
        }
    },
    showModal: function(){
        if(this.showModal == true && this.objectSelectedId != ""){
            var self = this;
            this.$axios
                .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/bids/' + self.objectSelectedId)
                .then(function (response) {
                    self.bid_serializer = response.data;
                    console.log(self.bid_serializer);
                })
        } else {
            this.bid_serializer = "";
        }
    },

  },
};
</script>
