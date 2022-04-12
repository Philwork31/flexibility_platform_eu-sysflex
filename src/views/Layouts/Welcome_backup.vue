<template>
    <div class="welcome">
        <div class="header-welcome">
            <span> Welcome Flexibility Platform </span>
        </div>
        <div class="welcome-content">
            <area-chart></area-chart>
            <bar-chart-vertical></bar-chart-vertical>
            <pie-chart></pie-chart>
            <donut-chart></donut-chart>
            <line-chart></line-chart>
        </div>
    </div>
</template>

<script >
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
