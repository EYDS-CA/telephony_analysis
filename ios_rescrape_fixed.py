#!/usr/bin/env python3
"""
iOS App Store Review Re-scraper (Fixed)
Handles timezone issues and API pagination limits
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time
import sys
import hashlib

def generate_review_id(review_data):
    """Generate consistent review ID for matching"""
    unique_string = f"{review_data.get('author', '')}{review_data.get('date', '')}{review_data.get('rating', '')}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def scrape_ios_reviews(app_id, app_name, country='ca', max_pages=10):
    """
    Scrape iOS App Store reviews using iTunes RSS API
    Note: iTunes RSS API typically limits to 10 pages (~500 reviews)
    
    Args:
        app_id: iTunes app ID
        app_name: Name for identification
        country: Country code
        max_pages: Maximum pages to attempt (API limit is ~10)
    
    Returns:
        List of review dictionaries
    """
    
    reviews = []
    base_url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={{page}}/id={app_id}/sortby=mostrecent/json"
    
    print(f"\n🍎 Scraping {app_name} iOS reviews...")
    print(f"   App ID: {app_id}")
    
    consecutive_errors = 0
    
    for page in range(1, max_pages + 1):
        try:
            url = base_url.format(page=page)
            print(f"   📄 Page {page}/{max_pages}", end='\r')
            
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            
            if response.status_code != 200:
                consecutive_errors += 1
                if consecutive_errors >= 3:
                    print(f"\n   ℹ️  Reached API limit after {page-1} pages")
                    break
                continue
            
            consecutive_errors = 0
            data = response.json()
            
            # Extract reviews from RSS feed
            if 'feed' in data and 'entry' in data['feed']:
                entries = data['feed']['entry']
                
                # Skip first entry (app info) on first page
                review_entries = entries[1:] if page == 1 and len(entries) > 1 else entries
                
                if not review_entries:
                    print(f"\n   ℹ️  No more reviews after page {page-1}")
                    break
                
                for entry in review_entries:
                    try:
                        # Extract review data
                        review = {
                            'title': entry.get('title', {}).get('label', ''),
                            'text': entry.get('content', {}).get('label', ''),
                            'rating': int(entry.get('im:rating', {}).get('label', 0)),
                            'author': entry.get('author', {}).get('name', {}).get('label', ''),
                            'app_version': entry.get('im:version', {}).get('label', ''),
                            'date': entry.get('updated', {}).get('label', ''),
                            'app_name': app_name,
                            'platform': 'iOS',
                            'extraction_method': 'itunes_rss',
                            'extraction_date': datetime.now().strftime('%Y-%m-%d'),
                            'vote_sum': entry.get('im:voteSum', {}).get('label', '0'),
                            'vote_count': entry.get('im:voteCount', {}).get('label', '0')
                        }
                        
                        # Parse and format date
                        if review['date']:
                            try:
                                # Parse the date and convert to timezone-naive
                                parsed_date = pd.to_datetime(review['date']).tz_localize(None)
                                review['date'] = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                                review['date_parsed'] = parsed_date
                            except:
                                review['date'] = ''
                                review['date_parsed'] = None
                        
                        # Generate review ID
                        review['review_id'] = generate_review_id(review)
                        
                        reviews.append(review)
                        
                    except Exception as e:
                        continue
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            consecutive_errors += 1
            if consecutive_errors >= 3:
                print(f"\n   ℹ️  Stopping after {page-1} pages due to errors")
                break
    
    print(f"\n   ✅ Scraped {len(reviews)} iOS reviews for {app_name}")
    return reviews

def load_existing_data(filepath):
    """Load existing review data"""
    print(f"\n📂 Loading existing data from: {filepath}")
    df = pd.read_csv(filepath)
    ios_df = df[df['platform'] == 'iOS'].copy()
    print(f"   Found {len(ios_df)} existing iOS reviews")
    return df, ios_df

def compare_reviews(new_reviews, existing_ios_df, app_name):
    """Compare new and existing reviews"""
    print(f"\n🔍 Comparing {app_name} reviews...")
    
    new_df = pd.DataFrame(new_reviews)
    
    if len(new_df) == 0:
        print("   ❌ No new reviews to compare")
        return pd.DataFrame()
    
    # Filter by app
    new_app_df = new_df[new_df['app_name'] == app_name].copy()
    existing_app_df = existing_ios_df[existing_ios_df['app_name'] == app_name].copy()
    
    print(f"   New reviews: {len(new_app_df)}")
    print(f"   Existing reviews: {len(existing_app_df)}")
    
    # Date analysis for new reviews
    if 'date_parsed' in new_app_df.columns:
        new_with_dates = new_app_df[new_app_df['date_parsed'].notna()]
        if len(new_with_dates) > 0:
            date_min = new_with_dates['date_parsed'].min()
            date_max = new_with_dates['date_parsed'].max()
            print(f"   New data date range: {date_min.strftime('%Y-%m-%d')} to {date_max.strftime('%Y-%m-%d')}")
            
            # Last 5 years analysis - ensure timezone-naive comparison
            five_years_ago = pd.Timestamp.now().tz_localize(None) - pd.Timedelta(days=5*365)
            recent_new = new_with_dates[new_with_dates['date_parsed'] >= five_years_ago]
            print(f"   Recent reviews (5 years): {len(recent_new)} ({len(recent_new)/len(new_with_dates)*100:.1f}%)")
    
    # Rating distribution comparison
    print("\n   📊 Rating Distribution Comparison:")
    print("   Rating | Existing | New     | New %")
    print("   -------|----------|---------|-------")
    for rating in range(1, 6):
        existing_count = len(existing_app_df[existing_app_df['rating'] == rating])
        new_count = len(new_app_df[new_app_df['rating'] == rating])
        new_pct = new_count/len(new_app_df)*100 if len(new_app_df) > 0 else 0
        print(f"   {rating}★     | {existing_count:8} | {new_count:7} | {new_pct:5.1f}%")
    
    # Average rating comparison
    if len(existing_app_df) > 0:
        existing_avg = existing_app_df['rating'].mean()
        print(f"\n   Existing average rating: {existing_avg:.2f}")
    
    if len(new_app_df) > 0:
        new_avg = new_app_df['rating'].mean()
        print(f"   New average rating: {new_avg:.2f}")
    
    return new_app_df

def main():
    """Main execution function"""
    
    print("🚀 iOS App Store Review Re-scraper (Fixed)")
    print("=" * 60)
    
    # Load existing data
    existing_file = '/Users/amirshayegh/Developer/temp/review_analysis/telecom_app_reviews_analyzed.csv'
    
    try:
        full_df, existing_ios_df = load_existing_data(existing_file)
    except Exception as e:
        print(f"❌ Error loading existing data: {e}")
        sys.exit(1)
    
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
            'description': 'MyRogers'
        }
    ]
    
    all_new_reviews = []
    comparison_results = {}
    
    for app in apps:
        # Scrape new reviews (iTunes RSS API typically limits to ~10 pages)
        new_reviews = scrape_ios_reviews(
            app_id=app['app_id'],
            app_name=app['app_name'],
            max_pages=15  # Try up to 15 but expect ~10 to work
        )
        
        all_new_reviews.extend(new_reviews)
        
        # Compare with existing
        app_comparison = compare_reviews(new_reviews, existing_ios_df, app['app_name'])
        comparison_results[app['app_name']] = app_comparison
    
    # Save new reviews
    if all_new_reviews:
        new_df = pd.DataFrame(all_new_reviews)
        
        # Remove temporary parsing column
        if 'date_parsed' in new_df.columns:
            new_df = new_df.drop('date_parsed', axis=1)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save new iOS reviews
        new_filename = f'ios_reviews_fresh_{timestamp}.csv'
        new_df.to_csv(new_filename, index=False)
        print(f"\n💾 Saved {len(all_new_reviews)} new iOS reviews to: {new_filename}")
        
        # Create comparison summary
        print("\n📋 COMPARISON SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Overall Statistics:")
        print(f"   Total new iOS reviews scraped: {len(all_new_reviews)}")
        print(f"   Total existing iOS reviews: {len(existing_ios_df)}")
        
        # Date coverage analysis
        new_with_dates = new_df[new_df['date'] != '']
        if len(new_with_dates) > 0:
            print(f"\n📅 Date Coverage:")
            print(f"   New reviews with dates: {len(new_with_dates)}/{len(new_df)} ({len(new_with_dates)/len(new_df)*100:.1f}%)")
            
            # Parse dates for analysis
            dates = pd.to_datetime(new_with_dates['date'], errors='coerce')
            valid_dates = dates.dropna()
            if len(valid_dates) > 0:
                print(f"   Date range: {valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}")
                
                # Recent coverage
                five_years_ago = pd.Timestamp.now() - pd.Timedelta(days=5*365)
                recent = valid_dates[valid_dates >= five_years_ago]
                print(f"   Recent (5 years): {len(recent)} ({len(recent)/len(valid_dates)*100:.1f}%)")
        
        # App breakdown
        print(f"\n📱 By App:")
        for app_name in ['Bell', 'Rogers']:
            app_reviews = new_df[new_df['app_name'] == app_name]
            print(f"   {app_name}: {len(app_reviews)} reviews")
            if len(app_reviews) > 0:
                print(f"      Average rating: {app_reviews['rating'].mean():.2f}")
        
        print("\n✅ SUCCESS! New iOS data collected with proper dates")
        print("\n🔄 Next Steps:")
        print("   1. Review the data above")
        print("   2. Run: python3 merge_ios_data.py telecom_app_reviews_analyzed.csv " + new_filename)
        print("   3. Run Claude sentiment analysis on merged data")
        print("   4. Update dashboard with refreshed data")
        
    else:
        print("\n❌ No reviews collected - check app IDs and network connection")
        sys.exit(1)

if __name__ == "__main__":
    main()