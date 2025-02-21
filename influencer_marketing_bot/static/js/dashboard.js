// Dashboard functionality for Influencer Marketing Bot

// Initialize charts when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    setupEventListeners();
});

// Initialize Chart.js charts
function initializeCharts() {
    // Engagement Rate Chart
    const engagementCtx = document.getElementById('engagementChart');
    if (engagementCtx) {
        new Chart(engagementCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Engagement Rate',
                    data: [4.2, 3.8, 5.1, 4.9, 5.3, 4.7],
                    borderColor: 'rgb(79, 70, 229)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Engagement Rate Trends'
                    }
                }
            }
        });
    }

    // Demographics Chart
    const demographicsCtx = document.getElementById('demographicsChart');
    if (demographicsCtx) {
        new Chart(demographicsCtx, {
            type: 'doughnut',
            data: {
                labels: ['13-17', '18-24', '25-34', '35-44', '45+'],
                datasets: [{
                    data: [10, 35, 25, 20, 10],
                    backgroundColor: [
                        'rgb(79, 70, 229)',
                        'rgb(67, 56, 202)',
                        'rgb(55, 48, 163)',
                        'rgb(49, 46, 129)',
                        'rgb(30, 27, 75)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    title: {
                        display: true,
                        text: 'Audience Demographics'
                    }
                }
            }
        });
    }
}

// Setup event listeners
function setupEventListeners() {
    // Campaign filter
    const campaignFilter = document.getElementById('campaignFilter');
    if (campaignFilter) {
        campaignFilter.addEventListener('change', filterCampaigns);
    }

    // Influencer search
    const searchInput = document.getElementById('influencerSearch');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(searchInfluencers, 300));
    }

    // Date range picker
    const dateRange = document.getElementById('dateRange');
    if (dateRange) {
        flatpickr(dateRange, {
            mode: 'range',
            dateFormat: 'Y-m-d',
            onChange: updateDateRange
        });
    }
}

// Filter campaigns
function filterCampaigns(event) {
    const status = event.target.value;
    const campaigns = document.querySelectorAll('.campaign-row');
    
    campaigns.forEach(campaign => {
        const campaignStatus = campaign.dataset.status;
        campaign.style.display = status === 'all' || campaignStatus === status ? '' : 'none';
    });
}

// Search influencers
async function searchInfluencers(event) {
    const query = event.target.value;
    if (query.length < 2) return;

    try {
        const response = await fetch(`/api/influencers/search/?q=${encodeURIComponent(query)}`);
        const data = await response.json();
        updateInfluencerResults(data);
    } catch (error) {
        console.error('Error searching influencers:', error);
    }
}

// Update influencer search results
function updateInfluencerResults(influencers) {
    const resultsContainer = document.getElementById('influencerResults');
    if (!resultsContainer) return;

    resultsContainer.innerHTML = '';
    
    influencers.forEach(influencer => {
        const card = createInfluencerCard(influencer);
        resultsContainer.appendChild(card);
    });
}

// Create influencer card
function createInfluencerCard(influencer) {
    const card = document.createElement('div');
    card.className = 'influencer-card relative rounded-lg border border-gray-300 bg-white px-6 py-5 shadow-sm flex items-center space-x-3 hover:border-gray-400';
    
    card.innerHTML = `
        <div class="flex-shrink-0">
            <img class="h-10 w-10 rounded-full" src="${influencer.profile_image || ''}" alt="">
        </div>
        <div class="flex-1 min-w-0">
            <a href="#" class="focus:outline-none">
                <p class="text-sm font-medium text-gray-900">${influencer.name}</p>
                <p class="text-sm text-gray-500 truncate">${influencer.followers_count.toLocaleString()} Followers • ${influencer.engagement_rate}% Engagement Rate</p>
            </a>
        </div>
    `;
    
    return card;
}

// Update date range
function updateDateRange(selectedDates, dateStr) {
    // Update charts and data based on selected date range
    const [startDate, endDate] = selectedDates;
    fetchDataForDateRange(startDate, endDate);
}

// Fetch data for date range
async function fetchDataForDateRange(startDate, endDate) {
    try {
        const response = await fetch(`/api/analytics/?start_date=${startDate.toISOString()}&end_date=${endDate.toISOString()}`);
        const data = await response.json();
        updateCharts(data);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Update charts with new data
function updateCharts(data) {
    // Update engagement rate chart
    const engagementChart = Chart.getChart('engagementChart');
    if (engagementChart) {
        engagementChart.data.labels = data.dates;
        engagementChart.data.datasets[0].data = data.engagement_rates;
        engagementChart.update();
    }

    // Update demographics chart
    const demographicsChart = Chart.getChart('demographicsChart');
    if (demographicsChart) {
        demographicsChart.data.datasets[0].data = data.demographics;
        demographicsChart.update();
    }
}

// Utility function to debounce API calls
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export functions for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initializeCharts,
        setupEventListeners,
        filterCampaigns,
        searchInfluencers,
        updateInfluencerResults,
        createInfluencerCard,
        updateDateRange,
        fetchDataForDateRange,
        updateCharts,
        debounce
    };
} 