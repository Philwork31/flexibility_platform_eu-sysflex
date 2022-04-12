<template>
    <div class="view-content">
        <transition name="modal">
            <modal v-if="showModal">
                <div class="modal-mask">
                    <div class="modal-wrapper">
                    <div class="modal-container">
                        <div class="modal-header">
                            <slot name="header">
                                Potential registration
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
                <h2>Register a potential</h2>
            </div>
            <div class="form-content">
                <div class="fsp_name_field fp-field">
                    <label for="fsp_name">FSP name</label>
                    <select class="fp-select" v-model="fsp_name">
                        <option value="1" class="option-fix">EnocoFSP</option>
                        <option value="2" class="option-fix">FSP_TEST_2</option>
                        <option value="3" class="option-fix">FSP_TEST_3</option>
                    </select>
                </div>
                <div class="product_name_field fp-field">
                    <label for="product_name">Product name</label>
                    <select class="fp-select" name="product" id="product" v-model="product">
                        <option v-for="product in product_list" v-bind:value="product.id">{{ product.product_name }}</product>
                    </select>
                </div>
                <div class="power_field fp-field">
                    <label for="power">Power (MW)</label>
                    <input class="fp-input" type="number" name="power" v-model="power" required>
                </div>
                <div class="availability_fields fp-field">
                    <label for="availabilityStart">Availability Start/End <span class="plusbutton" v-on:click="addAvailability();">+</span></label>
                    <div class="so-form-availabilityfield" v-for="n in availabilityCounter" ref="availabilityfield">
                        <span class="moinsbutton" v-on:click="removeAvailability(n);">-</span>
                        <VueCtkDateTimePicker v-bind:id="'availabilityStart-' + n" v-model="availabilityStart[n-1]" label="Start date"></VueCtkDateTimePicker>
                        <VueCtkDateTimePicker v-bind:id="'availabilityEnd-' + n" v-model="availabilityEnd[n-1]" label="End date"></VueCtkDateTimePicker>
                    </div>
                </div>
                <div class="preparation_period_field fp-field">
                    <label for="preparation_period">Preparation period (minute)</label>
                    <input class="fp-input" type="number" name="preparation_period" v-model="preparation_period" required>
                </div>
                <div class="compliance_demonstration_field fp-field">
                    <label for="compliance_demonstration">Compliance demonstration</label>
                    <input class="fp-input" type="textarea" name="compliance_demonstration" v-model="compliance_demonstration" required>
                </div>
                <div class="localization_factor_field fp-field">
                    <label for="localization_factor">Localization factor</label>
                    <input class="fp-input" type="textarea" name="localization_factor" v-model="localization_factor">
                </div>
                <div class="metering_point_id_field fp-field">
                    <label for="metering_point_id">Metering point id</label>
                    <input class="fp-input" type="textarea" name="metering_point_id" v-model="metering_point_id" required>
                </div>
                <div class="baseline_type_field fp-field">
                    <label for="baseline_type">Baseline type</label>
                    <select class="fp-select" v-model="baseline_type" required>
                        <option value="Ex ante" class="option-fix">Ex ante</option>
                        <option value="Ex post" class="option-fix" disabled>Ex post</option>
                    </select>
                </div>
                <div class="expiration_date_field fp-field">
                    <label for="expiration_date">Expiration date</label>
                    <VueCtkDateTimePicker id="expiration_date" v-model="expiration_date"></VueCtkDateTimePicker>
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
  name: "register-flexibility-potential",
  data() {
	return {
	  fsp_name: null,
	  product_list: null,
	  product: null,
	  availabilityStart: [],
	  availabilityEnd: [],
	  availabilityCounter: 1,
	  power: null,
	  preparation_period: null,
	  compliance_demonstration: null,
	  localization_factor: null,
	  metering_point_id: null,
	  baseline_type: null,
	  expiration_date: null,
      showModal: false,
      messageModal: null
	};
  },
  methods: {
    addAvailability(){
        this.availabilityCounter++;
	},
    removeAvailability(n){
        if(document.querySelectorAll('.so-form-availabilityfield').length > 1){
            this.$refs.availabilityfield[this.$refs.availabilityfield.length - 1].remove();
            this.$refs.availabilityfield.pop();
            this.availabilityStart.splice(n-1, 1);
            this.availabilityEnd.splice(n-1, 1);
            this.availabilityCounter--;
        }
	},
	addRandom() {
      var plusOrMinusArray = ["+", "-"];
      this.preparation_period =
        1 + Math.floor(Math.random() * Math.floor(1000));
      this.power =
        1 + Math.floor(Math.random() * Math.floor(1000));
      this.availabilityStart[0] = "2020-01-01 12:00 am";
      this.availabilityEnd[0] = "2021-12-31 12:00 am";
      this.expiration_date = "2024-12-31 12:00 am";
      this.localization_factor = "B";
      this.metering_point_id = "random_metering_id";
      this.baseline_type = "Ex ante";
      this.compliance_demonstration = "Random compliance demonstration";
    },
    addSecondsToDatetimeList(datetimeList) {
        for(var i=0; i<datetimeList.length; i++){
            if(datetimeList[i].indexOf('am') > -1 || datetimeList[i].indexOf('pm') > -1){
                datetimeList[i] = datetimeList[i].replace(" am", ":00 am");
                datetimeList[i] = datetimeList[i].replace(" pm", ":00 pm");
            } else {
                datetimeList[i] += ":00";
            }
        }
        return datetimeList;
    },
    addSecondsToDatetime(datetime) {
        console.log("datetime");
        console.log(datetime);
        console.log(datetime.indexOf('am') > -1);
        console.log(datetime.indexOf('pm') > -1);
        if(datetime.indexOf('am') > -1 || datetime.indexOf('pm') > -1){
            datetime = datetime.replace(" am", ":00 am");
            datetime = datetime.replace(" pm", ":00 pm");
        } else {
            datetime += ":00";
        }
        console.log("datetime result");
        console.log(datetime);
        return datetime;
    },
    submit() {
      var copyAvailabilityStart = []
      var copyAvailabilityEnd = []
      for (var i = 0; i < this.availabilityStart.length; i++) {
        copyAvailabilityStart[i] = new Date(this.availabilityStart[i].replaceAll("-", "/")).toUTCString().replace(",", "");
      }
      for (var i = 0; i < this.availabilityEnd.length; i++) {
        copyAvailabilityEnd[i] = new Date(this.availabilityEnd[i].replaceAll("-", "/")).toUTCString().replace(",", "");
      }
      let formData = new FormData();
      formData.append('product_id', this.product);
      formData.append('fsp_id', this.fsp_name);
      formData.append('availability_start', copyAvailabilityStart);
      formData.append('availability_end', copyAvailabilityEnd);
      formData.append('power', this.power);
      formData.append('preparation_period', this.preparation_period);
      formData.append('compliance_demonstration', this.compliance_demonstration);
      formData.append('localization_factor', this.localization_factor);
      formData.append('metering_point_id', this.metering_point_id);
      formData.append('baseline_type', this.baseline_type);
      formData.append('expiration_date', new Date(this.expiration_date.replaceAll("-", "/")).toUTCString().replace(",", ""));
      this.$axios.post(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + "/api/v1/potential_register/", formData,
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
            })
    },
};
</script>
