/**
 * JavaScript file for the network statistics page
 */

// DOM elements
const activeConnectionsElement = document.getElementById('activeConnections');
const totalConnectionsElement = document.getElementById('totalConnections');
const totalDownloadedElement = document.getElementById('totalDownloaded');
const downloadRateElement = document.getElementById('downloadRate');
const totalUploadedElement = document.getElementById('totalUploaded');
const uploadRateElement = document.getElementById('uploadRate');
const transferRatioElement = document.getElementById('transferRatio');
const totalTransferredElement = document.getElementById('totalTransferred');
const connectionListElement = document.getElementById('connectionList');
const refreshStatsBtn = document.getElementById('refreshStatsBtn');

// Chart variables
let transferChart = null;
let chartData = {
    labels: [],
    uploads: [],
    downloads: []
};

// Update interval (in ms)
const UPDATE_INTERVAL = 5000;
let updateTimer = null;

// Initialize chart
function initializeChart() {
    const ctx = document.getElementById('transferChart').getContext('2d');
    
    transferChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Uploads',
                    data: [],
                    borderColor: 'rgba(255, 193, 7, 1)',
                    backgroundColor: 'rgba(255, 193, 7, 0.2)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Downloads',
                    data: [],
                    borderColor: 'rgba(40, 167, 69, 1)',
                    backgroundColor: 'rgba(40, 167, 69, 0.2)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                },
                y: {
                    title: {
                        display: true,
                        text: 'Data (bytes)'
                    },
                    beginAtZero: true
                }
            }
        }
    });
}

// Load network statistics from the server
async function loadNetworkStats() {
    const stats = await fetchData('/api/network_stats');
    
    if (!stats) {
        return;
    }
    
    updateStatCards(stats);
    updateConnectionTable(stats.connection_history);
    updateChart(stats);
}

// Update the statistical cards
function updateStatCards(stats) {
    // Format values
    const formattedUploaded = formatFileSize(stats.total_bytes_uploaded);
    const formattedDownloaded = formatFileSize(stats.total_bytes_downloaded);
    const formattedTotalTransferred = formatFileSize(stats.total_bytes_uploaded + stats.total_bytes_downloaded);
    
    const uploadRateFormatted = formatFileSize(stats.upload_rate) + '/s';
    const downloadRateFormatted = formatFileSize(stats.download_rate) + '/s';
    
    // Calculate ratio
    let ratio = "N/A";
    if (stats.total_bytes_downloaded > 0) {
        ratio = (stats.total_bytes_uploaded / stats.total_bytes_downloaded).toFixed(2);
    }
    
    // Update DOM elements
    activeConnectionsElement.textContent = stats.active_connections;
    totalConnectionsElement.textContent = `Total: ${stats.total_connections}`;
    
    totalUploadedElement.textContent = formattedUploaded;
    uploadRateElement.textContent = `Rate: ${uploadRateFormatted}`;
    
    totalDownloadedElement.textContent = formattedDownloaded;
    downloadRateElement.textContent = `Rate: ${downloadRateFormatted}`;
    
    transferRatioElement.textContent = ratio;
    totalTransferredElement.textContent = `Total: ${formattedTotalTransferred}`;
}

// Update the connection history table
function updateConnectionTable(connections) {
    if (!connections || connections.length === 0) {
        connectionListElement.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">No connection history available</td>
            </tr>
        `;
        return;
    }
    
    // Sort connections by time (newest first)
    connections.sort((a, b) => b.connection_time - a.connection_time);
    
    let tableHtml = '';
    connections.forEach(conn => {
        const connectionTime = formatDate(conn.connection_time);
        const uploadedSize = formatFileSize(conn.bytes_uploaded);
        const downloadedSize = formatFileSize(conn.bytes_downloaded);
        const statusClass = conn.active ? 'bg-success' : 'bg-secondary';
        const statusText = conn.active ? 'Active' : 'Disconnected';
        
        tableHtml += `
            <tr>
                <td><code>${conn.client_id.substring(0, 8)}...</code></td>
                <td>${conn.ip_address}</td>
                <td>${connectionTime}</td>
                <td>${uploadedSize}</td>
                <td>${downloadedSize}</td>
                <td><span class="badge ${statusClass}">${statusText}</span></td>
            </tr>
        `;
    });
    
    connectionListElement.innerHTML = tableHtml;
}

// Update the transfer chart
function updateChart(stats) {
    const now = new Date();
    const timeLabel = now.toLocaleTimeString();
    
    // Add new data point
    chartData.labels.push(timeLabel);
    chartData.uploads.push(stats.total_bytes_uploaded);
    chartData.downloads.push(stats.total_bytes_downloaded);
    
    // Keep only the last 20 data points to avoid cluttering
    if (chartData.labels.length > 20) {
        chartData.labels.shift();
        chartData.uploads.shift();
        chartData.downloads.shift();
    }
    
    // Update chart
    transferChart.data.labels = chartData.labels;
    transferChart.data.datasets[0].data = chartData.uploads;
    transferChart.data.datasets[1].data = chartData.downloads;
    transferChart.update();
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize chart
    initializeChart();
    
    // Load initial stats
    loadNetworkStats();
    
    // Set up automatic updates
    updateTimer = setInterval(loadNetworkStats, UPDATE_INTERVAL);
    
    // Manual refresh button
    refreshStatsBtn.addEventListener('click', loadNetworkStats);
    
    // Clean up when navigating away
    window.addEventListener('beforeunload', () => {
        if (updateTimer) {
            clearInterval(updateTimer);
        }
    });
});
