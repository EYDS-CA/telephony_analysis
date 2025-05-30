#!/usr/bin/env python3
"""
iOS Data Merger
Merges newly scraped iOS reviews with existing dataset
Handles deduplication and data validation
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

def load_datasets(existing_path, new_ios_path):
    """Load existing and new datasets"""
    print("📂 Loading datasets...")
    
    # Load existing data
    print(f"   Loading existing data: {existing_path}")
    existing_df = pd.read_csv(existing_path)
    print(f"   ✅ Loaded {len(existing_df):,} existing reviews")
    
    # Load new iOS data
    print(f"   Loading new iOS data: {new_ios_path}")
    new_ios_df = pd.read_csv(new_ios_path)
    print(f"   ✅ Loaded {len(new_ios_df):,} new iOS reviews")
    
    return existing_df, new_ios_df

def analyze_overlap(existing_df, new_ios_df):
    """Analyze overlap between existing and new iOS data"""
    print("\n🔍 Analyzing data overlap...")
    
    # Get existing iOS reviews
    existing_ios = existing_df[existing_df['platform'] == 'iOS'].copy()
    print(f"   Existing iOS reviews: {len(existing_ios):,}")
    
    # Check for potential duplicates based on author + text
    duplicates = 0
    unique_new = []
    
    for idx, new_review in new_ios_df.iterrows():
        is_duplicate = False
        
        # Check if this review might already exist
        if pd.notna(new_review['author']):
            author_matches = existing_ios[existing_ios['author'] == new_review['author']]
            
            if len(author_matches) > 0:
                # Check text similarity
                for _, existing in author_matches.iterrows():
                    if pd.notna(new_review['text']) and pd.notna(existing['text']):
                        # Compare first 100 characters
                        if str(new_review['text'])[:100] == str(existing['text'])[:100]:
                            duplicates += 1
                            is_duplicate = True
                            break
        
        if not is_duplicate:
            unique_new.append(idx)
    
    print(f"   Potential duplicates found: {duplicates}")
    print(f"   Unique new reviews: {len(unique_new)}")
    
    return unique_new

def prepare_new_reviews(new_ios_df, unique_indices):
    """Prepare new reviews for merging"""
    print("\n🔧 Preparing new reviews...")
    
    # Filter to unique reviews only
    unique_df = new_ios_df.iloc[unique_indices].copy()
    
    # Ensure all required columns are present
    required_columns = [
        'review_id', 'title', 'text', 'rating', 'author', 'app_version',
        'date', 'app_name', 'platform', 'extraction_method', 'extraction_date',
        'sentiment_score', 'sentiment', 'userImage', 'thumbs_up',
        'developer_response', 'replied_at', 'appVersion', 'claude_summary',
        'claude_sentiment', 'claude_sentiment_score', 'primary_category',
        'sub_categories', 'issue_tags', 'feature_tags', 'severity',
        'customer_service_impact'
    ]
    
    # Add missing columns with appropriate defaults
    for col in required_columns:
        if col not in unique_df.columns:
            if col in ['sentiment_score', 'claude_sentiment_score']:
                unique_df[col] = np.nan
            elif col in ['thumbs_up']:
                unique_df[col] = 0
            else:
                unique_df[col] = ''
    
    # Set platform explicitly
    unique_df['platform'] = 'iOS'
    
    # Set extraction date if not present
    if 'extraction_date' not in unique_df.columns or unique_df['extraction_date'].isna().all():
        unique_df['extraction_date'] = datetime.now().strftime('%Y-%m-%d')
    
    print(f"   ✅ Prepared {len(unique_df):,} reviews for merging")
    
    return unique_df

def merge_datasets(existing_df, prepared_new_df):
    """Merge datasets"""
    print("\n🔄 Merging datasets...")
    
    # Remove existing iOS reviews (we're replacing them)
    android_only = existing_df[existing_df['platform'] == 'Android'].copy()
    print(f"   Keeping {len(android_only):,} Android reviews")
    
    # Combine with new iOS data
    merged_df = pd.concat([android_only, prepared_new_df], ignore_index=True)
    
    # Sort by date (newest first)
    if 'date' in merged_df.columns:
        merged_df['date_temp'] = pd.to_datetime(merged_df['date'], errors='coerce')
        merged_df = merged_df.sort_values('date_temp', ascending=False)
        merged_df = merged_df.drop('date_temp', axis=1)
    
    print(f"   ✅ Merged dataset contains {len(merged_df):,} reviews")
    
    return merged_df

def generate_summary_report(existing_df, new_ios_df, merged_df):
    """Generate summary report"""
    print("\n📊 Summary Report")
    print("=" * 60)
    
    # Before merge
    print("\n📈 Before Merge:")
    existing_android = len(existing_df[existing_df['platform'] == 'Android'])
    existing_ios = len(existing_df[existing_df['platform'] == 'iOS'])
    print(f"   Total reviews: {len(existing_df):,}")
    print(f"   Android: {existing_android:,} ({existing_android/len(existing_df)*100:.1f}%)")
    print(f"   iOS: {existing_ios:,} ({existing_ios/len(existing_df)*100:.1f}%)")
    
    # After merge
    print("\n📈 After Merge:")
    merged_android = len(merged_df[merged_df['platform'] == 'Android'])
    merged_ios = len(merged_df[merged_df['platform'] == 'iOS'])
    print(f"   Total reviews: {len(merged_df):,}")
    print(f"   Android: {merged_android:,} ({merged_android/len(merged_df)*100:.1f}%)")
    print(f"   iOS: {merged_ios:,} ({merged_ios/len(merged_df)*100:.1f}%)")
    
    # iOS data quality
    print("\n📱 iOS Data Quality:")
    ios_with_dates = merged_df[(merged_df['platform'] == 'iOS') & (merged_df['date'].notna()) & (merged_df['date'] != '')]
    print(f"   iOS reviews with dates: {len(ios_with_dates):,}/{merged_ios:,} ({len(ios_with_dates)/merged_ios*100:.1f}%)")
    
    if len(ios_with_dates) > 0:
        ios_dates = pd.to_datetime(ios_with_dates['date'], errors='coerce')
        valid_dates = ios_dates.dropna()
        if len(valid_dates) > 0:
            print(f"   iOS date range: {valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}")
            
            # Recent iOS reviews
            five_years_ago = datetime.now() - pd.Timedelta(days=5*365)
            recent_ios = valid_dates[valid_dates >= five_years_ago]
            print(f"   Recent iOS (5 years): {len(recent_ios):,} ({len(recent_ios)/len(ios_with_dates)*100:.1f}%)")
    
    # App distribution
    print("\n📱 App Distribution (After Merge):")
    for app in ['Bell', 'Rogers']:
        app_total = len(merged_df[merged_df['app_name'] == app])
        app_android = len(merged_df[(merged_df['app_name'] == app) & (merged_df['platform'] == 'Android')])
        app_ios = len(merged_df[(merged_df['app_name'] == app) & (merged_df['platform'] == 'iOS')])
        print(f"   {app}: {app_total:,} total (Android: {app_android:,}, iOS: {app_ios:,})")

def main():
    """Main execution"""
    print("🚀 iOS Data Merger Tool")
    print("=" * 60)
    
    # Check command line arguments
    if len(sys.argv) != 3:
        print("\n❌ Usage: python merge_ios_data.py <existing_data.csv> <new_ios_data.csv>")
        print("\nExample:")
        print("  python merge_ios_data.py telecom_app_reviews_analyzed.csv ios_reviews_fresh_20250528_214500.csv")
        sys.exit(1)
    
    existing_path = sys.argv[1]
    new_ios_path = sys.argv[2]
    
    # Validate files exist
    if not os.path.exists(existing_path):
        print(f"❌ Existing data file not found: {existing_path}")
        sys.exit(1)
    
    if not os.path.exists(new_ios_path):
        print(f"❌ New iOS data file not found: {new_ios_path}")
        sys.exit(1)
    
    try:
        # Load datasets
        existing_df, new_ios_df = load_datasets(existing_path, new_ios_path)
        
        # Analyze overlap
        unique_indices = analyze_overlap(existing_df, new_ios_df)
        
        # Prepare new reviews
        prepared_new_df = prepare_new_reviews(new_ios_df, unique_indices)
        
        # Merge datasets
        merged_df = merge_datasets(existing_df, prepared_new_df)
        
        # Generate summary report
        generate_summary_report(existing_df, new_ios_df, merged_df)
        
        # Save merged dataset
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'telecom_app_reviews_merged_{timestamp}.csv'
        merged_df.to_csv(output_filename, index=False)
        
        print(f"\n💾 Saved merged dataset to: {output_filename}")
        print(f"\n✅ Merge complete! Next steps:")
        print("   1. Review the merged data")
        print("   2. Run Claude sentiment analysis on new iOS reviews")
        print("   3. Update dashboard with refreshed data")
        
    except Exception as e:
        print(f"\n❌ Error during merge: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()