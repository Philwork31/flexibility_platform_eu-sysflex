<template>
    <div class="view-content notification-view">
        <transition name="modal">
            <modal v-if="showModal">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                        <div>
                            <div class="modal-container">
                                <div class="modal-header">
                                    <slot name="header">
                                        Selected item
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
                                          <tr v-for="val, key in objectJsons">
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
                    <select v-model="type_id" >
                        <option value="" disabled selected>Type</option>
                        <option value="">No filter</option>
                        <option v-for="option in type_list">{{ option }}</option>
                    </select>
                </div>
                <div class="product-filter">
                    <select v-model="product_id">
                        <option value="" disabled selected>Origin</option>
                        <option value="">No filter</option>
                        <option v-for="option in product_list">{{ option }}</option>
                    </select>
                </div>
            </div>
            <div class="tablewrapper" v-for="json in jsons">
                <div v-if="(json.types.includes(type_id) && json.product_name == product_id) ||
                (type_id === '' && json.product_name == product_id) ||
                (json.types.includes(type_id) && product_id === '') ||
                (type_id === '' && product_id === '')">
                    <div class="tablerowwrapper">
                        <div class="tablerowwrapper-left">
                            <div class="tablerowwrappername">
                                <div @click="modalEventListener" v-html="json.text"></div>
                            </div>
                            <div class="tablerowwrapperdetails" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
                                <div>Type : {{ json.types }}</div>
                            </div>
                        </div>
                        <div class="tablerowwrapper-right">
                            <div class="tablerowwrappercreated">
                                <div>Created at : {{ json.created_at }}</div>
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
    name: "ListNotificationData",
    data() {
        return {
            objectJsons: null,
            jsons: null,
            showModal: false,
            objectSelectedId: null,
            type_list: null,
            type_id: "",
            product_id: "",
        }
    },
    mounted() {
        var self = this;
        this.$axios
            .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/event_recorder/?format=json')
            .then(function (response) {
                var date_options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
                self.jsons = self.formatStringNotification(response.data);
                self.jsons.forEach(function (element) {
                    var created_at_object = new Date(element.created_at)
                    element.created_at = created_at_object.toLocaleDateString('en-EN', date_options)
                });
                self.type_list = self.getDistinctType(self.jsons);
            })
    },
    methods: {
        getDistinctType(json){
            var lookup = {};
            var event_items = json;
            var result = [];

            for (var event_item, i = 0; event_item = event_items[i++];) {
                var business_items = JSON.parse(event_item.business_object_info);
                for(var business_item, j = 0; business_item = business_items[j++];) {
                  var name = business_item.type;

                  if (!(name in lookup)) {
                    lookup[name] = 1;
                    result.push(name);
                  }
                }
            }
            return result.sort();
        },
        formatStringNotification: function(data){
            for (var k = 0; k < data.length; k++){
                var jsonData = JSON.parse(data[k].business_object_info);
                for (var i = 0; i < jsonData.length; i++) {
                    data[k].text = data[k].text.replace("%" + (i+1), '<a iditem="' + jsonData[i].id + '" class="' + jsonData[i].type + '">' + jsonData[i].text + '</a>');
                }
            }
            return data;
        },
        modalEventListener: function(e){
            if (['product', 'fsp', 'so', 'need', 'potential', 'cft', 'bid', 'metering_data', 'schedule', 'verification', 'activation_request'].indexOf(e.target.className) >= 0) {
                this.getModalInfo(e.target.className, e.target.attributes.iditem.nodeValue);
            }
        },
        getModalInfo: function(type, id){
            if(type == "product"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/product/" + id + "/?format=json" }
            if(type == "fsp"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/fsp/" + id + "/?format=json" }
            if(type == "so"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/so/" + id + "/?format=json" }
            if(type == "need"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/needs/" + id + "/?format=json" }
            if(type == "potential"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/potentials/" + id + "/?format=json" }
            if(type == "cft"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/callfortenders/" + id + "/?format=json" }
            if(type == "bid"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/bids/" + id + "/?format=json" }
            if(type == "metering_data"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/meteringdata/" + id + "/?format=json" }
            if(type == "schedule"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/schedule/" + id + "/?format=json" }
            if(type == "verification"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/verification/" + id + "/?format=json" }
            if(type == "activation_request"){ var url = location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/flexibilityrequestactivation/" + id + "/?format=json" }
            var self = this;
            this.$axios
                .get(url)
                .then(function (response) {
                    self.objectJsons = response.data;
                    self.showModal = true;
                }).catch(function (error) {
                    // handle error
                    self.objectJsons = {"error": "Not found"};
                    self.showModal = true;
                })
        }
    },
};
</script>
