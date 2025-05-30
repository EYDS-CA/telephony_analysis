#!/usr/bin/env python3
"""
Quick iOS Comparison Tool
Shows immediate comparison between current iOS data and what's available online
"""

import pandas as pd
import requests
import json
from datetime import datetime

def get_app_store_preview(app_id, app_name):
    """Get current app store information"""
    print(f"\n🔍 Checking {app_name} on App Store...")
    
    # Try to get current app info
    url = f"https://itunes.apple.com/ca/rss/customerreviews/page=1/id={app_id}/sortby=mostrecent/json"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'feed' in data:
            # Get app info from first entry
            if 'entry' in data['feed'] and len(data['feed']['entry']) > 0:
                app_info = data['feed']['entry'][0]
                
                # Get recent reviews (skip first entry which is app info)
                recent_reviews = data['feed']['entry'][1:6] if len(data['feed']['entry']) > 1 else []
                
                print(f"   ✅ Found app data")
                print(f"   📱 App: {app_info.get('im:name', {}).get('label', 'Unknown')}")
                
                if recent_reviews:
                    print(f"   📝 Sample of {len(recent_reviews)} most recent reviews:")
                    for i, review in enumerate(recent_reviews, 1):
                        rating = review.get('im:rating', {}).get('label', '?')
                        date = review.get('updated', {}).get('label', 'Unknown date')
                        author = review.get('author', {}).get('name', {}).get('label', 'Anonymous')
                        
                        # Parse date
                        try:
                            parsed_date = pd.to_datetime(date).strftime('%Y-%m-%d')
                        except:
                            parsed_date = date
                        
                        print(f"      {i}. {rating}★ by {author} on {parsed_date}")
                
                return True
            
    except Exception as e:
        print(f"   ❌ Error accessing app store: {e}")
    
    return False

def analyze_existing_ios_data(df):
    """Analyze existing iOS data in dataset"""
    print("\n📊 Current iOS Data Analysis")
    print("=" * 50)
    
    ios_df = df[df['platform'] == 'iOS']
    
    print(f"\n📈 Overview:")
    print(f"   Total iOS reviews: {len(ios_df):,}")
    print(f"   Percentage of dataset: {len(ios_df)/len(df)*100:.1f}%")
    
    # Check dates
    ios_with_dates = ios_df[ios_df['date'].notna()]
    print(f"   Reviews with dates: {len(ios_with_dates):,}")
    
    if len(ios_with_dates) > 0:
        # Try to parse dates
        try:
            ios_df['parsed_date'] = pd.to_datetime(ios_df['date'], errors='coerce')
            valid_dates = ios_df[ios_df['parsed_date'].notna()]
            
            if len(valid_dates) > 0:
                print(f"   Date range: {valid_dates['parsed_date'].min()} to {valid_dates['parsed_date'].max()}")
        except:
            print("   ⚠️  Unable to parse dates")
    else:
        print("   ⚠️  NO DATES FOUND IN iOS DATA")
    
    # App breakdown
    print(f"\n📱 By App:")
    for app in ['Bell', 'Rogers']:
        app_count = len(ios_df[ios_df['app_name'] == app])
        print(f"   {app}: {app_count:,} reviews")
    
    # Rating distribution
    print(f"\n⭐ Rating Distribution (iOS):")
    rating_dist = ios_df['rating'].value_counts().sort_index()
    for rating, count in rating_dist.items():
        percentage = count/len(ios_df)*100
        print(f"   {int(rating)}★: {count:,} ({percentage:.1f}%)")
    
    if len(ios_df) > 0:
        print(f"\n   Average rating: {ios_df['rating'].mean():.2f}")

def main():
    """Main comparison function"""
    print("🚀 Quick iOS Data Comparison")
    print("=" * 60)
    
    # Load existing data
    print("📂 Loading existing dataset...")
    try:
        df = pd.read_csv('/Users/amirshayegh/Developer/temp/review_analysis/telecom_app_reviews_analyzed.csv')
        print(f"   ✅ Loaded {len(df):,} total reviews")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Analyze existing iOS data
    analyze_existing_ios_data(df)
    
    # Check current app store status
    print("\n🌐 Current App Store Status")
    print("=" * 50)
    
    apps = [
        {'app_id': '850549838', 'name': 'Bell MyBell'},
        {'app_id': '337618972', 'name': 'Rogers MyRogers'}
    ]
    
    for app in apps:
        get_app_store_preview(app['app_id'], app['name'])
    
    # Recommendations
    print("\n💡 Recommendations")
    print("=" * 50)
    
    ios_df = df[df['platform'] == 'iOS']
    ios_percentage = len(ios_df)/len(df)*100
    
    if ios_percentage < 10:
        print("🔴 CRITICAL: iOS data is underrepresented")
        print(f"   Current: {ios_percentage:.1f}% (Expected: 10-15%)")
        print("   Action: Run ios_rescrape_and_compare.py to get fresh iOS data")
    
    ios_with_dates = ios_df[ios_df['date'].notna() & (ios_df['date'] != '')]
    if len(ios_with_dates) == 0:
        print("\n🔴 CRITICAL: iOS reviews missing date information")
        print("   This prevents freshness analysis")
        print("   Action: Re-scrape iOS data with proper date extraction")
    
    print("\n📋 To refresh iOS data:")
    print("   1. Run: python ios_rescrape_and_compare.py")
    print("   2. Review the comparison results")
    print("   3. Merge new data if satisfied")
    print("   4. Re-run sentiment analysis on new reviews")

if __name__ == "__main__":
    main()