#!/usr/bin/env python3
"""
Update Dashboard Data Script
Regenerates dashboard_complete_enhanced.js with the updated dataset
"""
import pandas as pd
import json
from datetime import datetime

def load_and_process_data():
    """Load the updated CSV and process it for the dashboard"""
    print("📂 Loading updated dataset...")
    
    # Load the updated dataset
    df = pd.read_csv('telecom_app_reviews_updated_20250529_064556.csv')
    
    print(f"📊 Loaded {len(df):,} reviews")
    
    # Basic statistics
    total_reviews = len(df)
    rogers_reviews = len(df[df['app_name'].str.contains('rogers', case=False, na=False)])
    bell_reviews = len(df[df['app_name'].str.contains('bell', case=False, na=False)])
    
    # Calculate average rating
    avg_rating = df['rating'].mean()
    
    # Sentiment distribution (using claude_sentiment)
    sentiment_dist = df['claude_sentiment'].value_counts().to_dict()
    
    # Rating distribution
    rating_dist = df['rating'].value_counts().sort_index().to_dict()
    # Convert rating keys to strings for JSON compatibility
    rating_dist = {str(k): v for k, v in rating_dist.items()}
    
    # Platform distribution
    platform_dist = df['platform'].value_counts().to_dict()
    
    # Category distribution
    category_dist = df['primary_category'].value_counts().to_dict()
    
    # Date analysis
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    reviews_with_dates = df.dropna(subset=['date'])
    
    # Platform and date statistics
    platform_stats = {}
    for platform in df['platform'].unique():
        if pd.isna(platform):
            continue
        platform_data = df[df['platform'] == platform]
        platform_dates = platform_data['date'].dropna()
        
        platform_stats[platform] = {
            'total': len(platform_data),
            'with_dates': len(platform_dates),
            'date_coverage': len(platform_dates) / len(platform_data) * 100 if len(platform_data) > 0 else 0,
            'date_range': {
                'min': platform_dates.min().isoformat() if len(platform_dates) > 0 else None,
                'max': platform_dates.max().isoformat() if len(platform_dates) > 0 else None
            }
        }
    
    # Prepare reviews data for dashboard (get representative sample of both platforms)
    # Get up to 800 Android reviews and up to 200 iOS reviews for balanced representation
    android_reviews = df[df['platform'] == 'Android'].head(800)
    ios_reviews = df[df['platform'] == 'iOS'].head(200)
    
    # Combine and shuffle
    reviews_sample = pd.concat([android_reviews, ios_reviews], ignore_index=True)
    reviews_sample = reviews_sample.sample(frac=1, random_state=42).reset_index(drop=True)  # Shuffle
    reviews_sample['date'] = reviews_sample['date'].dt.strftime('%Y-%m-%d').fillna('')
    
    # Convert to list of dictionaries
    reviews_list = []
    for _, row in reviews_sample.iterrows():
        # Helper function to clean values
        def clean_value(val, default=''):
            if pd.isna(val) or val is None:
                return default
            return str(val)
        
        review_dict = {
            'provider': 'Rogers' if 'rogers' in clean_value(row.get('app_name', '')).lower() else 'Bell',
            'platform': clean_value(row.get('platform', 'Unknown')),
            'rating': int(row.get('rating', 0)) if pd.notna(row.get('rating')) else 0,
            'date': clean_value(row.get('date', '')),
            'sentiment': clean_value(row.get('claude_sentiment', 'Neutral')),
            'claude_sentiment': clean_value(row.get('claude_sentiment', 'Neutral')),  # For dashboard_final.js compatibility
            'category': clean_value(row.get('primary_category', 'General')),
            'primary_category': clean_value(row.get('primary_category', 'General')),  # For dashboard_final.js compatibility
            'content': clean_value(row.get('text', ''))[:200],  # Limit text length
            'text': clean_value(row.get('text', ''))[:200],  # For compatibility
            'app_name': clean_value(row.get('app_name', '')),
            'author': clean_value(row.get('author', '')),
            'title': clean_value(row.get('title', ''))
        }
        reviews_list.append(review_dict)
    
    # Build complete dashboard data structure
    dashboard_data = {
        'summary': {
            'total_reviews': total_reviews,
            'rogers_reviews': rogers_reviews,
            'bell_reviews': bell_reviews,
            'average_rating': round(avg_rating, 2),
            'sentiment_distribution': sentiment_dist,
            'rating_distribution': rating_dist,
            'platform_distribution': platform_dist,
            'final_category_distribution': category_dist,
            'platform_stats': platform_stats,
            'last_updated': datetime.now().isoformat()
        },
        'reviews': reviews_list,
        'all_reviews': reviews_list  # For compatibility
    }
    
    return dashboard_data

