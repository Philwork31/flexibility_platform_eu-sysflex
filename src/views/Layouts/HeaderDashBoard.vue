<template>
    <div class="header-component" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
        <transition name="modal" v-if="modalSettingsDisplay">
            <modal>
                <div class="modal-mask settings-menu">
                    <div class="modal-wrapper">
                        <div class="modal-container" style="width: 385px;">
                            <div class="modal-header">
                                <slot name="header">
                                    <h2>Settings</h2>
                                </slot>
                            </div>
                            <div class="modal-body" style="text-align: center;">
                                <div class="service-period-part" style="display: none;">
                                    <h3>Activation service period</h3>
                                    <label for="service_period_start_time">Start time : </label>
                                    <VueCtkDateTimePicker id="service_period_start_time TimePicker" label="Select time" v-model="yourValue"
                                    format="hh:mm a" formatted="hh:mm a" inputSize="sm" minuteInterval="1"
                                    onlyTime="True" noLabel="True" v-model="service_period_start_time"/>
                                    <label for="service_period_range_time">Service period duration (in minutes) : </label>
                                    <input type="number" id="service_period_range_time" v-model="service_period_duration"/>
                                    <label for="service_period_gct">Gate closure time (in minutes) : </label>
                                    <input type="number" id="service_period_gct" v-model="service_period_gct"/>
                                    <br>
                                    <button class="btn btn-primary" v-on:click="activateServicePeriod();" style="text-align: center;">Activate</button>
                                    <button class="btn btn-danger" v-on:click="deactivateServicePeriod();" style="text-align: center;">Deactivate</button>
                                    <p v-if="validTextServicePeriod">{{ validTextServicePeriod }}</p>
                                </div>
                                <hr style="display: none">
                                <div class="cft-reset-part" style="display: none">
                                    <h3>CFT status reset : </h3>
                                    <button class="btn btn-danger" v-on:click="resetCFT();">
                                        Reset
                                    </button>
                                </div>
                                <hr>
                                <div class="theme-color-part">
                                    <h3>Theme color</h3>
                                    <div class="themeselector-container" v-bind:class="{ nighttheme: $route.params.theme == 'n' }">
                                        <select v-model="themeColor">
                                            <option value="l">Light</option>
                                            <option value="n">Night</option>
                                        </select>
                                    </div>
                                </div>
                                <hr>
                                <div class="fullscreen-part">
                                    <h3>Fullscreen</h3>
                                    <div class="fullscreen-container header-btn" style="transform: none; margin: auto;" v-on:click="toggleFullscreen();">
                                        <i class="fa fa-expand" aria-hidden="true"></i>
                                    </div>
                                </div>
                                <hr style="display: none">
                                <div class="admin-part" style="display: none">
                                    <a href="admin" target="_blank"><button class="btn btn-primary" style="text-align: center; background-color: #0025ff;">Admin</button></a>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <slot name="footer">
                                    <button class="btn btn-secondary" @click="modalSettingsDisplay = false">
                                    Close
                                    </button>
                                </slot>
                            </div>
                        </div>
                    </div>
                </div>
            </modal>
        </transition>
        <div class="header-left-side-container">
            <div class="hiddentool-container">
                <div class="hiddentool-btn header-btn hidden-btn" v-on:click="triggerHidden();">
                    <i class="fa fa-bars"></i>
                </div>
            </div>
            <div class="settings-button-container">
                <div class="settings-button header-btn" v-on:click="modalSettingsDisplay = true">
                    <i class="fas fa-cog"></i>
                </div>
            </div>
            <div class="search-bar-container">
                    <button type="button" ><i class="fa fa-search"></i></button>
                    <input id="searchBarInput" type="search" placeholder="Search..." name="search" v-model="typeahead" >
                    <div class="suggestions-list" v-if="!selected && typeahead">
                        <div class="suggest-element" v-for="item in items" v-if="filterBySelect(item)" >
                            <a v-bind:href="'#' + item.path">{{ item.name}}</a>
                        </div>
                    </div>
            </div>
        </div>

        <div class="header-right-side-container">
            <div class="fpo-container fpo-btn">
                <button>FPO</button>
            </div>
            <div class="last-notification-container" v-bind:class="{ hidden: !notificationHidden }">
            {{ lastNotification }}
            </div>
            <div class="notification-button-container header-btn" v-on:click="showNotification();">
                <span><i class="fa" v-bind:class="{ 'fa-bell': notificationHidden, 'fa-times': !notificationHidden }"></i></span>
                <span class="badge">4</span>
            </div>
            <a class="admin-container" href="/admin" style="display: none;">
                <span>ADMIN</span>
            </a>
        </div>
        <div class="notification-container" v-bind:class="{ hidden: notificationHidden }">
            <div class="notification-container-header">
                <div class="notification-link">
                    <router-link :to="{path: '/' + $route.params.theme + '/notifications'}">
                        More details
                    </router-link>
                </div>
            </div>
            <div class="notification-container-list">
                <div class="notification" v-for="item in listNotification"><span>{{ item }}</span></div>
            </div>
        </div>
    </div>
</template>

