<template>
    <div class="view-content">
        <transition name="modal">
            <modal v-if="showModal">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                    <div class="modal-container">
                        <div class="modal-header">
                            <slot name="header">
                                Schedule registration
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
                <h2>Register a schedule (ex ante baseline)</h2>
            </div>
            <div class="form-content">
                <div class="fsp_name_field fp-field">
                    <label for="fsp_name">FSP name</label>
                    <select class="fp-select" v-model="fsp_name" required>
                        <option value="1" class="option-fix">FSP_TEST_1</option>
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
                <div class="metering_point_id_field fp-field">
                    <label for="metering_point_id">Metering point id</label>
                    <input class="fp-input" type="textarea" name="metering_point_id" v-model="metering_point_id" required>
                </div>
                <div class="dp_energy_wrapper fp-field">
                    <div>
                        <span class="plusbutton" v-on:click="addDpEnergy();">+</span>
                    </div>
                    <div class="dp_energy_fields" v-for="n in dpEnergyCounter" ref="dpEnergyfield">
                        <span class="moinsbutton" v-on:click="removeDpEnergy(n);">-</span>
                        <div class="dp_energy_fields_flex">
                            <div class="start_of_dp_field fp-field">
                                <label for="start_of_delivery">Start of delivery period</label>
                                <div class="start_of_delivery_name_field_datetimepicker">
                                    <VueCtkDateTimePicker v-bind:id="'serviceDateStart' + n" v-model="serviceDateStart[n-1]" v-bind:minDate="min_start_service_date" label="Date" onlyDate="True" format="YYYY-MM-DD" formatted="ll"></VueCtkDateTimePicker>
                                    <button type="Button" v-on:click="moinsDeliveryTimeStart(n)" class="moins-button-delivery">-</button><input type="text" class="start_of_delivery_name_field_timepicker" disabled v-model="start_service_time[n-1]"><button type="Button" v-on:click="plusDeliveryTimeStart(n)" class="plus-button-delivery">+</button>
                                </div>
                            </div>
                            <div class="energy_field fp-field">
                                <label for="energy">Energy</label>
                                <input class="fp-input" type="textarea" name="energy" v-model="energy[n-1]" required>
                            </div>
                        </div>
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
  name: "register-schedule",
  data() {
	return {
	  fsp_name: null,
	  product_list: null,
	  product: null,
	  metering_point_id: null,
	  start_of_delivery: null,
      showModal: false,
      messageModal: null,
      original_last_active_dp_start: null,
      interval_duration: null,
      min_start_service_date: null,
      min_start_service_time: null,
      start_service_time: [],
      serviceDateStart: [],
      gct: null,
	  dpEnergyCounter: 1,
	  energy: [],
	  forceRender: false,
	};
  },
  methods: {
    addDpEnergy(){
        this.dpEnergyCounter++;
        this.start_service_time[this.dpEnergyCounter - 1] = this.min_start_service_time;
        console.log(this.start_service_time);
	},
    removeDpEnergy(n){
        if(document.querySelectorAll('.dp_energy_fields').length > 1){
            this.$refs.dpEnergyfield[this.$refs.dpEnergyfield.length - 1].remove();
            this.$refs.dpEnergyfield.pop();
            this.energy.splice(n-1, 1);
            this.serviceDateStart.splice(n-1, 1);
            this.start_service_time.splice(n-1, 1);
            this.dpEnergyCounter--;
        }
	},
    moinsDeliveryTimeStart(n){
        if(this.checkAmPm(this.start_service_time[n-1])){
            var mssd = new Date("01 01, 1990 " + this.start_service_time[n-1]);
        } else {
            var mssd = new Date("1990-01-01T" + this.start_service_time[n-1]);
        }
        var mssd_limit_min = new Date("1990-01-01T00:00:00");
        var mssd_check= new Date(mssd.setMinutes(mssd.getMinutes() - this.interval_duration));
        var mssd_check_2 = new Date(this.serviceDateStart[n-1] + "T00:00:00").setHours(mssd_check.getHours());
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
            this.start_service_time.splice(n-1, 1, mssd_check.toLocaleTimeString().replace(/\u200e/g, ''));
        }
    },
    plusDeliveryTimeStart(n){
        if(this.checkAmPm(this.start_service_time[n-1])){
            var mssd = new Date("01 01, 1990 " + this.start_service_time[n-1]);
        } else {
            var mssd = new Date("1990-01-01T" + this.start_service_time[n-1]);
        }
        var mssd_limit_max = new Date("1990-01-01T23:59:59");
        var mssd_check= new Date(mssd.setMinutes(mssd.getMinutes() + this.interval_duration));
        var mssd_check_2 = new Date(this.serviceDateStart[n-1] + "T00:00:00");
        if(isNaN(mssd_check_2.getTime())){
            console.log("Date not selected");
        } else if(mssd_check > mssd_limit_max){
            console.log("Can't set time outside of 24h base");
        } else {
            this.start_service_time.splice(n-1, 1, mssd_check.toLocaleTimeString().replace(/\u200e/g, ''));
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
      this.metering_point_id = "random_metering_id";
    },
    submit() {
      for (var i = 0; i < this.start_service_time.length; i++) {
        this.start_service_time[i].replace(/\u200e/g, '');
      }
      var start_service_datetime = []
      for (var i = 0; i < this.serviceDateStart.length; i++) {
        start_service_datetime[i] = new Date(this.serviceDateStart[i].replaceAll("-", "/") + " " + this.start_service_time[i]).toUTCString().replace(",", "");
      }
      let formData = new FormData();
      formData.append('product_id', this.product);
      formData.append('flexibility_service_provider_id', this.fsp_name);
      formData.append('metering_point_id', this.metering_point_id);
      formData.append('energy', this.energy);
      formData.append('start_of_delivery_date', this.serviceDateStart);
      formData.append('start_of_delivery_time', this.start_service_time);
      formData.append('start_of_delivery_datetime', start_service_datetime);
      formData.append('interval_duration', this.interval_duration);
      formData.append('gct', this.gct);
      this.$axios.post(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/registerschedule/", formData,
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
                self.start_service_time[0] = new Date(response.data.ending_date);
                self.start_service_time[0] = new Date(self.start_service_time[0].setMinutes(self.start_service_time[0].getMinutes()));
                self.start_service_time[0] = self.start_service_time[0].toLocaleTimeString().replace(/\u200e/g, '');

                /* Set timepicker */
                self.gct = response.data.gct;
            });
  },
    watch: {
        serviceDateStart: function(){
            /* Removed for now, i don't know how to do that with array
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
            */
        },
    }
};
</script>
