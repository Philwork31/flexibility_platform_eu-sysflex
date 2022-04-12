<template>
   <div class="left-component">
      <div class="toolbar" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
         <router-link to="/">
            <div class="title-toolbar">
               <img class="logo-dashboard" src="public/img/logo-sysflex.jpg"/>
               <span class="title">Flexibility Platform</span>
            </div>
         </router-link>
      </div>
      <div class="menu" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
         <!-- <<div class="apps-container">
            <span>Menu</span>
            i class="fa fa-sort-down" v-bind:class="{ dropdown: dropdownIsActive }"></i>
         </div>-->
         <router-link :to="{path: '/' + $route.params.theme + '/home/'}">
            <div class="menu-button">
               <span class="menutext"> Home</span>
            </div>
         </router-link>
         <div class="menu-content" v-bind:class="{ dropdown: dropdownIsActive }">
            <div class="scrolldown-menu-button" v-bind:class="{ active: productScroll }" v-on:click="productScroll = !productScroll;">
               <span class="menutext">Products</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: productScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/register_product/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Register</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/products-to-validate/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Validate</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/product/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> List</span>
                  </div>
               </router-link>
            </div>
            <div class="scrolldown-menu-button" v-bind:class="{ active: needScroll }" v-on:click="needScroll = !needScroll;">
               <span class="menutext">Needs</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: needScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/needs/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> List</span>
                  </div>
               </router-link>
            </div>
            <div class="scrolldown-menu-button" v-bind:class="{ active: potentialScroll }" v-on:click="potentialScroll = !potentialScroll;">
               <span class="menutext">Potentials</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: potentialScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/potentials/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> List</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/potentialsgridimpactassessmentresult/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Grid impact result</span>
                  </div>
               </router-link>
            </div>
            <div class="scrolldown-menu-button" v-bind:class="{ active: cftScroll }" v-on:click="cftScroll = !cftScroll;">
               <span class="menutext">Call for tenders</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: cftScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/callfortenders/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> List</span>
                  </div>
               </router-link>
            </div>
            <div class="scrolldown-menu-button" v-bind:class="{ active: bidScroll }" v-on:click="bidScroll = !bidScroll;">
               <span class="menutext">Bids</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: bidScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/bids/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> List</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/bidsgridimpactassessmentresult/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Grid impact result</span>
                  </div>
               </router-link>
            </div>
            <router-link :to="{path: '/' + $route.params.theme + '/bids-order/'}">
               <div class="menu-button">
                  <span class="menutext"> Merit order list</span>
               </div>
            </router-link>
            <div class="scrolldown-menu-button" v-bind:class="{ active: activationScroll }" v-on:click="activationScroll = !activationScroll;">
               <span class="menutext">Activations</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: activationScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/activation-requests/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Requests</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/activation-order/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Orders</span>
                  </div>
               </router-link>
            </div>
            <div class="scrolldown-menu-button" v-bind:class="{ active: verificationScroll }" v-on:click="verificationScroll = !verificationScroll;">
               <span class="menutext">Verifications</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: verificationScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/register-verification/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Verify</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/verification/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Results</span>
                  </div>
               </router-link>
            </div>
            <div class="scrolldown-menu-button" v-bind:class="{ active: fspDataScroll }" v-on:click="fspDataScroll = !fspDataScroll;">
               <span class="menutext">FSP Data</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: fspDataScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/schedules/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Schedules</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/meteringdatas/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Metering data</span>
                  </div>
               </router-link>
            </div>
            <div class="scrolldown-menu-button" v-bind:class="{ active: fspSimulatorScroll }" v-on:click="fspSimulatorScroll = !fspSimulatorScroll;">
               <span class="menutext">FSP Simulator</span><span class="scrolldown-arrow"><i class="fas fa-chevron-right"></i></span>
            </div>
            <div class="scrolleddown-menu-button" v-bind:class="{ scrolled: fspSimulatorScroll }">
               <router-link :to="{path: '/' + $route.params.theme + '/potential-register-demo/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Register a potential</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/bid-register-demo/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Register a bid</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/metering-data-register-demo/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Register metering data</span>
                  </div>
               </router-link>
               <router-link :to="{path: '/' + $route.params.theme + '/schedule-register-demo/'}">
                  <div class="menu-button">
                     <span class="menutext"><i class="fas fa-caret-right"></i> Register schedule</span>
                  </div>
               </router-link>
            </div>
            <router-link :to="{path: '/' + $route.params.theme + '/aggregatorinformation/'}">
               <div class="menu-button">
                  <span class="menutext"> Aggregator information</span>
               </div>
            </router-link>
         </div>
         <div class="dp-time-left">
            <div v-bind:class="{ green: statusDP, red: !statusDP }" class="dp-pastille"></div>
            {{ textDP }}{{ numberMinuteDP }}
         </div>
      </div>
   </div>
</template>

<script>
module.exports = {
    data() {
        return {
            dropdownIsActive: true,
            numberMinuteDP: "",
            textDP: "Trying to reach server.",
            statusDP: null,
            productScroll: false,
            needScroll: false,
            activationScroll: false,
            fspDataScroll: false,
            potentialScroll: false,
            cftScroll: false,
            bidScroll: false,
            verificationScroll: false,
            fspSimulatorScroll: false
        }
    },
    methods: {
        triggerDropdown: function() {
            if(this.dropdownIsActive == true){
                this.dropdownIsActive = false;

            } else {
                this.dropdownIsActive = true;
            }
        },
        pollDP () {
            var self = this;
            this.$axios
                .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/lastdeliveryperiod/?format=json')
                .then(function (response) {
                    var date_options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: 'numeric', minute: 'numeric', second: 'numeric' };
                    self.jsons = response.data;
                    if(response.data.status == "started"){
                        self.textDP = "Time left before GCT (min) : ";
                        self.statusDP = true;
                    } else {
                        self.textDP = "Time left before next delivery period (min) : ";
                        self.statusDP = false;
                    }
                    self.numberMinuteDP = response.data.time_left;
                })
                .catch(function (response) {
                    console.log(response);
                    self.textDP = "Delivery period not activated.";
                    self.numberMinuteDP = "";
                    self.statusDP = false;
                });
        }
    },
    mounted() {
        this.pollDP();
        setInterval(this.pollDP, 10000);
    },
}
</script>

