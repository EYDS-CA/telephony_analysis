// Shared Navigation Component for CX Dashboard
window.SharedNavigation = {
    currentTab: 'insights',
    
    // Initialize navigation on page load
    init: function() {
        // Check URL parameters for tab state
        const urlParams = new URLSearchParams(window.location.search);
        const tabParam = urlParams.get('tab');
        if (tabParam) {
            this.currentTab = tabParam;
        }
        
        // Check if we're on a report page
        const currentPage = window.location.pathname.split('/').pop();
        if (this.isReportPage(currentPage)) {
            this.currentTab = 'reports';
        }
        
        this.render();
    },
    
    // Check if current page is a report
    isReportPage: function(pageName) {
        const reportPages = [
            'executive_summary.html',
            'rogers_cx_transformation_report.html',
            'cx_ux_assessment_report.html',
            'metrics_calculations_verification.html',
            'key_metrics_reference.html',
            'research_process_approach.html',
            'bell_smart_cx_report.html'
        ];
        return reportPages.includes(pageName);
    },
    
    // Render navigation HTML
    render: function() {
        const navHTML = `
        <!-- Navigation -->
        <nav class="nav-container">
            <div class="nav-tabs" style="max-width: 1400px; margin: 0 auto">
                <button class="nav-tab ${this.currentTab === 'insights' ? 'active' : ''}" 
                        onclick="SharedNavigation.navigateTo('insights')">
                    Executive Insights
                </button>
                <button class="nav-tab ${this.currentTab === 'analysis' ? 'active' : ''}" 
                        onclick="SharedNavigation.navigateTo('analysis')">
                    Reviews
                </button>
                <button class="nav-tab ${this.currentTab === 'report' ? 'active' : ''}" 
                        onclick="SharedNavigation.navigateTo('report')">
                    Strategic Report
                </button>
                <button class="nav-tab ${this.currentTab === 'methodology' ? 'active' : ''}" 
                        onclick="SharedNavigation.navigateTo('methodology')">
                    Research Methodology
                </button>
                <button class="nav-tab ${this.currentTab === 'reports' ? 'active' : ''}" 
                        onclick="SharedNavigation.navigateTo('reports')">
                    All Reports
                </button>
            </div>
        </nav>
        `;
        
        // Insert navigation after header if exists
        const header = document.querySelector('.header');
        if (header && !document.querySelector('.nav-container')) {
            header.insertAdjacentHTML('afterend', navHTML);
        }
    },
    
    // Navigate to tab or dashboard
    navigateTo: function(tab) {
        const currentPage = window.location.pathname.split('/').pop();
        
        // If we're on dashboard, just switch tabs
        if (currentPage === 'dashboard.html' || currentPage === '') {
            this.currentTab = tab;
            
            // Update URL without reload
            const url = new URL(window.location);
            url.searchParams.set('tab', tab);
            window.history.pushState({tab: tab}, '', url);
            
            // Call dashboard's showTab function if available
            if (typeof showTab === 'function') {
                // Update nav
                document.querySelectorAll('.nav-tab').forEach(navTab => {
                    navTab.classList.remove('active');
                });
                event.target.classList.add('active');
                
                // Update content
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });
                document.getElementById(tab).classList.add('active');
            }
        } else {
            // Navigate to dashboard with tab parameter
            window.location.href = `dashboard.html?tab=${tab}`;
        }
    }
};

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    SharedNavigation.init();
});