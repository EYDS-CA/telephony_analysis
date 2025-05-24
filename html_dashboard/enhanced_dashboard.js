// Enhanced Dashboard JavaScript
let allReviews = [];
let filteredReviews = [];
let insightsData = {};
let currentFilters = {
    time: 'all',
    provider: 'all',
    platform: 'all',
    category: 'all'
};

// Load data on page load
document.addEventListener('DOMContentLoaded', () => {
    loadData();
});

function loadData() {
    // Load the enhanced CSV data with Papa Parse
    Papa.parse('../telecom_reviews_enhanced.csv', {
        download: true,
        header: true,
        complete: function(results) {
            allReviews = results.data.filter(row => row.review_id); // Filter out empty rows
            console.log(`Loaded ${allReviews.length} reviews`);
            
            // Load insights data
            fetch('enhanced_insights_data.json')
                .then(response => response.json())
                .then(data => {
                    insightsData = data;
                    initializeDashboard();
                })
                .catch(error => {
                    console.error('Error loading insights:', error);
                    // Continue with just CSV data
                    initializeDashboard();
                });
        },
        error: function(error) {
            console.error('Error parsing CSV:', error);
            document.getElementById('loading').innerHTML = '<p>Error loading data. Please refresh the page.</p>';
        }
    });
}

function initializeDashboard() {
    // Hide loading, show dashboard
    document.getElementById('loading').style.display = 'none';
    document.getElementById('dashboard').style.display = 'block';
    
    // Populate category filter
    populateCategoryFilter();
    
    // Apply initial filters (show all data)
    applyFilters();
}

function populateCategoryFilter() {
    const categories = [...new Set(allReviews.map(r => r.enhanced_category))].sort();
    const categorySelect = document.getElementById('categoryFilter');
    
    categories.forEach(category => {
        if (category) {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categorySelect.appendChild(option);
        }
    });
}

function applyFilters() {
    // Get current filter values
    currentFilters.time = document.getElementById('timeFilter').value;
    currentFilters.provider = document.getElementById('providerFilter').value;
    currentFilters.platform = document.getElementById('platformFilter').value;
    currentFilters.category = document.getElementById('categoryFilter').value;
    
    // Filter reviews
    filteredReviews = allReviews.filter(review => {
        let match = true;
        
        if (currentFilters.time !== 'all') {
            match = match && review.year === currentFilters.time;
        }
        
        if (currentFilters.provider !== 'all') {
            match = match && review.app_name === currentFilters.provider;
        }
        
        if (currentFilters.platform !== 'all') {
            match = match && review.platform === currentFilters.platform;
        }
        
        if (currentFilters.category !== 'all') {
            match = match && review.enhanced_category === currentFilters.category;
        }
        
        return match;
    });
    
    // Update filter status
    updateFilterStatus();
    
    // Update all visualizations
    updateOverview();
    updateStrategicInsights();
    updateReviewExamples();
}

function updateFilterStatus() {
    const status = document.getElementById('filterStatus');
    const activeFilters = Object.entries(currentFilters)
        .filter(([key, value]) => value !== 'all')
        .map(([key, value]) => `${key}: ${value}`);
    
    if (activeFilters.length > 0) {
        status.textContent = `Active filters: ${activeFilters.join(', ')} | Showing ${filteredReviews.length} of ${allReviews.length} reviews`;
    } else {
        status.textContent = `Showing all ${allReviews.length} reviews`;
    }
}

function updateOverview() {
    // Update stats
    document.getElementById('totalReviews').textContent = filteredReviews.length.toLocaleString();
    
    const avgRating = filteredReviews.length > 0 
        ? (filteredReviews.reduce((sum, r) => sum + parseFloat(r.rating), 0) / filteredReviews.length).toFixed(1)
        : '0.0';
    document.getElementById('avgRating').textContent = avgRating + '/5';
    
    const appIssues = filteredReviews.filter(r => r.enhanced_primary_focus === 'APP-RELATED').length;
    const serviceIssues = filteredReviews.filter(r => r.enhanced_primary_focus === 'SERVICE-RELATED').length;
    
    document.getElementById('appIssues').textContent = 
        `${appIssues} (${((appIssues / filteredReviews.length) * 100).toFixed(1)}%)`;
    document.getElementById('serviceIssues').textContent = 
        `${serviceIssues} (${((serviceIssues / filteredReviews.length) * 100).toFixed(1)}%)`;
    
    // Update charts
    updateIssueDistributionChart();
    updateProviderComparisonChart();
    updateSentimentTrendChart();
}

