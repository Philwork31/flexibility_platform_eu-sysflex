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
                                        Selected activation order : {{ json.id }}
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
                <div class="fsp-filter">
                    <select v-model="fsp_id" >
                        <option value="" disabled selected>FSP Id</option>
                        <option value="">No filter</option>
                        <option v-for="option in fsp_list">{{ option }}</option>
                    </select>
                </div>
            </div>
            <div class="tablewrapper" v-for="json in jsons" @click="showModal=true; objectSelectedId=json.id">
                <div v-if="json.fsp_name == fsp_id || fsp_id === ''">
                    <div class="tablerowwrapper">
                        <div class="tablerowwrapper-left">
                            <div class="tablerowwrappername">
                                <div>Aggregator {{ json.identification }} (name: {{ json.name }})</div>
                            </div>
                            <div class="tablerowwrapperdetails" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
                                <div>Details : Contact: {{ json.contact }}, FSP: {{ json.fsp_name}}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="fp-submit-form fp-field" style="text-align: center; margin-top: 5px;">
                <button v-on:click="updateAggregatorList()" type="button">Update</button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "ListAggregatorInformationsData",
    data() {
        return {
            jsons: null,
            showModal: false,
            objectSelectedId: null,
            fsp_list: null,
            fsp_id: "",
        }
    },
    mounted() {
        var self = this;
        this.$axios
            .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/aggregatorinformation/?format=json')
            .then(function (response) {
                var date_options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
                self.jsons = response.data;
                self.fsp_list = self.getDistinctFsp(self.jsons);
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
        updateAggregatorList(){
            alert("Service not implemented in Estfeed yet.");
        }
    },
};
</script>
