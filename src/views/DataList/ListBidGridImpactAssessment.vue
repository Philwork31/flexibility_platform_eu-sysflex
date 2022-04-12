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
                                        Bid grid impact assessment result
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
                    <select v-model="so_id" >
                        <option value="" disabled selected>System operator</option>
                        <option value="">No filter</option>
                        <option v-for="option in so_list">{{ option }}</option>
                    </select>
                </div>
                <div class="bid-filter">
                    <select v-model="bid_id">
                        <option value="" disabled selected>Bid</option>
                        <option value="">No filter</option>
                        <option v-for="option in bid_list">{{ option }}</option>
                    </select>
                </div>
            </div>
            <div class="tablewrapper" v-for="json in jsons" @click="showModal=true; objectSelectedId=json.id">
                <div v-if="(json.system_operator_name == so_id && json.bid_name == bid_id) ||
                (so_id === '' && json.bid_name == bid_id) ||
                (json.system_operator_name == so_id && bid_id === '') ||
                (so_id === '' && bid_id === '')">
                    <div class="tablerowwrapper">
                        <div class="tablerowwrapper-left">
                            <div class="tablerowwrappername">
                                <div>Identifier : {{ json.bid_name }}</div>
                            </div>
                            <div class="tablerowwrapperdetails" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
                                <div>Details : Result {{ json.result }} </div>
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
    name: "ListBidGridImpactAssessment",
    data() {
        return {
            jsons: null,
            showModal: false,
            objectSelectedId: null,
            so_list: null,
            bid_list: null,
            so_id: "",
            bid_id: "",
        }
    },
    mounted() {
        var self = this;
        this.$axios
            .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/bidgridimpactassessmentresults/?format=json')
            .then(function (response) {
                var date_options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
                self.jsons = response.data;
                self.jsons.forEach(function (element) {
                    var created_at_object = new Date(element.created_at)
                    element.created_at = created_at_object.toLocaleDateString('en-EN', date_options)
                    var updated_at_object = new Date(element.updated_at)
                    element.updated_at = updated_at_object.toLocaleDateString('en-EN', date_options)
                });
                self.so_list = self.getDistinctSo(self.jsons);
                self.bid_list = self.getDistinctBid(self.jsons);
            })
    },
    methods: {
        getDistinctSo(json){
            var lookup = {};
            var items = json;
            var result = [];

            for (var item, i = 0; item = items[i++];) {
              var name = item.system_operator_name;

              if (!(name in lookup)) {
                lookup[name] = 1;
                result.push(name);
              }
            }
            return result.sort();
        },
        getDistinctBid(json){
            var lookup = {};
            var items = json;
            var result = [];

            for (var item, i = 0; item = items[i++];) {
              var name = item.bid_name;

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