<script>
module.exports = {
    created() {
        this.$router.options.routes[0].children.forEach(routes => {
            this.items.push({
                name: routes.name,
                path: routes.path,
            })
        })
        this.fetchNotificationsList();
        this.openSocketListener();
    },
    data() {
        return {
            themeColor: this.$route.params.theme,
            hiddenIsActive: false,
            isFullscreen: false,
            message: '',
            selected: null,
            typeahead: null,
            items: [],
            eventRecorderShow: false,
            notificationHidden: true,
            lastNotification: null,
            listNotification: null,
            modalSettingsDisplay: false,
            service_period_duration: null,
            service_period_start_time: null,
            service_period_gct: null,
            validTextServicePeriod: null
        }
    },
    methods: {
        triggerHidden: function () {
            if (this.hiddenIsActive == true) {
                this.hiddenIsActive = false;
            } else {
                this.hiddenIsActive = true;
            }
            this.$emit("inputHiddenIsActive", this.hiddenIsActive);
        },

        /*  addMessage: function() {
                this.$router.push('/'+this.typeahead+'/');
        }, */

        filterBySelect: function (value) {
            console.log(value.name);
            if (value.name != undefined) {
                if (!this.typeahead || this.typeahead.length === 0) {
                    return true;
                }
                return value.name.toLowerCase().split(this.typeahead.toLowerCase()).length > 1;
            }
        },
        toggleFullscreen: function () {
            var elem = document.documentElement;
            if (
                document.fullscreenEnabled ||
                document.webkitFullscreenEnabled ||
                document.mozFullScreenEnabled ||
                document.msFullscreenEnabled
            ) {
                if (!this.isFullscreen) {
                    if (elem.requestFullscreen) {
                        elem.requestFullscreen();
                        this.isFullscreen = true;
                        return;
                    } else if (elem.webkitRequestFullscreen) {
                        elem.webkitRequestFullscreen();
                        this.isFullscreen = true;
                        return;
                    } else if (elem.mozRequestFullScreen) {
                        elem.mozRequestFullScreen();
                        this.isFullscreen = true;
                        return;
                    } else if (elem.msRequestFullscreen) {
                        elem.msRequestFullscreen();
                        this.isFullscreen = true;
                        return;
                    }
                } else {
                    if (document.exitFullscreen) {
                        document.exitFullscreen();
                        this.isFullscreen = false;
                        return;
                    } else if (document.webkitExitFullscreen) {
                        document.webkitExitFullscreen();
                        this.isFullscreen = false;
                        return;
                    } else if (document.mozCancelFullScreen) {
                        document.mozCancelFullScreen();
                        this.isFullscreen = false;
                        return;
                    } else if (document.msExitFullscreen) {
                        document.msExitFullscreen();
                        this.isFullscreen = false;
                        return;
                    }
                };
            }
        },
        showNotification: function(){
            if(this.notificationHidden){
                this.notificationHidden = false;
            } else {
                this.notificationHidden = true;
            }
        },
        fetchNotificationsList() {
            var self = this;
            this.$axios
                .get(location.protocol + "//" + location.hostname+(location.port ? ":" + location.port: "") + '/api/v1/event_recorder_limited/?format=json')
                .then(function (response) {
                    self.listNotification = self.formatStringNotification(response.data);
                    self.lastNotification = self.listNotification[0];
                });
        },
        openSocketListener: function(){
            var self = this;
            var socket = new WebSocket('wss://' + location.hostname+(location.port ? ":" + location.port: "") + '/websocket');
            socket.onmessage = function(e) {
                var data = JSON.parse(e.data);
                self.lastNotification = data['message'];
                self.listNotification.unshift(data['message']);
            }
        },
        formatStringNotification: function(data){
            var result = []
            for (var k = 0; k < data.length; k++){
                var jsonData = JSON.parse(data[k].business_object_info);
                var textToFormat = data[k].text;
                for (var i = 0; i < jsonData.length; i++) {
                    textToFormat = textToFormat.replace("%" + (i+1), jsonData[i].text);
                }
                result.push(textToFormat);
            }
            return result;
        },
        activateServicePeriod: function(){
            var dateToday = new Date();
            var hourFormatted = new Date("2020-01-01 " + this.service_period_start_time);
            dateToday.setHours(hourFormatted.getHours());
            dateToday.setMinutes(hourFormatted.getMinutes());
            var finalDate = dateToday.toUTCString().replace(",", "");
            self = this;
            var d = new Date();
            let formData = new FormData();
            formData.append('service_period_duration', this.service_period_duration);
            formData.append('service_period_start_time', finalDate);
            formData.append('service_period_gct', this.service_period_gct);
            this.$axios.post("/api/v1/activateserviceperiod/", formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            }
            ).then(response => {
                self.validTextServicePeriod = "Delivery period successfully activated.";
            })
            .catch(e => {
                self.validTextServicePeriod = "A problem occured when trying to activate delivery periods. Check the logs.";
            });
        },
        deactivateServicePeriod: function(){
            let formData = new FormData()
            this.$axios.post("/api/v1/deactivateserviceperiod/", formData,
            {
                headers: {
                    "Content-Type": "multipart/form-data"
                }
            }
            ).then(response => {
                self.validTextServicePeriod = "Delivery period successfully deactivated.";
            })
            .catch(e => {
                self.validTextServicePeriod = "A problem occured when trying to deactivate delivery periods. Check the logs.";
            });
        },
        resetCFT: function(){
            if (confirm("Are you sure you want to reset all CFT status ?")) {
                this.$axios.post("/api/v1/resetcft/",
                {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                }
                ).then(response => {
                    self.validTextServicePeriod = "CFT status successfully resetted.";
                })
                .catch(e => {
                    self.validTextServicePeriod = "A problem occured when trying to reset CFT status. Check the logs.";
                });
            }
        }
    },
    watch: {
        themeColor: function(){
            if(this.themeColor == "l"){
                this.$router.push({ path: this.$route.path.replace("/n", "/l") });
            }
            if(this.themeColor == "n"){
                this.$router.push({ path: this.$route.path.replace("/l", "/n") });
            }
        }
    },
}

</script>

