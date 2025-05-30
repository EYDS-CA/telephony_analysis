#!/usr/bin/env python3
"""
Complete Dashboard Update Script
1. Regenerates dashboard JS files with enhanced categories
2. Updates review tab data
3. Prepares accuracy verification for all reports
"""

import pandas as pd
import json
from datetime import datetime
from collections import Counter

def calculate_enhanced_metrics(df):
    """Calculate comprehensive metrics from enhanced dataset"""
    
    metrics = {}
    
    # Basic counts
    metrics['total_reviews'] = len(df)
    metrics['rogers_reviews'] = len(df[df['app_name'] == 'Rogers'])
    metrics['bell_reviews'] = len(df[df['app_name'] == 'Bell'])
    metrics['average_rating'] = round(df['rating'].mean(), 2)
    
    # Enhanced sentiment distribution (using claude_sentiment)
    sentiment_counts = df['claude_sentiment'].value_counts()
    metrics['sentiment_distribution'] = sentiment_counts.to_dict()
    
    # Rating distribution
    rating_counts = df['rating'].value_counts().sort_index()
    metrics['rating_distribution'] = {str(k): v for k, v in rating_counts.items()}
    
    # Platform distribution  
    platform_counts = df['platform'].value_counts()
    metrics['platform_distribution'] = platform_counts.to_dict()
    
    # ENHANCED category distribution (new categories)
    enhanced_category_counts = df['enhanced_category'].value_counts()
    metrics['enhanced_category_distribution'] = enhanced_category_counts.to_dict()
    
    # Platform stats by app
    platform_stats = {}
    for app in ['Rogers', 'Bell']:
        app_data = df[df['app_name'] == app]
        platform_stats[app.lower()] = {
            'android': len(app_data[app_data['platform'] == 'Android']),
            'ios': len(app_data[app_data['platform'] == 'iOS']),
            'total': len(app_data)
        }
    metrics['platform_stats'] = platform_stats
    
    # Enhanced category by provider
    category_by_provider = {}
    for app in ['Rogers', 'Bell']:
        app_data = df[df['app_name'] == app]
        category_by_provider[app.lower()] = {
            'total': len(app_data),
            'categories': app_data['enhanced_category'].value_counts().to_dict()
        }
    metrics['enhanced_category_by_provider'] = category_by_provider
    
    # Sentiment by platform and app
    sentiment_by_platform = {}
    for platform in ['Android', 'iOS']:
        platform_data = df[df['platform'] == platform]
        sentiment_by_platform[platform.lower()] = {
            'total': len(platform_data),
            'sentiment': platform_data['claude_sentiment'].value_counts().to_dict()
        }
    metrics['sentiment_by_platform'] = sentiment_by_platform
    
    sentiment_by_app = {}
    for app in ['Rogers', 'Bell']:
        app_data = df[df['app_name'] == app]
        sentiment_by_app[app.lower()] = {
            'total': len(app_data),
            'sentiment': app_data['claude_sentiment'].value_counts().to_dict()
        }
    metrics['sentiment_by_app'] = sentiment_by_app
    
    return metrics

def prepare_enhanced_reviews_data(df):
    """Prepare reviews data with enhanced categories for dashboard"""
    
    reviews = []
    for _, row in df.iterrows():
        review = {
            'id': row['review_id'],
            'content': row['text'] if pd.notna(row['text']) else '',
            'rating': int(row['rating']),
            'author': row['author'] if pd.notna(row['author']) else 'Anonymous',
            'date': row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else '',
            'app': row['app_name'],
            'platform': row['platform'],
            'sentiment': row['claude_sentiment'] if pd.notna(row['claude_sentiment']) else 'Neutral',
            'sentiment_score': float(row['claude_sentiment_score']) if pd.notna(row['claude_sentiment_score']) else 0,
            'category': row['enhanced_category'],  # Using enhanced categories
            'summary': row['claude_summary'] if pd.notna(row['claude_summary']) else ''
        }
        reviews.append(review)
    
    return reviews

def generate_enhanced_dashboard_js(metrics, reviews):
    """Generate dashboard JavaScript with enhanced categories"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    js_content = f"""// Enhanced Dashboard Data with Complete Re-categorization
// Generated: {timestamp}
// Dataset: {metrics['total_reviews']:,} reviews with enhanced categories
// Enhanced from generic categories to 28 specific actionable categories

