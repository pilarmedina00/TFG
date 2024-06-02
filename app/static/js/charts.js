document.addEventListener("DOMContentLoaded", function() {
    // Pie chart para sentimientos con filtros
    const labels = Object.keys(sentimentsData);
    const counts = Object.values(sentimentsData);

    const ctxPie = document.getElementById('myPieChart').getContext('2d');
    const myPieChart = new Chart(ctxPie, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',  // Verde para positivo
                    'rgba(255, 205, 86, 0.5)', // Amarillo para neutral
                    'rgba(75, 192, 192, 0.5)' // Rojo para negativo
                ],
                borderColor: [
                    'rgba(255, 99, 132, 1)',
                    'rgba(255, 205, 86, 1)',
                    'rgba(75, 192, 192, 1)'
                ],
                borderWidth: 1.5
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        generateLabels: function(chart) {
                            return chart.data.labels.map(function(label, i) {
                                return {
                                    text: label,
                                    fillStyle: chart.data.datasets[0].backgroundColor[i]
                                };
                            });
                        }
                    }
                }
            }
        }
    });
    
    // Chart de barras verticales para sentmientos de comentarios generales
    fetch('/data')
    .then(response => response.json())
    .then(data => {
        const labels = data.map(video => video.title);
        const sentiments = data.map(video => video.comments.reduce((acc, comment) => {
            acc[comment.sentiment] = (acc[comment.sentiment] || 0) + 1;
            return acc;
        }, {}));

        const positiveData = sentiments.map(sentiment => sentiment.positive || 0);
        const neutralData = sentiments.map(sentiment => sentiment.neutral || 0);
        const negativeData = sentiments.map(sentiment => sentiment.negative || 0);

        const ctx = document.getElementById('myChart').getContext('2d');
        const myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Positivo',
                        data: positiveData,
                        backgroundColor: 'rgba(75, 192, 192, 0.3)', // Verde
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1.5
                    },
                    {
                        label: 'Neutral',
                        data: neutralData,
                        backgroundColor: 'rgba(255, 205, 86, 0.3)', // Amarillo
                        borderColor: 'rgba(255, 205, 86, 1)',
                        borderWidth: 1.5
                    },
                    {
                        label: 'Negativo',
                        data: negativeData,
                        backgroundColor: 'rgba(224, 31, 44, 0.3)', // Rojo
                        borderColor: 'rgba(224, 31, 44, 1)',
                        borderWidth: 1.5
                    }
                ]
            },
            options: {
                maintainAspectRatio: false,
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    });

    // Chart de barras horizontales para top 5 de palabras más repetidas en el tópico
    fetch('/top_words')
    .then(response => response.json())
    .then(data => {
        // Procesar datos y dibujar gráfico de barras horizontales
        const ctx = document.getElementById('myBarChart').getContext('2d');
        const myBarChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.frequencies,
                    backgroundColor: [
                        'rgba(201, 97, 237, 0.5)', // Lila
                        'rgba(179, 237, 97, 0.5)', // Pistacho
                        'rgba(235, 152, 51, 0.5)', // Naranja
                        'rgba(159, 192, 239, 0.5)', // Azul
                        'rgba(233, 124, 195, 0.5)'  // Rosa
                    ],
                    borderColor: [
                        'rgba(201, 97, 237, 1)',
                        'rgba(179, 237, 97, 1)',
                        'rgba(235, 152, 51, 1)',
                        'rgba(159, 192, 239, 1)',
                        'rgba(233, 124, 195, 1)'
                    ],
                    borderWidth: 2.5
                }]
            },
            options: {
                responsive: true,
                indexAxis: 'y',
                scales: {
                    x: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    });
});
