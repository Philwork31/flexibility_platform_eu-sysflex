<template>
    <div class="view-content">
        <transition name="modal">
            <modal v-if="showModal">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                    <div class="modal-container">
                        <div class="modal-header">
                            <slot name="header">
                                Verification
                            </slot>
                        </div>
                        <div class="modal-body">
                            {{ messageModal }}
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
            </modal>
        </transition>
        <form class="fp-view-form" @submit.prevent="submit()">
            <div class="form-header">
                <h2>Verify activated flexibilities</h2>
            </div>
            <div class="form-content">
                <div class="product_name_field fp-field">
                    <label for="request">Choose an activation request</label>
                    <select class="fp-select" name="request" id="request" v-model="request" required>From: SO, Start of delivery: date, Product: product
                        <option v-for="request in request_list" v-bind:value="request.id">From {{ request.system_operator_name }}, Start of delivery : {{ request.start_of_delivery }}, Product : {{ request.product_name }}</product>
                    </select>
                </div>
                <div class="fp-submit-form fp-field">
                    <button type="submit">Submit</button>
                </div>
            </div>
        </form>
    </div>
</template>


<script>
export default {
  name: "register-verification",
  data() {
	return {
	  request_list: null,
	  request: null,
      showModal: false,
      messageModal: null,
	};
  },
  methods: {
    submit() {
      let formData = new FormData();
      formData.append('activation_request_id', this.request);
      this.$axios.post(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/processverification/", formData,
		{
			headers: {
				"Content-Type": "multipart/form-data"
			}
		}
		).then(response => {
          this.showModal = true;
          this.messageModal = response.data;
      })
      .catch(e => {
        this.showModal = true;
        this.messageModal = "An error happened. Be sure to complete all fields.";
      });
	}
  },
  mounted() {
        var self = this;
        this.$axios
            .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/activationavailableforverif/?format=json")
            .then(function (response) {
                self.request_list = response.data;
                var date_options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
                self.request_list.forEach(function (element) {
                    var start_of_delivery_object = new Date(element.start_of_delivery)
                    element.start_of_delivery = start_of_delivery_object.toLocaleDateString('en-EN', date_options)
                });
            });
  },
};
</script>