function updateIssueDistributionChart() {
    const ctx = document.getElementById('issueDistChart').getContext('2d');
    
    // Count categories
    const categoryCounts = {};
    filteredReviews.forEach(review => {
        const category = review.enhanced_category || 'Unknown';
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    // Sort and take top 10
    const sortedCategories = Object.entries(categoryCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);
    
    // Destroy existing chart if it exists
    if (window.issueDistChart) {
        window.issueDistChart.destroy();
    }
    
    window.issueDistChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: sortedCategories.map(([cat, _]) => cat),
            datasets: [{
                data: sortedCategories.map(([_, count]) => count),
                backgroundColor: [
                    '#0066cc', '#e50000', '#00b050', '#ff9500', '#9c27b0',
                    '#00bcd4', '#ff5722', '#607d8b', '#795548', '#3f51b5'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

function updateProviderComparisonChart() {
    const ctx = document.getElementById('providerCompChart').getContext('2d');
    
    // Count by provider and focus
    const rogersData = {
        app: filteredReviews.filter(r => r.app_name === 'Rogers' && r.enhanced_primary_focus === 'APP-RELATED').length,
        service: filteredReviews.filter(r => r.app_name === 'Rogers' && r.enhanced_primary_focus === 'SERVICE-RELATED').length
    };
    
    const bellData = {
        app: filteredReviews.filter(r => r.app_name === 'Bell' && r.enhanced_primary_focus === 'APP-RELATED').length,
        service: filteredReviews.filter(r => r.app_name === 'Bell' && r.enhanced_primary_focus === 'SERVICE-RELATED').length
    };
    
    // Destroy existing chart
    if (window.providerCompChart) {
        window.providerCompChart.destroy();
    }
    
    window.providerCompChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Rogers', 'Bell'],
            datasets: [
                {
                    label: 'App-Related',
                    data: [rogersData.app, bellData.app],
                    backgroundColor: '#0066cc'
                },
                {
                    label: 'Service-Related',
                    data: [rogersData.service, bellData.service],
                    backgroundColor: '#e50000'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

function updateSentimentTrendChart() {
    const ctx = document.getElementById('sentimentTrendChart').getContext('2d');
    
    // Group by year and sentiment
    const yearData = {};
    filteredReviews.forEach(review => {
        const year = review.year;
        if (!yearData[year]) {
            yearData[year] = { positive: 0, negative: 0, neutral: 0, total: 0 };
        }
        yearData[year].total++;
        
        if (review.claude_sentiment === 'Positive') yearData[year].positive++;
        else if (review.claude_sentiment === 'Negative') yearData[year].negative++;
        else yearData[year].neutral++;
    });
    
    const years = Object.keys(yearData).sort();
    const positiveData = years.map(y => (yearData[y].positive / yearData[y].total * 100).toFixed(1));
    const negativeData = years.map(y => (yearData[y].negative / yearData[y].total * 100).toFixed(1));
    
    // Destroy existing chart
    if (window.sentimentTrendChart) {
        window.sentimentTrendChart.destroy();
    }
    
    window.sentimentTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [
                {
                    label: 'Positive %',
                    data: positiveData,
                    borderColor: '#00b050',
                    backgroundColor: 'rgba(0, 176, 80, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Negative %',
                    data: negativeData,
                    borderColor: '#e50000',
                    backgroundColor: 'rgba(229, 0, 0, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            }
        }
    });
}

function updateStrategicInsights() {
    // Update Rogers platform analysis
    updateRogersPlatformAnalysis();
    
    // Update provider comparison
    updateProviderComparison();
    
    // Update critical flows
    updateCriticalFlows();
    
    // Update key findings
    updateKeyFindings();
}

function updateRogersPlatformAnalysis() {
    const container = document.getElementById('rogersPlatformAnalysis');
    const rogersReviews = filteredReviews.filter(r => r.app_name === 'Rogers');
    
    const iosReviews = rogersReviews.filter(r => r.platform === 'iOS');
    const androidReviews = rogersReviews.filter(r => r.platform === 'Android');
    
    // Calculate stats for each platform
    const iosStats = calculatePlatformStats(iosReviews);
    const androidStats = calculatePlatformStats(androidReviews);
    
    container.innerHTML = `
        <div class="platform-card">
            <div class="platform-icon ios-icon"><i class="fab fa-apple"></i></div>
            <h3>iOS</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${iosStats.count}</div>
                    <div class="stat-label">Reviews</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${iosStats.avgRating}/5</div>
                    <div class="stat-label">Avg Rating</div>
                </div>
            </div>
            <div class="issue-list">
                <h4>Top Issues:</h4>
                ${iosStats.topIssues.map(([issue, count]) => 
                    `<div class="issue-item">
                        <span class="issue-name">${issue}</span>
                        <span class="issue-count">${count} (${(count/iosStats.count*100).toFixed(1)}%)</span>
                    </div>`
                ).join('')}
            </div>
        </div>
        
        <div class="platform-card">
            <div class="platform-icon android-icon"><i class="fab fa-android"></i></div>
            <h3>Android</h3>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">${androidStats.count}</div>
                    <div class="stat-label">Reviews</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${androidStats.avgRating}/5</div>
                    <div class="stat-label">Avg Rating</div>
                </div>
            </div>
            <div class="issue-list">
                <h4>Top Issues:</h4>
                ${androidStats.topIssues.map(([issue, count]) => 
                    `<div class="issue-item">
                        <span class="issue-name">${issue}</span>
                        <span class="issue-count">${count} (${(count/androidStats.count*100).toFixed(1)}%)</span>
                    </div>`
                ).join('')}
            </div>
        </div>
    `;
}

function calculatePlatformStats(reviews) {
    const stats = {
        count: reviews.length,
        avgRating: reviews.length > 0 
            ? (reviews.reduce((sum, r) => sum + parseFloat(r.rating), 0) / reviews.length).toFixed(1)
            : '0.0',
        topIssues: []
    };
    
    // Count issues
    const issueCounts = {};
    reviews.forEach(r => {
        const category = r.enhanced_category || 'Unknown';
        issueCounts[category] = (issueCounts[category] || 0) + 1;
    });
    
    stats.topIssues = Object.entries(issueCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    return stats;
}

function updateProviderComparison() {
    const container = document.getElementById('providerComparison');
    
    const rogersReviews = filteredReviews.filter(r => r.app_name === 'Rogers');
    const bellReviews = filteredReviews.filter(r => r.app_name === 'Bell');
    
    const rogersIssues = getTopIssues(rogersReviews, 5);
    const bellIssues = getTopIssues(bellReviews, 5);
    
    container.innerHTML = `
        <div class="provider-card rogers-card">
            <h3 class="provider-title rogers-title">
                <i class="fas fa-mobile-alt"></i> Rogers Customers Complain About:
            </h3>
            <div class="issue-list">
                ${rogersIssues.map(([issue, count, pct]) => 
                    `<div class="issue-item">
                        <span class="issue-name">${issue}</span>
                        <span class="issue-stats">
                            <span class="issue-count">${count} reviews</span>
                            <span>(${pct}%)</span>
                        </span>
                    </div>`
                ).join('')}
            </div>
        </div>
        
        <div class="provider-card bell-card">
            <h3 class="provider-title bell-title">
                <i class="fas fa-phone"></i> Bell Customers Complain About:
            </h3>
            <div class="issue-list">
                ${bellIssues.map(([issue, count, pct]) => 
                    `<div class="issue-item">
                        <span class="issue-name">${issue}</span>
                        <span class="issue-stats">
                            <span class="issue-count">${count} reviews</span>
                            <span>(${pct}%)</span>
                        </span>
                    </div>`
                ).join('')}
            </div>
        </div>
    `;
}

function getTopIssues(reviews, limit = 5) {
    const issueCounts = {};
    const negativeReviews = reviews.filter(r => r.claude_sentiment === 'Negative');
    
    negativeReviews.forEach(r => {
        const category = r.enhanced_category || 'Unknown';
        issueCounts[category] = (issueCounts[category] || 0) + 1;
    });
    
    return Object.entries(issueCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit)
        .map(([issue, count]) => [issue, count, (count / reviews.length * 100).toFixed(1)]);
}

function updateCriticalFlows() {
    const container = document.getElementById('criticalFlows');
    
    // Define critical flows based on findings
    const flows = [
        {
            name: "Bill Payment & Management",
            description: "Users need to view bills, make payments, and manage payment methods",
            impact: "High",
            issues: countFlowIssues(['bill', 'payment', 'pay', 'charge'])
        },
        {
            name: "Account Access & Authentication",
            description: "Login, password reset, and secure access to account",
            impact: "Critical",
            issues: countFlowIssues(['login', 'sign in', 'password', 'access'])
        },
        {
            name: "Usage Monitoring",
            description: "Track data usage, minutes, and plan limits",
            impact: "High",
            issues: countFlowIssues(['usage', 'data', 'limit', 'balance'])
        },
        {
            name: "Plan & Service Management",
            description: "View plan details, make changes, add features",
            impact: "Medium",
            issues: countFlowIssues(['plan', 'upgrade', 'change', 'feature'])
        },
        {
            name: "Customer Support Access",
            description: "Contact support, find help, resolve issues",
            impact: "High",
            issues: countFlowIssues(['support', 'help', 'contact', 'chat'])
        }
    ];
    
    container.innerHTML = flows.map(flow => `
        <div class="flow-card">
            <div class="flow-header">
                <span class="flow-name">${flow.name}</span>
                <span class="issue-stats">Impact: <strong>${flow.impact}</strong></span>
            </div>
            <p>${flow.description}</p>
            <div class="flow-metrics">
                <div class="metric">
                    <span class="metric-value">${flow.issues.mentions}</span>
                    <span class="metric-label">Mentions</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${flow.issues.negativeRate}%</span>
                    <span class="metric-label">Negative</span>
                </div>
                <div class="metric">
                    <span class="metric-value">${flow.issues.avgRating}/5</span>
                    <span class="metric-label">Avg Rating</span>
                </div>
            </div>
        </div>
    `).join('');
}

function countFlowIssues(keywords) {
    const pattern = new RegExp(keywords.join('|'), 'i');
    const matching = filteredReviews.filter(r => pattern.test(r.text));
    
    return {
        mentions: matching.length,
        negativeRate: matching.length > 0 
            ? Math.round(matching.filter(r => r.claude_sentiment === 'Negative').length / matching.length * 100)
            : 0,
        avgRating: matching.length > 0
            ? (matching.reduce((sum, r) => sum + parseFloat(r.rating), 0) / matching.length).toFixed(1)
            : '0.0'
    };
}

function updateKeyFindings() {
    const container = document.getElementById('keyFindings');
    
    // Calculate key metrics
    const rogersReviews = filteredReviews.filter(r => r.app_name === 'Rogers');
    const bellReviews = filteredReviews.filter(r => r.app_name === 'Bell');
    
    const findings = [
        {
            title: "App vs Service Focus",
            insight: `Rogers customers focus ${calculateFocusPercentage(rogersReviews, 'APP-RELATED')}% on app issues vs ${calculateFocusPercentage(bellReviews, 'APP-RELATED')}% for Bell customers. This indicates Rogers has more app-specific problems.`
        },
        {
            title: "Platform Performance Gap",
            insight: `Android users report ${calculatePlatformGap()} more issues than iOS users, suggesting platform-specific optimization needs.`
        },
        {
            title: "Authentication Crisis",
            insight: `${calculateCategoryPercentage('Authentication')}% of reviews mention login/authentication issues, making it a critical barrier to app usage.`
        },
        {
            title: "Self-Service Opportunity",
            insight: `Many users contact support for issues that could be resolved in-app, particularly billing inquiries and usage checks.`
        }
    ];
    
    container.innerHTML = findings.map(finding => `
        <div class="key-insight">
            <div class="insight-title">${finding.title}</div>
            <div>${finding.insight}</div>
        </div>
    `).join('');
}

function calculateFocusPercentage(reviews, focus) {
    const count = reviews.filter(r => r.enhanced_primary_focus === focus).length;
    return reviews.length > 0 ? Math.round(count / reviews.length * 100) : 0;
}

function calculatePlatformGap() {
    const android = filteredReviews.filter(r => r.platform === 'Android' && r.claude_sentiment === 'Negative').length;
    const ios = filteredReviews.filter(r => r.platform === 'iOS' && r.claude_sentiment === 'Negative').length;
    const androidTotal = filteredReviews.filter(r => r.platform === 'Android').length;
    const iosTotal = filteredReviews.filter(r => r.platform === 'iOS').length;
    
    const androidRate = androidTotal > 0 ? android / androidTotal : 0;
    const iosRate = iosTotal > 0 ? ios / iosTotal : 0;
    
    return Math.round((androidRate - iosRate) * 100) + '%';
}

function calculateCategoryPercentage(category) {
    const count = filteredReviews.filter(r => r.enhanced_category === category).length;
    return filteredReviews.length > 0 ? Math.round(count / filteredReviews.length * 100) : 0;
}

function updateReviewExamples() {
    const container = document.getElementById('reviewExamples');
    
    // Get top categories
    const categoryCounts = {};
    filteredReviews.forEach(r => {
        const category = r.enhanced_category || 'Unknown';
        categoryCounts[category] = (categoryCounts[category] || 0) + 1;
    });
    
    const topCategories = Object.entries(categoryCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([cat, _]) => cat);
    
    // Get examples for each category
    let html = '';
    topCategories.forEach(category => {
        const examples = filteredReviews
            .filter(r => r.enhanced_category === category)
            .sort((a, b) => parseFloat(b.thumbs_up || 0) - parseFloat(a.thumbs_up || 0))
            .slice(0, 2);
        
        if (examples.length > 0) {
            html += `<h3>${category}</h3>`;
            examples.forEach(review => {
                html += `
                    <div class="review-example">
                        <div class="review-header">
                            <span>${review.app_name} - ${review.platform}</span>
                            <span class="rating">★ ${review.rating}/5</span>
                        </div>
                        <div class="review-text">"${review.text}"</div>
                        <div class="review-header">
                            <span>${new Date(review.date).toLocaleDateString()}</span>
                            <span>${review.claude_sentiment}</span>
                        </div>
                    </div>
                `;
            });
        }
    });
    
    container.innerHTML = html || '<p>No reviews match the current filters.</p>';
}

function showTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');
}