const ENHANCED_DASHBOARD_DATA = {{
    "summary": {{
        "total_reviews": {metrics['total_reviews']},
        "rogers_reviews": {metrics['rogers_reviews']},
        "bell_reviews": {metrics['bell_reviews']},
        "average_rating": {metrics['average_rating']},
        "sentiment_distribution": {json.dumps(metrics['sentiment_distribution'], indent=12)},
        "rating_distribution": {json.dumps(metrics['rating_distribution'], indent=12)},
        "platform_distribution": {json.dumps(metrics['platform_distribution'], indent=12)},
        "enhanced_category_distribution": {json.dumps(metrics['enhanced_category_distribution'], indent=12)},
        "platform_stats": {json.dumps(metrics['platform_stats'], indent=12)},
        "enhanced_category_by_provider": {json.dumps(metrics['enhanced_category_by_provider'], indent=12)},
        "sentiment_by_platform": {json.dumps(metrics['sentiment_by_platform'], indent=12)},
        "sentiment_by_app": {json.dumps(metrics['sentiment_by_app'], indent=12)}
    }},
    "reviews": {json.dumps(reviews, indent=4)}
}};

// Legacy compatibility - map enhanced categories to old structure
const DASHBOARD_DATA = {{
    "summary": {{
        "total_reviews": {metrics['total_reviews']},
        "rogers_reviews": {metrics['rogers_reviews']},
        "bell_reviews": {metrics['bell_reviews']},
        "average_rating": {metrics['average_rating']},
        "sentiment_distribution": {json.dumps(metrics['sentiment_distribution'], indent=12)},
        "rating_distribution": {json.dumps(metrics['rating_distribution'], indent=12)},
        "platform_distribution": {json.dumps(metrics['platform_distribution'], indent=12)},
        "final_category_distribution": {json.dumps(metrics['enhanced_category_distribution'], indent=12)},
        "platform_stats": {json.dumps(metrics['platform_stats'], indent=12)},
        "sentiment_by_platform": {json.dumps(metrics['sentiment_by_platform'], indent=12)},
        "sentiment_by_app": {json.dumps(metrics['sentiment_by_app'], indent=12)}
    }},
    "reviews": {json.dumps(reviews, indent=4)}
}};

// Export for global access
if (typeof window !== 'undefined') {{
    window.ENHANCED_DASHBOARD_DATA = ENHANCED_DASHBOARD_DATA;
    window.DASHBOARD_DATA = DASHBOARD_DATA; // Legacy compatibility
    window.COMPLETE_DASHBOARD_DATA = ENHANCED_DASHBOARD_DATA; // Alternative name
}}

// For Node.js environments
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = ENHANCED_DASHBOARD_DATA;
}}
"""
    
    return js_content

def generate_accuracy_report(df):
    """Generate accuracy verification report for all content"""
    
    report = f"""# Dashboard Accuracy Verification Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Dataset Summary
- **Total Reviews**: {len(df):,}
- **Rogers Reviews**: {len(df[df['app_name'] == 'Rogers']):,}
- **Bell Reviews**: {len(df[df['app_name'] == 'Bell']):,}
- **Android Reviews**: {len(df[df['platform'] == 'Android']):,}
- **iOS Reviews**: {len(df[df['platform'] == 'iOS']):,}
- **Average Rating**: {df['rating'].mean():.2f}
- **Date Range**: {df['date'].min()} to {df['date'].max()}

## Enhanced Categories ({len(df['enhanced_category'].value_counts())} total)
"""
    
    # Enhanced category breakdown
    enhanced_cats = df['enhanced_category'].value_counts()
    for category, count in enhanced_cats.items():
        pct = count/len(df)*100
        report += f"- **{category}**: {count:,} ({pct:.1f}%)\n"
    
    # Sentiment breakdown
    sentiment_dist = df['claude_sentiment'].value_counts()
    report += f"\n## Sentiment Distribution\n"
    for sentiment, count in sentiment_dist.items():
        pct = count/len(df)*100
        report += f"- **{sentiment}**: {count:,} ({pct:.1f}%)\n"
    
    # Platform performance comparison
    report += f"\n## Platform Performance\n"
    for platform in ['Android', 'iOS']:
        platform_data = df[df['platform'] == platform]
        avg_rating = platform_data['rating'].mean()
        negative_pct = len(platform_data[platform_data['claude_sentiment'] == 'Negative'])/len(platform_data)*100
        report += f"- **{platform}**: {len(platform_data):,} reviews, {avg_rating:.2f} avg rating, {negative_pct:.1f}% negative\n"
    
    # Provider comparison
    report += f"\n## Provider Performance\n"
    for provider in ['Rogers', 'Bell']:
        provider_data = df[df['app_name'] == provider]
        avg_rating = provider_data['rating'].mean()
        negative_pct = len(provider_data[provider_data['claude_sentiment'] == 'Negative'])/len(provider_data)*100
        report += f"- **{provider}**: {len(provider_data):,} reviews, {avg_rating:.2f} avg rating, {negative_pct:.1f}% negative\n"
    
    # Key insights for verification
    report += f"""
