#!/usr/bin/env python3
"""
Update dashboard data files to use the filtered, current telecom app reviews dataset.
"""

import pandas as pd
import json
import random
from datetime import datetime

def clean_value(val, default=''):
    """Clean values to prevent JSON serialization issues"""
    if pd.isna(val) or val is None:
        return default
    return str(val)

def update_dashboard_data():
    print("🔄 Loading filtered telecom app reviews dataset...")
    
    # Load the filtered dataset
    df = pd.read_csv('telecom_app_reviews_filtered_current.csv')
    print(f"📊 Loaded {len(df):,} filtered reviews")
    
    # Clean and prepare data
    df = df.copy()
    
    # Ensure required columns exist and clean them
    required_columns = ['app_name', 'platform', 'rating', 'date', 'primary_category', 'text', 
                       'claude_sentiment', 'claude_sentiment_score', 'author']
    
    for col in required_columns:
        if col not in df.columns:
            df[col] = ''
        df[col] = df[col].apply(lambda x: clean_value(x))
    
    # Convert date to string format for JSON
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    df['date'] = df['date'].fillna('')
    
    # Ensure rating is numeric
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce').fillna(0)
    
    print(f"\n📋 Platform distribution:")
    print(f"   - Android: {len(df[df['platform'] == 'Android']):,} reviews")
    print(f"   - iOS: {len(df[df['platform'] == 'iOS']):,} reviews")
    
    print(f"\n📋 Provider distribution:")
    for provider in df['app_name'].unique():
        count = len(df[df['app_name'] == provider])
        print(f"   - {provider}: {count:,} reviews")
    
    # Create balanced sample for dashboard (1000 reviews)
    # Maintain proportional representation but ensure good mix
    dashboard_data = []
    
    # Sample by provider and platform to maintain balance
    for provider in ['Rogers', 'Bell']:
        provider_data = df[df['app_name'] == provider]
        
        for platform in ['Android', 'iOS']:
            platform_data = provider_data[provider_data['platform'] == platform]
            
            if len(platform_data) > 0:
                # Calculate sample size (aim for ~250 per provider, split between platforms)
                if platform == 'Android':
                    sample_size = min(200, len(platform_data))  # More Android since there's more data
                else:
                    sample_size = min(50, len(platform_data))   # Fewer iOS since there's less data
                
                sample = platform_data.sample(n=sample_size, random_state=42)
                dashboard_data.append(sample)
                
                print(f"   - Sampled {len(sample):,} {provider} {platform} reviews")
    
    # Combine all samples
    dashboard_df = pd.concat(dashboard_data, ignore_index=True)
    print(f"\n📊 Dashboard dataset: {len(dashboard_df):,} reviews")
    
    # Convert to dashboard format
    dashboard_reviews = []
    
    for _, row in dashboard_df.iterrows():
        # Safe conversion for sentiment score
        try:
            sentiment_score = float(row['claude_sentiment_score']) if pd.notna(row['claude_sentiment_score']) and str(row['claude_sentiment_score']).strip() != '' else 0
        except (ValueError, TypeError):
            sentiment_score = 0
            
        # Safe conversion for rating
        try:
            rating = float(row['rating']) if pd.notna(row['rating']) and str(row['rating']).strip() != '' else 0
        except (ValueError, TypeError):
            rating = 0
        
        review = {
            'provider': clean_value(row['app_name']),
            'platform': clean_value(row['platform']),
            'rating': rating,
            'date': clean_value(row['date']),
            'category': clean_value(row['primary_category']),
            'review': clean_value(row['text']),
            'sentiment': clean_value(row['claude_sentiment']),
            'sentiment_score': sentiment_score,
            'author': clean_value(row['author'])
        }
        dashboard_reviews.append(review)
    
    # Sort by date (newest first)
    dashboard_reviews.sort(key=lambda x: x['date'] if x['date'] else '0000-00-00', reverse=True)
    
    # Generate analytics data
    analytics_data = generate_analytics(df)
    
    # Create the JavaScript file
    js_content = f'''// Dashboard data generated from filtered telecom app reviews
// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Source: telecom_app_reviews_filtered_current.csv ({len(df):,} reviews)
// Dashboard sample: {len(dashboard_reviews):,} reviews

window.DASHBOARD_DATA = {{
    reviews: {json.dumps(dashboard_reviews, indent=2)},
    analytics: {json.dumps(analytics_data, indent=2)},
    metadata: {{
        total_reviews: {len(df)},
        dashboard_sample: {len(dashboard_reviews)},
        last_updated: "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        data_period: "2020-2025 (filtered for currency)",
        platforms: {json.dumps(list(df['platform'].unique()))},
        providers: {json.dumps(list(df['app_name'].unique()))}
    }}
}};

// Legacy support
const telecomReviews = window.DASHBOARD_DATA.reviews;
'''
    
    # Save to dashboard files
    dashboard_files = [
        'html_dashboard/dashboard_complete_enhanced.js',
        'html_dashboard/dashboard_final.js'
    ]
    
    for file_path in dashboard_files:
        with open(file_path, 'w') as f:
            f.write(js_content)
        print(f"💾 Updated: {file_path}")
    
    print(f"\n✅ Dashboard data updated with filtered dataset!")
    return dashboard_df

def generate_analytics(df):
    """Generate analytics data for the dashboard"""
    
    analytics = {}
    
    # Overall sentiment distribution
    sentiment_dist = df['claude_sentiment'].value_counts().to_dict()
    analytics['sentiment_distribution'] = sentiment_dist
    
    # Platform breakdown
    platform_dist = df['platform'].value_counts().to_dict()
    analytics['platform_distribution'] = platform_dist
    
    # Provider breakdown
    provider_dist = df['app_name'].value_counts().to_dict()
    analytics['provider_distribution'] = provider_dist
    
    # Rating distribution
    rating_dist = df['rating'].value_counts().sort_index().to_dict()
    analytics['rating_distribution'] = {str(k): v for k, v in rating_dist.items()}
    
    # Category breakdown (top 10)
    category_dist = df['primary_category'].value_counts().head(10).to_dict()
    analytics['top_categories'] = category_dist
    
    # Date range
    df_with_dates = df.dropna(subset=['date'])
    if len(df_with_dates) > 0:
        df_with_dates['date'] = pd.to_datetime(df_with_dates['date'], errors='coerce')
        date_range = {
            'min_date': df_with_dates['date'].min().strftime('%Y-%m-%d'),
            'max_date': df_with_dates['date'].max().strftime('%Y-%m-%d'),
            'total_with_dates': len(df_with_dates)
        }
        analytics['date_range'] = date_range
    
    return analytics

if __name__ == "__main__":
    dashboard_data = update_dashboard_data()
    print(f"\n🎯 Ready to view updated dashboard with current, relevant data!")