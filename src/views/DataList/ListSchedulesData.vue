<template>
    <div class="view-content">
        <transition name="modal">
            <modal v-if="showModal">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                        <div v-for="json in jsons" v-bind:class="{ modalActive: objectSelectedId == json.id }">
                            <div class="modal-container" v-if="objectSelectedId == json.id">
                                <div class="modal-header">
                                    <slot name="header">
                                        Selected schedule : Schedule of {{ json.start_of_delivery_period }} from {{ json.fsp_name }} for {{ json.product_name }}
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
                                          <tr v-for="val, key in json">
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
                <div class="so-filter">
                    <select v-model="fsp_id" >
                        <option value="" disabled selected>FSP Id</option>
                        <option value="">No filter</option>
                        <option v-for="option in fsp_list">{{ option }}</option>
                    </select>
                </div>
                <div class="product-filter">
                    <select v-model="product_id">
                        <option value="" disabled selected>Product Name</option>
                        <option value="">No filter</option>
                        <option v-for="option in product_list">{{ option }}</option>
                    </select>
                </div>
            </div>
            <div class="tablewrapper" v-for="json in jsons" @click="showModal=true; objectSelectedId=json.id">
                <div v-if="(json.fsp_name == fsp_id && json.product_name == product_id) ||
                (fsp_id === '' && json.product_name == product_id) ||
                (json.fsp_name == fsp_id && product_id === '') ||
                (fsp_id === '' && product_id === '')">
                    <div class="tablerowwrapper">
                        <div class="tablerowwrapper-left">
                            <div class="tablerowwrappername">
                                <div>Schedule of {{ json.start_of_delivery_period }} from {{ json.fsp_name }} for {{ json.product_name }}</div>
                            </div>
                            <div class="tablerowwrapperdetails" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
                                <div>Details : Energy  {{ json.energy }}, Metering point id {{ json.metering_point_id }} ...</div>
                            </div>
                        </div>
                        <div class="tablerowwrapper-right">
                            <div class="tablerowwrappercreated">
                                <div>Created at : {{ json.created_at }}</div>
                            </div>
                            <div class="tablerowwrapperupdated">
                                <div>Updated at : {{ json.updated_at }}</div>
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
    name: "ListSchedulesData",
    data() {
        return {
            jsons: null,
            showModal: false,
            objectSelectedId: null,
            fsp_list: null,
            product_list: null,
            fsp_id: "",
            product_id: "",
        }
    },
    mounted() {
        var self = this;
        this.$axios
            .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/schedule/?format=json')
            .then(function (response) {
                var date_options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
                self.jsons = response.data;
                self.jsons.forEach(function (element) {
                    var created_at_object = new Date(element.created_at)
                    element.created_at = created_at_object.toLocaleDateString('en-EN', date_options)
                    var updated_at_object = new Date(element.updated_at)
                    element.updated_at = updated_at_object.toLocaleDateString('en-EN', date_options)
                    var start_of_delivery_period_object = new Date(element.start_of_delivery_period)
                    element.start_of_delivery_period = start_of_delivery_period_object.toLocaleDateString('en-EN', date_options)
                });
                self.fsp_list = self.getDistinctFsp(self.jsons);
                self.product_list = self.getDistinctProduct(self.jsons);
            })
    },
    methods: {
        getDistinctFsp(json){
            var lookup = {};
            var items = json;
            var result = [];

            for (var item, i = 0; item = items[i++];) {
              var name = item.fsp_name;

              if (!(name in lookup)) {
                lookup[name] = 1;
                result.push(name);
              }
            }
            return result.sort();
        },
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
        }
    },
};
</script>
