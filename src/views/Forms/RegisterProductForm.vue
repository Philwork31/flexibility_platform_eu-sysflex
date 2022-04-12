<template>
    <div class="view-content">
        <transition name="modal">
            <modal v-if="showModal">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                    <div class="modal-container">
                        <div class="modal-header">
                            <slot name="header">
                                Product registration
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
                <h2>Register a product</h2>
            </div>
            <div class="form-content">
                <div class="eic_code_field fp-field">
                    <label for="eic_code">EIC Code</label>
                    <input class="fp-input" type="textarea" name="eic_code" v-model="eic_code" required>
                </div>
                <div class="product_name_field fp-field">
                    <label for="product_name">Product name</label>
                    <input class="fp-input" type="text" name="product_name" v-model="product_name" required>
                </div>
                <div class="price_conditions_field fp-field">
                    <label for="price_conditions">Price conditions</label>
                    <input class="fp-input" type="number" name="price_conditions" v-model="price_conditions" required>
                </div>
                <div class="resolution_field fp-field">
                    <label for="resolution">Resolution (MW)</label>
                    <input class="fp-input" type="number" name="resolution" v-model="resolution" step="0.01" required>
                </div>
                <div class="divisibility_field fp-field">
                    <label for="divisibility">Divisibility</label>
                    <select class="fp-select" v-model="divisibility">
                        <option value="True" class="option-fix">YES</option>
                        <option value="False" class="option-fix">NO</option>
                    <select>
                </div><div class="direction_field fp-field">
                    <label for="direction">Direction</label>
                    <select class="fp-select" v-model="direction" required>
                        <option value="+" class="option-fix">+</option>
                        <option value="-" class="option-fix">-</option>
                    </select>
                </div>
                <div class="ramping_period_field fp-field">
                    <label for="ramping_period">Ramping period (minute)</label>
                    <input class="fp-input" type="number" name="ramping_period" v-model="ramping_period" required>
                </div>
                <div class="validity_field fp-field">
                    <label for="validity">Validity (minute)</label>
                    <input class="fp-input" type="number" name="validity" v-model="validity" required>
                </div>
                <div class="pricing_method_field fp-field">
                    <label for="pricing_method">Pricing method</label>
                    <input class="fp-input" type="textarea" name="pricing_method" v-model="pricing_method" required>
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
  name: "register-product-form",
  data() {
	return {
	  eic_code: null,
      product_name: null,
      price_conditions: null,
      resolution: null,
      divisibility: null,
      ramping_period: null,
      direction: null,
      delivery_period: null,
      validity: null,
      pricing_method: null,
      showModal: false,
      messageModal: null
	};
  },
  methods: {
    submit(){
		let formData = new FormData();
		formData.append('eic_code', this.eic_code);
		formData.append('product_name', this.product_name);
		formData.append('price_conditions', this.price_conditions);
		formData.append('resolution', this.resolution);
		formData.append('divisibility', this.divisibility);
		formData.append('direction', this.direction)
		formData.append('ramping_period', this.ramping_period);
		formData.append('delivery_period', 5);
		formData.append('validity', this.validity);
		formData.append('pricing_method', this.pricing_method);
        formData.append('gate_closure_time', 15);
		formData.append('validated_by_fpo', 'True');
		this.$axios.post(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/register_product/", formData,
		{
			headers: {
				"Content-Type": "multipart/form-data"
			}
		}
		).then(response => {
          this.showModal = true;
          this.messageModal = "The product has been successfully registered.";
      })
      .catch(e => {
        this.showModal = true;
        this.messageModal = "An error happened. Be sure to complete all fields.";
      });
	}
  }
};
</script>