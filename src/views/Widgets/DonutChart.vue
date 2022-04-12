<template>
    <div class="widget" id="donut-chart">
        <div>
            <span>Stat 4</span>
        </div>
        <canvas id="myDonutChart"></canvas>
    </div>
</template>

<script>
module.exports = {
    mounted() {

        var canvas = document.getElementById("myDonutChart");
        var ctx = canvas.getContext('2d');


        // Global Options:
        Chart.defaults.global.defaultFontColor = 'black';
        Chart.defaults.global.defaultFontSize = 16;

        var data = {
            labels: ["Orange", "Cyan", "Pink"],
            datasets: [{
                fill: true,
                backgroundColor: [
                    'orange',
                    'cyan',
                    'pink'
                ],
                data: [37, 55, 8],
                // Notice the borderColor

                borderWidth: [2, 2]
            }]
        };

        // Notice the rotation from the documentation.

        var options = {
            rotation: -0.7 * Math.PI
        };

        // Chart declaration:
        var myDonutChart = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: options
        });
    }
}
</script>