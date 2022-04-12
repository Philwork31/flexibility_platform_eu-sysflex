import Vue from 'vue'
import VueRouter from "vue-router";
import App from './App.vue';

// router setup
import routes from "./routes/routes";

// axios for http request
import axios from "axios";

// datetime
import VueCtkDateTimePicker from 'vue-ctk-date-time-picker';
import 'vue-ctk-date-time-picker/dist/vue-ctk-date-time-picker.css';

// crappy but only way to order for vue.js
window._ = require('lodash');

// configure router
const router = new VueRouter({
  routes, // short for routes: routes
  linkExactActiveClass: "nav-item active"
});

Vue.use(VueRouter);
Vue.prototype.$axios = axios;

Vue.component('VueCtkDateTimePicker', VueCtkDateTimePicker);

new Vue({
  el: '#app',
  components: {
    'app': App
  },
  render: h => h(App),
  router,
})
