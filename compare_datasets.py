#!/usr/bin/env python3
"""
Compare cleaned raw data with analyzed data to find unanalyzed reviews.
"""

import pandas as pd
import numpy as np

def compare_datasets():
    """Compare cleaned raw data with analyzed data to find gaps."""
    
    print("Loading datasets...")
    
    # Load both datasets
    raw_clean = pd.read_csv('telecom_app_reviews_cleaned.csv')
    analyzed = pd.read_csv('telecom_app_reviews_complete.csv')
    
    print(f"Cleaned raw data: {len(raw_clean)} reviews")
    print(f"Analyzed data: {len(analyzed)} reviews")
    print(f"Difference: {len(raw_clean) - len(analyzed)} reviews")
    
    # Create unique identifiers for matching
    # Use combination of text (first 100 chars), author, rating, and app_name
    def create_review_id(row):
        text = str(row['text'])[:100] if pd.notna(row['text']) else ''
        author = str(row['author']) if pd.notna(row['author']) else ''
        rating = str(row['rating'])
        app = str(row['app_name'])
        return f"{text}|{author}|{rating}|{app}"
    
    raw_clean['review_id_match'] = raw_clean.apply(create_review_id, axis=1)
    analyzed['review_id_match'] = analyzed.apply(create_review_id, axis=1)
    
    # Find reviews in raw that are not in analyzed
    analyzed_ids = set(analyzed['review_id_match'])
    raw_clean['is_analyzed'] = raw_clean['review_id_match'].isin(analyzed_ids)
    
    unanalyzed = raw_clean[~raw_clean['is_analyzed']].copy()
    
    # Also check using review_id if available
    if 'review_id' in raw_clean.columns and 'review_id' in analyzed.columns:
        analyzed_review_ids = set(analyzed['review_id'].astype(str))
        raw_clean['is_analyzed_by_id'] = raw_clean['review_id'].astype(str).isin(analyzed_review_ids)
        
        # Count matches
        matched_by_text = raw_clean['is_analyzed'].sum()
        matched_by_id = raw_clean['is_analyzed_by_id'].sum()
        
        print(f"\nMatching results:")
        print(f"Matched by text/author/rating: {matched_by_text}")
        print(f"Matched by review_id: {matched_by_id}")
        
        # Use the review_id matching if it finds more matches
        if matched_by_id > matched_by_text:
            raw_clean['is_analyzed'] = raw_clean['is_analyzed_by_id']
            unanalyzed = raw_clean[~raw_clean['is_analyzed']].copy()
    
    print(f"\n=== Unanalyzed Reviews ===")
    print(f"Total unanalyzed: {len(unanalyzed)} reviews")
    
    # Breakdown by app
    print("\nBy App:")
    for app in ['Rogers', 'Bell']:
        app_total = len(raw_clean[raw_clean['app_name'] == app])
        app_analyzed = len(analyzed[analyzed['app_name'] == app])
        app_unanalyzed = len(unanalyzed[unanalyzed['app_name'] == app])
        pct_analyzed = (app_analyzed / app_total * 100) if app_total > 0 else 0
        print(f"{app}:")
        print(f"  - Total in cleaned raw: {app_total}")
        print(f"  - Already analyzed: {app_analyzed} ({pct_analyzed:.1f}%)")
        print(f"  - Still need analysis: {app_unanalyzed}")
    
    # Breakdown by platform
    print("\nBy Platform:")
    platform_stats = unanalyzed.groupby(['app_name', 'platform']).size().reset_index(name='count')
    for _, row in platform_stats.iterrows():
        print(f"{row['app_name']} - {row['platform']}: {row['count']} unanalyzed")
    
    # Date analysis
    print("\nDate Range of Unanalyzed Reviews:")
    unanalyzed['date_parsed'] = pd.to_datetime(unanalyzed['date'], errors='coerce')
    date_min = unanalyzed['date_parsed'].min()
    date_max = unanalyzed['date_parsed'].max()
    print(f"Earliest: {date_min}")
    print(f"Latest: {date_max}")
    
    # Year distribution
    unanalyzed['year'] = unanalyzed['date_parsed'].dt.year
    year_counts = unanalyzed['year'].value_counts().sort_index()
    print("\nUnanalyzed reviews by year:")
    for year, count in year_counts.items():
        if pd.notna(year):
            print(f"  {int(year)}: {count}")
    
    # Rating distribution of unanalyzed
    print("\nRating distribution of unanalyzed reviews:")
    rating_counts = unanalyzed['rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        print(f"  {rating} stars: {count}")
    
    # Sample some unanalyzed reviews
    print("\n=== Sample Unanalyzed Reviews ===")
    
    # Get samples from each app
    for app in ['Rogers', 'Bell']:
        app_unanalyzed = unanalyzed[unanalyzed['app_name'] == app]
        if len(app_unanalyzed) > 0:
            print(f"\n{app} samples (showing 3):")
            samples = app_unanalyzed.sample(min(3, len(app_unanalyzed)), random_state=42)
            for idx, row in samples.iterrows():
                print(f"\n- Rating: {row['rating']}")
                print(f"  Platform: {row['platform']}")
                print(f"  Date: {row['date']}")
                print(f"  Text: {str(row['text'])[:200]}...")
    
    # Check for potential complaint reviews in unanalyzed set
    complaint_keywords = ['complaint', 'complain', 'ccts', 'escalat', 'regulatory', 
                         'ombudsman', 'rip off', 'ripped off', 'file a complaint']
    
    def has_complaint_keyword(text):
        if pd.isna(text):
            return False
        text_lower = str(text).lower()
        return any(keyword in text_lower for keyword in complaint_keywords)
    
    unanalyzed['potential_complaint'] = unanalyzed['text'].apply(has_complaint_keyword)
    complaint_count = unanalyzed['potential_complaint'].sum()
    
    print(f"\n=== Potential Complaints in Unanalyzed Reviews ===")
    print(f"Found {complaint_count} reviews with complaint keywords")
    
    if complaint_count > 0:
        print("\nBreakdown by app:")
        for app in ['Rogers', 'Bell']:
            app_complaints = unanalyzed[(unanalyzed['app_name'] == app) & 
                                       (unanalyzed['potential_complaint'])].shape[0]
            print(f"{app}: {app_complaints} potential complaints")
    
    # Save unanalyzed reviews to a file
    output_file = 'telecom_app_reviews_unanalyzed.csv'
    unanalyzed_output = unanalyzed.drop(['review_id_match', 'is_analyzed', 'date_parsed', 
                                         'year', 'potential_complaint'], axis=1)
    unanalyzed_output.to_csv(output_file, index=False)
    print(f"\nSaved {len(unanalyzed_output)} unanalyzed reviews to {output_file}")
    
    # Create summary statistics
    summary = {
        'total_raw_cleaned': len(raw_clean),
        'total_analyzed': len(analyzed),
        'total_unanalyzed': len(unanalyzed),
        'rogers_unanalyzed': len(unanalyzed[unanalyzed['app_name'] == 'Rogers']),
        'bell_unanalyzed': len(unanalyzed[unanalyzed['app_name'] == 'Bell']),
        'potential_complaints_unanalyzed': complaint_count,
        'date_range': f"{date_min} to {date_max}"
    }
    
    return summary, unanalyzed

if __name__ == "__main__":
    summary, unanalyzed_df = compare_datasets()