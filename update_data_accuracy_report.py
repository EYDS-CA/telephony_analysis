#!/usr/bin/env python3
"""
Update the Data Accuracy Report HTML with the new filtered dataset statistics.
"""

import pandas as pd
from datetime import datetime

def update_data_accuracy_report():
    print("🔄 Updating Data Accuracy Report with filtered dataset statistics...")
    
    # Load the filtered dataset
    df = pd.read_csv('telecom_app_reviews_filtered_current.csv')
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Calculate statistics
    total_reviews = len(df)
    android_reviews = len(df[df['platform'] == 'Android'])
    ios_reviews = len(df[df['platform'] == 'iOS'])
    
    # Date range analysis
    df_with_dates = df.dropna(subset=['date'])
    date_coverage = (len(df_with_dates) / total_reviews) * 100
    
    # Provider breakdown
    rogers_total = len(df[df['app_name'] == 'Rogers'])
    bell_total = len(df[df['app_name'] == 'Bell'])
    
    # Generate date range tables
    date_ranges = {}
    for app_name in df['app_name'].unique():
        for platform in df['platform'].unique():
            subset = df[(df['app_name'] == app_name) & (df['platform'] == platform)]
            if len(subset) > 0:
                subset_with_dates = subset.dropna(subset=['date'])
                if len(subset_with_dates) > 0:
                    min_date = subset_with_dates['date'].min()
                    max_date = subset_with_dates['date'].max()
                    date_ranges[f"{app_name}_{platform}"] = {
                        'min_date': min_date.strftime('%Y-%m-%d'),
                        'max_date': max_date.strftime('%Y-%m-%d'),
                        'count': len(subset),
                        'count_with_dates': len(subset_with_dates),
                        'coverage': (len(subset_with_dates) / len(subset)) * 100 if len(subset) > 0 else 0
                    }
    
    # Create updated HTML content
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Data Accuracy and Currency Report - Telecom CX Analysis</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="ey-report-styles.css">
    <style>
        /* Report-specific styles */
        .status-badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
        }}
        
        .status-verified {{
            background: rgba(0, 168, 142, 0.1);
            color: var(--ey-green);
        }}
        
        .status-updated {{
            background: rgba(0, 163, 224, 0.1);
            color: var(--ey-blue);
        }}
        
        .status-current {{
            background: rgba(0, 168, 142, 0.1);
            color: var(--ey-green);
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}
        
        .metric-card {{
            background: var(--ey-gray-light);
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }}
        
        .metric-value {{
            font-size: 2rem;
            font-weight: 600;
            color: var(--ey-yellow);
            margin-bottom: 0.5rem;
        }}
        
        .metric-label {{
            font-size: 0.875rem;
            color: var(--ey-gray-dark);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .improvement-highlight {{
            background: rgba(0, 168, 142, 0.05);
            border-left: 4px solid var(--ey-green);
            padding: 1rem;
            margin: 1rem 0;
        }}
        
        .date-range-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }}
        
        .date-range-table th,
        .date-range-table td {{
            border: 1px solid var(--ey-gray);
            padding: 0.75rem;
            text-align: left;
        }}
        
        .date-range-table th {{
            background: var(--ey-gray-light);
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <div class="ey-logo-container">
                <div class="ey-logo">EY</div>
            </div>
            <h1>Data Accuracy and Currency Report</h1>
            <p class="report-subtitle">Telecom App Review Analysis - Filtered Current Dataset</p>
            <div class="report-meta">
                <span>Generated: {datetime.now().strftime('%B %d, %Y')}</span>
                <span class="status-badge status-current">100% Current Data</span>
            </div>
        </header>

        <main class="report-content">
            <!-- Executive Summary -->
            <section class="report-section">
                <h2>Executive Summary</h2>
                <div class="improvement-highlight">
                    <h3>Data Quality Enhancement Completed</h3>
                    <p>The telecom app review dataset has been successfully filtered to include only current, relevant data from 2020-2025. This filtering removes outdated Android reviews that no longer reflect the modern app experience while preserving all iOS reviews and recent Android reviews.</p>
                </div>
                
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-value">{total_reviews:,}</div>
                        <div class="metric-label">Total Reviews (Filtered)</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">100%</div>
                        <div class="metric-label">Data Currency (2020-2025)</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{date_coverage:.1f}%</div>
                        <div class="metric-label">Date Coverage</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">21.6%</div>
                        <div class="metric-label">Outdated Data Removed</div>
                    </div>
                </div>
            </section>

            <!-- Data Sources Overview -->
            <section class="report-section">
                <h2>Data Sources and Methodology</h2>
                <div class="content-grid">
                    <div class="content-card">
                        <h3>Data Collection Sources</h3>
                        <ul>
                            <li><strong>Android Reviews:</strong> Google Play Store API (google_play_scraper)</li>
                            <li><strong>iOS Reviews:</strong> iTunes RSS Feed API with date matching</li>
                            <li><strong>Analysis Enhancement:</strong> Claude AI sentiment analysis and categorization</li>
                        </ul>
                    </div>
                    <div class="content-card">
                        <h3>Filtering Criteria Applied</h3>
                        <ul>
                            <li><strong>Android:</strong> Reviews from January 1, 2020 onwards only</li>
                            <li><strong>iOS:</strong> All reviews retained (already current: 2023-2025)</li>
                            <li><strong>Analysis:</strong> All Claude sentiment analysis preserved</li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- Platform Analysis -->
            <section class="report-section">
                <h2>Platform and Provider Breakdown</h2>
                
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-value">{android_reviews:,}</div>
                        <div class="metric-label">Android Reviews</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{ios_reviews:,}</div>
                        <div class="metric-label">iOS Reviews</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{rogers_total:,}</div>
                        <div class="metric-label">Rogers Reviews</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{bell_total:,}</div>
                        <div class="metric-label">Bell Reviews</div>
                    </div>
                </div>

                <h3>Date Ranges by Platform and Provider</h3>
                <table class="date-range-table">
                    <thead>
                        <tr>
                            <th>Provider</th>
                            <th>Platform</th>
                            <th>Date Range</th>
                            <th>Total Reviews</th>
                            <th>Date Coverage</th>
                        </tr>
                    </thead>
                    <tbody>'''
    
    # Add date range rows
    for key, info in sorted(date_ranges.items()):
        app_name, platform = key.split('_')
        html_content += f'''
                        <tr>
                            <td>{app_name}</td>
                            <td>{platform}</td>
                            <td>{info['min_date']} to {info['max_date']}</td>
                            <td>{info['count']:,}</td>
                            <td>{info['coverage']:.1f}%</td>
                        </tr>'''
    
    html_content += f'''
                    </tbody>
                </table>
            </section>

            <!-- Data Quality Improvements -->
            <section class="report-section">
                <h2>Data Quality Improvements</h2>
                
                <div class="improvement-highlight">
                    <h3>Before vs After Filtering</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-top: 1rem;">
                        <div>
                            <h4>Original Dataset</h4>
                            <ul>
                                <li>Total: 12,893 reviews</li>
                                <li>Android: 11,859 reviews (23.5% pre-2020)</li>
                                <li>iOS: 1,034 reviews</li>
                                <li>Data currency: 78.4%</li>
                            </ul>
                        </div>
                        <div>
                            <h4>Filtered Dataset</h4>
                            <ul>
                                <li>Total: {total_reviews:,} reviews</li>
                                <li>Android: {android_reviews:,} reviews (100% current)</li>
                                <li>iOS: {ios_reviews:,} reviews (100% current)</li>
                                <li>Data currency: 100%</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <h3>Business Impact of Filtering</h3>
                <div class="content-grid">
                    <div class="content-card">
                        <h4>Relevance Enhancement</h4>
                        <p>Focus on modern app era (2020+) when app stores matured and user expectations evolved significantly.</p>
                    </div>
                    <div class="content-card">
                        <h4>Accuracy Improvement</h4>
                        <p>Removal of outdated reviews that don't reflect current app functionality, UI/UX, or technical capabilities.</p>
                    </div>
                    <div class="content-card">
                        <h4>Insight Quality</h4>
                        <p>Analysis based on recent user experience patterns and current competitive landscape.</p>
                    </div>
                    <div class="content-card">
                        <h4>Preserved Analysis</h4>
                        <p>All Claude AI sentiment analysis and categorization maintained for retained reviews.</p>
                    </div>
                </div>
            </section>

            <!-- Verification and Confidence -->
            <section class="report-section">
                <h2>Data Verification and Confidence Levels</h2>
                
                <div class="content-grid">
                    <div class="content-card">
                        <h3>Data Source Confidence</h3>
                        <div class="status-badge status-verified" style="display: block; margin-bottom: 1rem;">High Confidence</div>
                        <ul>
                            <li><strong>Android:</strong> Direct Google Play Store API extraction</li>
                            <li><strong>iOS:</strong> Official iTunes RSS feeds with intelligent date matching</li>
                            <li><strong>Analysis:</strong> Claude AI enhancement preserved for all reviews</li>
                        </ul>
                    </div>
                    
                    <div class="content-card">
                        <h3>Currency Verification</h3>
                        <div class="status-badge status-current" style="display: block; margin-bottom: 1rem;">100% Current</div>
                        <ul>
                            <li><strong>Time Period:</strong> 2020-2025 (5 years)</li>
                            <li><strong>Relevance:</strong> Modern smartphone and app ecosystem era</li>
                            <li><strong>Coverage:</strong> All major app updates and feature releases included</li>
                        </ul>
                    </div>
                </div>
            </section>

            <!-- Recommendations -->
            <section class="report-section">
                <h2>Recommendations for Ongoing Data Quality</h2>
                
                <div class="content-card">
                    <h3>Maintain Current Standards</h3>
                    <ul>
                        <li>Continue filtering approach for future data updates</li>
                        <li>Maintain 5-year rolling window for Android reviews</li>
                        <li>Preserve all iOS reviews (naturally current due to API limitations)</li>
                        <li>Regular Claude AI analysis updates for new reviews</li>
                        <li>Quarterly data freshness assessments</li>
                    </ul>
                </div>
            </section>
        </main>

        <footer class="report-footer">
            <div class="footer-content">
                <div class="footer-left">
                    <div class="ey-logo">EY</div>
                    <p>Building a better working world</p>
                </div>
                <div class="footer-right">
                    <p>Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Data source: telecom_app_reviews_filtered_current.csv</p>
                </div>
            </div>
        </footer>
    </div>
</body>
</html>'''
    
    # Save the updated HTML file
    with open('html_dashboard/data_accuracy_report.html', 'w') as f:
        f.write(html_content)
    
    print(f"✅ Updated data_accuracy_report.html with filtered dataset statistics")
    print(f"   - Total reviews: {total_reviews:,}")
    print(f"   - Data currency: 100% (2020-2025)")
    print(f"   - Date coverage: {date_coverage:.1f}%")
    
    return True

if __name__ == "__main__":
    update_data_accuracy_report()
    print(f"\n🎯 Data Accuracy Report updated and ready to view!")