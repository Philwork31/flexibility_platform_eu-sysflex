<template>
    <div id="page"class="page-component" v-on:scroll="scrollFunction();">
        <router-view></router-view>
        <div id="top-btn" v-on:click="topFunction();" class ="scroll-up-btn" v-bind:class="{hiddenTopBtn: hiddenBtn}">
            <i class="fa fa-angle-up" v-bind:class="{hiddenIconBtn: hiddenBtn}"></i>
        </div>
    </div>
</template>

<script>
module.exports = {
    data() {
        return {
            hiddenBtn: true,
        }
    },
    methods: {
        scrollFunction: function () {
            if (document.getElementById("page").scrollTop == 0) {
                this.hiddenBtn = true;
            } else {
                this.hiddenBtn = false;
            }
        },
        topFunction: function () {
            document.getElementById("page").scrollTop = 0;
        }
    }
}
</script>
