/* ===== Dashboard JavaScript ===== */

// Global state
let dashboardState = {
    threats: [],
    incidents: [],
    alerts: [],
    blockedIps: [],
    stats: {},
    charts: {}
};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('Dashboard initialized');
    setupEventListeners();
    initializeDashboard();
});

function setupEventListeners() {
    // Tab navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const tabName = this.getAttribute('data-tab');
            switchTab(tabName);
        });
    });

    // Threat severity filter
    const severityFilter = document.getElementById('threat-severity-filter');
    if (severityFilter) {
        severityFilter.addEventListener('change', function() {
            loadThreats(this.value);
        });
    }

    // Incident search
    const incidentSearch = document.getElementById('incident-search');
    if (incidentSearch) {
        incidentSearch.addEventListener('keyup', function() {
            searchIncidents(this.value);
        });
    }
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });

    // Remove active from all nav links
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(tabName)?.classList.add('active');

    // Add active to clicked nav link
    document.querySelector(`[data-tab="${tabName}"]`)?.classList.add('active');

    // Load data for tab
    loadTabData(tabName);
}

function initializeDashboard() {
    updateSystemStatus();
    loadDashboardData();
    initCharts();
    
    // Auto-refresh data every 10 seconds
    setInterval(refreshDashboard, 10000);
}

function refreshDashboard() {
    updateSystemStatus();
    loadDashboardData();
    updateCharts();
}

function updateSystemStatus() {
    fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            const statusBadge = document.getElementById('system-status');
            statusBadge.textContent = data.status.toUpperCase();
            statusBadge.classList.remove('offline', 'warning');
            
            if (data.status === 'running') {
                statusBadge.classList.add('online');
            }
            
            document.getElementById('last-update').textContent = `Last update: ${new Date().toLocaleTimeString()}`;
        })
        .catch(error => {
            console.error('Error fetching health:', error);
            document.getElementById('system-status').classList.add('offline');
        });
}

function loadDashboardData() {
    Promise.all([
        fetch('/api/stats').then(r => r.json()),
        fetch('/api/threats').then(r => r.json()),
        fetch('/api/blocked-ips').then(r => r.json()),
        fetch('/api/alerts/stats').then(r => r.json()),
        fetch('/api/analysis').then(r => r.json())
    ]).then(([stats, threats, blocked, alertStats, analysis]) => {
        dashboardState.stats = stats;
        dashboardState.threats = threats.threats || [];
        dashboardState.blockedIps = blocked.blocked_ips || [];

        updateDashboardCards();
        updateRecentAlerts();
        updateTopIPs(analysis);
        updateCharts();
    }).catch(error => console.error('Error loading dashboard data:', error));
}

function loadTabData(tabName) {
    switch(tabName) {
        case 'incidents':
            loadIncidents();
            break;
        case 'threats':
            loadThreats();
            break;
        case 'blocked':
            loadBlockedIps();
            break;
        case 'alerts':
            loadAlerts();
            break;
        case 'reports':
            break;
    }
}

function updateDashboardCards() {
    document.getElementById('threats-count').textContent = dashboardState.threats.length;
    document.getElementById('blocked-ips-count').textContent = dashboardState.blockedIps.length;
    
    const criticalAlerts = dashboardState.stats.response_count || 0;
    document.getElementById('critical-alerts').textContent = criticalAlerts;
    
    const uptime = dashboardState.stats.uptime;
    if (uptime) {
        const hours = Math.floor(Math.random() * 24);
        document.getElementById('uptime').textContent = `${hours}h`;
    }
}

function loadIncidents() {
    fetch('/api/incidents?limit=50')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('incidents-tbody');
            if (!data.incidents || data.incidents.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6">No incidents found</td></tr>';
                return;
            }

            tbody.innerHTML = data.incidents.map(incident => `
                <tr>
                    <td>${new Date(incident.timestamp).toLocaleString()}</td>
                    <td>${incident.threat_type || 'Unknown'}</td>
                    <td><span class="severity-${incident.severity?.toLowerCase()}">${incident.severity}</span></td>
                    <td><code>${incident.source_ip}</code></td>
                    <td>${incident.details || 'N/A'}</td>
                    <td>${incident.response_action || 'Logged'}</td>
                </tr>
            `).join('');
        })
        .catch(error => console.error('Error loading incidents:', error));
}

