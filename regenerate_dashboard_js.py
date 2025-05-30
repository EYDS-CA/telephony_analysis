#!/usr/bin/env python3
"""
Dashboard JS Regeneration Script
Regenerates dashboard_complete_enhanced.js and dashboard_final.js with filtered data.
"""

import pandas as pd
import json
from datetime import datetime
from collections import Counter

def calculate_metrics(df):
    """Calculate all dashboard metrics from filtered dataset"""
    
    metrics = {}
    
    # Basic counts
    metrics['total_reviews'] = len(df)
    metrics['rogers_reviews'] = len(df[df['app_name'] == 'Rogers'])
    metrics['bell_reviews'] = len(df[df['app_name'] == 'Bell'])
    metrics['average_rating'] = round(df['rating'].mean(), 2)
    
    # Sentiment distribution
    sentiment_counts = df['claude_sentiment'].value_counts()
    metrics['sentiment_distribution'] = sentiment_counts.to_dict()
    
    # Rating distribution
    rating_counts = df['rating'].value_counts().sort_index()
    metrics['rating_distribution'] = rating_counts.to_dict()
    
    # Platform distribution
    platform_counts = df['platform'].value_counts()
    metrics['platform_distribution'] = platform_counts.to_dict()
    
    # Category distribution
    category_counts = df['primary_category'].value_counts()
    metrics['final_category_distribution'] = category_counts.to_dict()
    
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
    
    # Sentiment by platform and app
    sentiment_by_platform = {}
    for platform in ['Android', 'iOS']:
        platform_data = df[df['platform'] == platform]
        sentiment_by_platform[platform.lower()] = {
            'total': len(platform_data),
            'sentiment': platform_data['claude_sentiment'].value_counts().to_dict()
        }
    
    metrics['sentiment_by_platform'] = sentiment_by_platform
    
    # Sentiment by app
    sentiment_by_app = {}
    for app in ['Rogers', 'Bell']:
        app_data = df[df['app_name'] == app]
        sentiment_by_app[app.lower()] = {
            'total': len(app_data),
            'sentiment': app_data['claude_sentiment'].value_counts().to_dict()
        }
    
    metrics['sentiment_by_app'] = sentiment_by_app
    
    return metrics

def prepare_reviews_data(df):
    """Prepare reviews data for the dashboard"""
    
    # Convert dataframe to list of dictionaries for JavaScript
    reviews = []
    for _, row in df.iterrows():
        review = {
            'id': row['review_id'],
            'content': row['text'],  # Use 'text' column as main content
            'rating': int(row['rating']),
            'author': row['author'],
            'date': row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else '',
            'app': row['app_name'],
            'platform': row['platform'],
            'sentiment': row['claude_sentiment'],
            'sentiment_score': float(row['claude_sentiment_score']) if pd.notna(row['claude_sentiment_score']) else 0,
            'category': row['primary_category'],
            'summary': row['claude_summary'] if pd.notna(row['claude_summary']) else ''
        }
        reviews.append(review)
    
    return reviews

def generate_dashboard_js(metrics, reviews):
    """Generate the dashboard JavaScript file"""
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    js_content = f"""// Complete Enhanced Dashboard Data with Technical and Service Analysis
// Generated automatically on {timestamp}
// Filtered dataset: {metrics['total_reviews']:,} reviews (2020-2025, 99.6% current)

const COMPLETE_DASHBOARD_DATA = {{
    "summary": {{
        "total_reviews": {metrics['total_reviews']},
        "rogers_reviews": {metrics['rogers_reviews']},
        "bell_reviews": {metrics['bell_reviews']},
        "average_rating": {metrics['average_rating']},
        "sentiment_distribution": {json.dumps(metrics['sentiment_distribution'], indent=12)},
        "rating_distribution": {json.dumps(metrics['rating_distribution'], indent=12)},
        "platform_distribution": {json.dumps(metrics['platform_distribution'], indent=12)},
        "final_category_distribution": {json.dumps(metrics['final_category_distribution'], indent=12)},
        "platform_stats": {json.dumps(metrics['platform_stats'], indent=12)},
        "sentiment_by_platform": {json.dumps(metrics['sentiment_by_platform'], indent=12)},
        "sentiment_by_app": {json.dumps(metrics['sentiment_by_app'], indent=12)}
    }},
    "reviews": {json.dumps(reviews, indent=4)}
}};

// Export for global access
if (typeof window !== 'undefined') {{
    window.COMPLETE_DASHBOARD_DATA = COMPLETE_DASHBOARD_DATA;
    window.DASHBOARD_DATA = COMPLETE_DASHBOARD_DATA; // Legacy compatibility
}}

// For Node.js environments
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = COMPLETE_DASHBOARD_DATA;
}}
"""
    
    return js_content

def main():
    print("🔄 Loading filtered dataset...")
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"📊 Processing {len(df):,} filtered reviews...")
    
    # Calculate metrics
    print("🧮 Calculating dashboard metrics...")
    metrics = calculate_metrics(df)
    
    # Prepare reviews data
    print("📝 Preparing reviews data...")
    reviews = prepare_reviews_data(df)
    
    # Generate JavaScript content
    print("🔧 Generating JavaScript files...")
    js_content = generate_dashboard_js(metrics, reviews)
    
    # Write dashboard_complete_enhanced.js
    enhanced_file = 'html_dashboard/dashboard_complete_enhanced.js'
    with open(enhanced_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ Updated: {enhanced_file}")
    
    # Write dashboard_final.js (same content for consistency)
    final_file = 'html_dashboard/dashboard_final.js'
    with open(final_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ Updated: {final_file}")
    
    # Print summary
    print(f"""
🎯 Dashboard JS files regenerated successfully!

📊 Key metrics:
   • Total reviews: {metrics['total_reviews']:,}
   • Rogers: {metrics['rogers_reviews']:,}
   • Bell: {metrics['bell_reviews']:,}
   • Android: {metrics['platform_distribution'].get('Android', 0):,}
   • iOS: {metrics['platform_distribution'].get('iOS', 0):,}
   • Average rating: {metrics['average_rating']}
   • Data currency: 99.6% (2020-2025)
   
🔄 Ready for dashboard testing!
""")

if __name__ == "__main__":
    main()