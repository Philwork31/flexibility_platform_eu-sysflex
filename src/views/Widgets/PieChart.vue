<template>
    <div id="pie-chart" class="widget">
        <div>
            <span>Stat 3</span>
        </div>
        <canvas id="myPieChart"></canvas>
    </div>
</template>

<script>
module.exports = {
    mounted() {
        var canvas = document.getElementById("myPieChart");
        var ctx = canvas.getContext('2d');


        // Global Options:
        Chart.defaults.global.defaultFontColor = 'black';
        Chart.defaults.global.defaultFontSize = 16;

        var data = {
            labels: ["Red", "Blue"],
            datasets: [{
                fill: true,
                backgroundColor: [
                    'red',
                    'blue'
                ],
                data: [37, 63],
                // Notice the borderColor

                borderWidth: [2, 2]
            }]
        };

        // Notice the rotation from the documentation.
        var options = {
            title: {
                display: true,
                text: 'Your side  ?',
                position: 'top'
            },
            rotation: -0.7 * Math.PI
        };

        // Chart declaration:
        var myPieChart = new Chart(ctx, {
            type: 'pie',
            data: data,
            options: options
        });

    }
}
</script>