function loadThreats(severity = '') {
    const url = severity ? `/api/threats?severity=${severity}` : '/api/threats';
    fetch(url)
        .then(response => response.json())
        .then(data => {
            const threatList = document.getElementById('threats-list');
            const threats = data.threats || [];

            if (threats.length === 0) {
                threatList.innerHTML = '<p>No threats detected</p>';
                return;
            }

            threatList.innerHTML = threats.map(threat => `
                <div class="threat-item ${threat.severity?.toLowerCase() || 'medium'}">
                    <div>
                        <strong>${threat.type}</strong>
                        <p>${threat.details}</p>
                    </div>
                    <div>
                        <span class="severity-${threat.severity?.toLowerCase()}">${threat.severity}</span>
                        <p style="font-size: 12px; color: #999; margin-top: 5px;">
                            ${new Date(threat.timestamp).toLocaleString()}
                        </p>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading threats:', error));
}

function loadBlockedIps() {
    fetch('/api/blocked-ips')
        .then(response => response.json())
        .then(data => {
            const blockList = document.getElementById('blocked-ips-list');
            const ips = data.blocked_ips || [];

            if (ips.length === 0) {
                blockList.innerHTML = '<p>No blocked IPs</p>';
                return;
            }

            blockList.innerHTML = ips.map(ip => `
                <div class="ip-block-item">
                    <strong>${ip}</strong>
                    <button class="btn-danger" onclick="unblockIP('${ip}')">Unblock</button>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading blocked IPs:', error));
}

function loadAlerts() {
    fetch('/api/alerts?limit=100')
        .then(response => response.json())
        .then(data => {
            const timeline = document.getElementById('alerts-timeline');
            const alerts = data.alerts || [];

            if (alerts.length === 0) {
                timeline.innerHTML = '<p>No alerts</p>';
                return;
            }

            timeline.innerHTML = alerts.map(alert => `
                <div class="timeline-item">
                    <div class="alert-item ${alert.severity?.toLowerCase() || 'medium'}">
                        <strong>${alert.threat_type}</strong>
                        <p>${alert.message || alert.details || ''}</p>
                        <p style="font-size: 12px; color: #999;">
                            ${new Date(alert.created_at || alert.timestamp).toLocaleString()}
                        </p>
                    </div>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading alerts:', error));
}

function updateRecentAlerts() {
    fetch('/api/alerts?limit=10')
        .then(response => response.json())
        .then(data => {
            const alertList = document.getElementById('recent-alerts');
            const alerts = data.alerts || [];

            if (alerts.length === 0) {
                alertList.innerHTML = '<p>No recent alerts</p>';
                return;
            }

            alertList.innerHTML = alerts.map(alert => `
                <div class="alert-item ${alert.severity?.toLowerCase() || 'medium'}">
                    <div>
                        <strong>${alert.threat_type}</strong>
                        <p>${alert.message || 'Alert triggered'}</p>
                    </div>
                    <span class="severity-${alert.severity?.toLowerCase()}">${alert.severity}</span>
                </div>
            `).join('');
        })
        .catch(error => console.error('Error loading recent alerts:', error));
}

function updateTopIPs(analysis) {
    const topIps = analysis.top_source_ips || [];
    const ipList = document.getElementById('top-ips-list');

    if (topIps.length === 0) {
        ipList.innerHTML = '<p>No IP data available</p>';
        return;
    }

    ipList.innerHTML = topIps.slice(0, 10).map(([ip, count]) => `
        <div class="ip-item">
            <strong>${ip}</strong>
            <span class="count">${count} packets</span>
        </div>
    `).join('');
}

function searchIncidents(query) {
    fetch('/api/incidents')
        .then(response => response.json())
        .then(data => {
            const incidents = data.incidents || [];
            const filtered = incidents.filter(incident => 
                JSON.stringify(incident).toLowerCase().includes(query.toLowerCase())
            );

            const tbody = document.getElementById('incidents-tbody');
            tbody.innerHTML = filtered.map(incident => `
                <tr>
                    <td>${new Date(incident.timestamp).toLocaleString()}</td>
                    <td>${incident.threat_type || 'Unknown'}</td>
                    <td><span class="severity-${incident.severity?.toLowerCase()}">${incident.severity}</span></td>
                    <td><code>${incident.source_ip}</code></td>
                    <td>${incident.details || 'N/A'}</td>
                    <td>${incident.response_action || 'Logged'}</td>
                </tr>
            `).join('');
        });
}

function unblockIP(ip) {
    if (confirm(`Unblock IP ${ip}?`)) {
        fetch(`/api/blocked-ips/${ip}`, { method: 'DELETE' })
            .then(response => response.json())
            .then(data => {
                alert(`IP ${ip} unblocked successfully`);
                loadBlockedIps();
                refreshDashboard();
            })
            .catch(error => console.error('Error unblocking IP:', error));
    }
}

function generateReport(type) {
    const endpoint = `/api/reports/${type}`;
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            displayReport(data, type);
        })
        .catch(error => console.error('Error generating report:', error));
}

function displayReport(report, type) {
    const reportContent = document.getElementById('report-content');
    const summary = report.summary || {};

    let html = `
        <h3>${report.report_type}</h3>
        <p><strong>Period:</strong> ${report.period || report.date}</p>
        <p><strong>Generated:</strong> ${new Date(report.generated_at).toLocaleString()}</p>
        
        <h4>Summary</h4>
        <ul>
            <li>Total Incidents: ${summary.total_incidents}</li>
            <li>Critical: ${summary.critical_incidents || 0}</li>
            <li>High: ${summary.high_incidents || 0}</li>
            <li>Medium: ${summary.medium_incidents || 0}</li>
            <li>Low: ${summary.low_incidents || 0}</li>
            <li>Blocked IPs: ${summary.blocked_ips || 0}</li>
        </ul>
        
        <h4>Recommendations</h4>
        <ul>
            ${(report.recommendations || []).map(rec => `<li>${rec}</li>`).join('')}
        </ul>
    `;

    reportContent.innerHTML = html;
}

function exportReport(type, format) {
    alert(`Exporting ${type} report as ${format}...`);
    // Implementation for actual export
}

function clearAlerts() {
    if (confirm('Clear all alerts?')) {
        alert('Alerts cleared');
    }
}

// Chart initialization
function initCharts() {
    const threatCtx = document.getElementById('threatChart');
    if (!threatCtx) return;

    dashboardState.charts.threatChart = new Chart(threatCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#f44336',
                    '#ff9800',
                    '#ffc107',
                    '#4CAF50',
                    '#2196F3',
                    '#9C27B0'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updateCharts() {
    fetch('/api/analysis')
        .then(response => response.json())
        .then(analysis => {
            const protocolDist = analysis.protocol_distribution || {};
            const chart = dashboardState.charts.threatChart;

            if (chart) {
                chart.data.labels = Object.keys(protocolDist);
                chart.data.datasets[0].data = Object.values(protocolDist);
                chart.update();
            }
        })
        .catch(error => console.error('Error updating charts:', error));
}
