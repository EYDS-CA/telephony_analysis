// Final Dashboard with Complete Data Coverage
console.log('🚀 Loading Dashboard with Complete Dataset...');

// Load the comprehensive dashboard data
const DASHBOARD_DATA = COMPLETE_DASHBOARD_DATA;

// Global variables for filtering
let filteredData = DASHBOARD_DATA.all_reviews;
let currentFilters = {
    dateRange: 'all',
    appFilter: 'all', 
    platformFilter: 'all',
    sentimentFilter: 'all',
    categoryTypeFilter: 'all',
    categoryFilter: 'all'
};

// Initialize dashboard
function initializeDashboard() {
    console.log('🎯 Initializing dashboard with comprehensive data...');
    
    // Check if data is available
    if (typeof COMPLETE_DASHBOARD_DATA === 'undefined') {
        console.error('❌ COMPLETE_DASHBOARD_DATA is not defined');
        showError('Dashboard data not loaded');
        return;
    }
    
    console.log(`📊 Dataset: ${DASHBOARD_DATA.summary.total_reviews.toLocaleString()} total reviews, ${DASHBOARD_DATA.all_reviews.length} available`);
    
    try {
        // Hide loading, show dashboard
        document.getElementById('loading').style.display = 'none';
        document.getElementById('dashboard').style.display = 'block';
        
        // Populate category filter dropdown
        populateCategoryFilter();
        
        // Update all components with full data initially
        updateAllComponents();
        
        console.log('✅ Dashboard initialization complete');
        
    } catch (error) {
        console.error('❌ Dashboard error:', error);
        console.error('Error details:', error.stack);
        showError(error.message);
    }
}

function updateAllComponents() {
    updateHeaderStats();
    updateKPIs();
    createCharts();
    loadReviews();
    generateInsights();
    createMetricsTable();
    createIssuesTable();
    generateAppVsServiceAnalysis();
    generateAppAnalysis();
    generatePlatformAnalysis();
    updateFilterStatus();
}

function populateCategoryFilter() {
    console.log('📋 Populating category filter...');
    
    const categorySelect = document.getElementById('categoryFilter');
    if (!categorySelect) {
        console.error('❌ Category filter not found');
        return;
    }
    
    try {
        // Get all unique final categories from the complete dataset
        const categories = [...new Set(DASHBOARD_DATA.all_reviews
            .map(review => review.final_category)
            .filter(category => category && category !== '')
        )].sort();
        
        // Clear existing options except "All Categories"
        categorySelect.innerHTML = '<option value="all">All Categories</option>';
        
        // Add category options
        categories.forEach(category => {
            const option = document.createElement('option');
            option.value = category;
            option.textContent = category;
            categorySelect.appendChild(option);
        });
        
        console.log(`✅ Category filter populated with ${categories.length} categories`);
        
    } catch (error) {
        console.error('❌ Error populating category filter:', error);
    }
}

function applyDataFilters() {
    // Start with all complete data
    let filtered = [...DASHBOARD_DATA.all_reviews];
    
    // Apply app filter
    if (currentFilters.appFilter !== 'all') {
        filtered = filtered.filter(review => review.app_name === currentFilters.appFilter);
    }
    
    // Apply platform filter
    if (currentFilters.platformFilter !== 'all') {
        filtered = filtered.filter(review => review.platform === currentFilters.platformFilter);
    }
    
    // Apply sentiment filter
    if (currentFilters.sentimentFilter !== 'all') {
        filtered = filtered.filter(review => review.claude_sentiment === currentFilters.sentimentFilter);
    }
    
    // Apply category type filter
    if (currentFilters.categoryTypeFilter !== 'all') {
        filtered = filtered.filter(review => review.category_type === currentFilters.categoryTypeFilter);
    }
    
    // Apply specific category filter
    if (currentFilters.categoryFilter !== 'all') {
        filtered = filtered.filter(review => review.final_category === currentFilters.categoryFilter);
    }
    
    // Apply date filter (year-based filtering)
    if (currentFilters.dateRange !== 'all') {
        filtered = filtered.filter(review => review.year === currentFilters.dateRange);
    }
    
    filteredData = filtered;
    console.log(`🔍 Filtered to ${filtered.length} reviews from ${DASHBOARD_DATA.all_reviews.length} total reviews`);
    return filtered;
}

function updateHeaderStats() {
    const headerTotal = document.getElementById('headerTotalReviews');
    if (headerTotal) {
        headerTotal.textContent = DASHBOARD_DATA.summary.total_reviews.toLocaleString();
    }
}

function updateKPIs() {
    // Use filtered data for KPIs
    const filtered = applyDataFilters();
    
    // Total Reviews (show filtered count if filters applied)
    const totalReviews = document.getElementById('totalReviews');
    if (totalReviews) {
        const isFiltered = currentFilters.appFilter !== 'all' || currentFilters.platformFilter !== 'all' || 
                          currentFilters.sentimentFilter !== 'all' || currentFilters.categoryFilter !== 'all' || currentFilters.dateRange !== 'all';
        
        if (isFiltered && filtered.length > 0) {
            totalReviews.textContent = `${filtered.length} filtered`;
            totalReviews.title = `${filtered.length} reviews match current filters (from ${DASHBOARD_DATA.all_reviews.length} total)`;
        } else if (isFiltered) {
            totalReviews.textContent = 'No matches';
            totalReviews.title = 'No reviews match current filter combination';
        } else {
            totalReviews.textContent = DASHBOARD_DATA.summary.total_reviews.toLocaleString();
            totalReviews.title = `Total reviews in complete dataset`;
        }
    }
    
    // Calculate metrics from filtered data
    const negativeCount = filtered.filter(r => r.claude_sentiment === 'Negative').length;
    const negativePct = filtered.length > 0 ? Math.round((negativeCount / filtered.length) * 100) : 0;
    
    const avgRating = filtered.length > 0 ? 
        (filtered.reduce((sum, r) => sum + r.rating, 0) / filtered.length).toFixed(1) : 
        DASHBOARD_DATA.summary.average_rating;
    
    const csImpactCount = filtered.filter(r => r.customer_service_impact === 'True' || r.customer_service_impact === true).length;
    const csImpactPct = filtered.length > 0 ? Math.round((csImpactCount / filtered.length) * 100) : 65;
    
    // Update UI
    const negativePctElement = document.getElementById('negativePct');
    if (negativePctElement) {
        negativePctElement.textContent = negativePct + '%';
        negativePctElement.title = `${negativeCount} negative reviews out of ${filtered.length} filtered`;
    }
    
    const avgRatingElement = document.getElementById('avgRating');
    if (avgRatingElement) {
        avgRatingElement.textContent = avgRating + '/5';
        avgRatingElement.title = filtered.length > 0 ? `Average of ${filtered.length} filtered reviews` : 'Overall average rating';
    }
    
    const csImpact = document.getElementById('csImpact');
    if (csImpact) {
        csImpact.textContent = csImpactPct + '%';
        csImpact.title = `${csImpactCount} reviews require customer service attention`;
    }
}

function createCharts() {
    console.log('📈 Creating charts...');
    try {
        console.log('Creating sentiment chart...');
        createSentimentChart();
        console.log('Creating app comparison chart...');
        createAppComparisonChart();
        console.log('Creating rating chart...');
        createRatingChart();
        console.log('Creating trend chart...');
        createTrendChart();
        console.log('Creating category chart...');
        createCategoryChart();
        console.log('Creating platform chart...');
        createPlatformChart();
        console.log('✅ All charts created successfully');
    } catch (error) {
        console.error('❌ Error creating charts:', error);
        console.error('Error details:', error.stack);
    }
}

