<template>
    <div class="welcome">
        <div class="welcome-content">
            <div class="welcome-upside">
                <div>Welcome to the Flexibility Platform</div>
            </div>
            <!-- <div class="welcome-downside">
                <div class="welcome-downside-left">
                     <area-chart></area-chart>
                </div>
                <div class="welcome-downside-right">
                     <bar-chart-vertical></bar-chart-vertical>
                </div>
            </div>-->
        </div>
    </div>
</template>

<script>
import AreaChart from "../Widgets/AreaChart.vue";
import BarChartVertical from "../Widgets/BarChartVertical.vue";
import PieChart from "../Widgets/PieChart.vue";
import DonutChart from "../Widgets/DonutChart.vue";
import Activities from "../Widgets/Activities.vue";
import LineChart from "../Widgets/LineChart.vue";
export default {
    components: {
        'area-chart': AreaChart,
        'bar-chart-vertical': BarChartVertical,
        'pie-chart': PieChart,
        'donut-chart': DonutChart,
        'activities': Activities,
        'line-chart': LineChart
    }
};
</script>