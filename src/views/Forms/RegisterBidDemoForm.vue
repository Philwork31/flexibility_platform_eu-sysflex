<template>
    <div class="view-content">
        <transition name="modal">
            <modal v-if="showModal">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                    <div class="modal-container">
                        <div class="modal-header">
                            <slot name="header">
                                Bid registration
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
                <h2>Register a bid</h2>
            </div>
            <div class="form-content">
                <div class="fsp_name_field fp-field">
                    <label for="fsp_name">FSP name</label>
                    <select class="fp-select" v-model="fsp_name" required>
                        <option value="1" class="option-fix">EnocoFSP</option>
                        <option value="2" class="option-fix">FSP_TEST_2</option>
                        <option value="3" class="option-fix">FSP_TEST_3</option>
                    </select>
                </div>
                <div class="product_name_field fp-field">
                    <label for="product_name">Product name</label>
                    <select class="fp-select" name="product" id="product" v-model="product" required>
                        <option v-for="product in product_list" v-bind:value="product.id">{{ product.product_name }}</product>
                    </select>
                </div>
                <div class="price_field fp-field">
                    <label for="price">Price (€/MWh)</label>
                    <input class="fp-input" type="number" name="price" v-model="price" required>
                </div>
                <div class="power_field fp-field">
                    <label for="power">Power (MW)</label>
                    <input class="fp-input" type="number" name="power" v-model="power" required>
                </div>
                <div class="linking_of_bids_field fp-field">
                    <label for="linking_of_bids">Linking of bids</label>
                    <select class="fp-select" v-model="linking_of_bids" required>
                        <option value="True" class="option-fix">Yes</option>
                        <option value="False" class="option-fix">No</option>
                    </select>
                </div>
                <div class="metering_point_id_field fp-field">
                    <label for="metering_point_id">Metering point id</label>
                    <input class="fp-input" type="textarea" name="metering_point_id" v-model="metering_point_id" required>
                </div>
                <div class="localization_factor_field fp-field">
                    <label for="localization_factor">Localization factor</label>
                    <input class="fp-input" type="textarea" name="localization_factor" v-model="localization_factor">
                </div>
                <div class="start_of_delivery_name_field fp-field">
                    <label for="start_of_delivery">Start of delivery</label>
                    <div class="start_of_delivery_name_field_datetimepicker">
                        <VueCtkDateTimePicker id="serviceDateStart" v-model="serviceDateStart" v-bind:minDate="min_start_service_date" label="Start date" onlyDate="True" format="YYYY-MM-DD" formatted="ll"></VueCtkDateTimePicker>
                        <button type="Button" v-on:click="moinsDeliveryTimeStart()" class="moins-button-delivery">-</button><input type="text" class="start_of_delivery_name_field_timepicker" disabled v-model="start_service_time"><button type="Button" v-on:click="plusDeliveryTimeStart()" class="plus-button-delivery">+</button>
                    </div>
                </div>
                <div class="fp-submit-form fp-field">
                    <button v-on:click="addRandom()" class="so-form-warn" style="background-color: #ff9800;" type="Button">Random data</button>
                    <button type="submit">Submit</button>
                </div>
            </div>
        </form>
    </div>
</template>


