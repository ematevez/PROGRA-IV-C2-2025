// Charts
function createChart(title = '', type = 'bar', labels = [], mdata = [], canvasId) {
    if (labels.length == 0 && mdata.length == 0) return;

    let data = {};
    let config = {};

    if (type == 'doughnut') {
        data = {
            labels,
            datasets: [{
                data: mdata,
                backgroundColor: [
                    'rgb(255, 205, 86)',
                    'rgb(255, 99, 132)',
                    'rgb(30, 99, 255)',
                    'rgb(25, 55, 86)'
                ],
                hoverOffset: 4
            }]
        };

        config = {
            type: 'doughnut',
            data: data,
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'right',
                    }
                }
            },
        };

    } else {
        data = {
            labels: labels,
            datasets: [{
                label: title,
                backgroundColor: '#ecab08',
                borderColor: '#ecab08',
                data: mdata,
            }]
        };

        config = {
            type: type,
            data: data,
            options: {
                scales: {
                    y: {
                        startAtZero: true
                    }
                }
            }
        };
    }

    // Render chart
    const myChart = new Chart(
        document.getElementById(canvasId),
        config
    );
    return myChart;
}
