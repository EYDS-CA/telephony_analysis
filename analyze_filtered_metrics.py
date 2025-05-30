#!/usr/bin/env python3

import pandas as pd
import json
from datetime import datetime

def analyze_filtered_dataset():
    """Analyze the filtered dataset to generate accurate metrics for all HTML reports"""
    
    # Load the filtered dataset
    df = pd.read_csv('telecom_app_reviews_filtered_current.csv')
    
    print("=== FILTERED DATASET ANALYSIS ===")
    print(f"Total reviews: {len(df):,}")
    
    # Platform breakdown
    platform_counts = df['platform'].value_counts()
    print(f"\nPlatform breakdown:")
    for platform, count in platform_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {platform}: {count:,} ({percentage:.1f}%)")
    
    # App/Provider breakdown  
    app_counts = df['app_name'].value_counts()
    print(f"\nApp/Provider breakdown:")
    for app, count in app_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {app}: {count:,} ({percentage:.1f}%)")
    
    # Date range analysis
    df['date'] = pd.to_datetime(df['date'])
    print(f"\nDate range:")
    print(f"  Earliest: {df['date'].min().strftime('%Y-%m-%d')}")
    print(f"  Latest: {df['date'].max().strftime('%Y-%m-%d')}")
    
    # Year breakdown
    df['year'] = df['date'].dt.year
    year_counts = df['year'].value_counts().sort_index()
    print(f"\nYear breakdown:")
    for year, count in year_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {year}: {count:,} ({percentage:.1f}%)")
    
    # Data currency calculation (2020-2025)
    current_data = df[df['year'] >= 2020]
    data_currency = (len(current_data) / len(df)) * 100
    print(f"\nData currency (2020-2025): {data_currency:.1f}%")
    
    # Rating analysis
    print(f"\nRating analysis:")
    avg_rating = df['rating'].mean()
    print(f"  Average rating: {avg_rating:.2f}")
    
    rating_counts = df['rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  {rating} stars: {count:,} ({percentage:.1f}%)")
    
    # Sentiment analysis
    if 'claude_sentiment' in df.columns:
        sentiment_counts = df['claude_sentiment'].value_counts()
        print(f"\nSentiment breakdown:")
        for sentiment, count in sentiment_counts.items():
            percentage = (count / len(df)) * 100
            print(f"  {sentiment}: {count:,} ({percentage:.1f}%)")
    
    # Issue categories analysis
    if 'primary_category' in df.columns:
        category_counts = df['primary_category'].value_counts()
        print(f"\nTop 10 Issue Categories:")
        for i, (category, count) in enumerate(category_counts.head(10).items()):
            percentage = (count / len(df)) * 100
            print(f"  {i+1}. {category}: {count:,} ({percentage:.1f}%)")
    
    # Generate metrics dictionary for use in updates
    metrics = {
        'total_reviews': len(df),
        'android_reviews': int(platform_counts.get('Android', 0)),
        'ios_reviews': int(platform_counts.get('iOS', 0)),
        'rogers_reviews': int(app_counts.get('Rogers', 0)),
        'bell_reviews': int(app_counts.get('Bell', 0)),
        'average_rating': round(avg_rating, 2),
        'data_currency': round(data_currency, 1),
        'date_range_start': df['date'].min().strftime('%Y-%m-%d'),
        'date_range_end': df['date'].max().strftime('%Y-%m-%d'),
        'android_percentage': round((platform_counts.get('Android', 0) / len(df)) * 100, 1),
        'ios_percentage': round((platform_counts.get('iOS', 0) / len(df)) * 100, 1),
        'rogers_percentage': round((app_counts.get('Rogers', 0) / len(df)) * 100, 1),
        'bell_percentage': round((app_counts.get('Bell', 0) / len(df)) * 100, 1)
    }
    
    # Add sentiment metrics if available
    if 'claude_sentiment' in df.columns:
        for sentiment, count in sentiment_counts.items():
            metrics[f'{sentiment.lower()}_reviews'] = int(count)
            metrics[f'{sentiment.lower()}_percentage'] = round((count / len(df)) * 100, 1)
    
    # Save metrics to JSON for easy access
    with open('filtered_dataset_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n=== SUMMARY FOR REPORTS ===")
    print(f"Total Reviews: {metrics['total_reviews']:,}")
    print(f"Android: {metrics['android_reviews']:,} ({metrics['android_percentage']}%)")
    print(f"iOS: {metrics['ios_reviews']:,} ({metrics['ios_percentage']}%)")
    print(f"Rogers: {metrics['rogers_reviews']:,} ({metrics['rogers_percentage']}%)")
    print(f"Bell: {metrics['bell_reviews']:,} ({metrics['bell_percentage']}%)")
    print(f"Average Rating: {metrics['average_rating']}")
    print(f"Data Currency: {metrics['data_currency']}%")
    print(f"Date Range: {metrics['date_range_start']} to {metrics['date_range_end']}")
    
    return metrics

if __name__ == "__main__":
    metrics = analyze_filtered_dataset()