def generate_js_file(data):
    """Generate the JavaScript file with the data"""
    
    js_content = f"""// Complete Enhanced Dashboard Data with Technical and Service Analysis
// Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Updated with iOS date information and new reviews
// Total reviews: {data['summary']['total_reviews']:,}

const COMPLETE_DASHBOARD_DATA = {json.dumps(data, indent=4, default=str)};

// Make data available globally
if (typeof window !== 'undefined') {{
    window.COMPLETE_DASHBOARD_DATA = COMPLETE_DASHBOARD_DATA;
    window.dashboardData = COMPLETE_DASHBOARD_DATA;  // For dashboard.html compatibility
    window.DASHBOARD_DATA = COMPLETE_DASHBOARD_DATA; // For dashboard_final.js compatibility
}}

console.log('📊 Dashboard data loaded:', {{
    totalReviews: COMPLETE_DASHBOARD_DATA.summary.total_reviews,
    lastUpdated: COMPLETE_DASHBOARD_DATA.summary.last_updated,
    platforms: COMPLETE_DASHBOARD_DATA.summary.platform_distribution,
    dateRanges: COMPLETE_DASHBOARD_DATA.summary.platform_stats,
    reviewsCount: COMPLETE_DASHBOARD_DATA.reviews ? COMPLETE_DASHBOARD_DATA.reviews.length : 0
}});

// Ensure the dashboard initializes when this data is loaded
if (typeof window !== 'undefined' && window.initializeStandaloneMode) {{
    console.log('🔄 Auto-initializing dashboard with new data...');
    window.initializeStandaloneMode();
}} else if (typeof window !== 'undefined') {{
    // Set a flag to initialize when the dashboard is ready
    window.dashboardDataReady = true;
}}
"""
    
    return js_content

def main():
    """Main function to update dashboard data"""
    print("🚀 Updating Dashboard Data")
    print("=" * 50)
    
    try:
        # Load and process data
        dashboard_data = load_and_process_data()
        
        # Generate JavaScript file
        js_content = generate_js_file(dashboard_data)
        
        # Write to file
        output_file = 'html_dashboard/dashboard_complete_enhanced.js'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ Successfully updated {output_file}")
        print(f"📊 Dashboard now includes:")
        print(f"   • Total reviews: {dashboard_data['summary']['total_reviews']:,}")
        print(f"   • Rogers: {dashboard_data['summary']['rogers_reviews']:,}")
        print(f"   • Bell: {dashboard_data['summary']['bell_reviews']:,}")
        print(f"   • Avg rating: {dashboard_data['summary']['average_rating']}")
        
        # Platform statistics
        for platform, stats in dashboard_data['summary']['platform_stats'].items():
            print(f"   • {platform}: {stats['total']:,} reviews ({stats['date_coverage']:.1f}% with dates)")
            if stats['date_range']['min'] and stats['date_range']['max']:
                print(f"     Date range: {stats['date_range']['min']} to {stats['date_range']['max']}")
        
        print("🎉 Dashboard data update complete!")
        
    except Exception as e:
        print(f"❌ Error updating dashboard data: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())