<script>
export default {
  name: "register-flexibility-bid",
  data() {
	return {
	  fsp_name: null,
	  product_list: null,
	  product: null,
	  price: null,
	  power: null,
	  linking_of_bids: null,
	  metering_point_id: null,
	  localization_factor: null,
	  start_of_delivery: null,
      showModal: false,
      messageModal: null,
      original_last_active_dp_start: null,
      interval_duration: null,
      min_start_service_date: null,
      min_start_service_time: null,
      start_service_time: null,
      serviceDateStart: null,
      gct: null
	};
  },
  methods: {
    moinsDeliveryTimeStart(){
        if(this.checkAmPm(this.start_service_time)){
            var mssd = new Date("01 01, 1990 " + this.start_service_time);
        } else {
            var mssd = new Date("1990-01-01T" + this.start_service_time);
        }
        var mssd_limit_min = new Date("1990-01-01T00:00:00");
        var mssd_check= new Date(mssd.setMinutes(mssd.getMinutes() - this.interval_duration));
        var mssd_check_2 = new Date(this.serviceDateStart + "T00:00:00").setHours(mssd_check.getHours());
        var mssd_check_2 = new Date(mssd_check_2).setMinutes(mssd_check.getMinutes());
        var mssd_check_2 = new Date(mssd_check_2).setSeconds(mssd_check.getSeconds());
        var mssd_check_2 = new Date(mssd_check_2);
        var date_now = new Date(Date.now());
        if(isNaN(mssd_check_2.getTime())){
            console.log("Date not selected");
        } else if(mssd_check < mssd_limit_min){
            console.log("Can't set time outside of 24h base");
        } else if(mssd_check_2 <= date_now){
            console.log("Can't set time inferior to current");
        } else {
            this.start_service_time = mssd_check.toLocaleTimeString().replace(/\u200e/g, '');
        }
    },
    plusDeliveryTimeStart(){
        if(this.checkAmPm(this.start_service_time)){
            var mssd = new Date("01 01, 1990 " + this.start_service_time);
        } else {
            var mssd = new Date("1990-01-01T" + this.start_service_time);
        }
        var mssd_limit_max = new Date("1990-01-01T23:59:59");
        var mssd_check= new Date(mssd.setMinutes(mssd.getMinutes() + this.interval_duration));
        var mssd_check_2 = new Date(this.serviceDateStart + "T00:00:00");
        if(isNaN(mssd_check_2.getTime())){
            console.log("Date not selected");
        } else if(mssd_check > mssd_limit_max){
            console.log("Can't set time outside of 24h base");
        } else {
            this.start_service_time = mssd_check.toLocaleTimeString().replace(/\u200e/g, '');
        }
    },
    checkAmPm(str) {
        if (str.includes('am') || str.includes('pm') || str.includes('AM') || str.includes('PM')){
            return true;
        } else {
            return false;
        }
    },
	addRandom() {
      var plusOrMinusArray = ["+", "-"];
      var trueOrFalseArray = ["True", "False"];
      this.price =
        1 + Math.floor(Math.random() * Math.floor(1000));
      this.power =
        1 + Math.floor(Math.random() * Math.floor(1000));
      this.linking_of_bids =
        trueOrFalseArray[Math.floor(Math.random() * trueOrFalseArray.length)];
      this.localization_factor = "B";
      this.metering_point_id = "random_metering_id";
    },
    submit() {
      var s_o_d = new Date(this.serviceDateStart.replaceAll("-", "/") + " " + this.start_service_time.replace(/\u200e/g, '')).toUTCString().replace(",", "");
      let formData = new FormData();
      formData.append('product_id', this.product);
      formData.append('flexibility_service_provider_id', this.fsp_name);
      formData.append('price', this.price);
      formData.append('power', this.power);
      formData.append('linking_of_bids', this.linking_of_bids);
      formData.append('metering_point_id', this.metering_point_id);
      formData.append('localization_factor', this.localization_factor);
      formData.append('start_of_delivery', s_o_d);
      formData.append('interval_duration', this.interval_duration);
      formData.append('gct', this.gct);
      this.$axios.post(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/registerbid/", formData,
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
            .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/product/?format=json")
            .then(function (response) {
                self.product_list = response.data;
            });
        this.$axios
            .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/lastdeliveryperiod/?format=json')
            .then(function (response) {
                self.original_last_active_dp_start = new Date(response.data.ending_date);
                var temp_copie = new Date(response.data.ending_date);
                self.interval_duration = response.data.duration;

                /* Datepicker set minDate */
                self.min_start_service_date = new Date(response.data.ending_date);
                self.min_start_service_date = new Date(self.min_start_service_date.setDate(self.min_start_service_date.getDate()-1));

                /* Timepicker set min */
                self.min_start_service_time = new Date(response.data.ending_date);
                self.min_start_service_time = new Date(self.min_start_service_time.setMinutes(self.min_start_service_time.getMinutes()));
                self.min_start_service_time = self.min_start_service_time.toLocaleTimeString().replace(/\u200e/g, '');

                /* Set timepicker */
                self.start_service_time = new Date(response.data.ending_date);
                self.start_service_time = new Date(self.start_service_time.setMinutes(self.start_service_time.getMinutes()));
                self.start_service_time = self.start_service_time.toLocaleTimeString().replace(/\u200e/g, '');

                /* Set timepicker */
                self.gct = response.data.gct;
            });
  },
    watch: {
        serviceDateStart: function(){
            if(this.checkAmPm(this.start_service_time)){
                var testing_date = new Date(this.serviceDateStart + " 12:00:00 AM");
            } else {
                var testing_date = new Date(this.serviceDateStart + "T00:00:00");
            }
            if(testing_date.toDateString() == this.original_last_active_dp_start.toDateString()){
                if(this.checkAmPm(this.min_start_service_time)){
                    var testing_time_min = new Date("01 01, 1990 " + this.min_start_service_time);
                } else {
                    var testing_time_min = new Date("1990-01-01T" + this.min_start_service_time);
                }
                if(this.checkAmPm(this.start_service_time)){
                    var testing_time = new Date("01 01, 1990 " + this.start_service_time);
                } else {
                    var testing_time = new Date("1990-01-01T" + this.start_service_time);
                }
                if(testing_time < testing_time_min){
                    this.start_service_time = this.min_start_service_time;
                }
            }
        },
    }
};
</script>
