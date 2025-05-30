#!/usr/bin/env python3
"""
Export the current dashboard data to a CSV file that matches what's displayed
"""
import re
import pandas as pd
import json

def main():
    print("=== EXPORTING DASHBOARD DATA TO CSV ===")
    
    # Read the dashboard JS file
    with open('html_dashboard/dashboard_complete_enhanced.js', 'r') as f:
        content = f.read()

    # Extract the data
    data_match = re.search(r'window\.ENHANCED_DASHBOARD_DATA\s*=\s*({.*?});', content, re.DOTALL)
    if not data_match:
        print("❌ Could not find ENHANCED_DASHBOARD_DATA")
        return
        
    data_str = data_match.group(1)
    data_str = data_str.replace('true', 'True').replace('false', 'False').replace('null', 'None').replace('NaN', 'None')
    
    try:
        data = eval(data_str)
    except Exception as e:
        print(f"❌ Error parsing data: {e}")
        return
    
    print(f"✅ Loaded {len(data['reviews'])} reviews")
    
    # Convert reviews to DataFrame
    reviews_df = pd.DataFrame(data['reviews'])
    
    # Add some basic mappings to match typical CSV structure
    if 'app' in reviews_df.columns:
        reviews_df['app_name'] = reviews_df['app']
    if 'content' in reviews_df.columns:
        reviews_df['text'] = reviews_df['content']
    if 'category' in reviews_df.columns:
        reviews_df['enhanced_category'] = reviews_df['category']
    
    # Save to CSV
    output_file = 'Data/dashboard_current_data.csv'
    reviews_df.to_csv(output_file, index=False)
    
    print(f"✅ Exported to {output_file}")
    
    # Verify the export
    verify_df = pd.read_csv(output_file)
    print(f"✅ Verification: {len(verify_df)} rows exported")
    
    if 'enhanced_category' in verify_df.columns:
        print(f"\n=== CATEGORY VERIFICATION ===")
        category_counts = verify_df['enhanced_category'].value_counts()
        
        key_categories = ['Customer Support', 'App Complaints', 'Authentication', 'Performance', 'Service Quality', 'Billing']
        for cat in key_categories:
            count = category_counts.get(cat, 0)
            print(f"  {cat}: {count}")
        
        print(f"\nTop 10 categories:")
        for cat, count in category_counts.head(10).items():
            print(f"  {cat}: {count}")
    
    print(f"\n🎯 CSV file ready: {output_file}")
    print(f"This file matches exactly what's displayed in the dashboard.")

if __name__ == "__main__":
    main()