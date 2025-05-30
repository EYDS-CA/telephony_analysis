#!/usr/bin/env python3
"""
Clean Data Filtering Script
Creates a single filtered dataset by removing pre-2020 Android reviews while keeping all iOS reviews.
This provides 100% current, relevant data for analysis.
"""

import pandas as pd
from datetime import datetime

def create_filtered_dataset():
    """Create filtered dataset with only current, relevant reviews"""
    
    print("🔄 Loading Data/analyzed_reviews.csv...")
    df = pd.read_csv('Data/analyzed_reviews.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    print(f"📊 Original dataset: {len(df):,} reviews")
    print(f"   Android: {len(df[df['platform'] == 'Android']):,}")
    print(f"   iOS: {len(df[df['platform'] == 'iOS']):,}")
    
    # Filter criteria:
    # 1. Keep ALL iOS reviews (they're already current: 2023-2025)
    # 2. Keep only Android reviews from 2020-01-01 onwards
    
    ios_reviews = df[df['platform'] == 'iOS']
    android_recent = df[
        (df['platform'] == 'Android') & 
        (df['date'] >= '2020-01-01')
    ]
    
    # Combine filtered data
    filtered_df = pd.concat([ios_reviews, android_recent], ignore_index=True)
    
    # Sort by date (most recent first)
    filtered_df = filtered_df.sort_values('date', ascending=False)
    
    print(f"\n📊 Filtered dataset: {len(filtered_df):,} reviews")
    print(f"   Android (2020+): {len(filtered_df[filtered_df['platform'] == 'Android']):,}")
    print(f"   iOS (all): {len(filtered_df[filtered_df['platform'] == 'iOS']):,}")
    
    # Show date range
    print(f"\n📅 Date range: {filtered_df['date'].min().strftime('%Y-%m-%d')} to {filtered_df['date'].max().strftime('%Y-%m-%d')}")
    
    # Calculate data currency
    total_reviews = len(filtered_df)
    recent_reviews = len(filtered_df[filtered_df['date'] >= '2020-01-01'])
    currency_percent = (recent_reviews / total_reviews) * 100
    print(f"📈 Data currency: {currency_percent:.1f}% (reviews from 2020+)")
    
    # Show provider breakdown
    provider_breakdown = filtered_df['app_name'].value_counts()
    print(f"\n🏢 Provider breakdown:")
    for provider, count in provider_breakdown.items():
        print(f"   {provider}: {count:,}")
    
    # Save filtered dataset
    output_file = 'Data/analyzed_reviews_filtered_clean.csv'
    filtered_df.to_csv(output_file, index=False)
    print(f"\n✅ Saved filtered dataset to: {output_file}")
    
    return filtered_df, {
        'total_reviews': len(filtered_df),
        'android_reviews': len(filtered_df[filtered_df['platform'] == 'Android']),
        'ios_reviews': len(filtered_df[filtered_df['platform'] == 'iOS']),
        'rogers_reviews': len(filtered_df[filtered_df['app_name'] == 'Rogers']),
        'bell_reviews': len(filtered_df[filtered_df['app_name'] == 'Bell']),
        'data_currency': currency_percent,
        'date_range': {
            'start': filtered_df['date'].min().strftime('%Y-%m-%d'),
            'end': filtered_df['date'].max().strftime('%Y-%m-%d')
        }
    }

if __name__ == "__main__":
    df, stats = create_filtered_dataset()
    print(f"\n🎯 Ready for dashboard regeneration with {stats['total_reviews']:,} clean, current reviews!")