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
                                        Selected product : {{ json.product_name }}
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
                                        <button class="btn btn-secondary" @click="showModal = false">
                                        Cancel
                                        </button>
                                        <button class="btn btn-primary" @click="validate()" style="background-color: blue;">
                                        Validate
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
            <div class="tablewrapper" v-for="json in jsons" @click="showModal=true; objectSelectedId=json.id">
                <div>
                    <div class="tablerowwrapper">
                        <div class="tablerowwrapper-left">
                            <div class="tablerowwrappername">
                                <div>Identifier : {{ json.product_name }}</div>
                            </div>
                            <div class="tablerowwrapperdetails" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
                                <div>Details : EIC Code ({{ json.eic_code }}), Divisibility ({{ json.divisibility }}) ...</div>
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
    name: "ListProductsToValidateData",
    data() {
        return {
            jsons: null,
            showModal: false,
            objectSelectedId: null,
            so_list: null,
            product_list: null,
            so_id: "",
            product_id: "",
        }
    },
    mounted() {
        var self = this;
        this.$axios
        .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/productnotvalidated/?format=json')
            .then(function (response) {
                var date_options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
                self.jsons = response.data;
                self.jsons.forEach(function (element) {
                    element.availability = element.availability.replace(/{/g, "").replace(/}/g, "").replace(/\[/g, "")
                        .replace(/\]/g, "").replace(/\"/g, "");
                    var created_at_object = new Date(element.created_at)
                    element.created_at = created_at_object.toLocaleDateString('en-EN', date_options)
                    var updated_at_object = new Date(element.updated_at)
                    element.updated_at = updated_at_object.toLocaleDateString('en-EN', date_options)
                });
                /*
                self.so_list = self.getDistinctSo(self.jsons);
                self.product_list = self.getDistinctProduct(self.jsons);
                */
            })
    },
    methods: {
        validate(){
            this.$axios.get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/validate_product/' + this.objectSelectedId,
            {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            }
            ).then(response => {
              document.location.reload();
          })
        },
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
