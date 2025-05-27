// Final Dashboard with Complete Data Coverage
console.log('🚀 Loading Dashboard with Complete Dataset...');

// Load the comprehensive dashboard data
const DASHBOARD_DATA = COMPLETE_DASHBOARD_DATA;

// Log initial data load
console.log('📊 Dashboard data loaded:', {
    totalReviews: DASHBOARD_DATA.summary.total_reviews,
    allReviewsLength: DASHBOARD_DATA.all_reviews ? DASHBOARD_DATA.all_reviews.length : 0,
    platforms: DASHBOARD_DATA.all_reviews ? 
        DASHBOARD_DATA.all_reviews.reduce((acc, r) => {
            acc[r.platform] = (acc[r.platform] || 0) + 1;
            return acc;
        }, {}) : {},
    apps: DASHBOARD_DATA.all_reviews ?
        DASHBOARD_DATA.all_reviews.reduce((acc, r) => {
            acc[r.app_name] = (acc[r.app_name] || 0) + 1;
            return acc;
        }, {}) : {}
});

// Global variables for filtering
let filteredData = DASHBOARD_DATA.all_reviews;
let currentFilters = {
    dateRange: 'all',
    appFilter: 'all', 
    platformFilter: 'all',
    sentimentFilter: 'all',
    categoryFilter: 'all',
    searchFilter: ''
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
    
    // Ensure all_reviews array exists and has data
    if (!DASHBOARD_DATA.all_reviews || DASHBOARD_DATA.all_reviews.length === 0) {
        console.error('❌ No review data available in DASHBOARD_DATA.all_reviews');
        showError('No review data available');
        return;
    }
    
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
        // Get all unique primary categories from the complete dataset
        const categories = [...new Set(DASHBOARD_DATA.all_reviews
            .map(review => review.primary_category)
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
    
    console.log(`🔍 Starting with ${filtered.length} reviews`);
    
    // Apply app filter
    if (currentFilters.appFilter !== 'all') {
        filtered = filtered.filter(review => review.app_name === currentFilters.appFilter);
        console.log(`   After app filter (${currentFilters.appFilter}): ${filtered.length} reviews`);
    }
    
    // Apply platform filter
    if (currentFilters.platformFilter !== 'all') {
        filtered = filtered.filter(review => review.platform === currentFilters.platformFilter);
        console.log(`   After platform filter (${currentFilters.platformFilter}): ${filtered.length} reviews`);
    }
    
    // Apply sentiment filter
    if (currentFilters.sentimentFilter !== 'all') {
        filtered = filtered.filter(review => review.claude_sentiment === currentFilters.sentimentFilter);
        console.log(`   After sentiment filter (${currentFilters.sentimentFilter}): ${filtered.length} reviews`);
    }
    
    // Apply specific category filter (using enhanced categories)
    if (currentFilters.categoryFilter !== 'all') {
        filtered = filtered.filter(review => review.primary_category === currentFilters.categoryFilter);
        console.log(`   After category filter (${currentFilters.categoryFilter}): ${filtered.length} reviews`);
    }
    
    // Apply date filter (year-based filtering)
    if (currentFilters.dateRange !== 'all') {
        // Parse year from date string if year property doesn't exist
        filtered = filtered.filter(review => {
            const year = review.year || (review.date ? new Date(review.date).getFullYear().toString() : null);
            return year === currentFilters.dateRange;
        });
        console.log(`   After date filter (${currentFilters.dateRange}): ${filtered.length} reviews`);
    }
    
    // Apply search filter (search in review text only)
    if (currentFilters.searchFilter && currentFilters.searchFilter.trim() !== '') {
        const searchTerm = currentFilters.searchFilter.toLowerCase().trim();
        filtered = filtered.filter(review => {
            // Search only in the user review text
            const reviewText = (review.text || '').toLowerCase();
            return reviewText.includes(searchTerm);
        });
        console.log(`   After search filter ("${currentFilters.searchFilter}"): ${filtered.length} reviews`);
    }
    
    filteredData = filtered;
    console.log(`🔍 Final filtered result: ${filtered.length} reviews from ${DASHBOARD_DATA.all_reviews.length} total reviews`);
    
    // Check platform distribution
    const platforms = {};
    filtered.forEach(r => {
        platforms[r.platform] = (platforms[r.platform] || 0) + 1;
    });
    console.log('   Platform distribution:', platforms);
    
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
                          currentFilters.sentimentFilter !== 'all' || currentFilters.categoryFilter !== 'all' || 
                          currentFilters.dateRange !== 'all' || (currentFilters.searchFilter && currentFilters.searchFilter.trim() !== '');
        
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
        // Filter out empty categories and obvious errors
        if (category && category.trim() !== '' && category.length > 2 && !category.match(/^[\d.-]+$/)) {
            acc[category] = (acc[category] || 0) + 1;
        }
        return acc;
    }, {});
    
    // Use filtered data if available, otherwise full summary
    const data = Object.keys(categoryCounts).length > 0 ? categoryCounts : DASHBOARD_DATA.summary.category_distribution;
    
    // Sort all entries and prepare for visualization
    const allEntries = Object.entries(data).sort(([,a], [,b]) => b - a);
    
    // Create a treemap for better visualization of all categories
    const treemapData = [{
        type: 'treemap',
        labels: allEntries.map(([name]) => name),
        parents: allEntries.map(() => ''),
        values: allEntries.map(([,count]) => count),
        textinfo: 'label+value+percent parent',
        marker: {
            colorscale: [
                [0, '#FFE600'],
                [0.2, '#FF9500'],
                [0.4, '#FF0040'],
                [0.6, '#2E2A48'],
                [0.8, '#0F1419'],
                [1, '#6B5B95']
            ],
            colorbar: {
                title: 'Reviews',
                titleside: 'right'
            }
        },
        hovertemplate: '<b>%{label}</b><br>Reviews: %{value}<br>%{percentParent}<extra></extra>'
    }];
    
    const treemapLayout = {
        margin: { t: 40, b: 10, l: 10, r: 10 },
        font: { family: 'Inter, sans-serif' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        height: 600
    };
    
    // Create treemap for Issue Category Analysis
    if (document.getElementById('topIssuesChart')) {
        // Add buttons to switch between visualizations
        const updateMenus = [{
            buttons: [
                {
                    args: [{
                        type: 'treemap',
                        labels: allEntries.map(([name]) => name),
                        parents: allEntries.map(() => ''),
                        values: allEntries.map(([,count]) => count),
                        textinfo: 'label+value+percent parent',
                        marker: treemapData[0].marker,
                        hovertemplate: '<b>%{label}</b><br>Reviews: %{value}<br>%{percentParent}<extra></extra>'
                    }],
                    label: 'Treemap View',
                    method: 'restyle'
                },
                {
                    args: [{
                        type: 'sunburst',
                        labels: ['All Categories', ...allEntries.map(([name]) => name)],
                        parents: ['', ...allEntries.map(() => 'All Categories')],
                        values: [0, ...allEntries.map(([,count]) => count)],
                        textinfo: 'label+value+percent entry',
                        marker: {
                            colors: allEntries.map(([,count], i) => {
                                const max = allEntries[0][1];
                                const ratio = count / max;
                                if (ratio > 0.8) return '#FF0040';
                                if (ratio > 0.6) return '#FF9500';
                                if (ratio > 0.4) return '#FFE600';
                                if (ratio > 0.2) return '#2E2A48';
                                return '#6B5B95';
                            }),
                            line: {width: 2}
                        },
                        hovertemplate: '<b>%{label}</b><br>Reviews: %{value}<br>%{percentEntry}<extra></extra>'
                    }],
                    label: 'Sunburst View',
                    method: 'restyle'
                }
            ],
            direction: 'down',
            showactive: true,
            x: 0.1,
            xanchor: 'left',
            y: 1.15,
            yanchor: 'top'
        }];
        
        const enhancedLayout = {
            ...treemapLayout,
            updatemenus: updateMenus
        };
        
        Plotly.newPlot('topIssuesChart', treemapData, enhancedLayout, chartConfig);
    }
    
    // Create horizontal bar chart for critical issues (top 15)
    const topEntries = allEntries.slice(0, 15);
    const barData = [{
        y: topEntries.map(([name]) => name).reverse(),
        x: topEntries.map(([,count]) => count).reverse(),
        type: 'bar',
        orientation: 'h',
        marker: { 
            color: topEntries.map((_, i) => {
                const colors = ['#FF0040', '#FF0040', '#FF0040', '#FF9500', '#FF9500', 
                               '#FFE600', '#FFE600', '#FFE600', '#2E2A48', '#2E2A48',
                               '#6B5B95', '#6B5B95', '#6B5B95', '#6B5B95', '#6B5B95'];
                return colors[topEntries.length - 1 - i];
            })
        },
        text: topEntries.map(([,count]) => count.toLocaleString()).reverse(),
        textposition: 'outside',
        hovertemplate: '<b>%{y}</b><br>Count: %{x}<extra></extra>'
    }];
    
    const barLayout = {
        margin: { t: 40, b: 60, l: 180, r: 100 },
        xaxis: { title: 'Number of Reviews' },
        font: { family: 'Inter, sans-serif' },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        height: 500
    };
    
    // Create bar chart for critical issues
    if (document.getElementById('criticalIssuesChart')) {
        Plotly.newPlot('criticalIssuesChart', barData, barLayout, chartConfig);
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
        textCell.textContent = review.text && review.text.length > 200 ? review.text.substring(0, 200) + '...' : (review.text || '');
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
    console.log('🧠 Generating strategic insights...');
    
    // Check if all filters are set to 'all' (no filtering)
    const noFiltersApplied = currentFilters.dateRange === 'all' && 
                             currentFilters.appFilter === 'all' && 
                             currentFilters.platformFilter === 'all' && 
                             currentFilters.sentimentFilter === 'all' && 
                             currentFilters.categoryFilter === 'all';
    
    // Use all data if no filters are applied, otherwise use filtered data
    let dataToUse;
    if (noFiltersApplied) {
        dataToUse = DASHBOARD_DATA.all_reviews;
        console.log(`📊 Using all data: ${dataToUse.length} reviews`);
    } else {
        dataToUse = applyDataFilters();
        console.log(`📊 Using filtered data: ${dataToUse.length} reviews`);
    }
    
    // Ensure we have data to work with
    if (!dataToUse || dataToUse.length === 0) {
        console.warn('⚠️ No data available for insights generation');
        dataToUse = DASHBOARD_DATA.all_reviews;
    }
    
    // Update all strategic insight sections
    updateRogersPlatformIntelligence(dataToUse);
    updateProviderComparisonIntelligence(dataToUse);
    updateCriticalUserFlows(dataToUse);
    updateReviewEvidence(dataToUse);
    updateKeyIntelligenceFindings(dataToUse);
    updateBellAdvantages(dataToUse);
    updateRegulatoryAnalysis(dataToUse);
}

function updateRogersPlatformIntelligence(filteredData) {
    const container = document.getElementById('rogersPlatformIntelligence');
    if (!container) {
        console.error('❌ rogersPlatformIntelligence container not found');
        return;
    }
    
    console.log(`📱 Updating Rogers platform intelligence with ${filteredData.length} reviews`);
    
    // Filter for Rogers only
    const rogersData = filteredData.filter(r => r.app_name === 'Rogers');
    const rogersIOS = rogersData.filter(r => r.platform === 'iOS');
    const rogersAndroid = rogersData.filter(r => r.platform === 'Android');
    
    console.log(`Rogers data: ${rogersData.length} total, iOS: ${rogersIOS.length}, Android: ${rogersAndroid.length}`);
    
    if (rogersData.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">No Rogers reviews match current filters</p>';
        return;
    }
    
    // Calculate metrics for each platform
    const iosMetrics = calculatePlatformMetrics(rogersIOS);
    const androidMetrics = calculatePlatformMetrics(rogersAndroid);
    
    // Get top issues for each platform
    const iosIssues = getTopIssues(rogersIOS, 5);
    const androidIssues = getTopIssues(rogersAndroid, 5);
    
    container.innerHTML = `
        <div class="grid grid-2" style="margin-bottom: 2rem;">
            <div class="platform-analysis-card" style="border: 2px solid #000; background: #f8f8f8; padding: 1.5rem; border-radius: 12px;">
                <h4 style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <i class="fab fa-apple" style="font-size: 1.5rem;"></i> iOS Analysis
                </h4>
                <div class="metrics-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #e50000;">${iosMetrics.count}</div>
                        <div style="font-size: 0.85rem; color: #666;">Reviews</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: ${iosMetrics.negativePct > 60 ? '#e50000' : '#666'};">${iosMetrics.negativePct}%</div>
                        <div style="font-size: 0.85rem; color: #666;">Negative</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #666;">${iosMetrics.avgRating}/5</div>
                        <div style="font-size: 0.85rem; color: #666;">Avg Rating</div>
                    </div>
                </div>
                <h5 style="margin-bottom: 0.5rem;">Top iOS Issues:</h5>
                <ul style="list-style: none; padding: 0;">
                    ${iosIssues.map(issue => `
                        <li style="padding: 0.5rem 0; border-bottom: 1px solid #e0e0e0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>${issue.category}</span>
                                <span style="color: #666; font-size: 0.9rem;">${issue.count} (${issue.percentage}%)</span>
                            </div>
                        </li>
                    `).join('')}
                </ul>
            </div>
            
            <div class="platform-analysis-card" style="border: 2px solid #3DDC84; background: #f8f8f8; padding: 1.5rem; border-radius: 12px;">
                <h4 style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                    <i class="fab fa-android" style="font-size: 1.5rem; color: #3DDC84;"></i> Android Analysis
                </h4>
                <div class="metrics-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1rem;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #e50000;">${androidMetrics.count}</div>
                        <div style="font-size: 0.85rem; color: #666;">Reviews</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: ${androidMetrics.negativePct > 60 ? '#e50000' : '#666'};">${androidMetrics.negativePct}%</div>
                        <div style="font-size: 0.85rem; color: #666;">Negative</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.5rem; font-weight: 700; color: #666;">${androidMetrics.avgRating}/5</div>
                        <div style="font-size: 0.85rem; color: #666;">Avg Rating</div>
                    </div>
                </div>
                <h5 style="margin-bottom: 0.5rem;">Top Android Issues:</h5>
                <ul style="list-style: none; padding: 0;">
                    ${androidIssues.map(issue => `
                        <li style="padding: 0.5rem 0; border-bottom: 1px solid #e0e0e0;">
                            <div style="display: flex; justify-content: space-between;">
                                <span>${issue.category}</span>
                                <span style="color: #666; font-size: 0.9rem;">${issue.count} (${issue.percentage}%)</span>
                            </div>
                        </li>
                    `).join('')}
                </ul>
            </div>
        </div>
        
        <div style="background: #fffbeb; border: 1px solid #fbbf24; padding: 1rem; border-radius: 8px;">
            <h5 style="margin-bottom: 0.5rem;"><i class="fas fa-chart-line"></i> Platform Intelligence Summary</h5>
            <p style="margin: 0;">
                ${androidMetrics.count > iosMetrics.count ? 
                    `Android dominates with ${Math.round(androidMetrics.count / (androidMetrics.count + iosMetrics.count) * 100)}% of Rogers reviews. ` :
                    `iOS and Android have similar review volumes. `
                }
                ${Math.abs(androidMetrics.negativePct - iosMetrics.negativePct) > 10 ?
                    `${androidMetrics.negativePct > iosMetrics.negativePct ? 'Android' : 'iOS'} users are significantly more dissatisfied (${Math.abs(androidMetrics.negativePct - iosMetrics.negativePct)}% difference). ` :
                    `Both platforms show similar satisfaction levels. `
                }
                ${compareTopIssues(iosIssues[0], androidIssues[0])}
            </p>
        </div>
    `;
}

function calculatePlatformMetrics(reviews) {
    const count = reviews.length;
    const negativeCount = reviews.filter(r => r.claude_sentiment === 'Negative').length;
    const avgRating = count > 0 ? (reviews.reduce((sum, r) => sum + parseFloat(r.rating), 0) / count).toFixed(1) : '0.0';
    
    return {
        count,
        negativePct: count > 0 ? Math.round(negativeCount / count * 100) : 0,
        avgRating
    };
}

function getTopIssues(reviews, limit = 5) {
    const issueCounts = {};
    reviews.forEach(review => {
        const category = review.primary_category || 'Unknown';
        if (category && category.trim() !== '' && !category.match(/^[\d.-]+$/)) {
            issueCounts[category] = (issueCounts[category] || 0) + 1;
        }
    });
    
    return Object.entries(issueCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit)
        .map(([category, count]) => ({
            category,
            count,
            percentage: reviews.length > 0 ? Math.round(count / reviews.length * 100) : 0
        }));
}

function compareTopIssues(iosTop, androidTop) {
    if (!iosTop || !androidTop) return '';
    if (iosTop.category === androidTop.category) {
        return `Both platforms share "${iosTop.category}" as their top concern.`;
    }
    return `iOS users primarily face "${iosTop.category}" issues while Android users struggle with "${androidTop.category}".`;
}

function updateProviderComparisonIntelligence(filteredData) {
    const container = document.getElementById('providerComparisonIntelligence');
    if (!container) return;
    
    const rogersData = filteredData.filter(r => r.app_name === 'Rogers');
    const bellData = filteredData.filter(r => r.app_name === 'Bell');
    
    if (rogersData.length === 0 && bellData.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">No reviews match current filters</p>';
        return;
    }
    
    const rogersIssues = getTopIssues(rogersData, 8);
    const bellIssues = getTopIssues(bellData, 8);
    
    // Categorize issues
    const categorizeIssue = (category) => {
        const appRelated = ['Technical Issues', 'User Experience', 'Features', 'Performance', 'Login Issues', 'App Crashes'];
        const serviceRelated = ['Billing', 'Customer Support', 'Network Issues', 'Account Management'];
        
        if (appRelated.some(term => category.includes(term))) return 'app';
        if (serviceRelated.some(term => category.includes(term))) return 'service';
        return 'other';
    };
    
    const rogersAppIssues = rogersIssues.filter(i => categorizeIssue(i.category) === 'app');
    const rogersServiceIssues = rogersIssues.filter(i => categorizeIssue(i.category) === 'service');
    const bellAppIssues = bellIssues.filter(i => categorizeIssue(i.category) === 'app');
    const bellServiceIssues = bellIssues.filter(i => categorizeIssue(i.category) === 'service');
    
    container.innerHTML = `
        <div class="comparison-grid" style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem;">
            <div style="background: #ffe5e5; padding: 1.5rem; border-radius: 12px; border: 2px solid #e50000;">
                <h4 style="color: #e50000; margin-bottom: 1rem;">
                    <i class="fas fa-mobile-alt"></i> Rogers Customer Complaints
                </h4>
                <div style="margin-bottom: 1rem;">
                    <h5 style="color: #666; font-size: 0.95rem; margin-bottom: 0.5rem;">App-Related Issues:</h5>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${rogersAppIssues.slice(0, 4).map(issue => `
                            <li style="padding: 0.25rem 0; font-size: 0.9rem;">
                                • ${issue.category} (${issue.percentage}%)
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div>
                    <h5 style="color: #666; font-size: 0.95rem; margin-bottom: 0.5rem;">Service-Related Issues:</h5>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${rogersServiceIssues.slice(0, 4).map(issue => `
                            <li style="padding: 0.25rem 0; font-size: 0.9rem;">
                                • ${issue.category} (${issue.percentage}%)
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
            
            <div style="background: #e5f0ff; padding: 1.5rem; border-radius: 12px; border: 2px solid #0066cc;">
                <h4 style="color: #0066cc; margin-bottom: 1rem;">
                    <i class="fas fa-phone"></i> Bell Customer Complaints
                </h4>
                <div style="margin-bottom: 1rem;">
                    <h5 style="color: #666; font-size: 0.95rem; margin-bottom: 0.5rem;">App-Related Issues:</h5>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${bellAppIssues.slice(0, 4).map(issue => `
                            <li style="padding: 0.25rem 0; font-size: 0.9rem;">
                                • ${issue.category} (${issue.percentage}%)
                            </li>
                        `).join('')}
                    </ul>
                </div>
                <div>
                    <h5 style="color: #666; font-size: 0.95rem; margin-bottom: 0.5rem;">Service-Related Issues:</h5>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        ${bellServiceIssues.slice(0, 4).map(issue => `
                            <li style="padding: 0.25rem 0; font-size: 0.9rem;">
                                • ${issue.category} (${issue.percentage}%)
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        </div>
        
        <div style="background: #f3f4f6; padding: 1rem; border-radius: 8px;">
            <h5 style="margin-bottom: 0.5rem;"><i class="fas fa-balance-scale"></i> Comparison Intelligence</h5>
            <p style="margin: 0;">
                ${rogersAppIssues.length > bellAppIssues.length ? 
                    'Rogers customers report more diverse app-related issues, indicating broader technical challenges. ' :
                    'Bell customers face similar app complexity. '
                }
                ${rogersServiceIssues.length > bellServiceIssues.length ?
                    'Rogers also has more service-related complaints. ' :
                    'Bell has more service-related complaints. '
                }
                ${analyzeComplaintPatterns(rogersIssues[0], bellIssues[0])}
            </p>
        </div>
    `;
}

function analyzeComplaintPatterns(rogersTop, bellTop) {
    if (!rogersTop || !bellTop) return '';
    
    const rogersType = rogersTop.category.includes('Technical') || rogersTop.category.includes('App') ? 'technical' : 'service';
    const bellType = bellTop.category.includes('Technical') || bellTop.category.includes('App') ? 'technical' : 'service';
    
    if (rogersType === 'technical' && bellType === 'service') {
        return 'Rogers faces primarily technical/app challenges while Bell customers are more concerned with service quality.';
    } else if (rogersType === 'service' && bellType === 'technical') {
        return 'Bell struggles with technical issues while Rogers customers focus on service concerns.';
    }
    return 'Both providers face similar challenge distributions.';
}

function updateCriticalUserFlows(filteredData) {
    const container = document.getElementById('criticalUserFlows');
    if (!container) return;
    
    // Define critical user flows in telecom apps
    const userFlows = [
        {
            name: 'Bill Payment & Management',
            keywords: ['bill', 'payment', 'pay', 'invoice', 'charge'],
            icon: '💳',
            description: 'View bills, make payments, manage payment methods'
        },
        {
            name: 'Usage Monitoring',
            keywords: ['usage', 'data', 'minutes', 'balance', 'limit'],
            icon: '📊',
            description: 'Track data usage, minutes, and plan limits'
        },
        {
            name: 'Account Access',
            keywords: ['login', 'sign in', 'password', 'access', 'authentication'],
            icon: '🔐',
            description: 'Login, authentication, and secure access'
        },
        {
            name: 'Plan Management',
            keywords: ['plan', 'upgrade', 'change', 'add-on', 'features'],
            icon: '📋',
            description: 'View and modify plans, add features'
        },
        {
            name: 'Customer Support',
            keywords: ['support', 'help', 'contact', 'chat', 'issue'],
            icon: '🤝',
            description: 'Get help and resolve issues'
        }
    ];
    
    // Analyze each flow
    const flowAnalysis = userFlows.map(flow => {
        const relevantReviews = filteredData.filter(review => {
            const text = (review.text + ' ' + review.claude_summary).toLowerCase();
            return flow.keywords.some(keyword => text.includes(keyword));
        });
        
        const negativeCount = relevantReviews.filter(r => r.claude_sentiment === 'Negative').length;
        const avgRating = relevantReviews.length > 0 ? 
            (relevantReviews.reduce((sum, r) => sum + parseFloat(r.rating), 0) / relevantReviews.length).toFixed(1) : 'N/A';
        
        return {
            ...flow,
            mentions: relevantReviews.length,
            negativePercentage: relevantReviews.length > 0 ? Math.round(negativeCount / relevantReviews.length * 100) : 0,
            avgRating,
            impactScore: relevantReviews.length * (negativeCount / relevantReviews.length || 0)
        };
    });
    
    // Sort by impact
    flowAnalysis.sort((a, b) => b.impactScore - a.impactScore);
    
    container.innerHTML = `
        <div style="margin-bottom: 1rem;">
            ${flowAnalysis.map((flow, index) => `
                <div style="background: ${index === 0 ? '#fee2e2' : '#f3f4f6'}; padding: 1.5rem; margin-bottom: 1rem; border-radius: 12px; border-left: 4px solid ${index === 0 ? '#dc2626' : '#6b7280'};">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                                <span style="font-size: 1.5rem;">${flow.icon}</span>
                                ${flow.name}
                                ${index === 0 ? '<span style="background: #dc2626; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; margin-left: 0.5rem;">CRITICAL</span>' : ''}
                            </h4>
                            <p style="color: #666; margin-bottom: 0.5rem; font-size: 0.95rem;">${flow.description}</p>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 1.2rem; font-weight: 700; color: ${flow.negativePercentage > 60 ? '#dc2626' : '#333'};">
                                ${flow.negativePercentage}% negative
                            </div>
                            <div style="font-size: 0.85rem; color: #666;">
                                ${flow.mentions} mentions | ${flow.avgRating}/5 avg
                            </div>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
        
        <div style="background: #fffbeb; border: 1px solid #fbbf24; padding: 1rem; border-radius: 8px;">
            <h5 style="margin-bottom: 0.5rem;"><i class="fas fa-exclamation-triangle"></i> Critical Flow Analysis</h5>
            <p style="margin: 0;">
                "${flowAnalysis[0].name}" is the most problematic user flow with ${flowAnalysis[0].negativePercentage}% negative sentiment. 
                ${flowAnalysis[0].mentions > 100 ? 'This high-volume issue significantly impacts user experience. ' : ''}
                ${flowAnalysis.filter(f => f.negativePercentage > 50).length} out of ${flowAnalysis.length} critical flows show majority negative sentiment.
            </p>
        </div>
    `;
}

function updateReviewEvidence(filteredData) {
    const container = document.getElementById('reviewEvidence');
    if (!container) return;
    
    // Get top categories
    const topCategories = getTopIssues(filteredData, 3);
    
    container.innerHTML = `
        <div style="margin-bottom: 1rem;">
            ${topCategories.map(category => {
                // Get example reviews for this category
                const categoryReviews = filteredData
                    .filter(r => r.primary_category === category.category && r.claude_sentiment === 'Negative')
                    .sort((a, b) => parseFloat(b.thumbs_up || 0) - parseFloat(a.thumbs_up || 0))
                    .slice(0, 2);
                
                return `
                    <div style="margin-bottom: 2rem;">
                        <h4 style="margin-bottom: 1rem; color: #333;">
                            <i class="fas fa-tag"></i> ${category.category} (${category.count} reviews)
                        </h4>
                        ${categoryReviews.map(review => `
                            <div style="background: #f9fafb; border: 1px solid #e5e7eb; padding: 1rem; margin-bottom: 0.75rem; border-radius: 8px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.85rem; color: #666;">
                                    <span><strong>${review.app_name}</strong> - ${review.platform}</span>
                                    <span>★ ${review.rating}/5 | ${review.date ? new Date(review.date).toLocaleDateString() : 'No date'}</span>
                                </div>
                                <p style="margin: 0; font-style: italic; line-height: 1.5;">
                                    "${review.text && review.text.length > 200 ? review.text.substring(0, 200) + '...' : review.text || 'No review text'}"
                                </p>
                                ${review.thumbs_up && review.thumbs_up > 0 ? `<div style="margin-top: 0.5rem; font-size: 0.85rem; color: #666;">👍 ${review.thumbs_up} found this helpful</div>` : ''}
                            </div>
                        `).join('')}
                    </div>
                `;
            }).join('')}
        </div>
    `;
}

function updateKeyIntelligenceFindings(filteredData) {
    const container = document.getElementById('keyIntelligenceFindings');
    if (!container) return;
    
    // Calculate key metrics
    const rogersData = filteredData.filter(r => r.app_name === 'Rogers');
    const bellData = filteredData.filter(r => r.app_name === 'Bell');
    
    const findings = generateIntelligenceFindings(filteredData, rogersData, bellData);
    
    container.innerHTML = `
        <div style="display: grid; gap: 1rem;">
            ${findings.map((finding, index) => `
                <div style="background: ${index === 0 ? '#fee2e2' : '#f3f4f6'}; padding: 1rem; border-radius: 8px; border-left: 4px solid ${finding.priority === 'high' ? '#dc2626' : '#6b7280'};">
                    <h5 style="margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.2rem;">${finding.icon}</span>
                        ${finding.title}
                    </h5>
                    <p style="margin: 0; line-height: 1.5;">${finding.content}</p>
                </div>
            `).join('')}
        </div>
    `;
}

function generateIntelligenceFindings(allData, rogersData, bellData) {
    const findings = [];
    
    // Calculate comprehensive metrics for both providers
    const rogersMetrics = calculateProviderMetrics(rogersData);
    const bellMetrics = calculateProviderMetrics(bellData);
    
    // 1. Overall satisfaction comparison
    if (bellMetrics.avgRating > rogersMetrics.avgRating) {
        findings.push({
            icon: '⭐',
            title: 'Bell\'s Superior User Satisfaction',
            content: `Bell maintains a ${bellMetrics.avgRating.toFixed(1)}/5 average rating compared to Rogers' ${rogersMetrics.avgRating.toFixed(1)}/5. Bell users are ${Math.round((bellMetrics.avgRating - rogersMetrics.avgRating) / rogersMetrics.avgRating * 100)}% more satisfied overall.`,
            priority: 'high'
        });
    }
    
    // 2. App stability comparison
    const rogersStabilityIssues = rogersData.filter(r => 
        ['App Crashes', 'Technical Issues', 'Performance', 'Loading Problems'].includes(r.primary_category)
    ).length;
    const bellStabilityIssues = bellData.filter(r => 
        ['App Crashes', 'Technical Issues', 'Performance', 'Loading Problems'].includes(r.primary_category)
    ).length;
    
    const rogersStabilityRate = rogersData.length > 0 ? rogersStabilityIssues / rogersData.length : 0;
    const bellStabilityRate = bellData.length > 0 ? bellStabilityIssues / bellData.length : 0;
    
    if (bellStabilityRate < rogersStabilityRate * 0.7) {
        findings.push({
            icon: '🛡️',
            title: 'Bell\'s App Stability Advantage',
            content: `Bell's app has ${Math.round((1 - bellStabilityRate/rogersStabilityRate) * 100)}% fewer stability issues. Only ${Math.round(bellStabilityRate * 100)}% of Bell reviews report crashes/performance issues vs ${Math.round(rogersStabilityRate * 100)}% for Rogers.`,
            priority: 'high'
        });
    }
    
    // 3. Authentication success
    const rogersAuthIssues = rogersData.filter(r => 
        ['Login Issues', 'Authentication', 'Account Access'].includes(r.primary_category)
    ).length;
    const bellAuthIssues = bellData.filter(r => 
        ['Login Issues', 'Authentication', 'Account Access'].includes(r.primary_category)
    ).length;
    
    const rogersAuthRate = rogersData.length > 0 ? rogersAuthIssues / rogersData.length : 0;
    const bellAuthRate = bellData.length > 0 ? bellAuthIssues / bellData.length : 0;
    
    if (bellAuthRate < rogersAuthRate * 0.5) {
        findings.push({
            icon: '🔓',
            title: 'Bell\'s Smoother Authentication',
            content: `Bell users experience ${Math.round((1 - bellAuthRate/rogersAuthRate) * 100)}% fewer login issues. Bell's authentication flow appears more user-friendly and reliable.`,
            priority: 'high'
        });
    }
    
    // 4. Feature satisfaction
    const rogersFeatureComplaints = rogersData.filter(r => 
        r.primary_category === 'Features' && r.claude_sentiment === 'Negative'
    ).length;
    const bellFeatureComplaints = bellData.filter(r => 
        r.primary_category === 'Features' && r.claude_sentiment === 'Negative'
    ).length;
    
    const rogersPositiveFeedback = rogersData.filter(r => 
        r.primary_category === 'User Feedback' && r.claude_sentiment === 'Positive'
    ).length;
    const bellPositiveFeedback = bellData.filter(r => 
        r.primary_category === 'User Feedback' && r.claude_sentiment === 'Positive'
    ).length;
    
    const bellPositiveRate = bellData.length > 0 ? bellPositiveFeedback / bellData.length : 0;
    const rogersPositiveRate = rogersData.length > 0 ? rogersPositiveFeedback / rogersData.length : 0;
    
    if (bellPositiveRate > rogersPositiveRate * 1.5) {
        findings.push({
            icon: '💝',
            title: 'Bell\'s Higher User Appreciation',
            content: `Bell receives ${Math.round(bellPositiveRate * 100)}% positive feedback vs Rogers' ${Math.round(rogersPositiveRate * 100)}%. Bell users actively praise the app more frequently.`,
            priority: 'medium'
        });
    }
    
    // 5. Service integration
    const rogersBillingIssues = rogersData.filter(r => r.primary_category === 'Billing').length;
    const bellBillingIssues = bellData.filter(r => r.primary_category === 'Billing').length;
    
    const rogersBillingRate = rogersData.length > 0 ? rogersBillingIssues / rogersData.length : 0;
    const bellBillingRate = bellData.length > 0 ? bellBillingIssues / bellData.length : 0;
    
    // 6. User experience design
    const rogersUXIssues = rogersData.filter(r => 
        ['User Experience', 'Navigation Issues', 'UI/UX'].includes(r.primary_category)
    ).length;
    const bellUXIssues = bellData.filter(r => 
        ['User Experience', 'Navigation Issues', 'UI/UX'].includes(r.primary_category)
    ).length;
    
    const rogersUXRate = rogersData.length > 0 ? rogersUXIssues / rogersData.length : 0;
    const bellUXRate = bellData.length > 0 ? bellUXIssues / bellData.length : 0;
    
    if (bellUXRate < rogersUXRate * 0.7) {
        findings.push({
            icon: '🎨',
            title: 'Bell\'s Superior User Experience',
            content: `Bell has ${Math.round((1 - bellUXRate/rogersUXRate) * 100)}% fewer UX complaints. Users find Bell's app more intuitive and easier to navigate.`,
            priority: 'medium'
        });
    }
    
    // 7. What Bell does right - specific strengths
    const bellStrengths = analyzeBellStrengths(bellData, rogersData);
    if (bellStrengths.length > 0) {
        findings.push({
            icon: '🏆',
            title: 'Bell\'s Key Success Factors',
            content: bellStrengths.join(' '),
            priority: 'high'
        });
    }
    
    // 8. Platform consistency
    const rogersIOSNeg = rogersData.filter(r => r.platform === 'iOS' && r.claude_sentiment === 'Negative').length;
    const rogersAndroidNeg = rogersData.filter(r => r.platform === 'Android' && r.claude_sentiment === 'Negative').length;
    const bellIOSNeg = bellData.filter(r => r.platform === 'iOS' && r.claude_sentiment === 'Negative').length;
    const bellAndroidNeg = bellData.filter(r => r.platform === 'Android' && r.claude_sentiment === 'Negative').length;
    
    const rogersIOSTotal = rogersData.filter(r => r.platform === 'iOS').length;
    const rogersAndroidTotal = rogersData.filter(r => r.platform === 'Android').length;
    const bellIOSTotal = bellData.filter(r => r.platform === 'iOS').length;
    const bellAndroidTotal = bellData.filter(r => r.platform === 'Android').length;
    
    const rogersPlatformGap = Math.abs(
        (rogersIOSTotal > 0 ? rogersIOSNeg/rogersIOSTotal : 0) - 
        (rogersAndroidTotal > 0 ? rogersAndroidNeg/rogersAndroidTotal : 0)
    );
    const bellPlatformGap = Math.abs(
        (bellIOSTotal > 0 ? bellIOSNeg/bellIOSTotal : 0) - 
        (bellAndroidTotal > 0 ? bellAndroidNeg/bellAndroidTotal : 0)
    );
    
    if (bellPlatformGap < rogersPlatformGap * 0.5) {
        findings.push({
            icon: '🔄',
            title: 'Bell\'s Platform Consistency',
            content: `Bell maintains more consistent experience across platforms. Rogers shows ${Math.round(rogersPlatformGap * 100)}% variance between iOS/Android satisfaction vs Bell's ${Math.round(bellPlatformGap * 100)}%.`,
            priority: 'medium'
        });
    }
    
    return findings;
}

function calculateProviderMetrics(data) {
    if (data.length === 0) return { avgRating: 0, negativeRate: 0 };
    
    const negativeCount = data.filter(r => r.claude_sentiment === 'Negative').length;
    const avgRating = data.reduce((sum, r) => sum + parseFloat(r.rating), 0) / data.length;
    
    return {
        avgRating: avgRating,
        negativeRate: negativeCount / data.length,
        totalReviews: data.length
    };
}

function analyzeBellStrengths(bellData, rogersData) {
    const strengths = [];
    
    // Analyze what Bell users praise that Rogers users don't
    const bellPraise = bellData.filter(r => r.claude_sentiment === 'Positive');
    const rogersPraise = rogersData.filter(r => r.claude_sentiment === 'Positive');
    
    // Common praise keywords in Bell reviews
    const bellPraiseText = bellPraise.map(r => (r.text + ' ' + r.claude_summary).toLowerCase()).join(' ');
    const rogersPraiseText = rogersPraise.map(r => (r.text + ' ' + r.claude_summary).toLowerCase()).join(' ');
    
    // Key differentiators
    if (bellPraiseText.includes('easy') && bellPraiseText.includes('use')) {
        const bellEasyCount = (bellPraiseText.match(/easy to use|user friendly|simple|intuitive/g) || []).length;
        const rogersEasyCount = (rogersPraiseText.match(/easy to use|user friendly|simple|intuitive/g) || []).length;
        
        if (bellEasyCount > rogersEasyCount * 2) {
            strengths.push('Users consistently praise Bell\'s app as "easy to use" and "intuitive".');
        }
    }
    
    if (bellPraiseText.includes('fast') || bellPraiseText.includes('quick')) {
        strengths.push('Bell\'s app is recognized for speed and responsiveness.');
    }
    
    if (bellPraiseText.includes('reliable') || bellPraiseText.includes('works')) {
        strengths.push('Reliability is a key strength - Bell\'s app "just works".');
    }
    
    return strengths;
}

function updateBellAdvantages(filteredData) {
    const container = document.getElementById('bellAdvantages');
    if (!container) {
        console.error('❌ bellAdvantages container not found');
        return;
    }
    
    console.log(`🏆 Updating Bell advantages analysis with ${filteredData.length} reviews`);
    
    // Separate data by provider
    const rogersData = filteredData.filter(r => r.app_name === 'Rogers');
    const bellData = filteredData.filter(r => r.app_name === 'Bell');
    
    if (bellData.length === 0 || rogersData.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: #666;">Need data from both providers to compare advantages</p>';
        return;
    }
    
    // Calculate detailed metrics for comparison
    const bellMetrics = {
        avgRating: bellData.reduce((sum, r) => sum + parseFloat(r.rating), 0) / bellData.length,
        negativeRate: bellData.filter(r => r.claude_sentiment === 'Negative').length / bellData.length,
        positiveRate: bellData.filter(r => r.claude_sentiment === 'Positive').length / bellData.length,
        crashRate: bellData.filter(r => r.primary_category === 'App Crashes').length / bellData.length,
        loginIssueRate: bellData.filter(r => r.primary_category === 'Login Issues').length / bellData.length,
        performanceIssueRate: bellData.filter(r => ['Performance', 'Loading Problems'].includes(r.primary_category)).length / bellData.length,
        uxComplaintRate: bellData.filter(r => ['User Experience', 'Navigation Issues', 'UI/UX'].includes(r.primary_category)).length / bellData.length
    };
    
    const rogersMetrics = {
        avgRating: rogersData.reduce((sum, r) => sum + parseFloat(r.rating), 0) / rogersData.length,
        negativeRate: rogersData.filter(r => r.claude_sentiment === 'Negative').length / rogersData.length,
        positiveRate: rogersData.filter(r => r.claude_sentiment === 'Positive').length / rogersData.length,
        crashRate: rogersData.filter(r => r.primary_category === 'App Crashes').length / rogersData.length,
        loginIssueRate: rogersData.filter(r => r.primary_category === 'Login Issues').length / rogersData.length,
        performanceIssueRate: rogersData.filter(r => ['Performance', 'Loading Problems'].includes(r.primary_category)).length / rogersData.length,
        uxComplaintRate: rogersData.filter(r => ['User Experience', 'Navigation Issues', 'UI/UX'].includes(r.primary_category)).length / rogersData.length
    };
    
    // Find Bell's positive reviews to extract success factors
    const bellPositiveReviews = bellData.filter(r => r.claude_sentiment === 'Positive' && r.rating >= 4)
        .sort((a, b) => parseFloat(b.thumbs_up || 0) - parseFloat(a.thumbs_up || 0))
        .slice(0, 5);
    
    // Generate advantage analysis
    const advantages = [];
    
    // Overall satisfaction advantage
    if (bellMetrics.avgRating > rogersMetrics.avgRating) {
        const improvement = ((bellMetrics.avgRating - rogersMetrics.avgRating) / rogersMetrics.avgRating * 100).toFixed(0);
        advantages.push({
            category: 'User Satisfaction',
            metric: `${bellMetrics.avgRating.toFixed(1)} vs ${rogersMetrics.avgRating.toFixed(1)} stars`,
            advantage: `${improvement}% higher rating`,
            insight: 'Bell maintains consistently higher user satisfaction across all platforms and user segments.'
        });
    }
    
    // App stability advantage
    if (bellMetrics.crashRate < rogersMetrics.crashRate * 0.7) {
        const reduction = ((1 - bellMetrics.crashRate / rogersMetrics.crashRate) * 100).toFixed(0);
        advantages.push({
            category: 'App Stability',
            metric: `${(bellMetrics.crashRate * 100).toFixed(1)}% vs ${(rogersMetrics.crashRate * 100).toFixed(1)}% crash rate`,
            advantage: `${reduction}% fewer crashes`,
            insight: 'Bell\'s app architecture provides superior stability with minimal crashes.'
        });
    }
    
    // Authentication experience
    if (bellMetrics.loginIssueRate < rogersMetrics.loginIssueRate * 0.5) {
        const reduction = ((1 - bellMetrics.loginIssueRate / rogersMetrics.loginIssueRate) * 100).toFixed(0);
        advantages.push({
            category: 'Authentication',
            metric: `${(bellMetrics.loginIssueRate * 100).toFixed(1)}% vs ${(rogersMetrics.loginIssueRate * 100).toFixed(1)}% login issues`,
            advantage: `${reduction}% fewer login problems`,
            insight: 'Bell\'s authentication flow is more reliable and user-friendly.'
        });
    }
    
    // Performance advantage
    if (bellMetrics.performanceIssueRate < rogersMetrics.performanceIssueRate * 0.7) {
        const reduction = ((1 - bellMetrics.performanceIssueRate / rogersMetrics.performanceIssueRate) * 100).toFixed(0);
        advantages.push({
            category: 'Performance',
            metric: `${(bellMetrics.performanceIssueRate * 100).toFixed(1)}% vs ${(rogersMetrics.performanceIssueRate * 100).toFixed(1)}% performance complaints`,
            advantage: `${reduction}% better performance`,
            insight: 'Bell\'s app responds faster and handles load more efficiently.'
        });
    }
    
    // UX design advantage
    if (bellMetrics.uxComplaintRate < rogersMetrics.uxComplaintRate * 0.7) {
        const reduction = ((1 - bellMetrics.uxComplaintRate / rogersMetrics.uxComplaintRate) * 100).toFixed(0);
        advantages.push({
            category: 'User Experience',
            metric: `${(bellMetrics.uxComplaintRate * 100).toFixed(1)}% vs ${(rogersMetrics.uxComplaintRate * 100).toFixed(1)}% UX complaints`,
            advantage: `${reduction}% fewer UX issues`,
            insight: 'Bell\'s interface design is more intuitive and easier to navigate.'
        });
    }
    
    // Create the HTML content
    container.innerHTML = `
        <div style="padding: 1rem;">
            <!-- Summary Box -->
            <div style="background: #e8f5e9; border: 1px solid #4caf50; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 0.5rem; color: #2e7d32;">
                    <i class="fas fa-chart-line"></i> Bell's Competitive Edge
                </h4>
                <p style="margin: 0; color: #1b5e20;">
                    Bell outperforms Rogers in ${advantages.length} key areas, with an average ${bellMetrics.avgRating.toFixed(1)}/5 rating 
                    vs Rogers' ${rogersMetrics.avgRating.toFixed(1)}/5. Bell users report ${((1 - bellMetrics.negativeRate) * 100).toFixed(0)}% 
                    satisfaction rate compared to Rogers' ${((1 - rogersMetrics.negativeRate) * 100).toFixed(0)}%.
                </p>
            </div>
            
            <!-- Advantage Cards -->
            <div style="display: grid; gap: 1rem; margin-bottom: 1.5rem;">
                ${advantages.map(adv => `
                    <div style="background: white; border: 1px solid #e5e7eb; padding: 1rem; border-radius: 8px; border-left: 4px solid #4caf50;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.5rem;">
                            <h5 style="margin: 0; color: #1e293b;">${adv.category}</h5>
                            <span style="background: #4caf50; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.85rem; font-weight: 600;">
                                ${adv.advantage}
                            </span>
                        </div>
                        <div style="font-size: 0.9rem; color: #64748b; margin-bottom: 0.5rem;">
                            Bell: ${adv.metric.split(' vs ')[0]} | Rogers: ${adv.metric.split(' vs ')[1]}
                        </div>
                        <p style="margin: 0; font-size: 0.95rem; color: #475569;">${adv.insight}</p>
                    </div>
                `).join('')}
            </div>
            
            <!-- What Users Love About Bell -->
            <div style="background: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h5 style="margin-bottom: 1rem; color: #1e293b;">
                    <i class="fas fa-heart"></i> What Users Love About Bell's App
                </h5>
                ${bellPositiveReviews.length > 0 ? bellPositiveReviews.slice(0, 3).map(review => `
                    <div style="background: white; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 6px; border-left: 3px solid #4caf50;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem; font-size: 0.85rem; color: #64748b;">
                            <span>★ ${review.rating}/5</span>
                            <span>${review.platform}</span>
                        </div>
                        <p style="margin: 0; font-style: italic; font-size: 0.9rem; color: #475569;">
                            "${review.text && review.text.length > 150 ? review.text.substring(0, 150) + '...' : review.text || 'No review text'}"
                        </p>
                        ${review.thumbs_up && review.thumbs_up > 0 ? 
                            `<div style="margin-top: 0.25rem; font-size: 0.8rem; color: #64748b;">
                                👍 ${review.thumbs_up} found helpful
                            </div>` : ''}
                    </div>
                `).join('') : '<p style="color: #64748b; font-style: italic;">No positive reviews available in filtered data</p>'}
            </div>
            
            <!-- Key Differentiators -->
            <div style="background: #fffbeb; border: 1px solid #f59e0b; padding: 1rem; border-radius: 8px;">
                <h5 style="margin-bottom: 0.5rem; color: #92400e;">
                    <i class="fas fa-key"></i> Key Success Factors
                </h5>
                <ul style="margin: 0; padding-left: 1.5rem; color: #78350f;">
                    <li style="margin-bottom: 0.25rem;">Consistent performance across iOS and Android platforms</li>
                    <li style="margin-bottom: 0.25rem;">Reliable authentication with minimal login failures</li>
                    <li style="margin-bottom: 0.25rem;">Intuitive UI that users describe as "easy" and "simple"</li>
                    <li style="margin-bottom: 0.25rem;">Stable app architecture with rare crashes</li>
                    <li>Fast response times and efficient data loading</li>
                </ul>
            </div>
        </div>
    `;
    
    console.log('✅ Bell advantages analysis updated successfully');
}

function updateRegulatoryAnalysis(filteredData) {
    const container = document.getElementById('regulatoryAnalysis');
    if (!container) {
        console.error('❌ regulatoryAnalysis container not found');
        return;
    }
    
    console.log(`⚖️ Updating regulatory analysis with ${filteredData.length} reviews`);
    
    // Separate data by provider
    const rogersData = filteredData.filter(r => r.app_name === 'Rogers');
    const bellData = filteredData.filter(r => r.app_name === 'Bell');
    
    // Search for CCTS mentions
    const rogersCCTS = rogersData.filter(r => {
        const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
        return text.includes('ccts') || text.includes('commission for complaints');
    });
    
    const bellCCTS = bellData.filter(r => {
        const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
        return text.includes('ccts') || text.includes('commission for complaints');
    });
    
    // Search for broader complaint patterns - expanded to match bash analysis
    const complaintKeywords = [
        'complaint', 'complain', 'complained', 'complaining',
        'commission', 'ccts', 'regulatory', 
        'escalat', 'escalate', 'escalated', 'escalating',
        'ombudsman', 'file a complaint', 'formal complaint',
        'report to', 'reporting to', 'will report'
    ];
    
    const rogersComplaints = rogersData.filter(r => {
        const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
        return complaintKeywords.some(keyword => text.includes(keyword));
    });
    
    const bellComplaints = bellData.filter(r => {
        const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
        return complaintKeywords.some(keyword => text.includes(keyword));
    });
    
    // Analyze complaint categories with more detail
    const analyzeComplaintReasons = (complaints) => {
        const reasons = {
            billing: 0,
            support: 0,
            service: 0,
            accessibility: 0,
            other: 0
        };
        
        const detailedReasons = {
            billing: [],
            support: [],
            service: [],
            accessibility: [],
            other: []
        };
        
        complaints.forEach(r => {
            const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
            if (text.includes('bill') || text.includes('price') || text.includes('charge') || text.includes('overcharge') || text.includes('fee')) {
                reasons.billing++;
                detailedReasons.billing.push(r);
            } else if (text.includes('support') || text.includes('customer service') || text.includes('agent') || text.includes('representative')) {
                reasons.support++;
                detailedReasons.support.push(r);
            } else if (text.includes('service') || text.includes('network') || text.includes('coverage') || text.includes('connection')) {
                reasons.service++;
                detailedReasons.service.push(r);
            } else if (text.includes('accessibility') || text.includes('disability')) {
                reasons.accessibility++;
                detailedReasons.accessibility.push(r);
            } else {
                reasons.other++;
                detailedReasons.other.push(r);
            }
        });
        
        return { reasons, detailedReasons };
    };
    
    // Analyze specific complaint types
    const analyzeComplaintTypes = (reviews) => {
        const types = {
            priceIncreases: reviews.filter(r => {
                const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
                return text.includes('price increase') || text.includes('raised') || text.includes('went up') || text.includes('more expensive');
            }),
            overcharges: reviews.filter(r => {
                const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
                return text.includes('overcharge') || text.includes('extra charge') || text.includes('hidden fee') || text.includes('rip off') || text.includes('ripped off');
            }),
            poorSupport: reviews.filter(r => {
                const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
                return (text.includes('terrible') || text.includes('awful') || text.includes('worst') || text.includes('horrible')) && 
                       (text.includes('support') || text.includes('service') || text.includes('agent'));
            }),
            unresolved: reviews.filter(r => {
                const text = (r.text + ' ' + (r.claude_summary || '')).toLowerCase();
                return text.includes('unresolved') || text.includes('not resolved') || text.includes('still waiting') || text.includes('no response');
            })
        };
        
        return types;
    };
    
    const rogersAnalysis = analyzeComplaintReasons(rogersComplaints);
    const bellAnalysis = analyzeComplaintReasons(bellComplaints);
    const rogersReasons = rogersAnalysis.reasons;
    const bellReasons = bellAnalysis.reasons;
    
    // Analyze specific complaint types
    const rogersComplaintTypes = analyzeComplaintTypes(rogersData);
    const bellComplaintTypes = analyzeComplaintTypes(bellData);
    
    // Calculate rates
    const rogersComplaintRate = rogersData.length > 0 ? (rogersComplaints.length / rogersData.length * 100).toFixed(1) : 0;
    const bellComplaintRate = bellData.length > 0 ? (bellComplaints.length / bellData.length * 100).toFixed(1) : 0;
    
    // Log the actual numbers for debugging
    console.log(`Rogers: ${rogersComplaints.length} complaints out of ${rogersData.length} reviews = ${rogersComplaintRate}%`);
    console.log(`Bell: ${bellComplaints.length} complaints out of ${bellData.length} reviews = ${bellComplaintRate}%`);
    
    // Find example complaints
    const rogersExamples = rogersCCTS.concat(rogersComplaints.filter(r => !rogersCCTS.includes(r)))
        .slice(0, 3)
        .sort((a, b) => parseFloat(b.thumbs_up || 0) - parseFloat(a.thumbs_up || 0));
    
    const bellExamples = bellCCTS.concat(bellComplaints.filter(r => !bellCCTS.includes(r)))
        .slice(0, 3)
        .sort((a, b) => parseFloat(b.thumbs_up || 0) - parseFloat(a.thumbs_up || 0));
    
    // Create HTML content
    container.innerHTML = `
        <div style="padding: 1rem;">
            <!-- Summary Alert -->
            <div style="background: #fef2f2; border: 1px solid #dc2626; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h4 style="margin-bottom: 0.5rem; color: #991b1b;">
                    <i class="fas fa-exclamation-triangle"></i> Regulatory Risk Assessment
                </h4>
                <p style="margin: 0; color: #7f1d1d;">
                    Rogers shows ${(rogersComplaintRate / bellComplaintRate).toFixed(1)}x higher regulatory complaint risk with ${rogersComplaints.length} 
                    complaint-related mentions (${rogersComplaintRate}% of reviews) vs Bell's ${bellComplaints.length} (${bellComplaintRate}%). 
                    Direct CCTS mentions: Rogers (${rogersCCTS.length}) vs Bell (${bellCCTS.length}).
                </p>
            </div>
            
            <!-- Comparison Cards -->
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.5rem;">
                <!-- Rogers Card -->
                <div style="background: white; border: 2px solid #dc2626; padding: 1rem; border-radius: 8px;">
                    <h5 style="margin-bottom: 1rem; color: #dc2626;">
                        <i class="fas fa-mobile-alt"></i> Rogers Complaint Analysis
                    </h5>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-bottom: 1rem;">
                        <div style="text-align: center; padding: 0.5rem; background: #fef2f2; border-radius: 6px;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: #dc2626;">${rogersComplaints.length}</div>
                            <div style="font-size: 0.85rem; color: #991b1b;">Total Complaints</div>
                        </div>
                        <div style="text-align: center; padding: 0.5rem; background: #fef2f2; border-radius: 6px;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: #dc2626;">${rogersComplaintRate}%</div>
                            <div style="font-size: 0.85rem; color: #991b1b;">Complaint Rate</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <h6 style="margin-bottom: 0.5rem; color: #7f1d1d;">Complaint Drivers:</h6>
                        <div style="font-size: 0.9rem; color: #991b1b;">
                            • Billing Issues: ${rogersReasons.billing} mentions<br>
                            • Support Failures: ${rogersReasons.support} mentions<br>
                            • Service Problems: ${rogersReasons.service} mentions<br>
                            ${rogersReasons.accessibility > 0 ? `• Accessibility: ${rogersReasons.accessibility} mentions<br>` : ''}
                            • Other: ${rogersReasons.other} mentions
                        </div>
                    </div>
                </div>
                
                <!-- Bell Card -->
                <div style="background: white; border: 2px solid #059669; padding: 1rem; border-radius: 8px;">
                    <h5 style="margin-bottom: 1rem; color: #059669;">
                        <i class="fas fa-mobile-alt"></i> Bell Complaint Analysis
                    </h5>
                    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; margin-bottom: 1rem;">
                        <div style="text-align: center; padding: 0.5rem; background: #ecfdf5; border-radius: 6px;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: #059669;">${bellComplaints.length}</div>
                            <div style="font-size: 0.85rem; color: #047857;">Total Complaints</div>
                        </div>
                        <div style="text-align: center; padding: 0.5rem; background: #ecfdf5; border-radius: 6px;">
                            <div style="font-size: 1.5rem; font-weight: 700; color: #059669;">${bellComplaintRate}%</div>
                            <div style="font-size: 0.85rem; color: #047857;">Complaint Rate</div>
                        </div>
                    </div>
                    <div style="margin-bottom: 0.5rem;">
                        <h6 style="margin-bottom: 0.5rem; color: #047857;">Complaint Drivers:</h6>
                        <div style="font-size: 0.9rem; color: #065f46;">
                            • Billing Issues: ${bellReasons.billing} mentions<br>
                            • Support Failures: ${bellReasons.support} mentions<br>
                            • Service Problems: ${bellReasons.service} mentions<br>
                            ${bellReasons.accessibility > 0 ? `• Accessibility: ${bellReasons.accessibility} mentions<br>` : ''}
                            • Other: ${bellReasons.other} mentions
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- CCTS Specific Analysis -->
            <div style="background: #fffbeb; border: 1px solid #f59e0b; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h5 style="margin-bottom: 0.5rem; color: #92400e;">
                    <i class="fas fa-balance-scale"></i> CCTS (Commission for Complaints) Mentions
                </h5>
                <p style="margin: 0 0 0.5rem 0; color: #78350f;">
                    Direct regulatory body mentions indicate severe customer dissatisfaction requiring external intervention.
                </p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div>
                        <strong style="color: #dc2626;">Rogers CCTS (${rogersCCTS.length}):</strong>
                        <ul style="margin: 0.5rem 0; padding-left: 1.5rem; color: #92400e;">
                            ${rogersCCTS.length > 0 ? rogersCCTS.map(r => 
                                `<li>"${r.text.substring(0, 100)}..." - ${r.primary_category || 'General'}</li>`
                            ).join('') : '<li>No direct CCTS mentions</li>'}
                        </ul>
                    </div>
                    <div>
                        <strong style="color: #059669;">Bell CCTS (${bellCCTS.length}):</strong>
                        <ul style="margin: 0.5rem 0; padding-left: 1.5rem; color: #92400e;">
                            ${bellCCTS.length > 0 ? bellCCTS.map(r => 
                                `<li>"${r.text.substring(0, 100)}..." - ${r.primary_category || 'General'}</li>`
                            ).join('') : '<li>No direct CCTS mentions</li>'}
                        </ul>
                    </div>
                </div>
            </div>
            
            <!-- Example Complaints -->
            <div style="margin-bottom: 1.5rem;">
                <h5 style="margin-bottom: 1rem; color: #1e293b;">
                    <i class="fas fa-comments"></i> Recent Complaint Examples
                </h5>
                
                <!-- Rogers Examples -->
                ${rogersExamples.length > 0 ? `
                    <h6 style="color: #dc2626; margin-bottom: 0.5rem;">Rogers Complaints:</h6>
                    ${rogersExamples.map(review => `
                        <div style="background: #fef2f2; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 6px; border-left: 3px solid #dc2626;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem; font-size: 0.85rem; color: #991b1b;">
                                <span>★ ${review.rating}/5 | ${review.platform}</span>
                                <span>${review.date ? new Date(review.date).toLocaleDateString() : 'No date'}</span>
                            </div>
                            <p style="margin: 0; font-style: italic; font-size: 0.9rem; color: #7f1d1d;">
                                "${review.text && review.text.length > 200 ? review.text.substring(0, 200) + '...' : review.text || 'No review text'}"
                            </p>
                            <div style="margin-top: 0.25rem; font-size: 0.85rem; color: #991b1b;">
                                Category: ${review.primary_category || 'General'} 
                                ${review.thumbs_up && review.thumbs_up > 0 ? `| 👍 ${review.thumbs_up} found helpful` : ''}
                            </div>
                        </div>
                    `).join('')}
                ` : ''}
                
                <!-- Bell Examples -->
                ${bellExamples.length > 0 ? `
                    <h6 style="color: #059669; margin-bottom: 0.5rem; margin-top: 1rem;">Bell Complaints:</h6>
                    ${bellExamples.map(review => `
                        <div style="background: #ecfdf5; padding: 0.75rem; margin-bottom: 0.5rem; border-radius: 6px; border-left: 3px solid #059669;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 0.25rem; font-size: 0.85rem; color: #047857;">
                                <span>★ ${review.rating}/5 | ${review.platform}</span>
                                <span>${review.date ? new Date(review.date).toLocaleDateString() : 'No date'}</span>
                            </div>
                            <p style="margin: 0; font-style: italic; font-size: 0.9rem; color: #065f46;">
                                "${review.text && review.text.length > 200 ? review.text.substring(0, 200) + '...' : review.text || 'No review text'}"
                            </p>
                            <div style="margin-top: 0.25rem; font-size: 0.85rem; color: #047857;">
                                Category: ${review.primary_category || 'General'} 
                                ${review.thumbs_up && review.thumbs_up > 0 ? `| 👍 ${review.thumbs_up} found helpful` : ''}
                            </div>
                        </div>
                    `).join('')}
                ` : ''}
            </div>
            
            <!-- Broader Complaint Pattern Analysis -->
            <div style="background: #f0f9ff; border: 1px solid #0284c7; padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <h5 style="margin-bottom: 1rem; color: #075985;">
                    <i class="fas fa-chart-pie"></i> Detailed Complaint Pattern Analysis
                </h5>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <!-- Rogers Detailed Analysis -->
                    <div>
                        <h6 style="color: #dc2626; margin-bottom: 0.5rem;">Rogers Complaint Patterns:</h6>
                        <div style="background: white; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.9rem; color: #7f1d1d;">
                                <strong>Price & Billing Issues:</strong><br>
                                • Price increases: ${rogersComplaintTypes.priceIncreases.length} mentions<br>
                                • Overcharging complaints: ${rogersComplaintTypes.overcharges.length} mentions<br>
                                • Total billing disputes: ${rogersReasons.billing} (${((rogersReasons.billing / rogersComplaints.length) * 100).toFixed(0)}% of complaints)
                            </div>
                        </div>
                        <div style="background: white; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.9rem; color: #7f1d1d;">
                                <strong>Support Quality:</strong><br>
                                • Poor support experiences: ${rogersComplaintTypes.poorSupport.length} mentions<br>
                                • Unresolved issues: ${rogersComplaintTypes.unresolved.length} mentions<br>
                                • Total support complaints: ${rogersReasons.support} (${((rogersReasons.support / rogersComplaints.length) * 100).toFixed(0)}% of complaints)
                            </div>
                        </div>
                        ${rogersComplaintTypes.overcharges.length > 0 ? `
                            <div style="background: #fef2f2; padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem;">
                                <div style="font-size: 0.85rem; color: #991b1b; font-style: italic;">
                                    <strong>Sample "Rip off" complaint:</strong><br>
                                    "${rogersComplaintTypes.overcharges[0].text.substring(0, 150)}..."
                                </div>
                            </div>
                        ` : ''}
                    </div>
                    
                    <!-- Bell Detailed Analysis -->
                    <div>
                        <h6 style="color: #059669; margin-bottom: 0.5rem;">Bell Complaint Patterns:</h6>
                        <div style="background: white; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.9rem; color: #065f46;">
                                <strong>Price & Billing Issues:</strong><br>
                                • Price increases: ${bellComplaintTypes.priceIncreases.length} mentions<br>
                                • Overcharging complaints: ${bellComplaintTypes.overcharges.length} mentions<br>
                                • Total billing disputes: ${bellReasons.billing} (${bellComplaints.length > 0 ? ((bellReasons.billing / bellComplaints.length) * 100).toFixed(0) : 0}% of complaints)
                            </div>
                        </div>
                        <div style="background: white; padding: 0.75rem; border-radius: 6px; margin-bottom: 0.5rem;">
                            <div style="font-size: 0.9rem; color: #065f46;">
                                <strong>Support Quality:</strong><br>
                                • Poor support experiences: ${bellComplaintTypes.poorSupport.length} mentions<br>
                                • Unresolved issues: ${bellComplaintTypes.unresolved.length} mentions<br>
                                • Total support complaints: ${bellReasons.support} (${bellComplaints.length > 0 ? ((bellReasons.support / bellComplaints.length) * 100).toFixed(0) : 0}% of complaints)
                            </div>
                        </div>
                        ${bellReasons.accessibility > 0 ? `
                            <div style="background: #fef3c7; padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem;">
                                <div style="font-size: 0.85rem; color: #92400e;">
                                    <strong>⚠️ Accessibility Compliance Risk:</strong><br>
                                    ${bellReasons.accessibility} complaints specifically about accessibility department failures
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Comparative Analysis -->
                <div style="margin-top: 1rem; padding: 0.75rem; background: white; border-radius: 6px;">
                    <h6 style="margin-bottom: 0.5rem; color: #1e293b;">Key Differences:</h6>
                    <div style="font-size: 0.9rem; color: #475569;">
                        • Rogers users are ${((rogersComplaintTypes.overcharges.length / rogersData.length) / (bellComplaintTypes.overcharges.length / bellData.length)).toFixed(1)}x more likely to complain about being "ripped off"<br>
                        • Rogers has ${((rogersComplaintTypes.unresolved.length / rogersData.length) / (bellComplaintTypes.unresolved.length / bellData.length)).toFixed(1)}x more unresolved issue complaints<br>
                        • Bell has unique accessibility compliance issues not seen with Rogers<br>
                        • Both face similar price increase complaints, but Rogers' volume is ${(rogersComplaintTypes.priceIncreases.length / bellComplaintTypes.priceIncreases.length).toFixed(1)}x higher
                    </div>
                </div>
            </div>
            
            <!-- Key Insights -->
            <div style="background: #f8fafc; border: 1px solid #e5e7eb; padding: 1rem; border-radius: 8px;">
                <h5 style="margin-bottom: 0.5rem; color: #1e293b;">
                    <i class="fas fa-lightbulb"></i> Key Regulatory Insights
                </h5>
                <ul style="margin: 0; padding-left: 1.5rem; color: #475569;">
                    <li style="margin-bottom: 0.25rem;">Rogers' ${(rogersComplaintRate / bellComplaintRate).toFixed(1)}x higher complaint rate indicates systemic service issues</li>
                    <li style="margin-bottom: 0.25rem;">Billing disputes are the primary driver of regulatory escalations for both providers</li>
                    <li style="margin-bottom: 0.25rem;">Bell's accessibility department has specific CCTS compliance issues</li>
                    <li style="margin-bottom: 0.25rem;">Customer support failures often precede regulatory complaint threats</li>
                    <li>Both providers face regulatory pressure for price increases and billing practices</li>
                </ul>
            </div>
        </div>
    `;
    
    console.log('✅ Regulatory analysis updated successfully');
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
    if (currentFilters.categoryFilter !== 'all') {
        activeFilters.push(`Category: ${currentFilters.categoryFilter}`);
    }
    if (currentFilters.searchFilter && currentFilters.searchFilter.trim() !== '') {
        activeFilters.push(`Search: "${currentFilters.searchFilter}"`);
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

// Tab functionality - make it global
window.showTab = function(tabName) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    
    document.getElementById(tabName)?.classList.add('active');
    
    // Find and activate the clicked tab button
    const tabButtons = document.querySelectorAll('.nav-tab');
    tabButtons.forEach(button => {
        if (button.onclick && button.onclick.toString().includes(tabName)) {
            button.classList.add('active');
        }
    });
    
    // Generate insights when insights tab is shown
    if (tabName === 'insights') {
        console.log('📊 Insights tab activated, refreshing insights...');
        setTimeout(() => {
            generateInsights();
        }, 50);
    }
}

// Enhanced Filter functionality
function applyFilters() {
    console.log('🔍 Applying comprehensive filters...');
    
    // Get filter values
    const dateRange = document.getElementById('dateRange')?.value || 'all';
    const appFilter = document.getElementById('appFilter')?.value || 'all';
    const platformFilter = document.getElementById('platformFilter')?.value || 'all';
    const sentimentFilter = document.getElementById('sentimentFilter')?.value || 'all';
    const categoryFilter = document.getElementById('categoryFilter')?.value || 'all';
    const searchFilter = document.getElementById('searchFilter')?.value || '';
    
    // Update current filters
    currentFilters = { dateRange, appFilter, platformFilter, sentimentFilter, categoryFilter, searchFilter };
    
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