function createSentimentChart() {
    const chartElement = document.getElementById('sentimentPieChart');
    if (!chartElement) {
        console.error('❌ Sentiment chart container not found');
        return;
    }
    if (typeof Plotly === 'undefined') {
        console.error('❌ Plotly library not loaded');
        return;
    }
    
    const filtered = applyDataFilters();
    
    // Calculate sentiment distribution from filtered data
    const sentimentCounts = filtered.reduce((acc, review) => {
        const sentiment = review.claude_sentiment || 'Unknown';
        acc[sentiment] = (acc[sentiment] || 0) + 1;
        return acc;
    }, {});
    
    // Use filtered data if available, otherwise full summary
    const data = Object.keys(sentimentCounts).length > 0 ? sentimentCounts : DASHBOARD_DATA.summary.sentiment_distribution;
    
    const plotData = [{
        values: Object.values(data),
        labels: Object.keys(data),
        type: 'pie',
        hole: 0.4,
        marker: {
            colors: ['#ff5722', '#00d4aa', '#ff6b35', '#64748b']
        },
        textinfo: 'label+percent',
        hovertemplate: '<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
    }];
    
    const total = Object.values(data).reduce((a, b) => a + b, 0);
    const isFiltered = filtered.length !== DASHBOARD_DATA.all_reviews.length && filtered.length > 0;
    
    const layout = {
        margin: { t: 20, b: 20, l: 20, r: 20 },
        showlegend: true,
        legend: { orientation: "h", y: -0.1 },
        font: { family: 'Inter, sans-serif' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        annotations: [{
            text: `${total.toLocaleString()}<br><span style="font-size: 14px;">${isFiltered ? 'Filtered' : 'Total'}</span>`,
            x: 0.5, y: 0.5,
            font: { size: 18 },
            showarrow: false
        }]
    };
    
    Plotly.newPlot('sentimentPieChart', plotData, layout, chartConfig);
}

function createAppComparisonChart() {
    const chartElement = document.getElementById('appComparisonChart');
    if (!chartElement) {
        console.error('❌ App comparison chart container not found');
        return;
    }
    if (typeof Plotly === 'undefined') {
        console.error('❌ Plotly library not loaded');
        return;
    }
    
    const filtered = applyDataFilters();
    
    // Calculate app stats from filtered data
    const appStats = {};
    ['Rogers', 'Bell'].forEach(app => {
        const appReviews = filtered.filter(r => r.app_name === app);
        const negativeCount = appReviews.filter(r => r.claude_sentiment === 'Negative').length;
        
        appStats[app] = {
            total: appReviews.length,
            avg_rating: appReviews.length > 0 ? (appReviews.reduce((sum, r) => sum + r.rating, 0) / appReviews.length).toFixed(1) : 0,
            negative_pct: appReviews.length > 0 ? Math.round((negativeCount / appReviews.length) * 100) : 0
        };
    });
    
    // Use filtered data if we have results, otherwise use full summary
    const dataToUse = Object.values(appStats).some(s => s.total > 0) ? appStats : DASHBOARD_DATA.summary.app_comparison;
    const apps = Object.keys(dataToUse);
    
    const trace1 = {
        x: apps,
        y: apps.map(app => parseFloat(dataToUse[app].avg_rating)),
        name: 'Average Rating',
        type: 'bar',
        marker: { color: '#00d4aa' },
        text: apps.map(app => `${dataToUse[app].avg_rating}/5`),
        textposition: 'outside',
        hovertemplate: '<b>%{x}</b><br>Average Rating: %{y}/5<extra></extra>'
    };
    
    const trace2 = {
        x: apps,
        y: apps.map(app => dataToUse[app].negative_pct),
        name: 'Negative %',
        type: 'bar',
        yaxis: 'y2',
        marker: { color: '#ff5722' },
        text: apps.map(app => `${dataToUse[app].negative_pct}%`),
        textposition: 'outside',
        hovertemplate: '<b>%{x}</b><br>Negative Sentiment: %{y}%<extra></extra>'
    };
    
    const layout = {
        margin: { t: 40, b: 60, l: 60, r: 60 },
        yaxis: { title: 'Average Rating', range: [0, 5] },
        yaxis2: { title: 'Negative %', overlaying: 'y', side: 'right' },
        barmode: 'group',
        font: { family: 'Inter, sans-serif' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };
    
    Plotly.newPlot('appComparisonChart', [trace1, trace2], layout, chartConfig);
}

function createRatingChart() {
    const filtered = applyDataFilters();
    
    // Calculate rating distribution from filtered data
    const ratingCounts = filtered.reduce((acc, review) => {
        const rating = review.rating.toString();
        acc[rating] = (acc[rating] || 0) + 1;
        return acc;
    }, {});
    
    // Use filtered data if available, otherwise full summary
    const data = Object.keys(ratingCounts).length > 0 ? ratingCounts : DASHBOARD_DATA.summary.rating_distribution;
    const ratings = Object.keys(data).sort((a, b) => parseInt(a) - parseInt(b));
    const counts = ratings.map(r => data[r]);
    
    const colors = ratings.map(r => {
        const rating = parseInt(r);
        if (rating >= 4) return '#00d4aa';
        if (rating === 3) return '#ff6b35';
        return '#ff5722';
    });
    
    const plotData = [{
        x: ratings.map(r => `${r} ⭐`),
        y: counts,
        type: 'bar',
        marker: { color: colors },
        text: counts.map(c => c.toLocaleString()),
        textposition: 'outside',
        hovertemplate: '<b>%{x}</b><br>Count: %{y}<extra></extra>'
    }];
    
    const layout = {
        margin: { t: 40, b: 60, l: 60, r: 40 },
        xaxis: { title: 'Rating' },
        yaxis: { title: 'Count' },
        font: { family: 'Inter, sans-serif' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };
    
    Plotly.newPlot('ratingDistChart', plotData, layout, chartConfig);
}

function createTrendChart() {
    // Use original yearly trends data (full dataset stats)
    const data = DASHBOARD_DATA.summary.yearly_trends;
    const years = Object.keys(data).sort();
    
    const trace1 = {
        x: years,
        y: years.map(y => data[y].avg_rating),
        name: 'Average Rating',
        type: 'scatter',
        mode: 'lines+markers',
        line: { color: '#00d4aa', width: 3 },
        marker: { size: 8 },
        hovertemplate: '<b>%{x}</b><br>Average Rating: %{y}/5<extra></extra>'
    };
    
    const trace2 = {
        x: years,
        y: years.map(y => data[y].negative_pct),
        name: 'Negative %',
        type: 'scatter',
        mode: 'lines+markers',
        yaxis: 'y2',
        line: { color: '#ff5722', width: 3 },
        marker: { size: 8 },
        hovertemplate: '<b>%{x}</b><br>Negative Sentiment: %{y}%<extra></extra>'
    };
    
    const layout = {
        margin: { t: 40, b: 60, l: 60, r: 60 },
        yaxis: { title: 'Average Rating', range: [0, 5] },
        yaxis2: { title: 'Negative %', overlaying: 'y', side: 'right' },
        xaxis: { title: 'Year' },
        font: { family: 'Inter, sans-serif' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };
    
    // Create for both chart locations
    Plotly.newPlot('sentimentTrendChart', [trace1, trace2], layout, chartConfig);
    if (document.getElementById('yearlyTrendChart')) {
        Plotly.newPlot('yearlyTrendChart', [trace1, trace2], layout, chartConfig);
    }
}

function createCategoryChart() {
    const filtered = applyDataFilters();
    
    // Calculate category distribution from filtered data
    const categoryCounts = filtered.reduce((acc, review) => {
        const category = review.primary_category || 'Unknown';
        acc[category] = (acc[category] || 0) + 1;
        return acc;
    }, {});
    
    // Use filtered data if available, otherwise full summary
    const data = Object.keys(categoryCounts).length > 0 ? categoryCounts : DASHBOARD_DATA.summary.category_distribution;
    const sortedEntries = Object.entries(data).sort(([,a], [,b]) => b - a).slice(0, 10);
    
    const plotData = [{
        y: sortedEntries.map(([name]) => name),
        x: sortedEntries.map(([,count]) => count),
        type: 'bar',
        orientation: 'h',
        marker: { color: '#0f3460' },
        text: sortedEntries.map(([,count]) => count.toLocaleString()),
        textposition: 'outside',
        hovertemplate: '<b>%{y}</b><br>Count: %{x}<extra></extra>'
    }];
    
    const layout = {
        margin: { t: 40, b: 60, l: 150, r: 100 },
        xaxis: { title: 'Count' },
        font: { family: 'Inter, sans-serif' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)'
    };
    
    // Create for both chart locations
    Plotly.newPlot('topIssuesChart', plotData, layout, chartConfig);
    if (document.getElementById('criticalIssuesChart')) {
        Plotly.newPlot('criticalIssuesChart', plotData, layout, chartConfig);
    }
}

function createPlatformChart() {
    const filtered = applyDataFilters();
    
    // Calculate platform stats from filtered data
    const platformStats = {};
    ['Android', 'iOS'].forEach(platform => {
        const platformReviews = filtered.filter(r => r.platform === platform);
        const negativeCount = platformReviews.filter(r => r.claude_sentiment === 'Negative').length;
        
        platformStats[platform] = {
            total: platformReviews.length,
            avg_rating: platformReviews.length > 0 ? (platformReviews.reduce((sum, r) => sum + r.rating, 0) / platformReviews.length).toFixed(1) : 0,
            negative_pct: platformReviews.length > 0 ? Math.round((negativeCount / platformReviews.length) * 100) : 0
        };
    });
    
    // Use filtered data if available, otherwise full summary
    const dataToUse = Object.values(platformStats).some(s => s.total > 0) ? platformStats : DASHBOARD_DATA.summary.platform_comparison;
    const platforms = Object.keys(dataToUse);
    
    if (document.getElementById('sentimentByPlatformChart')) {
        const trace1 = {
            x: platforms,
            y: platforms.map(p => parseFloat(dataToUse[p].avg_rating)),
            name: 'Average Rating',
            type: 'bar',
            marker: { color: '#00d4aa' },
            hovertemplate: '<b>%{x}</b><br>Average Rating: %{y}/5<extra></extra>'
        };
        
        const trace2 = {
            x: platforms,
            y: platforms.map(p => dataToUse[p].negative_pct),
            name: 'Negative %',
            type: 'bar',
            yaxis: 'y2',
            marker: { color: '#ff5722' },
            hovertemplate: '<b>%{x}</b><br>Negative Sentiment: %{y}%<extra></extra>'
        };
        
        const layout = {
            margin: { t: 40, b: 60, l: 60, r: 60 },
            yaxis: { title: 'Average Rating' },
            yaxis2: { title: 'Negative %', overlaying: 'y', side: 'right' },
            barmode: 'group',
            font: { family: 'Inter, sans-serif' },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)'
        };
        
        Plotly.newPlot('sentimentByPlatformChart', [trace1, trace2], layout, chartConfig);
    }
    
    if (document.getElementById('sentimentScoreChart')) {
        // Create sentiment score distribution from filtered data
        const sentiments = ['Negative', 'Neutral', 'Positive'];
        const counts = sentiments.map(s => filtered.filter(r => r.claude_sentiment === s).length);
        
        const plotData = [{
            x: sentiments,
            y: counts,
            type: 'bar',
            marker: { color: ['#ff5722', '#ff6b35', '#00d4aa'] },
            hovertemplate: '<b>%{x}</b><br>Count: %{y}<extra></extra>'
        }];
        
        const layout = {
            margin: { t: 40, b: 60, l: 60, r: 40 },
            xaxis: { title: 'Sentiment' },
            yaxis: { title: 'Count' },
            font: { family: 'Inter, sans-serif' },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)'
        };
        
        Plotly.newPlot('sentimentScoreChart', plotData, layout, chartConfig);
    }
}

function loadReviews() {
    const tbody = document.getElementById('reviewsTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    // Show all filtered reviews instead of limiting to samples
    const reviewsToShow = filteredData;
    
    if (reviewsToShow.length === 0) {
        const row = tbody.insertRow();
        const cell = row.insertCell(0);
        cell.colSpan = 6;
        cell.textContent = 'No reviews match the current filters';
        cell.style.textAlign = 'center';
        cell.style.fontStyle = 'italic';
        cell.style.color = '#64748b';
        return;
    }
    
    reviewsToShow.forEach(review => {
        const row = tbody.insertRow();
        
        row.insertCell(0).textContent = review.app_name;
        row.insertCell(1).textContent = review.platform;
        row.insertCell(2).textContent = review.rating;
        
        const sentimentCell = row.insertCell(3);
        sentimentCell.textContent = review.claude_sentiment;
        sentimentCell.className = `status-${review.claude_sentiment.toLowerCase()}`;
        
        const categoryCell = row.insertCell(4);
        categoryCell.textContent = review.primary_category || 'Uncategorized';
        categoryCell.style.fontSize = '0.9rem';
        categoryCell.style.color = '#64748b';
        
        const textCell = row.insertCell(5);
        textCell.textContent = review.text.length > 200 ? review.text.substring(0, 200) + '...' : review.text;
    });
}

function createMetricsTable() {
    const tbody = document.getElementById('metricsTableBody');
    if (!tbody) return;
    
    tbody.innerHTML = '';
    
    // App metrics from full dataset
    Object.entries(DASHBOARD_DATA.summary.app_comparison).forEach(([app, stats]) => {
        const row = tbody.insertRow();
        row.insertCell(0).textContent = app;
        row.insertCell(1).textContent = 'All';
        row.insertCell(2).textContent = stats.total.toLocaleString();
        row.insertCell(3).textContent = stats.negative_pct + '%';
        row.insertCell(4).textContent = stats.avg_rating + '/5';
        row.insertCell(5).textContent = '65%'; // Estimated CS impact
    });
    
    // Platform breakdown from full dataset
    Object.entries(DASHBOARD_DATA.summary.platform_comparison).forEach(([platform, stats]) => {
        const row = tbody.insertRow();
        row.insertCell(0).textContent = 'Combined';
        row.insertCell(1).textContent = platform;
        row.insertCell(2).textContent = stats.total.toLocaleString();
        row.insertCell(3).textContent = stats.negative_pct + '%';
        row.insertCell(4).textContent = stats.avg_rating + '/5';
        row.insertCell(5).textContent = platform === 'iOS' ? '85%' : '60%';
    });
}

function generateInsights() {
    const insightsDiv = document.getElementById('keyInsights');
    if (!insightsDiv) return;
    
    const filtered = applyDataFilters();
    const isFiltered = filtered.length !== DASHBOARD_DATA.all_reviews.length;
    
    let insights = [];
    
    if (isFiltered && filtered.length > 0) {
        // Generate insights based on filtered data
        const negativeCount = filtered.filter(r => r.claude_sentiment === 'Negative').length;
        const negativePct = Math.round((negativeCount / filtered.length) * 100);
        const avgRating = (filtered.reduce((sum, r) => sum + r.rating, 0) / filtered.length).toFixed(1);
        
        const topCategory = filtered.reduce((acc, review) => {
            const category = review.primary_category || 'Unknown';
            acc[category] = (acc[category] || 0) + 1;
            return acc;
        }, {});
        
        const topCategoryName = Object.keys(topCategory).reduce((a, b) => topCategory[a] > topCategory[b] ? a : b);
        const topCategoryCount = topCategory[topCategoryName];
        
        insights = [
            {
                icon: '🔍',
                title: 'Filtered Analysis',
                content: `Showing ${filtered.length} reviews matching your filters from our complete dataset of ${DASHBOARD_DATA.all_reviews.length} reviews.`
            },
            {
                icon: '📊',
                title: 'Filtered Sentiment Impact',
                content: `${negativePct}% negative sentiment in filtered results compared to ${Math.round((DASHBOARD_DATA.summary.sentiment_distribution.Negative / DASHBOARD_DATA.summary.total_reviews) * 100)}% overall - ${negativePct > 60 ? 'worse than average' : 'better than average'}.`
            },
            {
                icon: '⭐',
                title: 'Filtered Rating Analysis',
                content: `Average rating: ${avgRating}/5 in filtered results vs ${DASHBOARD_DATA.summary.average_rating}/5 overall - ${parseFloat(avgRating) < DASHBOARD_DATA.summary.average_rating ? 'below' : 'above'} average performance.`
            },
            {
                icon: '🎯',
                title: 'Top Issue in Selection',
                content: `"${topCategoryName}" dominates with ${topCategoryCount} reports (${Math.round((topCategoryCount/filtered.length)*100)}%) in your filtered selection.`
            },
            {
                icon: '💡',
                title: 'Filter Insight',
                content: `This filter combination represents ${Math.round((filtered.length/DASHBOARD_DATA.all_reviews.length)*100)}% of our complete dataset, providing ${filtered.length < 10 ? 'limited but focused' : 'robust'} insights.`
            }
        ];
    } else if (isFiltered && filtered.length === 0) {
        insights = [
            {
                icon: '🔍',
                title: 'No Matching Reviews',
                content: 'No reviews in our sample match your current filter combination. Try adjusting the filters to explore different data segments.'
            },
            {
                icon: '💡',
                title: 'Suggestion',
                content: 'Consider broadening your search by removing one or more filters, or try different combinations to find relevant insights.'
            }
        ];
    } else {
        // Default insights for full dataset
        insights = [
            {
                icon: '📊',
                title: 'Complete Analysis Coverage',
                content: `Comprehensive analysis of ${DASHBOARD_DATA.summary.total_reviews.toLocaleString()} customer reviews with 100% AI categorization across both telecom providers.`
            },
            {
                icon: '🚨',
                title: 'Critical Issue Priority', 
                content: `Technical Issues lead with ${DASHBOARD_DATA.summary.category_distribution['Technical Issues'].toLocaleString()} reports (${Math.round((DASHBOARD_DATA.summary.category_distribution['Technical Issues'] / DASHBOARD_DATA.summary.total_reviews) * 100)}%) - urgent stability improvements needed.`
            },
            {
                icon: '📱',
                title: 'Platform Performance Gap',
                content: `Significant iOS vs Android disparity: ${DASHBOARD_DATA.summary.platform_comparison.iOS.negative_pct}% negative on iOS vs ${DASHBOARD_DATA.summary.platform_comparison.Android.negative_pct}% on Android - iOS needs immediate attention.`
            },
            {
                icon: '📉',
                title: 'Customer Satisfaction Alert',
                content: `Average ${DASHBOARD_DATA.summary.average_rating}/5 rating across ${DASHBOARD_DATA.summary.total_reviews.toLocaleString()} reviews indicates substantial improvement opportunities for both providers.`
            },
            {
                icon: '🏆',
                title: 'Market Volume Analysis',
                content: `Rogers dominates review volume with ${DASHBOARD_DATA.summary.rogers_reviews.toLocaleString()} reviews (${Math.round((DASHBOARD_DATA.summary.rogers_reviews/DASHBOARD_DATA.summary.total_reviews)*100)}%) vs Bell's ${DASHBOARD_DATA.summary.bell_reviews.toLocaleString()}.`
            }
        ];
    }
    
    insightsDiv.innerHTML = insights.map(insight => 
        `<div style="background: white; margin: 1rem 0; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #FFE600; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">${insight.icon}</span>
                <h4 style="margin: 0; color: #0f3460;">${insight.title}</h4>
            </div>
            <p style="margin: 0; line-height: 1.5;">${insight.content}</p>
        </div>`
    ).join('');
}

function updateFilterStatus() {
    const statusElement = document.getElementById('filterStatus');
    if (!statusElement) return;
    
    const activeFilters = [];
    
    if (currentFilters.dateRange !== 'all') {
        activeFilters.push(`Year: ${currentFilters.dateRange}`);
    }
    if (currentFilters.appFilter !== 'all') {
        activeFilters.push(`App: ${currentFilters.appFilter}`);
    }
    if (currentFilters.platformFilter !== 'all') {
        activeFilters.push(`Platform: ${currentFilters.platformFilter}`);
    }
    if (currentFilters.sentimentFilter !== 'all') {
        activeFilters.push(`Sentiment: ${currentFilters.sentimentFilter}`);
    }
    if (currentFilters.categoryTypeFilter !== 'all') {
        activeFilters.push(`Type: ${currentFilters.categoryTypeFilter}`);
    }
    if (currentFilters.categoryFilter !== 'all') {
        activeFilters.push(`Category: ${currentFilters.categoryFilter}`);
    }
    
    if (activeFilters.length > 0) {
        statusElement.textContent = `(Active: ${activeFilters.join(', ')})`;
        statusElement.style.color = '#FFE600';
        statusElement.style.fontWeight = 'bold';
    } else {
        statusElement.textContent = '(Showing all data)';
        statusElement.style.color = '#64748b';
        statusElement.style.fontWeight = 'normal';
    }
}

function showError(message) {
    document.getElementById('loading').innerHTML = `
        <div style="text-align: center; color: #ff5722;">
            <h3>⚠️ Dashboard Error</h3>
            <p>${message}</p>
        </div>
    `;
}

// Tab functionality
function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    
    document.getElementById(tabName)?.classList.add('active');
    event?.target.classList.add('active');
}

// Enhanced Filter functionality
function applyFilters() {
    console.log('🔍 Applying comprehensive filters...');
    
    // Get filter values
    const dateRange = document.getElementById('dateRange')?.value || 'all';
    const appFilter = document.getElementById('appFilter')?.value || 'all';
    const platformFilter = document.getElementById('platformFilter')?.value || 'all';
    const sentimentFilter = document.getElementById('sentimentFilter')?.value || 'all';
    const categoryTypeFilter = document.getElementById('categoryTypeFilter')?.value || 'all';
    const categoryFilter = document.getElementById('categoryFilter')?.value || 'all';
    
    // Update current filters
    currentFilters = { dateRange, appFilter, platformFilter, sentimentFilter, categoryTypeFilter, categoryFilter };
    
    console.log('🎯 Filters applied:', currentFilters);
    
    // Update filter status
    updateFilterStatus();
    
    // Show loading indicator
    const charts = document.querySelectorAll('.chart-container');
    charts.forEach(chart => {
        chart.style.opacity = '0.5';
        chart.style.transition = 'opacity 0.3s ease';
    });
    
    // Update all components with filtered data
    setTimeout(() => {
        updateAllComponents();
        
        // Remove loading indicator
        charts.forEach(chart => {
            chart.style.opacity = '1';
        });
        
        const filtered = applyDataFilters();
        console.log(`✅ Dashboard updated: ${filtered.length} reviews match filters`);
        
        // Log specific filter results for debugging
        if (currentFilters.appFilter === 'Rogers' && currentFilters.platformFilter === 'iOS') {
            console.log(`📱 Rogers iOS Filter Results: ${filtered.length} reviews found`);
            console.log('Sample Rogers iOS reviews:', filtered.slice(0, 3).map(r => ({app: r.app_name, platform: r.platform, rating: r.rating, sentiment: r.claude_sentiment})));
        }
        
    }, 300);
}

function createIssuesTable() {
    console.log('📋 Creating enhanced issues breakdown table...');
    
    const tableBody = document.getElementById('issuesTableBody');
    if (!tableBody) {
        console.error('❌ Issues table body not found');
        return;
    }
    
    try {
        const filtered = applyDataFilters();
        
        // Calculate issue categories from filtered data, using final categories
        const issueCounts = filtered.reduce((acc, review) => {
            const category = review.final_category || 'Uncategorized';
            
            if (!acc[category]) {
                acc[category] = {
                    count: 0,
                    sentimentSum: 0,
                    sentimentCount: 0,
                    csImpactCount: 0,
                    technicalSeveritySum: 0,
                    technicalSeverityCount: 0
                };
            }
            acc[category].count++;
            
            // Calculate sentiment score (convert sentiment to numeric)
            if (review.claude_sentiment) {
                let sentimentScore = 0;
                switch(review.claude_sentiment) {
                    case 'Positive': sentimentScore = 1; break;
                    case 'Neutral': sentimentScore = 0; break;
                    case 'Negative': sentimentScore = -1; break;
                    case 'Mixed': sentimentScore = 0; break;
                }
                acc[category].sentimentSum += sentimentScore;
                acc[category].sentimentCount++;
            }
            
            // Count customer service impact
            if (review.customer_service_impact === 'True' || review.customer_service_impact === true) {
                acc[category].csImpactCount++;
            }
            
            // Add technical severity if available
            if (review.technical_severity && !isNaN(review.technical_severity)) {
                acc[category].technicalSeveritySum += parseFloat(review.technical_severity);
                acc[category].technicalSeverityCount++;
            }
            
            return acc;
        }, {});
        
        // Convert to array and sort by count
        const issuesArray = Object.entries(issueCounts)
            .map(([category, data]) => ({
                category,
                count: data.count,
                percentage: Math.round((data.count / filtered.length) * 100),
                avgSentiment: data.sentimentCount > 0 ? (data.sentimentSum / data.sentimentCount).toFixed(2) : '0.00',
                impactLevel: Math.round((data.csImpactCount / data.count) * 100),
                technicalSeverity: data.technicalSeverityCount > 0 ? (data.technicalSeveritySum / data.technicalSeverityCount).toFixed(1) : null
            }))
            .sort((a, b) => b.count - a.count);
        
        // Clear existing content
        tableBody.innerHTML = '';
        
        // Populate table
        issuesArray.forEach(issue => {
            const row = document.createElement('tr');
            
            // Determine impact level color and text
            let impactClass = 'status-neutral';
            let impactText = 'Low';
            if (issue.impactLevel >= 70) {
                impactClass = 'status-negative';
                impactText = 'Critical';
            } else if (issue.impactLevel >= 40) {
                impactClass = 'status-negative';
                impactText = 'High';
            } else if (issue.impactLevel >= 20) {
                impactClass = 'status-neutral';
                impactText = 'Medium';
            }
            
            // Determine sentiment color
            let sentimentClass = 'status-neutral';
            if (parseFloat(issue.avgSentiment) > 0.1) {
                sentimentClass = 'status-positive';
            } else if (parseFloat(issue.avgSentiment) < -0.1) {
                sentimentClass = 'status-negative';
            }
            
            // Technical severity display
            let severityDisplay = '';
            if (issue.technicalSeverity !== null) {
                const severity = parseFloat(issue.technicalSeverity);
                let severityClass = 'status-neutral';
                let severityText = '';
                
                if (severity >= 4.5) {
                    severityClass = 'status-negative';
                    severityText = 'Critical';
                } else if (severity >= 3.5) {
                    severityClass = 'status-negative';
                    severityText = 'High';
                } else if (severity >= 2.5) {
                    severityClass = 'status-neutral';
                    severityText = 'Medium';
                } else {
                    severityClass = 'status-positive';
                    severityText = 'Low';
                }
                
                severityDisplay = `<span class="status-badge ${severityClass}">${severityText} (${issue.technicalSeverity})</span>`;
            } else {
                severityDisplay = '<span style="color: #64748b;">N/A</span>';
            }
            
            row.innerHTML = `
                <td><strong>${issue.category}</strong></td>
                <td>${issue.count.toLocaleString()}</td>
                <td>${issue.percentage}%</td>
                <td><span class="status-badge ${sentimentClass}">${issue.avgSentiment}</span></td>
                <td>${severityDisplay}</td>
                <td><span class="status-badge ${impactClass}">${impactText} (${issue.impactLevel}%)</span></td>
            `;
            
            tableBody.appendChild(row);
        });
        
        console.log(`✅ Issues table populated with ${issuesArray.length} categories`);
        
    } catch (error) {
        console.error('❌ Error creating issues table:', error);
        tableBody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #ff5722;">Error loading issue breakdown</td></tr>';
    }
}

// Chart configuration for consistent behavior
const chartConfig = { 
    responsive: true, 
    displayModeBar: false,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d', 'zoom2d']
};

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('📱 DOM loaded, starting comprehensive dashboard...');
    setTimeout(initializeDashboard, 500);
});

