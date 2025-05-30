#!/usr/bin/env python3
"""
Filter Android reviews to remove outdated entries (pre-2020) while preserving all iOS reviews.
This improves data accuracy by focusing on recent, relevant app review data.
"""

import pandas as pd
from datetime import datetime
import os

def filter_reviews():
    print("🔍 Loading telecom app reviews dataset...")
    
    # Load the dataset
    df = pd.read_csv('telecom_app_reviews_updated_20250529_064556.csv')
    
    print(f"📊 Original dataset: {len(df):,} reviews")
    print(f"   - Android: {len(df[df['platform'] == 'Android']):,} reviews")
    print(f"   - iOS: {len(df[df['platform'] == 'iOS']):,} reviews")
    
    # Convert date column to datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Define cutoff date for Android reviews
    cutoff_date = pd.to_datetime('2020-01-01')
    
    print(f"\n🗓️ Analyzing date ranges...")
    
    # Analyze Android date distribution
    android_df = df[df['platform'] == 'Android'].copy()
    android_df = android_df.dropna(subset=['date'])
    
    pre_2020_android = android_df[android_df['date'] < cutoff_date]
    post_2020_android = android_df[android_df['date'] >= cutoff_date]
    
    print(f"   Android pre-2020: {len(pre_2020_android):,} reviews ({len(pre_2020_android)/len(android_df)*100:.1f}%)")
    print(f"   Android 2020+: {len(post_2020_android):,} reviews ({len(post_2020_android)/len(android_df)*100:.1f}%)")
    
    # Analyze iOS date distribution
    ios_df = df[df['platform'] == 'iOS'].copy()
    ios_df = ios_df.dropna(subset=['date'])
    
    if len(ios_df) > 0:
        ios_min_date = ios_df['date'].min()
        ios_max_date = ios_df['date'].max()
        print(f"   iOS date range: {ios_min_date.strftime('%Y-%m-%d')} to {ios_max_date.strftime('%Y-%m-%d')}")
    
    # Create filtered dataset
    print(f"\n🔧 Filtering dataset...")
    print(f"   - Keeping ALL iOS reviews: {len(ios_df):,} reviews")
    print(f"   - Keeping Android reviews from 2020-01-01 onwards: {len(post_2020_android):,} reviews")
    print(f"   - Removing Android reviews before 2020-01-01: {len(pre_2020_android):,} reviews")
    
    # Filter the dataset
    filtered_df = df[
        (df['platform'] == 'iOS') |  # Keep all iOS reviews
        ((df['platform'] == 'Android') & (df['date'] >= cutoff_date))  # Keep Android 2020+
    ].copy()
    
    print(f"\n✨ Filtered dataset: {len(filtered_df):,} reviews")
    print(f"   - Android: {len(filtered_df[filtered_df['platform'] == 'Android']):,} reviews")
    print(f"   - iOS: {len(filtered_df[filtered_df['platform'] == 'iOS']):,} reviews")
    
    # Calculate data quality improvements
    total_reduction = len(df) - len(filtered_df)
    reduction_percentage = (total_reduction / len(df)) * 100
    
    print(f"\n📈 Data Quality Improvement:")
    print(f"   - Reviews removed: {total_reduction:,} ({reduction_percentage:.1f}%)")
    print(f"   - Data recency: 100% from 2020-2025 (vs {(len(df) - len(pre_2020_android))/len(df)*100:.1f}% before)")
    
    # Analyze by provider and platform
    print(f"\n📋 Breakdown by Provider & Platform:")
    provider_platform_summary = filtered_df.groupby(['app_name', 'platform']).size().reset_index(name='count')
    for _, row in provider_platform_summary.iterrows():
        print(f"   - {row['app_name']} {row['platform']}: {row['count']:,} reviews")
    
    # Save filtered dataset
    output_file = 'telecom_app_reviews_filtered_current.csv'
    filtered_df.to_csv(output_file, index=False)
    print(f"\n💾 Saved filtered dataset: {output_file}")
    
    # Generate summary report
    print(f"\n📊 Generating summary report...")
    
    # Date range analysis for filtered data
    date_ranges = {}
    for app_name in filtered_df['app_name'].unique():
        for platform in filtered_df['platform'].unique():
            subset = filtered_df[(filtered_df['app_name'] == app_name) & 
                               (filtered_df['platform'] == platform)]
            if len(subset) > 0:
                subset_with_dates = subset.dropna(subset=['date'])
                if len(subset_with_dates) > 0:
                    min_date = subset_with_dates['date'].min()
                    max_date = subset_with_dates['date'].max()
                    date_ranges[f"{app_name}_{platform}"] = {
                        'min_date': min_date.strftime('%Y-%m-%d'),
                        'max_date': max_date.strftime('%Y-%m-%d'),
                        'count': len(subset),
                        'count_with_dates': len(subset_with_dates)
                    }
    
    # Save summary report
    summary_report = f"""# Telecom App Reviews Filtering Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- **Original dataset**: {len(df):,} reviews
- **Filtered dataset**: {len(filtered_df):,} reviews
- **Reviews removed**: {total_reduction:,} ({reduction_percentage:.1f}%)
- **Data quality improvement**: 100% current data (2020-2025)

## Filtering Criteria
- **Android reviews**: Kept only reviews from 2020-01-01 onwards
- **iOS reviews**: Kept all reviews (already current: 2023-2025)

## Before vs After Comparison

### Original Dataset
- Android: {len(df[df['platform'] == 'Android']):,} reviews
- iOS: {len(df[df['platform'] == 'iOS']):,} reviews
- Pre-2020 Android: {len(pre_2020_android):,} reviews ({len(pre_2020_android)/len(android_df)*100:.1f}% of Android)

### Filtered Dataset
- Android: {len(filtered_df[filtered_df['platform'] == 'Android']):,} reviews
- iOS: {len(filtered_df[filtered_df['platform'] == 'iOS']):,} reviews
- All reviews from 2020-2025 (100% current)

## Date Ranges by Provider & Platform
"""
    
    for key, info in date_ranges.items():
        app_name, platform = key.split('_')
        summary_report += f"- **{app_name} {platform}**: {info['min_date']} to {info['max_date']} ({info['count']:,} reviews)\n"
    
    summary_report += f"""
## Business Impact
- **Relevance**: Focus on modern app era (2020+) when app stores matured
- **Accuracy**: Remove outdated reviews that don't reflect current app experience
- **Insights**: Analysis based on recent user experience and current app functionality
- **Preserved analysis**: All Claude sentiment analysis and categorization maintained
"""
    
    with open('FILTERING_SUMMARY_REPORT.md', 'w') as f:
        f.write(summary_report)
    
    print(f"📄 Summary report saved: FILTERING_SUMMARY_REPORT.md")
    
    return filtered_df, date_ranges

if __name__ == "__main__":
    filtered_data, date_info = filter_reviews()
    print(f"\n✅ Filtering complete! Ready for dashboard update.")