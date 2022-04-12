<template>
    <div class="widget" id="area-chart">
        <div>
            <span>Stat 1</span>
        </div>
        <canvas id="myAreaChart"></canvas>
    </div>
</template>

<script>
module.exports = {
    mounted() {

        var ctx = document.getElementById('myAreaChart').getContext('2d');
        var chart = new Chart(ctx, {
            // The type of chart we want to create
            type: 'line',

            // The data for our dataset
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
                datasets: [{
                    label: 'My First dataset',
                    backgroundColor: 'rgb(99, 132, 0, 0.6)',
                    borderColor: 'rgb(24, 201, 71)',
                    data: [0, 10, 5, 2, 20, 30, 45]
                }]
            },

            // Configuration options go here
            options: {}
        });
    }
}
</script>