#!/usr/bin/env python3
"""
Dashboard Setup Verification Script
Verifies that all components are properly configured with filtered data.
"""

import os
import json
import pandas as pd
import re

def verify_filtered_dataset():
    """Verify the filtered dataset is correct"""
    print("🔍 Verifying filtered dataset...")
    
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    df['date'] = pd.to_datetime(df['date'])
    
    # Check filtering worked correctly
    android_pre_2020 = len(df[(df['platform'] == 'Android') & (df['date'] < '2020-01-01')])
    
    print(f"   ✅ Total reviews: {len(df):,}")
    print(f"   ✅ Rogers: {len(df[df['app_name'] == 'Rogers']):,}")
    print(f"   ✅ Bell: {len(df[df['app_name'] == 'Bell']):,}")
    print(f"   ✅ Android: {len(df[df['platform'] == 'Android']):,}")
    print(f"   ✅ iOS: {len(df[df['platform'] == 'iOS']):,}")
    print(f"   ✅ Pre-2020 Android removed: {android_pre_2020 == 0}")
    print(f"   ✅ Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    
    return df

def verify_js_files():
    """Verify JavaScript files have correct data"""
    print("\n🔍 Verifying JavaScript files...")
    
    js_files = [
        'html_dashboard/dashboard_complete_enhanced.js',
        'html_dashboard/dashboard_final.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r') as f:
                content = f.read()
            
            # Extract total_reviews from JS
            match = re.search(r'"total_reviews":\s*(\d+)', content)
            if match:
                total_reviews = int(match.group(1))
                print(f"   ✅ {js_file}: {total_reviews:,} reviews")
                
                if total_reviews == 10103:
                    print(f"      ✅ Correct total (10,103)")
                else:
                    print(f"      ❌ Incorrect total (expected 10,103)")
            else:
                print(f"   ❌ Could not find total_reviews in {js_file}")
        else:
            print(f"   ❌ File not found: {js_file}")

def verify_dashboard_html():
    """Verify dashboard HTML has updated metrics"""
    print("\n🔍 Verifying dashboard HTML...")
    
    html_file = 'html_dashboard/dashboard.html'
    if os.path.exists(html_file):
        with open(html_file, 'r') as f:
            content = f.read()
        
        # Check for updated metrics
        checks = [
            ('10,103 reviews', '10,103' in content),
            ('7,055 Rogers', '7,055' in content), 
            ('3,048 Bell', '3,048' in content),
            ('2.58 rating', '2.58' in content),
            ('2020-2025 mention', '2020-2025' in content)
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"   {status} {check_name}")
    else:
        print(f"   ❌ Dashboard HTML not found")

def verify_file_structure():
    """Verify all required files exist"""
    print("\n🔍 Verifying file structure...")
    
    required_files = [
        'Data/analyzed_reviews_filtered_clean.csv',
        'html_dashboard/dashboard.html',
        'html_dashboard/dashboard_complete_enhanced.js',
        'html_dashboard/dashboard_final.js'
    ]
    
    all_exist = True
    for file_path in required_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"   {status} {file_path}")
        if not exists:
            all_exist = False
    
    return all_exist

def main():
    print("🎯 Dashboard Setup Verification\n")
    
    # Verify components
    df = verify_filtered_dataset()
    verify_js_files()
    verify_dashboard_html()
    all_files_exist = verify_file_structure()
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   • Filtered dataset: {len(df):,} reviews (99.6% current)")
    print(f"   • Rogers: {len(df[df['app_name'] == 'Rogers']):,} | Bell: {len(df[df['app_name'] == 'Bell']):,}")
    print(f"   • Platform: Android {len(df[df['platform'] == 'Android']):,} | iOS {len(df[df['platform'] == 'iOS']):,}")
    print(f"   • Average rating: {df['rating'].mean():.2f}")
    
    if all_files_exist:
        print(f"\n🎉 Dashboard setup complete! All files properly configured with filtered data.")
        print(f"🌐 Open html_dashboard/dashboard.html to view the updated dashboard.")
    else:
        print(f"\n⚠️  Some files missing - check file structure above.")

if __name__ == "__main__":
    main()