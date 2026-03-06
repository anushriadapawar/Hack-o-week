// Global variables
let currentData = null;
let energyChart = null;
let carbonChart = null;
let wasteChart = null;
let waterChart = null;
let forecastChart = null;

// Chart color scheme
const colors = {
    primary: 'rgba(46, 204, 113, 0.8)',
    primaryBorder: 'rgb(46, 204, 113)',
    secondary: 'rgba(26, 188, 156, 0.8)',
    secondaryBorder: 'rgb(26, 188, 156)',
    danger: 'rgba(231, 76, 60, 0.8)',
    dangerBorder: 'rgb(231, 76, 60)',
    info: 'rgba(52, 152, 219, 0.8)',
    infoBorder: 'rgb(52, 152, 219)',
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadDefaultData();
});

function setupEventListeners() {
    // File upload
    document.getElementById('file-upload').addEventListener('change', handleFileUpload);
    
    // Load default data button
    document.getElementById('load-default-btn').addEventListener('click', loadDefaultData);
    
    // Filter
    document.getElementById('apply-filter').addEventListener('click', applyBuildingFilter);
    
    // Forecast buttons
    document.getElementById('forecast-btn').addEventListener('click', loadForecast);
    document.getElementById('ma-btn').addEventListener('click', loadMovingAverage);
    document.getElementById('exp-smooth-btn').addEventListener('click', loadExponentialSmoothing);
}

function showLoading(show = true) {
    const loadingEl = document.getElementById('loading');
    if (show) {
        loadingEl.classList.remove('hidden');
    } else {
        loadingEl.classList.add('hidden');
    }
}

function loadDefaultData() {
    showLoading(true);
    fetch('/api/load-data', { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentData = data;
                updateDashboard(data);
                populateBuildingFilter(data.buildings);
            } else {
                alert('Error loading data: ' + data.message);
            }
            showLoading(false);
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Failed to load data');
            showLoading(false);
        });
}

function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    showLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    fetch('/api/upload', { method: 'POST', body: formData })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentData = data;
                updateDashboard(data);
                populateBuildingFilter(data.buildings);
                alert('File uploaded successfully!');
            } else {
                alert('Error: ' + data.message);
            }
            showLoading(false);
        })
        .catch(err => {
            console.error('Error:', err);
            alert('Failed to upload file');
            showLoading(false);
        });
}

function updateDashboard(data) {
    // Update KPI cards
    document.getElementById('total-energy').textContent = data.kpis.total_energy.toLocaleString();
    document.getElementById('total-carbon').textContent = data.kpis.total_carbon.toLocaleString();
    document.getElementById('carbon-savings').textContent = data.kpis.carbon_savings.toLocaleString();
    document.getElementById('total-water').textContent = data.kpis.total_water.toLocaleString();
    document.getElementById('total-waste').textContent = data.kpis.total_waste.toLocaleString();
    document.getElementById('avg-energy').textContent = data.kpis.avg_energy.toLocaleString();

    // Update charts
    updateEnergyChart(data.time_series);
    updateCarbonChart(data.time_series);
    updateWasteChart(data.time_series);
    updateWaterChart(data.time_series);
}

function populateBuildingFilter(buildings) {
    const select = document.getElementById('building-filter');
    select.innerHTML = '<option value="">All Buildings</option>';
    buildings.forEach(building => {
        const option = document.createElement('option');
        option.value = building;
        option.textContent = building;
        select.appendChild(option);
    });
}

function applyBuildingFilter() {
    const building = document.getElementById('building-filter').value;
    
    if (!building) {
        // Show all buildings data
        document.getElementById('building-details').style.display = 'none';
        updateDashboard(currentData);
    } else {
        // Fetch building-specific data
        showLoading(true);
        fetch(`/api/building/${encodeURIComponent(building)}`)
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    displayBuildingDetails(data.data);
                    showLoading(false);
                }
            })
            .catch(err => {
                console.error('Error:', err);
                showLoading(false);
            });
    }
}

