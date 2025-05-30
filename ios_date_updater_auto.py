#!/usr/bin/env python3
"""
iOS Date Updater (Automatic)
Matches existing iOS reviews with new scraped data to add missing dates
Preserves all existing Claude analysis and only adds truly new reviews
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os
from difflib import SequenceMatcher

def similarity_score(str1, str2):
    """Calculate similarity between two strings"""
    if pd.isna(str1) or pd.isna(str2):
        return 0.0
    return SequenceMatcher(None, str(str1), str(str2)).ratio()

def load_data(existing_path, new_ios_path):
    """Load both datasets"""
    print("📂 Loading datasets...")
    
    # Load existing data
    print(f"   Loading existing data: {existing_path}")
    existing_df = pd.read_csv(existing_path)
    print(f"   ✅ Loaded {len(existing_df):,} total reviews")
    
    # Load new iOS data with dates
    print(f"   Loading new iOS data: {new_ios_path}")
    new_ios_df = pd.read_csv(new_ios_path)
    print(f"   ✅ Loaded {len(new_ios_df):,} new iOS reviews with dates")
    
    return existing_df, new_ios_df

def match_reviews(existing_ios_df, new_ios_df):
    """Match existing reviews with new ones based on multiple criteria"""
    print("\n🔍 Matching existing iOS reviews with new data...")
    
    matches = []
    unmatched_existing = []
    unmatched_new = list(range(len(new_ios_df)))
    
    # Create a copy for matching
    existing_ios_df = existing_ios_df.copy()
    new_ios_df = new_ios_df.copy()
    
    # First pass: Exact matches on author + rating + app_name
    print("\n   Pass 1: Exact author + rating + app matches...")
    matched_count = 0
    
    for idx_e, existing in existing_ios_df.iterrows():
        found_match = False
        
        for idx_n in unmatched_new[:]:  # Create a copy to iterate
            new = new_ios_df.iloc[idx_n]
            
            # Check exact match on key fields
            if (existing['author'] == new['author'] and 
                existing['rating'] == new['rating'] and
                existing['app_name'] == new['app_name']):
                
                # Check text similarity (at least 90% similar)
                text_sim = similarity_score(existing.get('text', ''), new.get('text', ''))
                
                if text_sim > 0.9:
                    matches.append({
                        'existing_idx': idx_e,
                        'new_idx': idx_n,
                        'match_type': 'exact',
                        'confidence': text_sim,
                        'date_to_add': new['date']
                    })
                    unmatched_new.remove(idx_n)
                    found_match = True
                    matched_count += 1
                    break
        
        if not found_match:
            unmatched_existing.append(idx_e)
    
    print(f"   ✅ Found {matched_count} exact matches")
    
    # Second pass: Fuzzy matching on remaining reviews
    print("\n   Pass 2: Fuzzy matching on text similarity...")
    fuzzy_matched = 0
    
    for idx_e in unmatched_existing[:]:
        existing = existing_ios_df.loc[idx_e]
        best_match = None
        best_score = 0
        best_idx = None
        
        for idx_n in unmatched_new:
            new = new_ios_df.iloc[idx_n]
            
            # Must be same app and similar rating
            if (existing['app_name'] == new['app_name'] and 
                abs(existing['rating'] - new['rating']) <= 1):
                
                # Calculate text similarity
                text_sim = similarity_score(existing.get('text', ''), new.get('text', ''))
                
                # Also check title similarity if available
                title_sim = similarity_score(existing.get('title', ''), new.get('title', ''))
                
                # Combined score (weighted average)
                combined_score = (text_sim * 0.7 + title_sim * 0.3) if title_sim > 0 else text_sim
                
                if combined_score > best_score and combined_score > 0.7:  # 70% threshold
                    best_score = combined_score
                    best_match = new
                    best_idx = idx_n
        
        if best_match is not None:
            matches.append({
                'existing_idx': idx_e,
                'new_idx': best_idx,
                'match_type': 'fuzzy',
                'confidence': best_score,
                'date_to_add': best_match['date']
            })
            unmatched_existing.remove(idx_e)
            unmatched_new.remove(best_idx)
            fuzzy_matched += 1
    
    print(f"   ✅ Found {fuzzy_matched} fuzzy matches")
    
    # Summary
    print(f"\n   📊 Matching Summary:")
    print(f"      Total existing iOS reviews: {len(existing_ios_df)}")
    print(f"      Successfully matched: {len(matches)} ({len(matches)/len(existing_ios_df)*100:.1f}%)")
    print(f"      Unmatched existing: {len(unmatched_existing)}")
    print(f"      New reviews not in existing: {len(unmatched_new)}")
    
    return matches, unmatched_existing, unmatched_new

def update_dates(existing_df, matches):
    """Update existing dataframe with matched dates"""
    print("\n🔄 Updating dates in existing data...")
    
    updated_df = existing_df.copy()
    updated_count = 0
    
    for match in matches:
        # Update the date for matched iOS review
        updated_df.loc[match['existing_idx'], 'date'] = match['date_to_add']
        updated_count += 1
    
    print(f"   ✅ Updated {updated_count} iOS reviews with dates")
    
    return updated_df

def add_new_reviews(updated_df, new_ios_df, unmatched_new_indices):
    """Add genuinely new reviews that weren't in existing data"""
    print(f"\n➕ Adding {len(unmatched_new_indices)} genuinely new iOS reviews...")
    
    if len(unmatched_new_indices) == 0:
        return updated_df
    
    # Get the new reviews
    new_reviews = new_ios_df.iloc[unmatched_new_indices].copy()
    
    # Add required columns with defaults (preserve structure)
    required_columns = updated_df.columns
    for col in required_columns:
        if col not in new_reviews.columns:
            if col in ['sentiment_score', 'claude_sentiment_score', 'thumbs_up']:
                new_reviews[col] = np.nan
            else:
                new_reviews[col] = ''
    
    # Mark these as needing Claude analysis
    new_reviews['needs_claude_analysis'] = True
    
    # Ensure column order matches
    new_reviews = new_reviews[required_columns.tolist() + ['needs_claude_analysis']]
    
    # Combine dataframes
    combined_df = pd.concat([updated_df, new_reviews], ignore_index=True)
    
    print(f"   ✅ Added {len(new_reviews)} new iOS reviews")
    print(f"   ⚠️  These new reviews need Claude sentiment analysis")
    
    return combined_df

