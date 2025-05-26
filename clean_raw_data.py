#!/usr/bin/env python3
"""
Clean the raw telecom app reviews CSV data to fix data quality issues.
"""

import pandas as pd
import re
from datetime import datetime

def clean_raw_data(input_file='telecom_app_reviews_raw.csv', output_file='telecom_app_reviews_cleaned.csv'):
    """Clean the raw CSV data and fix data quality issues."""
    
    print(f"Loading {input_file}...")
    
    # Read CSV with proper handling of problematic rows
    df = pd.read_csv(input_file, 
                     dtype={'review_id': str, 'rating': str, 'thumbs_up': str},
                     on_bad_lines='warn')
    
    print(f"Loaded {len(df)} rows")
    
    # 1. Fix app_name field - many rows have incorrect values
    valid_apps = ['Rogers', 'Bell']
    
    # Count issues before fixing
    invalid_app_count = (~df['app_name'].isin(valid_apps)).sum()
    print(f"\nFound {invalid_app_count} rows with invalid app_name values")
    
    # Try to recover app_name from other fields
    def fix_app_name(row):
        app_name = str(row['app_name'])
        
        # If app_name is already valid, keep it
        if app_name in valid_apps:
            return app_name
            
        # Check if Rogers or Bell appears in other fields
        text_fields = str(row.get('text', '')) + ' ' + str(row.get('title', '')) + ' ' + str(row.get('developer_response', ''))
        text_lower = text_fields.lower()
        
        if 'rogers' in text_lower and 'bell' not in text_lower:
            return 'Rogers'
        elif 'bell' in text_lower and 'rogers' not in text_lower:
            return 'Bell'
        
        # If app_name looks like a date or version, it's corrupted
        if re.match(r'^\d{4}-\d{2}-\d{2}', app_name) or re.match(r'^\d+\.', app_name):
            return None
            
        return None
    
    # Apply fixes
    df['app_name_fixed'] = df.apply(fix_app_name, axis=1)
    
    # Remove rows where we couldn't determine the app
    df_clean = df[df['app_name_fixed'].notna()].copy()
    df_clean['app_name'] = df_clean['app_name_fixed']
    df_clean = df_clean.drop('app_name_fixed', axis=1)
    
    print(f"After fixing app_name: {len(df_clean)} valid rows")
    
    # 2. Fix platform field
    valid_platforms = ['Android', 'iOS']
    df_clean = df_clean[df_clean['platform'].isin(valid_platforms)]
    print(f"After validating platform: {len(df_clean)} rows")
    
    # 3. Fix rating field - convert to numeric
    def clean_rating(rating):
        try:
            r = float(str(rating))
            if 0 <= r <= 5:
                return r
        except:
            pass
        return None
    
    df_clean['rating'] = df_clean['rating'].apply(clean_rating)
    df_clean = df_clean[df_clean['rating'].notna()]
    print(f"After cleaning ratings: {len(df_clean)} rows")
    
    # 4. Remove duplicates based on review text and author
    df_clean['text_clean'] = df_clean['text'].fillna('').str.strip()
    df_clean = df_clean[df_clean['text_clean'] != '']
    
    # Remove exact duplicates
    before_dedup = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['text_clean', 'author', 'rating'])
    print(f"Removed {before_dedup - len(df_clean)} duplicate reviews")
    
    # 5. Clean date field
    def parse_date(date_str):
        if pd.isna(date_str):
            return None
        try:
            # Try to parse ISO format
            return pd.to_datetime(date_str)
        except:
            try:
                # Try other formats
                return pd.to_datetime(date_str, errors='coerce')
            except:
                return None
    
    df_clean['date_parsed'] = df_clean['date'].apply(parse_date)
    
    # 6. Final cleanup
    df_clean = df_clean.drop('text_clean', axis=1)
    
    # Summary statistics
    print("\n=== Final Data Summary ===")
    print(f"Total cleaned reviews: {len(df_clean)}")
    print(f"\nReviews by app:")
    print(df_clean['app_name'].value_counts())
    print(f"\nReviews by platform:")
    print(df_clean['platform'].value_counts())
    print(f"\nRating distribution:")
    print(df_clean['rating'].value_counts().sort_index())
    
    # Check for complaint patterns
    complaint_keywords = ['complaint', 'complain', 'ccts', 'escalat', 'regulatory', 
                         'ombudsman', 'rip off', 'ripped off', 'file a complaint']
    
    def has_complaint(text):
        if pd.isna(text):
            return False
        text_lower = str(text).lower()
        return any(keyword in text_lower for keyword in complaint_keywords)
    
    df_clean['has_complaint'] = df_clean['text'].apply(has_complaint)
    
    print(f"\nComplaint analysis:")
    for app in ['Rogers', 'Bell']:
        app_data = df_clean[df_clean['app_name'] == app]
        complaint_count = app_data['has_complaint'].sum()
        total = len(app_data)
        pct = (complaint_count / total * 100) if total > 0 else 0
        print(f"{app}: {complaint_count} complaints out of {total} reviews ({pct:.1f}%)")
    
    # Save cleaned data
    print(f"\nSaving cleaned data to {output_file}...")
    df_clean.to_csv(output_file, index=False)
    print("Done!")
    
    return df_clean

if __name__ == "__main__":
    clean_raw_data()