#!/usr/bin/env python3
"""
Verify dashboard data accuracy for Issue Categories chart
"""
import re
import json

def main():
    print("=== DASHBOARD DATA ACCURACY VERIFICATION ===")
    
    # Read the dashboard JS file
    with open('html_dashboard/dashboard_complete_enhanced.js', 'r') as f:
        content = f.read()

    # Extract the data using regex
    data_match = re.search(r'window\.ENHANCED_DASHBOARD_DATA\s*=\s*({.*?});', content, re.DOTALL)
    if not data_match:
        print("❌ Could not find ENHANCED_DASHBOARD_DATA in file")
        return
        
    data_str = data_match.group(1)
    # Simple JS to Python conversion for the data object
    data_str = data_str.replace('true', 'True').replace('false', 'False').replace('null', 'None').replace('NaN', 'None')
    
    try:
        data = eval(data_str)
    except Exception as e:
        print(f"❌ Error parsing dashboard data: {e}")
        return
        
    print(f"✅ Total reviews loaded: {len(data['reviews'])}")
    
    # Count categories manually from reviews (excluding App Praise)
    category_counts = {}
    app_praise_count = 0
    
    for review in data['reviews']:
        category = review.get('category', 'Unknown')
        if category == 'App Praise':
            app_praise_count += 1
        else:
            category_counts[category] = category_counts.get(category, 0) + 1
    
    print(f"✅ Issue categories found (excluding App Praise): {len(category_counts)}")
    print(f"✅ App Praise reviews: {app_praise_count}")
    
    # Compare with summary data
    summary_categories = data['summary'].get('enhanced_category_distribution', {})
    print(f"✅ Categories in summary: {len(summary_categories)}")
    
    print("\n=== TOP 10 ISSUE CATEGORIES (Manual Count vs Summary) ===")
    top_manual = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    discrepancies = []
    for category, count in top_manual:
        summary_count = summary_categories.get(category, 0)
        if count == summary_count:
            status = "✅"
        else:
            status = f"❌ (summary: {summary_count})"
            discrepancies.append((category, count, summary_count))
        print(f"{category}: {count} {status}")
    
    # Check App Praise accuracy
    summary_app_praise = summary_categories.get('App Praise', 0)
    if app_praise_count == summary_app_praise:
        print(f"\n✅ App Praise: {app_praise_count} (matches summary)")
    else:
        print(f"\n❌ App Praise: {app_praise_count} (summary: {summary_app_praise})")
        discrepancies.append(('App Praise', app_praise_count, summary_app_praise))
    
    if discrepancies:
        print(f"\n❌ Found {len(discrepancies)} discrepancies that need fixing:")
        for category, actual, summary in discrepancies:
            print(f"  - {category}: actual={actual}, summary={summary}")
    else:
        print("\n✅ All category counts are accurate!")
        
    # Check for missing categories in color map
    print("\n=== COLOR MAPPING VERIFICATION ===")
    with open('html_dashboard/dashboard.html', 'r') as f:
        html_content = f.read()
    
    # Extract category color map
    color_map_match = re.search(r'categoryColorMap\s*=\s*{([^}]+)}', html_content, re.DOTALL)
    if color_map_match:
        color_map_content = color_map_match.group(1)
        color_categories = re.findall(r"'([^']+)':", color_map_content)
        
        print(f"✅ Categories with colors defined: {len(color_categories)}")
        
        # Find categories without colors
        all_categories = set(category_counts.keys()) | {'App Praise'}
        missing_colors = all_categories - set(color_categories)
        
        if missing_colors:
            print(f"❌ Categories missing colors: {missing_colors}")
        else:
            print("✅ All categories have colors defined")
    else:
        print("❌ Could not find categoryColorMap in HTML")

if __name__ == "__main__":
    main()