function displayBuildingDetails(building) {
    const detailsSection = document.getElementById('building-details');
    detailsSection.style.display = 'block';
    
    document.getElementById('building-name').textContent = building.building;
    document.getElementById('building-energy').textContent = building.total_energy + ' kWh';
    document.getElementById('building-carbon').textContent = building.total_carbon + ' kg CO₂';
    document.getElementById('building-water').textContent = building.total_water + ' Liters';
    document.getElementById('building-waste').textContent = building.total_waste + ' kg';
    document.getElementById('building-avg-energy').textContent = building.avg_energy + ' kWh';
}

// Chart update functions
function updateEnergyChart(timeSeries) {
    const ctx = document.getElementById('energyChart').getContext('2d');
    
    if (energyChart) {
        energyChart.destroy();
    }
    
    energyChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeSeries.dates,
            datasets: [{
                label: 'Energy Usage (kWh)',
                data: timeSeries.energy,
                borderColor: colors.primaryBorder,
                backgroundColor: colors.primary,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function updateCarbonChart(timeSeries) {
    const ctx = document.getElementById('carbonChart').getContext('2d');
    
    if (carbonChart) {
        carbonChart.destroy();
    }
    
    carbonChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeSeries.dates,
            datasets: [{
                label: 'Carbon Emissions (kg CO₂)',
                data: timeSeries.carbon,
                borderColor: colors.dangerBorder,
                backgroundColor: colors.danger,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function updateWasteChart(timeSeries) {
    const ctx = document.getElementById('wasteChart').getContext('2d');
    
    if (wasteChart) {
        wasteChart.destroy();
    }
    
    wasteChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: timeSeries.dates,
            datasets: [{
                label: 'Waste Generation (kg)',
                data: timeSeries.waste,
                borderColor: colors.infoBorder,
                backgroundColor: colors.info,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function updateWaterChart(timeSeries) {
    const ctx = document.getElementById('waterChart').getContext('2d');
    
    if (waterChart) {
        waterChart.destroy();
    }
    
    waterChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: timeSeries.dates,
            datasets: [{
                label: 'Water Consumption (Liters)',
                data: timeSeries.water,
                borderColor: colors.secondaryBorder,
                backgroundColor: colors.secondary,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                pointHoverRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

function loadForecast() {
    showLoading(true);
    fetch('/api/forecast')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayForecast(data.forecast, 'Linear Regression - 30 Day Forecast');
                showLoading(false);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            showLoading(false);
        });
}

function loadMovingAverage() {
    showLoading(true);
    fetch('/api/smoothing')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayForecast(data.moving_average, 'Moving Average (7-Day Window)');
                showLoading(false);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            showLoading(false);
        });
}

function loadExponentialSmoothing() {
    showLoading(true);
    fetch('/api/exponential-smoothing')
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                displayForecast(data.exponential_smoothing, 'Exponential Smoothing (α=0.3)');
                showLoading(false);
            }
        })
        .catch(err => {
            console.error('Error:', err);
            showLoading(false);
        });
}

function displayForecast(forecastData, title) {
    const container = document.getElementById('forecast-chart-container');
    container.style.display = 'block';
    
    // Update title
    container.querySelector('h3').textContent = title;
    
    const ctx = document.getElementById('forecastChart').getContext('2d');
    
    if (forecastChart) {
        forecastChart.destroy();
    }
    
    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: forecastData.dates,
            datasets: [{
                label: 'Predicted Energy Usage (kWh)',
                data: forecastData.values,
                borderColor: 'rgb(155, 89, 182)',
                backgroundColor: 'rgba(155, 89, 182, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                borderDash: [5, 5]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: { position: 'top' },
                title: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
    
    // Scroll to chart
    container.scrollIntoView({ behavior: 'smooth' });
}
