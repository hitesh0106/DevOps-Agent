/**
 * DevOps Agent — Charts Controller
 * Manages all data visualizations using Chart.js.
 */

document.addEventListener('DOMContentLoaded', () => {
    initMainHealthChart();
    initSecurityChart();
    initCostChart();
});

// Chart Global Defaults
Chart.defaults.color = '#8892a4';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.05)';

// ── MAIN HEALTH CHART (DASHBOARD) ───────────────────────────────────────
function initMainHealthChart() {
    const ctx = document.getElementById('mainHealthChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
            datasets: [
                {
                    label: 'CPU Usage %',
                    data: [42, 38, 55, 78, 62, 58, 45],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Memory Usage %',
                    data: [65, 62, 68, 72, 70, 75, 70],
                    borderColor: '#8b5cf6',
                    backgroundColor: 'rgba(139, 92, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top', align: 'end' }
            },
            scales: {
                y: { beginAtZero: true, max: 100 }
            }
        }
    });
}

// ── SECURITY VULNERABILITY CHART ────────────────────────────────────────
function initSecurityChart() {
    const ctx = document.getElementById('securityChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Passed'],
            datasets: [{
                data: [0, 2, 14, 142],
                backgroundColor: [
                    '#ef4444', // Danger
                    '#f59e0b', // Warning
                    '#3b82f6', // Info/Primary
                    '#10b981'  // Success
                ],
                borderWidth: 0,
                hoverOffset: 15
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });
}

// ── FINOPS COST TREND CHART ─────────────────────────────────────────────
function initCostChart() {
    const ctx = document.getElementById('costChart');
    if (!ctx) return;

    new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
            datasets: [
                {
                    label: 'Actual Spend',
                    data: [850, 920, 1100, 1050],
                    backgroundColor: 'rgba(59, 130, 246, 0.5)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                },
                {
                    label: 'Budget',
                    data: [1000, 1000, 1000, 1000],
                    type: 'line',
                    borderColor: '#ef4444',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'top' }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}