def generate_report(existing_df, updated_df, matches, unmatched_existing, unmatched_new):
    """Generate detailed report of the update process"""
    print("\n📊 FINAL REPORT")
    print("=" * 60)
    
    # Before update
    ios_before = existing_df[existing_df['platform'] == 'iOS']
    ios_with_dates_before = ios_before[ios_before['date'].notna() & (ios_before['date'] != '')]
    
    # After update
    ios_after = updated_df[updated_df['platform'] == 'iOS']
    ios_with_dates_after = ios_after[ios_after['date'].notna() & (ios_after['date'] != '')]
    
    print("\n📈 iOS Date Coverage:")
    print(f"   Before: {len(ios_with_dates_before)}/{len(ios_before)} ({len(ios_with_dates_before)/len(ios_before)*100:.1f}%)")
    print(f"   After:  {len(ios_with_dates_after)}/{len(ios_after)} ({len(ios_with_dates_after)/len(ios_after)*100:.1f}%)")
    
    # Data quality
    print(f"\n✅ Data Quality:")
    print(f"   Existing reviews preserved: {len(ios_before) - len(unmatched_existing)}/{len(ios_before)}")
    print(f"   Claude analysis preserved: 100% (all existing data kept)")
    print(f"   New reviews added: {len(unmatched_new)}")
    
    # Match quality
    exact_matches = len([m for m in matches if m['match_type'] == 'exact'])
    fuzzy_matches = len([m for m in matches if m['match_type'] == 'fuzzy'])
    print(f"\n🔍 Match Quality:")
    print(f"   Exact matches: {exact_matches}")
    print(f"   Fuzzy matches: {fuzzy_matches}")
    print(f"   Total matched: {len(matches)}")
    
    if len(matches) > 0:
        avg_confidence = np.mean([m['confidence'] for m in matches])
        print(f"   Average confidence: {avg_confidence:.1%}")
    
    # Unmatched analysis
    if len(unmatched_existing) > 0:
        print(f"\n⚠️  Unmatched existing reviews: {len(unmatched_existing)}")
        print("   These keep their original data (no date)")
        # Show a few examples
        print("   Examples:")
        for idx in unmatched_existing[:3]:
            review = existing_df.loc[idx]
            print(f"      - {review['author']} ({review['app_name']}) - {review['rating']}★")
    
    # Check date quality
    print(f"\n📅 Date Quality Check:")
    ios_updated = updated_df[updated_df['platform'] == 'iOS']
    ios_dates = pd.to_datetime(ios_updated['date'], errors='coerce')
    valid_dates = ios_dates.dropna()
    
    if len(valid_dates) > 0:
        print(f"   Date range: {valid_dates.min().strftime('%Y-%m-%d')} to {valid_dates.max().strftime('%Y-%m-%d')}")
        five_years_ago = pd.Timestamp.now() - pd.Timedelta(days=5*365)
        recent = valid_dates[valid_dates >= five_years_ago]
        print(f"   Recent (5 years): {len(recent)}/{len(valid_dates)} ({len(recent)/len(valid_dates)*100:.1f}%)")
    
    return exact_matches, fuzzy_matches

