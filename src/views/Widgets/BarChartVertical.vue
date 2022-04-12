<template>
    <div id="bar-chart-vertical" class="widget">
        <div>
            <span>Stats 2</span>
        </div>
        <canvas id="myChartBarVertical"></canvas>
    </div>
</template>
<script>


module.exports = {
    mounted() {
        var myCanvas = document.getElementById("myChartBarVertical");

        Chart.defaults.global.defaultFontFamily = "Lato";
        Chart.defaults.global.defaultFontSize = 18;

        var firstData = {
            label: 'First Data',
            data: [5427, 5243, 5514, 3933, 1326, 687, 1271, 1638],
            backgroundColor: 'rgba(0, 99, 132, 0.6)',
            borderWidth: 0,
            yAxisID: "y-axis-density"
        };

        var secondData = {
            label: 'Second Data',
            data: [3.7, 8.9, 9.8, 3.7, 23.1, 9.0, 8.7, 11.0],
            backgroundColor: 'rgba(99, 132, 0, 0.6)',
            borderWidth: 0,
            yAxisID: "y-axis-gravity"
        };

        var month = {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [firstData, secondData]
        };

        var chartOptions = {
            scales: {
                xAxes: [{
                    barPercentage: 1,
                    categoryPercentage: 0.6
                }],
                yAxes: [{
                    id: "y-axis-density"
                }, {
                    id: "y-axis-gravity"
                }]
            }
        };

        var barChart = new Chart(myCanvas, {
            type: 'bar',
            data: month,
            options: chartOptions
        });

    }
}
</script>