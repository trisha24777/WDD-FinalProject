document.addEventListener('DOMContentLoaded', function() {
    const dataElement = document.getElementById('chart-data');
    if (!dataElement || typeof Chart === 'undefined') {
        console.error('Chart.js or chartData element not found');
        return;
    }

    const chartData = JSON.parse(dataElement.textContent);

    // Common Tooltip Config
    const tooltipConfig = {
        backgroundColor: '#0f172a',
        titleFont: { size: 14, weight: 'bold' },
        bodyFont: { size: 13 },
        padding: 12,
        displayColors: false,
        borderRadius: 10
    };

    // 1. Sales Performance (Line Chart)
    const salesCtx = document.getElementById('salesChart');
    if (salesCtx) {
        new Chart(salesCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: chartData.salesDates,
                datasets: [{
                    label: 'Revenue',
                    data: chartData.salesValues,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 3,
                    pointBackgroundColor: '#1e293b',
                    pointRadius: 4,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { display: false },
                    tooltip: tooltipConfig
                },
                scales: {
                    y: { 
                        beginAtZero: true, 
                        grid: { color: '#f1f5f9', drawBorder: false },
                        ticks: {
                            callback: function(value) { return '$' + value.toLocaleString(); }
                        }
                    },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 2. User Growth (Bar Chart)
    const userCtx = document.getElementById('userChart');
    if (userCtx) {
        const ctx = userCtx.getContext('2d');
        const userGradient = ctx.createLinearGradient(0, 0, 0, 400);
        userGradient.addColorStop(0, '#3b82f6');
        userGradient.addColorStop(1, '#1e293b');

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.userDates,
                datasets: [{
                    label: 'New Users',
                    data: chartData.userCounts,
                    backgroundColor: userGradient,
                    hoverBackgroundColor: '#2563eb',
                    borderRadius: 6,
                    barThickness: 20
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { display: false },
                    tooltip: tooltipConfig
                },
                scales: {
                    y: { 
                        beginAtZero: true, 
                        grid: { color: '#f1f5f9', drawBorder: false },
                        ticks: { stepSize: 1, color: '#64748b' }
                    },
                    x: { 
                        grid: { display: false },
                        ticks: { color: '#64748b' }
                    }
                }
            }
        });
    }

    // 3. Room Type Distribution (Doughnut)
    const roomCtx = document.getElementById('roomChart');
    if (roomCtx) {
        new Chart(roomCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: chartData.roomLabels,
                datasets: [{
                    data: chartData.roomCounts,
                    backgroundColor: ['#1e293b', '#3b82f6', '#94a3b8', '#64748b'],
                    borderWidth: 0,
                    hoverOffset: 10
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { 
                    legend: { 
                        position: 'bottom',
                        labels: { 
                            boxWidth: 12, 
                            padding: 20, 
                            font: { size: 12, family: "'Inter', sans-serif" },
                            usePointStyle: true
                        }
                    },
                    tooltip: tooltipConfig
                },
                cutout: '75%'
            }
        });
    }
});