def main():
    """Main execution"""
    print("🚀 iOS Date Updater (Automatic)")
    print("=" * 60)
    
    # Check arguments
    if len(sys.argv) != 3:
        print("\n❌ Usage: python ios_date_updater_auto.py <existing_data.csv> <new_ios_data.csv>")
        print("\nExample:")
        print("  python ios_date_updater_auto.py telecom_app_reviews_analyzed.csv ios_reviews_fresh_20250529_063833.csv")
        sys.exit(1)
    
    existing_path = sys.argv[1]
    new_ios_path = sys.argv[2]
    
    # Validate files
    if not os.path.exists(existing_path):
        print(f"❌ Existing data file not found: {existing_path}")
        sys.exit(1)
    
    if not os.path.exists(new_ios_path):
        print(f"❌ New iOS data file not found: {new_ios_path}")
        sys.exit(1)
    
    try:
        # Load data
        existing_df, new_ios_df = load_data(existing_path, new_ios_path)
        
        # Get existing iOS reviews
        existing_ios_df = existing_df[existing_df['platform'] == 'iOS'].copy()
        
        # Match reviews
        matches, unmatched_existing, unmatched_new = match_reviews(existing_ios_df, new_ios_df)
        
        # Only proceed if we have good match rate
        match_rate = len(matches) / len(existing_ios_df) * 100
        
        if match_rate < 80:
            print(f"\n⚠️  Low match rate ({match_rate:.1f}%). Manual review recommended.")
            print("   Exiting without changes.")
            sys.exit(1)
        
        print(f"\n✅ High match rate ({match_rate:.1f}%). Proceeding with automatic update...")
        
        # Update dates
        updated_df = update_dates(existing_df, matches)
        
        # Decision: Add new reviews only if reasonable number
        if len(unmatched_new) > 0 and len(unmatched_new) < 200:
            print(f"\n✅ Adding {len(unmatched_new)} new iOS reviews (reasonable number)")
            updated_df = add_new_reviews(updated_df, new_ios_df, unmatched_new)
        elif len(unmatched_new) >= 200:
            print(f"\n⚠️  Skipping {len(unmatched_new)} new reviews (too many - manual review needed)")
        
        # Generate report
        exact_matches, fuzzy_matches = generate_report(existing_df, updated_df, matches, unmatched_existing, unmatched_new)
        
        # Save updated data
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f'telecom_app_reviews_updated_{timestamp}.csv'
        
        # Remove temporary column if added
        if 'needs_claude_analysis' in updated_df.columns:
            needs_analysis = updated_df[updated_df['needs_claude_analysis'] == True]
            if len(needs_analysis) > 0:
                # Save list of reviews needing analysis
                analysis_filename = f'reviews_needing_claude_analysis_{timestamp}.csv'
                needs_analysis[['review_id', 'app_name', 'text', 'date']].to_csv(
                    analysis_filename, 
                    index=False
                )
                print(f"\n📄 Saved {len(needs_analysis)} reviews needing Claude analysis to: {analysis_filename}")
            
            # Remove temporary column
            updated_df = updated_df.drop('needs_claude_analysis', axis=1)
        
        updated_df.to_csv(output_filename, index=False)
        print(f"\n💾 Saved updated dataset to: {output_filename}")
        print(f"   Total reviews: {len(updated_df):,}")
        
        # Summary statistics
        print(f"\n📊 Update Summary:")
        print(f"   Match rate: {match_rate:.1f}%")
        print(f"   Exact matches: {exact_matches}")
        print(f"   Fuzzy matches: {fuzzy_matches}")
        print(f"   iOS reviews with dates: {len(updated_df[(updated_df['platform'] == 'iOS') & updated_df['date'].notna()])}")
        print(f"   Total dataset size: {len(updated_df):,} reviews")
        
        print(f"\n✅ SUCCESS! iOS dates have been updated while preserving all Claude analysis.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()