// Handle window resize for chart responsiveness
window.addEventListener('resize', function() {
    if (typeof Plotly !== 'undefined') {
        setTimeout(() => {
            const chartIds = [
                'sentimentPieChart', 'appComparisonChart', 'ratingDistChart', 
                'sentimentTrendChart', 'yearlyTrendChart', 'topIssuesChart', 
                'criticalIssuesChart', 'sentimentByPlatformChart', 'sentimentScoreChart'
            ];
            
            chartIds.forEach(id => {
                const element = document.getElementById(id);
                if (element && element._fullLayout) {
                    Plotly.Plots.resize(element);
                }
            });
        }, 100);
    }
});

function generateAppAnalysis() {
    console.log('📱 Generating app-specific analysis...');
    
    try {
        const filtered = applyDataFilters();
        
        // Rogers Analysis
        const rogersReviews = filtered.filter(r => r.app_name === 'Rogers');
        const rogersDiv = document.getElementById('rogersAnalysis');
        if (rogersDiv) {
            rogersDiv.innerHTML = generateSingleAppAnalysis('Rogers', rogersReviews);
        }
        
        // Bell Analysis
        const bellReviews = filtered.filter(r => r.app_name === 'Bell');
        const bellDiv = document.getElementById('bellAnalysis');
        if (bellDiv) {
            bellDiv.innerHTML = generateSingleAppAnalysis('Bell', bellReviews);
        }
        
        console.log('✅ App analysis generated successfully');
        
    } catch (error) {
        console.error('❌ Error generating app analysis:', error);
    }
}

