<template>
    <div class="widget" id="line-chart">
        <div>
            <span>Stat 5</span>
        </div>
        <canvas id="myChart"></canvas>
    </div>
</template>

<script>
module.exports = {
    mounted() {
        var canvas = document.getElementById("myChart");
        var ctx = canvas.getContext('2d');

        // Global Options:
        Chart.defaults.global.defaultFontColor = 'black';
        Chart.defaults.global.defaultFontSize = 16;

        var data = {
            labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
            datasets: [{
                    label: "Auctions",
                    fill: false,
                    lineTension: 0.1,
                    backgroundColor: "red",
                    borderColor: "red", // The main line color
                    borderCapStyle: 'square',
                    borderDash: [], // try [5, 15] for instance
                    borderDashOffset: 0.0,
                    borderJoinStyle: 'miter',
                    pointBorderColor: "black",
                    pointBackgroundColor: "white",
                    pointBorderWidth: 1,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: "white",
                    pointHoverBorderColor: "black",
                    pointHoverBorderWidth: 2,
                    pointRadius: 4,
                    pointHitRadius: 10,
                    // notice the gap in the data and the spanGaps: true
                    data: [65, 59, 80, 81, 56, 55, 40, , 60, 55, 30, 78],
                    spanGaps: true,
                }, {
                    label: "bids",
                    fill: false,
                    lineTension: 0.1,
                    backgroundColor: "cyan",
                    borderColor: "cyan", // The main line color
                    borderCapStyle: 'square',
                    borderDash: [], // try [5, 15] for instance
                    borderDashOffset: 0.0,
                    borderJoinStyle: 'miter',
                    pointBorderColor: "black",
                    pointBackgroundColor: "white",
                    pointBorderWidth: 1,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: "white",
                    pointHoverBorderColor: "black",
                    pointHoverBorderWidth: 2,
                    pointRadius: 4,
                    pointHitRadius: 10,
                    // notice the gap in the data and the spanGaps: true
                    data: [23, 78, 34, 33, 90, 12, 87, , 78, 62, 70, 8],
                    spanGaps: true,

                }


            ]
        };

        // Notice the scaleLabel at the same level as Ticks
        var options = {
            scales: {
                yAxes: [{
                    ticks: {
                        beginAtZero: true
                    },
                    scaleLabel: {
                        display: true,
                        labelString: 'Power',
                        fontSize: 20
                    }
                }]
            }
        };

        // Chart declaration:
        var myChart = new Chart(ctx, {
            type: 'line',
            data: data,
            options: options
        });
    }
}
</script>