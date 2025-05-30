#!/usr/bin/env python3
"""
iOS App Store Review Scraper
Refreshes iOS review data with proper date extraction
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import sys

def scrape_ios_reviews(app_id, app_name, country='ca', pages=10):
    """
    Scrape iOS App Store reviews using iTunes RSS API
    
    Args:
        app_id: iTunes app ID (e.g., '850549838' for MyBell)
        app_name: Name for identification (e.g., 'Bell')
        country: Country code (default 'ca' for Canada)
        pages: Number of pages to scrape
    
    Returns:
        List of review dictionaries
    """
    
    reviews = []
    base_url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={{page}}/id={app_id}/sortby=mostrecent/json"
    
    print(f"🍎 Scraping {app_name} iOS reviews...")
    
    for page in range(1, pages + 1):
        try:
            url = base_url.format(page=page)
            print(f"  📄 Page {page}/{pages}")
            
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract reviews from RSS feed
            if 'feed' in data and 'entry' in data['feed']:
                entries = data['feed']['entry']
                
                # Skip first entry (app info)
                review_entries = entries[1:] if len(entries) > 1 else []
                
                for entry in review_entries:
                    try:
                        # Extract review data
                        review = {
                            'review_id': entry.get('id', {}).get('label', ''),
                            'title': entry.get('title', {}).get('label', ''),
                            'text': entry.get('content', {}).get('label', ''),
                            'rating': int(entry.get('im:rating', {}).get('label', 0)),
                            'author': entry.get('author', {}).get('name', {}).get('label', ''),
                            'app_version': entry.get('im:version', {}).get('label', ''),
                            'date': entry.get('updated', {}).get('label', ''),
                            'app_name': app_name,
                            'platform': 'iOS',
                            'extraction_method': 'itunes_rss_refresh',
                            'extraction_date': datetime.now().strftime('%Y-%m-%d')
                        }
                        
                        # Clean and validate date
                        if review['date']:
                            try:
                                # iTunes dates are in ISO format: 2025-05-20T10:30:00-07:00
                                review['date'] = pd.to_datetime(review['date']).strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                review['date'] = ''
                        
                        reviews.append(review)
                        
                    except Exception as e:
                        print(f"    ⚠️ Error parsing review: {e}")
                        continue
            
            # Rate limiting
            time.sleep(1)
            
        except Exception as e:
            print(f"    ❌ Error fetching page {page}: {e}")
            continue
    
    print(f"  ✅ Scraped {len(reviews)} iOS reviews for {app_name}")
    return reviews

def main():
    """Main scraping function"""
    
    print("🚀 iOS App Store Review Refresh")
    print("=" * 50)
    
    # App configurations
    apps = [
        {
            'app_id': '850549838',
            'app_name': 'Bell',
            'description': 'MyBell'
        },
        {
            'app_id': '337618972', 
            'app_name': 'Rogers',
            'description': 'MyRogers - Manage your account'
        }
    ]
    
    all_reviews = []
    
    for app in apps:
        reviews = scrape_ios_reviews(
            app_id=app['app_id'],
            app_name=app['app_name'],
            pages=20  # Increased pages for better coverage
        )
        all_reviews.extend(reviews)
        
        print(f"  📱 {app['description']}: {len(reviews)} reviews")
        print()
    
    if all_reviews:
        # Create DataFrame
        df = pd.DataFrame(all_reviews)
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'ios_reviews_refresh_{timestamp}.csv'
        df.to_csv(filename, index=False)
        
        print(f"💾 Saved {len(all_reviews)} iOS reviews to: {filename}")
        print()
        
        # Summary statistics
        print("📊 Summary:")
        print(f"  Total reviews: {len(all_reviews)}")
        print(f"  Bell: {len(df[df['app_name'] == 'Bell'])}")
        print(f"  Rogers: {len(df[df['app_name'] == 'Rogers'])}")
        
        # Check date coverage
        valid_dates = df[df['date'] != '']['date']
        if len(valid_dates) > 0:
            print(f"  Date range: {pd.to_datetime(valid_dates).min().strftime('%Y-%m-%d')} to {pd.to_datetime(valid_dates).max().strftime('%Y-%m-%d')}")
            print(f"  Reviews with dates: {len(valid_dates)}/{len(all_reviews)} ({len(valid_dates)/len(all_reviews)*100:.1f}%)")
        
        print()
        print("✅ iOS refresh complete!")
        print(f"🔄 Next step: Merge with existing data and regenerate dashboard")
        
    else:
        print("❌ No reviews collected - check app IDs and network connection")
        sys.exit(1)

if __name__ == "__main__":
    main()