#!/usr/bin/env python3
"""
iOS App Store Review Re-scraper with Comparison
Scrapes fresh iOS reviews and compares with existing data
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
    # Create unique ID from author + date + rating
    unique_string = f"{review_data.get('author', '')}{review_data.get('date', '')}{review_data.get('rating', '')}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def scrape_ios_reviews(app_id, app_name, country='ca', pages=50):
    """
    Scrape iOS App Store reviews using iTunes RSS API
    
    Args:
        app_id: iTunes app ID
        app_name: Name for identification
        country: Country code
        pages: Number of pages to scrape (50 pages = ~500 reviews)
    
    Returns:
        List of review dictionaries
    """
    
    reviews = []
    base_url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={{page}}/id={app_id}/sortby=mostrecent/json"
    
    print(f"\n🍎 Scraping {app_name} iOS reviews...")
    print(f"   App ID: {app_id}")
    
    consecutive_empty = 0
    
    for page in range(1, pages + 1):
        try:
            url = base_url.format(page=page)
            
            # Show progress every 5 pages
            if page % 5 == 0:
                print(f"   📄 Progress: {page}/{pages} pages ({len(reviews)} reviews collected)")
            
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            })
            response.raise_for_status()
            
            data = response.json()
            
            # Extract reviews from RSS feed
            if 'feed' in data and 'entry' in data['feed']:
                entries = data['feed']['entry']
                
                # Skip first entry (app info) on first page
                review_entries = entries[1:] if page == 1 and len(entries) > 1 else entries
                
                if not review_entries:
                    consecutive_empty += 1
                    if consecutive_empty >= 3:
                        print(f"   ⚠️  No more reviews found after page {page}")
                        break
                else:
                    consecutive_empty = 0
                
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
                                parsed_date = pd.to_datetime(review['date'])
                                review['date'] = parsed_date.strftime('%Y-%m-%d %H:%M:%S')
                                review['date_parsed'] = parsed_date
                            except:
                                review['date'] = ''
                                review['date_parsed'] = None
                        
                        # Generate review ID
                        review['review_id'] = generate_review_id(review)
                        
                        reviews.append(review)
                        
                    except Exception as e:
                        print(f"    ⚠️  Error parsing review: {e}")
                        continue
            
            # Rate limiting
            time.sleep(0.5)
            
        except requests.exceptions.RequestException as e:
            print(f"    ❌ Network error on page {page}: {e}")
            time.sleep(2)
            continue
        except Exception as e:
            print(f"    ❌ Error fetching page {page}: {e}")
            continue
    
    print(f"   ✅ Scraped {len(reviews)} iOS reviews for {app_name}")
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
            
            # Last 5 years analysis
            five_years_ago = datetime.now() - pd.Timedelta(days=5*365)
            recent_new = new_with_dates[new_with_dates['date_parsed'] >= five_years_ago]
            print(f"   Recent reviews (5 years): {len(recent_new)} ({len(recent_new)/len(new_with_dates)*100:.1f}%)")
    
    # Rating distribution comparison
    print("\n   📊 Rating Distribution Comparison:")
    print("   Rating | Existing | New")
    print("   -------|----------|-----")
    for rating in range(1, 6):
        existing_count = len(existing_app_df[existing_app_df['rating'] == rating])
        new_count = len(new_app_df[new_app_df['rating'] == rating])
        print(f"   {rating}★     | {existing_count:8} | {new_count:4}")
    
    # Average rating comparison
    if len(existing_app_df) > 0:
        existing_avg = existing_app_df['rating'].mean()
        print(f"\n   Existing average rating: {existing_avg:.2f}")
    
    if len(new_app_df) > 0:
        new_avg = new_app_df['rating'].mean()
        print(f"   New average rating: {new_avg:.2f}")
    
    # Check for matching reviews (by author + text similarity)
    print("\n   🔄 Checking for overlapping reviews...")
    matches = 0
    if len(existing_app_df) > 0 and len(new_app_df) > 0:
        for _, new_review in new_app_df.iterrows():
            # Check for exact author match with similar text
            author_matches = existing_app_df[existing_app_df['author'] == new_review['author']]
            if len(author_matches) > 0:
                for _, existing in author_matches.iterrows():
                    if pd.notna(new_review['text']) and pd.notna(existing['text']):
                        # Simple text similarity check
                        if str(new_review['text'])[:50] == str(existing['text'])[:50]:
                            matches += 1
                            break
    
    print(f"   Found {matches} potential matching reviews")
    
    return new_app_df

def main():
    """Main execution function"""
    
    print("🚀 iOS App Store Review Re-scrape and Comparison Tool")
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
            'description': 'MyRogers - Manage your account'
        }
    ]
    
    all_new_reviews = []
    comparison_results = {}
    
    for app in apps:
        # Scrape new reviews
        new_reviews = scrape_ios_reviews(
            app_id=app['app_id'],
            app_name=app['app_name'],
            pages=50  # Scrape up to 50 pages for comprehensive coverage
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
        
        # Create comparison report
        print("\n📋 COMPARISON SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 Overall Statistics:")
        print(f"   Total new iOS reviews scraped: {len(all_new_reviews)}")
        print(f"   Total existing iOS reviews: {len(existing_ios_df)}")
        print(f"   Existing Android reviews: {len(full_df[full_df['platform'] == 'Android'])}")
        
        # Date coverage analysis
        new_with_dates = new_df[new_df['date'] != '']
        if len(new_with_dates) > 0:
            print(f"\n📅 Date Coverage:")
            print(f"   New reviews with dates: {len(new_with_dates)}/{len(new_df)} ({len(new_with_dates)/len(new_df)*100:.1f}%)")
            print(f"   Date range: {new_with_dates['date'].min()[:10]} to {new_with_dates['date'].max()[:10]}")
        
        print("\n🔄 Next Steps:")
        print("   1. Review the comparison results above")
        print("   2. If satisfied, merge new iOS data with existing dataset")
        print("   3. Re-run Claude sentiment analysis on new reviews")
        print("   4. Update dashboard with fresh data")
        
        # Create a detailed comparison report
        report_filename = f'ios_comparison_report_{timestamp}.txt'
        with open(report_filename, 'w') as f:
            f.write("iOS Review Data Comparison Report\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for app_name, comparison_df in comparison_results.items():
                f.write(f"\n{app_name} Comparison:\n")
                f.write("-" * 40 + "\n")
                f.write(f"New reviews: {len(comparison_df)}\n")
                f.write(f"Existing reviews: {len(existing_ios_df[existing_ios_df['app_name'] == app_name])}\n")
                
                if len(comparison_df) > 0:
                    f.write(f"Average rating (new): {comparison_df['rating'].mean():.2f}\n")
                    f.write(f"Rating distribution (new):\n")
                    rating_dist = comparison_df['rating'].value_counts().sort_index()
                    for rating, count in rating_dist.items():
                        f.write(f"  {rating}★: {count} ({count/len(comparison_df)*100:.1f}%)\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("End of report\n")
        
        print(f"\n📄 Detailed comparison report saved to: {report_filename}")
        
    else:
        print("\n❌ No reviews collected - check app IDs and network connection")
        sys.exit(1)
    
    print("\n✅ iOS re-scrape and comparison complete!")

if __name__ == "__main__":
    main()