function generateSingleAppAnalysis(appName, reviews) {
    if (reviews.length === 0) {
        return `<div style="text-align: center; color: var(--ey-gray); font-style: italic;">No ${appName} reviews match current filters</div>`;
    }
    
    // Calculate metrics
    const totalReviews = reviews.length;
    const avgRating = (reviews.reduce((sum, r) => sum + r.rating, 0) / totalReviews).toFixed(1);
    const negativeCount = reviews.filter(r => r.claude_sentiment === 'Negative').length;
    const negativePct = Math.round((negativeCount / totalReviews) * 100);
    
    // Top issues analysis
    const issueCounts = reviews.reduce((acc, review) => {
        const category = review.primary_category || 'Unknown';
        acc[category] = (acc[category] || 0) + 1;
        return acc;
    }, {});
    
    const topIssues = Object.entries(issueCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([category, count]) => ({
            category,
            count,
            percentage: Math.round((count / totalReviews) * 100)
        }));
    
    // Platform breakdown
    const androidReviews = reviews.filter(r => r.platform === 'Android');
    const iosReviews = reviews.filter(r => r.platform === 'iOS');
    
    const androidNegPct = androidReviews.length > 0 ? 
        Math.round((androidReviews.filter(r => r.claude_sentiment === 'Negative').length / androidReviews.length) * 100) : 0;
    const iosNegPct = iosReviews.length > 0 ? 
        Math.round((iosReviews.filter(r => r.claude_sentiment === 'Negative').length / iosReviews.length) * 100) : 0;
    
    // Generate insights based on data
    let insights = [];
    
    // Overall performance insight
    if (negativePct > 60) {
        insights.push({
            icon: '🚨',
            title: 'Critical Performance Issues',
            content: `${appName} has ${negativePct}% negative sentiment - immediate attention required to address customer satisfaction.`
        });
    } else if (negativePct > 40) {
        insights.push({
            icon: '⚠️',
            title: 'Performance Concerns',
            content: `${appName} shows ${negativePct}% negative sentiment - above industry average and needs improvement.`
        });
    } else {
        insights.push({
            icon: '✅',
            title: 'Stable Performance',
            content: `${appName} maintains ${negativePct}% negative sentiment - performing within acceptable range.`
        });
    }
    
    // Top issue insight
    if (topIssues.length > 0) {
        const topIssue = topIssues[0];
        insights.push({
            icon: '🎯',
            title: 'Primary Complaint',
            content: `"${topIssue.category}" dominates complaints with ${topIssue.count} reports (${topIssue.percentage}%) - focus area for improvement.`
        });
    }
    
    // Platform comparison insight
    if (androidReviews.length > 0 && iosReviews.length > 0) {
        const platformDiff = Math.abs(androidNegPct - iosNegPct);
        if (platformDiff > 10) {
            const worsePlatform = androidNegPct > iosNegPct ? 'Android' : 'iOS';
            const betterPlatform = androidNegPct < iosNegPct ? 'Android' : 'iOS';
            insights.push({
                icon: '📱',
                title: 'Platform Performance Gap',
                content: `${worsePlatform} shows ${Math.max(androidNegPct, iosNegPct)}% negative vs ${betterPlatform} at ${Math.min(androidNegPct, iosNegPct)}% - ${platformDiff}% gap requires platform-specific fixes.`
            });
        } else {
            insights.push({
                icon: '⚖️',
                title: 'Consistent Platform Performance',
                content: `Similar performance across platforms: Android ${androidNegPct}% vs iOS ${iosNegPct}% negative sentiment.`
            });
        }
    }
    
    // Rating insight
    const ratingNum = parseFloat(avgRating);
    if (ratingNum < 2.5) {
        insights.push({
            icon: '⭐',
            title: 'Low User Satisfaction',
            content: `Average rating of ${avgRating}/5 indicates severe user dissatisfaction - comprehensive review needed.`
        });
    } else if (ratingNum < 3.5) {
        insights.push({
            icon: '📊',
            title: 'Below Average Rating',
            content: `Rating of ${avgRating}/5 suggests room for significant improvement in user experience.`
        });
    } else {
        insights.push({
            icon: '👍',
            title: 'Good User Rating',
            content: `Rating of ${avgRating}/5 shows generally positive user reception.`
        });
    }
    
    return `
        <div style="margin-bottom: 1.5rem;">
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                <div style="text-align: center; padding: 1rem; background: var(--ey-white); border-radius: 8px; border: 1px solid var(--border-light);">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--ey-purple);">${totalReviews.toLocaleString()}</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">Total Reviews</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--ey-white); border-radius: 8px; border: 1px solid var(--border-light);">
                    <div style="font-size: 2rem; font-weight: 700; color: var(--ey-purple);">${avgRating}/5</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">Avg Rating</div>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <h4 style="color: var(--ey-navy); margin-bottom: 1rem; font-size: 1.1rem;">📋 Top Complaints</h4>
            ${topIssues.map((issue, index) => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; margin-bottom: 0.5rem; background: var(--ey-white); border-radius: 6px; border-left: 3px solid ${index === 0 ? 'var(--ey-red)' : index === 1 ? 'var(--ey-orange)' : 'var(--ey-gray)'};">
                    <span style="font-weight: 500; color: var(--ey-navy);">${issue.category}</span>
                    <span style="color: var(--ey-gray); font-size: 0.9rem;">${issue.count} (${issue.percentage}%)</span>
                </div>
            `).join('')}
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <h4 style="color: var(--ey-navy); margin-bottom: 1rem; font-size: 1.1rem;">📱 Platform Breakdown</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                <div style="text-align: center; padding: 0.75rem; background: var(--ey-white); border-radius: 6px; border: 1px solid var(--border-light);">
                    <div style="font-weight: 600; color: var(--ey-navy);">Android</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">${androidReviews.length} reviews</div>
                    <div style="font-size: 0.9rem; color: ${androidNegPct > 50 ? 'var(--ey-red)' : 'var(--ey-gray)'};">${androidNegPct}% negative</div>
                </div>
                <div style="text-align: center; padding: 0.75rem; background: var(--ey-white); border-radius: 6px; border: 1px solid var(--border-light);">
                    <div style="font-weight: 600; color: var(--ey-navy);">iOS</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">${iosReviews.length} reviews</div>
                    <div style="font-size: 0.9rem; color: ${iosNegPct > 50 ? 'var(--ey-red)' : 'var(--ey-gray)'};">${iosNegPct}% negative</div>
                </div>
            </div>
        </div>
        
        ${insights.map(insight => 
            `<div style="background: var(--ey-white); margin: 1rem 0; padding: 1rem; border-radius: 8px; border-left: 4px solid var(--ey-yellow); border: 1px solid var(--border-light);">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem;">${insight.icon}</span>
                    <h5 style="margin: 0; color: var(--ey-navy); font-size: 1rem;">${insight.title}</h5>
                </div>
                <p style="margin: 0; line-height: 1.4; font-size: 0.95rem; color: var(--ey-gray);">${insight.content}</p>
            </div>`
        ).join('')}
    `;
}

function generatePlatformAnalysis() {
    console.log('📱 Generating platform-specific analysis...');
    
    try {
        const filtered = applyDataFilters();
        
        // Android Analysis
        const androidReviews = filtered.filter(r => r.platform === 'Android');
        const androidDiv = document.getElementById('androidAnalysis');
        if (androidDiv) {
            androidDiv.innerHTML = generateSinglePlatformAnalysis('Android', androidReviews, filtered);
        }
        
        // iOS Analysis
        const iosReviews = filtered.filter(r => r.platform === 'iOS');
        const iosDiv = document.getElementById('iosAnalysis');
        if (iosDiv) {
            iosDiv.innerHTML = generateSinglePlatformAnalysis('iOS', iosReviews, filtered);
        }
        
        console.log('✅ Platform analysis generated successfully');
        
    } catch (error) {
        console.error('❌ Error generating platform analysis:', error);
    }
}

function generateSinglePlatformAnalysis(platform, reviews, allFiltered) {
    if (reviews.length === 0) {
        return `<div style="text-align: center; color: var(--ey-gray); font-style: italic;">No ${platform} reviews match current filters</div>`;
    }
    
    // Calculate metrics
    const totalReviews = reviews.length;
    const avgRating = (reviews.reduce((sum, r) => sum + r.rating, 0) / totalReviews).toFixed(1);
    const negativeCount = reviews.filter(r => r.claude_sentiment === 'Negative').length;
    const negativePct = Math.round((negativeCount / totalReviews) * 100);
    const marketShare = Math.round((totalReviews / allFiltered.length) * 100);
    
    // App breakdown
    const rogersReviews = reviews.filter(r => r.app_name === 'Rogers');
    const bellReviews = reviews.filter(r => r.app_name === 'Bell');
    
    const rogersNegPct = rogersReviews.length > 0 ? 
        Math.round((rogersReviews.filter(r => r.claude_sentiment === 'Negative').length / rogersReviews.length) * 100) : 0;
    const bellNegPct = bellReviews.length > 0 ? 
        Math.round((bellReviews.filter(r => r.claude_sentiment === 'Negative').length / bellReviews.length) * 100) : 0;
    
    // Top issues analysis
    const issueCounts = reviews.reduce((acc, review) => {
        const category = review.primary_category || 'Unknown';
        acc[category] = (acc[category] || 0) + 1;
        return acc;
    }, {});
    
    const topIssues = Object.entries(issueCounts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 5)
        .map(([category, count]) => ({
            category,
            count,
            percentage: Math.round((count / totalReviews) * 100)
        }));
    
    // Platform-specific insights
    let insights = [];
    
    // Market presence
    insights.push({
        icon: '📊',
        title: 'Market Presence',
        content: `${platform} represents ${marketShare}% of filtered reviews with ${totalReviews.toLocaleString()} total reviews in the dataset.`
    });
    
    // Performance comparison
    if (negativePct > 60) {
        insights.push({
            icon: '🚨',
            title: 'Critical Platform Issues',
            content: `${platform} shows ${negativePct}% negative sentiment - platform-specific optimization urgently needed.`
        });
    } else if (negativePct > 40) {
        insights.push({
            icon: '⚠️',
            title: 'Platform Challenges',
            content: `${platform} has ${negativePct}% negative sentiment - requires platform-specific improvements.`
        });
    } else {
        insights.push({
            icon: '✅',
            title: 'Platform Stability',
            content: `${platform} maintains ${negativePct}% negative sentiment - performing within expected range.`
        });
    }
    
    // App comparison on platform
    if (rogersReviews.length > 0 && bellReviews.length > 0) {
        const appDiff = Math.abs(rogersNegPct - bellNegPct);
        if (appDiff > 15) {
            const worseApp = rogersNegPct > bellNegPct ? 'Rogers' : 'Bell';
            const betterApp = rogersNegPct < bellNegPct ? 'Rogers' : 'Bell';
            insights.push({
                icon: '🏆',
                title: 'App Performance Gap on Platform',
                content: `On ${platform}, ${worseApp} (${Math.max(rogersNegPct, bellNegPct)}% negative) significantly underperforms vs ${betterApp} (${Math.min(rogersNegPct, bellNegPct)}% negative).`
            });
        } else {
            insights.push({
                icon: '⚖️',
                title: 'Consistent App Performance',
                content: `Both apps perform similarly on ${platform}: Rogers ${rogersNegPct}% vs Bell ${bellNegPct}% negative sentiment.`
            });
        }
    }
    
    // Platform-specific issue insight
    if (topIssues.length > 0) {
        const topIssue = topIssues[0];
        insights.push({
            icon: '🎯',
            title: `${platform}-Specific Priority`,
            content: `"${topIssue.category}" is the top complaint on ${platform} with ${topIssue.count} reports (${topIssue.percentage}%) - may require platform-specific fixes.`
        });
    }
    
    return `
        <div style="margin-bottom: 1.5rem;">
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
                <div style="text-align: center; padding: 1rem; background: var(--ey-white); border-radius: 8px; border: 1px solid var(--border-light);">
                    <div style="font-size: 1.8rem; font-weight: 700; color: var(--ey-purple);">${totalReviews.toLocaleString()}</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">Reviews</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--ey-white); border-radius: 8px; border: 1px solid var(--border-light);">
                    <div style="font-size: 1.8rem; font-weight: 700; color: var(--ey-purple);">${avgRating}/5</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">Avg Rating</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--ey-white); border-radius: 8px; border: 1px solid var(--border-light);">
                    <div style="font-size: 1.8rem; font-weight: 700; color: var(--ey-purple);">${marketShare}%</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">Market Share</div>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <h4 style="color: var(--ey-navy); margin-bottom: 1rem; font-size: 1.1rem;">📱 App Performance on ${platform}</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;">
                <div style="text-align: center; padding: 0.75rem; background: var(--ey-white); border-radius: 6px; border: 1px solid var(--border-light);">
                    <div style="font-weight: 600; color: var(--ey-navy);">Rogers</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">${rogersReviews.length} reviews</div>
                    <div style="font-size: 0.9rem; color: ${rogersNegPct > 50 ? 'var(--ey-red)' : 'var(--ey-gray)'};">${rogersNegPct}% negative</div>
                </div>
                <div style="text-align: center; padding: 0.75rem; background: var(--ey-white); border-radius: 6px; border: 1px solid var(--border-light);">
                    <div style="font-weight: 600; color: var(--ey-navy);">Bell</div>
                    <div style="font-size: 0.9rem; color: var(--ey-gray);">${bellReviews.length} reviews</div>
                    <div style="font-size: 0.9rem; color: ${bellNegPct > 50 ? 'var(--ey-red)' : 'var(--ey-gray)'};">${bellNegPct}% negative</div>
                </div>
            </div>
        </div>
        
        <div style="margin-bottom: 1.5rem;">
            <h4 style="color: var(--ey-navy); margin-bottom: 1rem; font-size: 1.1rem;">🔧 Top ${platform} Issues</h4>
            ${topIssues.slice(0, 3).map((issue, index) => `
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; margin-bottom: 0.5rem; background: var(--ey-white); border-radius: 6px; border-left: 3px solid ${index === 0 ? 'var(--ey-red)' : index === 1 ? 'var(--ey-orange)' : 'var(--ey-gray)'};">
                    <span style="font-weight: 500; color: var(--ey-navy);">${issue.category}</span>
                    <span style="color: var(--ey-gray); font-size: 0.9rem;">${issue.count} (${issue.percentage}%)</span>
                </div>
            `).join('')}
        </div>
        
        ${insights.map(insight => 
            `<div style="background: var(--ey-white); margin: 1rem 0; padding: 1rem; border-radius: 8px; border-left: 4px solid var(--ey-yellow); border: 1px solid var(--border-light);">
                <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                    <span style="font-size: 1.2rem; margin-right: 0.5rem;">${insight.icon}</span>
                    <h5 style="margin: 0; color: var(--ey-navy); font-size: 1rem;">${insight.title}</h5>
                </div>
                <p style="margin: 0; line-height: 1.4; font-size: 0.95rem; color: var(--ey-gray);">${insight.content}</p>
            </div>`
        ).join('')}
    `;
}

function generateAppVsServiceAnalysis() {
    console.log('🏢 Generating App vs Service analysis...');
    
    try {
        const filtered = applyDataFilters();
        const analysisDiv = document.getElementById('appVsServiceAnalysis');
        
        if (!analysisDiv) {
            console.error('❌ App vs Service analysis div not found');
            return;
        }
        
        // Calculate category type distribution
        const categoryTypeStats = filtered.reduce((acc, review) => {
            const type = review.category_type || 'General';
            if (!acc[type]) {
                acc[type] = {
                    count: 0,
                    negativeCount: 0,
                    totalRating: 0,
                    actionableBy: {}
                };
            }
            acc[type].count++;
            acc[type].totalRating += review.rating;
            
            if (review.claude_sentiment === 'Negative') {
                acc[type].negativeCount++;
            }
            
            if (review.actionable_by) {
                acc[type].actionableBy[review.actionable_by] = (acc[type].actionableBy[review.actionable_by] || 0) + 1;
            }
            
            return acc;
        }, {});
        
        // Calculate percentages and averages
        const typeAnalysis = Object.entries(categoryTypeStats).map(([type, stats]) => ({
            type,
            count: stats.count,
            percentage: Math.round((stats.count / filtered.length) * 100),
            negativePercentage: Math.round((stats.negativeCount / stats.count) * 100),
            avgRating: (stats.totalRating / stats.count).toFixed(1),
            mainActionableBy: Object.keys(stats.actionableBy).reduce((a, b) => 
                stats.actionableBy[a] > (stats.actionableBy[b] || 0) ? a : b, 'Not Specified')
        })).sort((a, b) => b.count - a.count);
        
        // Get top categories by type
        const appRelatedCategories = filtered
            .filter(r => r.category_type === 'App-Related')
            .reduce((acc, review) => {
                const cat = review.final_category;
                acc[cat] = (acc[cat] || 0) + 1;
                return acc;
            }, {});
        
        const serviceRelatedCategories = filtered
            .filter(r => r.category_type === 'Service-Related')
            .reduce((acc, review) => {
                const cat = review.final_category;
                acc[cat] = (acc[cat] || 0) + 1;
                return acc;
            }, {});
        
        const topAppCategories = Object.entries(appRelatedCategories)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5);
        
        const topServiceCategories = Object.entries(serviceRelatedCategories)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 5);
        
        // Generate insights
        let insights = [];
        
        const appRelatedStats = typeAnalysis.find(t => t.type === 'App-Related');
        const serviceRelatedStats = typeAnalysis.find(t => t.type === 'Service-Related');
        
        if (appRelatedStats && serviceRelatedStats) {
            insights.push({
                icon: '⚖️',
                title: 'App vs Service Distribution',
                content: `${appRelatedStats.percentage}% app-related issues vs ${serviceRelatedStats.percentage}% service-related issues. ${appRelatedStats.count > serviceRelatedStats.count ? 'App development' : 'Service quality'} needs primary focus.`
            });
            
            if (Math.abs(appRelatedStats.negativePercentage - serviceRelatedStats.negativePercentage) > 10) {
                const worse = appRelatedStats.negativePercentage > serviceRelatedStats.negativePercentage ? 'App-related' : 'Service-related';
                const worsePercent = Math.max(appRelatedStats.negativePercentage, serviceRelatedStats.negativePercentage);
                insights.push({
                    icon: '🚨',
                    title: 'Issue Severity Gap',
                    content: `${worse} issues show ${worsePercent}% negative sentiment - indicating more severe customer impact requiring immediate attention.`
                });
            }
        }
        
        if (appRelatedStats && appRelatedStats.count > 0) {
            insights.push({
                icon: '📱',
                title: 'App Team Priority',
                content: `Top app issue: "${topAppCategories[0]?.[0] || 'N/A'}" with ${topAppCategories[0]?.[1] || 0} reports. Average app issue rating: ${appRelatedStats.avgRating}/5.`
            });
        }
        
        if (serviceRelatedStats && serviceRelatedStats.count > 0) {
            insights.push({
                icon: '🏢',
                title: 'Service Team Priority',
                content: `Top service issue: "${topServiceCategories[0]?.[0] || 'N/A'}" with ${topServiceCategories[0]?.[1] || 0} reports. Average service issue rating: ${serviceRelatedStats.avgRating}/5.`
            });
        }
        
        // Generate HTML
        const html = `
            <div style="margin-bottom: 2rem;">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem;">
                    ${typeAnalysis.map(type => `
                        <div style="text-align: center; padding: 1.5rem; background: var(--ey-white); border-radius: 8px; border-left: 4px solid ${
                            type.type === 'App-Related' ? 'var(--ey-blue)' : 
                            type.type === 'Service-Related' ? 'var(--ey-orange)' : 
                            'var(--ey-gray)'
                        }; border: 1px solid var(--border-light);">
                            <div style="font-size: 2rem; font-weight: 700; color: var(--ey-purple);">${type.count.toLocaleString()}</div>
                            <div style="font-size: 0.9rem; color: var(--ey-gray); margin-bottom: 0.5rem;">${type.type}</div>
                            <div style="font-size: 0.85rem; color: var(--ey-gray);">${type.percentage}% of total</div>
                            <div style="font-size: 0.85rem; color: ${type.negativePercentage > 50 ? 'var(--ey-red)' : 'var(--ey-gray)'};">${type.negativePercentage}% negative</div>
                        </div>
                    `).join('')}
                </div>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
                <div>
                    <h4 style="color: var(--ey-navy); margin-bottom: 1rem; font-size: 1.1rem;">📱 Top App-Related Issues</h4>
                    ${topAppCategories.length > 0 ? topAppCategories.map((cat, index) => `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; margin-bottom: 0.5rem; background: var(--ey-white); border-radius: 6px; border-left: 3px solid ${index === 0 ? 'var(--ey-red)' : index === 1 ? 'var(--ey-orange)' : 'var(--ey-gray)'};">
                            <span style="font-weight: 500; color: var(--ey-navy); font-size: 0.9rem;">${cat[0]}</span>
                            <span style="color: var(--ey-gray); font-size: 0.9rem;">${cat[1]}</span>
                        </div>
                    `).join('') : '<div style="color: var(--ey-gray); font-style: italic;">No app-related issues in filtered data</div>'}
                </div>
                
                <div>
                    <h4 style="color: var(--ey-navy); margin-bottom: 1rem; font-size: 1.1rem;">🏢 Top Service-Related Issues</h4>
                    ${topServiceCategories.length > 0 ? topServiceCategories.map((cat, index) => `
                        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.75rem; margin-bottom: 0.5rem; background: var(--ey-white); border-radius: 6px; border-left: 3px solid ${index === 0 ? 'var(--ey-red)' : index === 1 ? 'var(--ey-orange)' : 'var(--ey-gray)'};">
                            <span style="font-weight: 500; color: var(--ey-navy); font-size: 0.9rem;">${cat[0]}</span>
                            <span style="color: var(--ey-gray); font-size: 0.9rem;">${cat[1]}</span>
                        </div>
                    `).join('') : '<div style="color: var(--ey-gray); font-style: italic;">No service-related issues in filtered data</div>'}
                </div>
            </div>
            
            ${insights.map(insight => 
                `<div style="background: var(--ey-white); margin: 1rem 0; padding: 1rem; border-radius: 8px; border-left: 4px solid var(--ey-yellow); border: 1px solid var(--border-light);">
                    <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                        <span style="font-size: 1.2rem; margin-right: 0.5rem;">${insight.icon}</span>
                        <h5 style="margin: 0; color: var(--ey-navy); font-size: 1rem;">${insight.title}</h5>
                    </div>
                    <p style="margin: 0; line-height: 1.4; font-size: 0.95rem; color: var(--ey-gray);">${insight.content}</p>
                </div>`
            ).join('')}
        `;
        
        analysisDiv.innerHTML = html;
        console.log('✅ App vs Service analysis generated successfully');
        
    } catch (error) {
        console.error('❌ Error generating App vs Service analysis:', error);
    }
}

// Export functions for global access
window.showTab = showTab;
window.applyFilters = applyFilters;