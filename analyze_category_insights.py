#!/usr/bin/env python3
"""
Analyze category differences to generate insights for chart annotations
"""
import re

def main():
    print("=== ANALYZING CATEGORY INSIGHTS ===")
    
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
    
    # Calculate categories for each provider
    def calculate_categories(filter_app=None):
        categories = {}
        for review in data['reviews']:
            if filter_app and review.get('app', '').lower() != filter_app:
                continue
            category = review.get('category', 'Unknown')
            if category != 'App Praise':  # Exclude App Praise from issues
                categories[category] = categories.get(category, 0) + 1
        return categories
    
    all_categories = calculate_categories()
    rogers_categories = calculate_categories('rogers')
    bell_categories = calculate_categories('bell')
    
    # Get top 8 for each
    all_top8 = dict(sorted(all_categories.items(), key=lambda x: x[1], reverse=True)[:8])
    rogers_top8 = dict(sorted(rogers_categories.items(), key=lambda x: x[1], reverse=True)[:8])
    bell_top8 = dict(sorted(bell_categories.items(), key=lambda x: x[1], reverse=True)[:8])
    
    print(f"✅ Calculated top 8 for all providers")
    
    # Find interesting insights
    insights = {
        'all': [],
        'rogers': [],
        'bell': []
    }
    
    # Categories that appear in one provider's top 8 but not the other
    rogers_unique = set(rogers_top8.keys()) - set(bell_top8.keys())
    bell_unique = set(bell_top8.keys()) - set(rogers_top8.keys())
    
    print(f"\n=== PROVIDER-SPECIFIC INSIGHTS ===")
    
    # Rogers-specific insights
    for category in rogers_unique:
        rogers_count = rogers_categories[category]
        bell_count = bell_categories.get(category, 0)
        if bell_count > 0:
            ratio = rogers_count / bell_count
            insights['rogers'].append(f"{category}: {ratio:.1f}x more issues than Bell ({rogers_count} vs {bell_count})")
        else:
            insights['rogers'].append(f"{category}: Rogers-exclusive issue ({rogers_count} reviews)")
        print(f"📱 Rogers: {insights['rogers'][-1]}")
    
    # Bell-specific insights  
    for category in bell_unique:
        bell_count = bell_categories[category]
        rogers_count = rogers_categories.get(category, 0)
        if rogers_count > 0:
            ratio = bell_count / rogers_count
            insights['bell'].append(f"{category}: {ratio:.1f}x more issues than Rogers ({bell_count} vs {rogers_count})")
        else:
            insights['bell'].append(f"{category}: Bell-exclusive issue ({bell_count} reviews)")
        print(f"🔔 Bell: {insights['bell'][-1]}")
    
    # Categories with significant differences (even if both in top 8)
    common_categories = set(rogers_top8.keys()) & set(bell_top8.keys())
    
    print(f"\n=== SIGNIFICANT DIFFERENCES IN COMMON CATEGORIES ===")
    for category in common_categories:
        rogers_count = rogers_categories[category]
        bell_count = bell_categories[category]
        
        # Calculate ratio (higher / lower)
        if rogers_count > bell_count:
            ratio = rogers_count / bell_count
            if ratio >= 2.0:  # Significant difference
                insight = f"{category}: Rogers reports {ratio:.1f}x more issues ({rogers_count} vs {bell_count})"
                insights['rogers'].append(insight)
                print(f"📱 {insight}")
        else:
            ratio = bell_count / rogers_count
            if ratio >= 1.5:  # Lower threshold for Bell since they have fewer total reviews
                insight = f"{category}: Bell reports {ratio:.1f}x more issues ({bell_count} vs {rogers_count})"
                insights['bell'].append(insight)
                print(f"🔔 {insight}")
    
    # Categories just outside top 8 that are interesting
    print(f"\n=== NOTABLE CATEGORIES JUST OUTSIDE TOP 8 ===")
    
    # Rogers categories ranked 9-12
    rogers_all = sorted(rogers_categories.items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(rogers_all[8:12], 9):
        if category in bell_top8:
            bell_rank = list(bell_top8.keys()).index(category) + 1
            insight = f"{category}: Ranks #{bell_rank} for Bell but #{i} for Rogers"
            insights['all'].append(insight)
            print(f"📊 {insight}")
    
    # Bell categories ranked 9-12
    bell_all = sorted(bell_categories.items(), key=lambda x: x[1], reverse=True)
    for i, (category, count) in enumerate(bell_all[8:12], 9):
        if category in rogers_top8:
            rogers_rank = list(rogers_top8.keys()).index(category) + 1
            insight = f"{category}: Ranks #{rogers_rank} for Rogers but #{i} for Bell"
            if insight not in [x for x in insights['all']]:  # Avoid duplicates
                insights['all'].append(insight)
                print(f"📊 {insight}")
    
    # Generate final insights for UI
    print(f"\n=== FINAL INSIGHTS FOR UI ===")
    
    # Select top 2-3 most interesting insights for each view
    final_insights = {
        'all': insights['all'][:2],
        'rogers': [x for x in insights['rogers'] if any(keyword in x for keyword in ['Authentication', 'App Crashes', 'Performance'])][:2],
        'bell': [x for x in insights['bell'] if any(keyword in x for keyword in ['Pricing/Value', 'Billing', 'General Dissatisfaction'])][:2]
    }
    
    print(f"\n📊 ALL PROVIDERS:")
    for insight in final_insights['all']:
        print(f"  • {insight}")
    
    print(f"\n📱 ROGERS:")
    for insight in final_insights['rogers']:
        print(f"  • {insight}")
    
    print(f"\n🔔 BELL:")
    for insight in final_insights['bell']:
        print(f"  • {insight}")
    
    return final_insights

if __name__ == "__main__":
    main()