## Key Insights for Dashboard Text Verification

### Critical Numbers to Update:
1. **Total Reviews**: {len(df):,} (was 12,785 in old version)
2. **Rogers Reviews**: {len(df[df['app_name'] == 'Rogers']):,} (was 9,038)  
3. **Bell Reviews**: {len(df[df['app_name'] == 'Bell']):,} (was 3,747)
4. **Average Rating**: {df['rating'].mean():.2f} (was 2.64)
5. **Data Currency**: 99.6% (2020-2025 data)

### Enhanced Categories Added:
- Performance (app performance merged): {enhanced_cats.get('Performance', 0):,}
- UX Praise: {enhanced_cats.get('UX Praise', 0):,}
- UX Complaints: {enhanced_cats.get('UX Complaints', 0):,}
- Brand Loyalty: {enhanced_cats.get('Brand Loyalty', 0):,}
- General Dissatisfaction: {enhanced_cats.get('General Dissatisfaction', 0):,}

### Reports Needing Text Updates:
1. Executive Summary - Update total reviews, provider counts
2. CX Assessment Report - Update methodology description  
3. Research Methodology - Update data processing description
4. Key Metrics Reference - Update all numbers
5. Dashboard header - Update review counts and methodology

### Search for These Outdated Numbers:
- "12,785" or "12,893" → {len(df):,}
- "9,038" → {len(df[df['app_name'] == 'Rogers']):,}
- "3,747" → {len(df[df['app_name'] == 'Bell']):,}
- "2.64" → {df['rating'].mean():.2f}
"""
    
    return report

def main():
    """Complete dashboard update process"""
    
    print("🔄 COMPLETE DASHBOARD UPDATE")
    print("=" * 50)
    
    # Load enhanced dataset
    print("📊 Loading enhanced dataset...")
    df = pd.read_csv('Data/recategorized_analysis_final_20250529_125620.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"   Total reviews: {len(df):,}")
    print(f"   Enhanced categories: {len(df['enhanced_category'].value_counts())}")
    
    # Calculate enhanced metrics
    print("🧮 Calculating enhanced metrics...")
    metrics = calculate_enhanced_metrics(df)
    
    # Prepare enhanced reviews data
    print("📝 Preparing enhanced reviews data...")
    reviews = prepare_enhanced_reviews_data(df)
    
    # Generate enhanced JavaScript files
    print("🔧 Generating enhanced dashboard JS files...")
    js_content = generate_enhanced_dashboard_js(metrics, reviews)
    
    # Update dashboard files
    enhanced_files = [
        'html_dashboard/dashboard_complete_enhanced.js',
        'html_dashboard/dashboard_final.js'
    ]
    
    for file_path in enhanced_files:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Updated: {file_path}")
    
    # Generate accuracy verification report
    print("📋 Generating accuracy verification report...")
    accuracy_report = generate_accuracy_report(df)
    
    report_file = f'dashboard_accuracy_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(accuracy_report)
    print(f"✅ Accuracy report: {report_file}")
    
    # Summary
    print(f"""
🎯 DASHBOARD UPDATE COMPLETE!

📊 Enhanced Metrics Summary:
   • Total reviews: {metrics['total_reviews']:,}
   • Rogers: {metrics['rogers_reviews']:,}
   • Bell: {metrics['bell_reviews']:,}
   • Enhanced categories: {len(metrics['enhanced_category_distribution'])}
   • Average rating: {metrics['average_rating']}

📈 Top Enhanced Categories:
""")
    
    # Show top categories
    for category, count in list(metrics['enhanced_category_distribution'].items())[:10]:
        pct = count/metrics['total_reviews']*100
        print(f"   • {category}: {count:,} ({pct:.1f}%)")
    
    print(f"""
✅ Files Updated:
   • Dashboard JS files regenerated
   • Reviews tab data enhanced
   • Accuracy report generated

🔄 Next Steps:
   1. Test dashboard functionality
   2. Verify charts display correctly
   3. Check Reviews tab has enhanced categories
   4. Review accuracy report for text updates needed
   5. Update all HTML reports with new numbers

📋 Accuracy Report: {report_file}
   Contains all numbers that need updating in reports
""")

if __name__ == "__main__":
    main()