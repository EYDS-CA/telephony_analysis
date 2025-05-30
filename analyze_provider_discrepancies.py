#!/usr/bin/env python3
"""
Analyze category distribution differences between Rogers and Bell
"""
import re

def main():
    print("=== ROGERS vs BELL CATEGORY ANALYSIS ===")
    
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
    
    # Count categories by provider from actual reviews
    rogers_categories = {}
    bell_categories = {}
    
    for review in data['reviews']:
        category = review.get('category', 'Unknown')
        app = review.get('app', '').lower()
        
        if category != 'App Praise':  # Exclude App Praise from issue analysis
            if app == 'rogers':
                rogers_categories[category] = rogers_categories.get(category, 0) + 1
            elif app == 'bell':
                bell_categories[category] = bell_categories.get(category, 0) + 1
    
    print(f"✅ Rogers categories: {len(rogers_categories)}")
    print(f"✅ Bell categories: {len(bell_categories)}")
    
    # Find categories that appear in one provider but not the other
    rogers_only = set(rogers_categories.keys()) - set(bell_categories.keys())
    bell_only = set(bell_categories.keys()) - set(rogers_categories.keys())
    common_categories = set(rogers_categories.keys()) & set(bell_categories.keys())
    
    print(f"\n=== CATEGORY DISTRIBUTION ANALYSIS ===")
    print(f"Categories in both: {len(common_categories)}")
    print(f"Rogers only: {len(rogers_only)}")
    print(f"Bell only: {len(bell_only)}")
    
    if rogers_only:
        print(f"\n📱 ROGERS-ONLY CATEGORIES:")
        for category in sorted(rogers_only):
            count = rogers_categories[category]
            print(f"  - {category}: {count} reviews")
    
    if bell_only:
        print(f"\n🔔 BELL-ONLY CATEGORIES:")
        for category in sorted(bell_only):
            count = bell_categories[category]
            print(f"  - {category}: {count} reviews")
    
    # Show top categories for each provider
    print(f"\n📱 TOP 10 ROGERS CATEGORIES:")
    rogers_top = sorted(rogers_categories.items(), key=lambda x: x[1], reverse=True)[:10]
    for category, count in rogers_top:
        bell_count = bell_categories.get(category, 0)
        print(f"  {category}: {count} (Bell: {bell_count})")
    
    print(f"\n🔔 TOP 10 BELL CATEGORIES:")
    bell_top = sorted(bell_categories.items(), key=lambda x: x[1], reverse=True)[:10]
    for category, count in bell_top:
        rogers_count = rogers_categories.get(category, 0)
        print(f"  {category}: {count} (Rogers: {rogers_count})")
    
    # Check specific categories mentioned by user
    print(f"\n=== SPECIFIC CATEGORY VERIFICATION ===")
    
    auth_rogers = rogers_categories.get('Authentication', 0)
    auth_bell = bell_categories.get('Authentication', 0)
    print(f"Authentication - Rogers: {auth_rogers}, Bell: {auth_bell}")
    
    pricing_rogers = rogers_categories.get('Pricing/Value Comments', 0)
    pricing_bell = bell_categories.get('Pricing/Value Comments', 0)
    print(f"Pricing/Value Comments - Rogers: {pricing_rogers}, Bell: {pricing_bell}")
    
    # Check if this matches the summary data
    summary_rogers = data['summary'].get('enhanced_category_by_provider', {}).get('rogers', {}).get('categories', {})
    summary_bell = data['summary'].get('enhanced_category_by_provider', {}).get('bell', {}).get('categories', {})
    
    print(f"\n=== SUMMARY DATA VERIFICATION ===")
    auth_rogers_summary = summary_rogers.get('Authentication', 0)
    auth_bell_summary = summary_bell.get('Authentication', 0)
    print(f"Authentication (Summary) - Rogers: {auth_rogers_summary}, Bell: {auth_bell_summary}")
    
    pricing_rogers_summary = summary_rogers.get('Pricing/Value Comments', 0)
    pricing_bell_summary = summary_bell.get('Pricing/Value Comments', 0)
    print(f"Pricing/Value Comments (Summary) - Rogers: {pricing_rogers_summary}, Bell: {pricing_bell_summary}")
    
    # Find discrepancies
    discrepancies = []
    if auth_rogers != auth_rogers_summary:
        discrepancies.append(f"Rogers Authentication: actual={auth_rogers}, summary={auth_rogers_summary}")
    if auth_bell != auth_bell_summary:
        discrepancies.append(f"Bell Authentication: actual={auth_bell}, summary={auth_bell_summary}")
    if pricing_rogers != pricing_rogers_summary:
        discrepancies.append(f"Rogers Pricing/Value: actual={pricing_rogers}, summary={pricing_rogers_summary}")
    if pricing_bell != pricing_bell_summary:
        discrepancies.append(f"Bell Pricing/Value: actual={pricing_bell}, summary={pricing_bell_summary}")
    
    if discrepancies:
        print(f"\n❌ DISCREPANCIES FOUND:")
        for disc in discrepancies:
            print(f"  - {disc}")
    else:
        print(f"\n✅ No discrepancies found between actual counts and summary")
    
    # Check what the top 8 categories would be for each provider (what shows in charts)
    print(f"\n=== CHART TOP 8 CATEGORIES ===")
    print(f"📱 Rogers Top 8 (shown in chart):")
    for i, (category, count) in enumerate(rogers_top[:8]):
        print(f"  {i+1}. {category}: {count}")
    
    print(f"\n🔔 Bell Top 8 (shown in chart):")
    for i, (category, count) in enumerate(bell_top[:8]):
        print(f"  {i+1}. {category}: {count}")

if __name__ == "__main__":
    main()