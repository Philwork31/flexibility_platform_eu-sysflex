<template>

    <div class="wrapper">
        <div class="box-left" v-bind:class="{ hiddenMenu: hiddenIsActive }">
            <left-dashboard></left-dashboard>
        </div>

        <div class="box-right" v-bind:class="{ hiddenMenu: hiddenIsActive, nighttheme: $route.params.theme == 'n' }">
            <header-dashboard @inputHiddenIsActive="updateHiddenBoxLeft"></header-dashboard>
            <page-dashboard></page-dashboard>
        </div>

    </div>

</template>

<script>
import HeaderDashBoard from './HeaderDashBoard.vue'
import LeftBarTool from './LeftBarTool.vue'
import PageContent from './PageContent.vue'

export default {
    data() {
        return {
            hiddenIsActive: false,
        }
    },
    components: {
        'header-dashboard': HeaderDashBoard,
        'page-dashboard': PageContent,
        'left-dashboard': LeftBarTool
    },
    mounted() {
        this.$nextTick(function () {
            window.addEventListener('resize', this.ResponsiveHidden);

            //Init
            this.ResponsiveHidden();
        });
    },
    methods: {
        ResponsiveHidden(event) {
            if (document.documentElement.clientWidth <= 1025) {
                this.hiddenIsActive = true;
            } else {
                this.hiddenIsActive = false;
            }
        },

        updateHiddenBoxLeft: function (variable) {
            this.hiddenIsActive = variable;
        }
    }
}

</script>