#!/usr/bin/env python3
"""
Fix the summary data discrepancies in dashboard
"""
import re
import json

def main():
    print("=== FIXING SUMMARY DATA DISCREPANCIES ===")
    
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
    
    # Recalculate all category distributions from actual reviews
    total_categories = {}
    rogers_categories = {}
    bell_categories = {}
    rogers_total = 0
    bell_total = 0
    
    for review in data['reviews']:
        category = review.get('category', 'Unknown')
        app = review.get('app', '').lower()
        
        # Count total categories
        total_categories[category] = total_categories.get(category, 0) + 1
        
        # Count by provider
        if app == 'rogers':
            rogers_categories[category] = rogers_categories.get(category, 0) + 1
            rogers_total += 1
        elif app == 'bell':
            bell_categories[category] = bell_categories.get(category, 0) + 1
            bell_total += 1
    
    print(f"✅ Rogers reviews: {rogers_total}")
    print(f"✅ Bell reviews: {bell_total}")
    print(f"✅ Total categories: {len(total_categories)}")
    
    # Update the data structure
    data['summary']['enhanced_category_distribution'] = total_categories
    data['summary']['enhanced_category_by_provider'] = {
        'rogers': {
            'total': rogers_total,
            'categories': rogers_categories
        },
        'bell': {
            'total': bell_total,
            'categories': bell_categories
        }
    }
    
    # Convert back to JavaScript format
    def python_to_js(obj, indent=0):
        spaces = "    " * indent
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            lines = ["{"]
            items = list(obj.items())
            for i, (key, value) in enumerate(items):
                comma = "," if i < len(items) - 1 else ""
                if isinstance(key, str):
                    key_str = f'"{key}"'
                else:
                    key_str = str(key)
                val_str = python_to_js(value, indent + 1)
                lines.append(f"{spaces}    {key_str}: {val_str}{comma}")
            lines.append(f"{spaces}}}")
            return "\n".join(lines)
        elif isinstance(obj, list):
            if not obj:
                return "[]"
            lines = ["["]
            for i, item in enumerate(obj):
                comma = "," if i < len(obj) - 1 else ""
                val_str = python_to_js(item, indent + 1)
                lines.append(f"{spaces}    {val_str}{comma}")
            lines.append(f"{spaces}]")
            return "\n".join(lines)
        elif isinstance(obj, str):
            # Escape quotes and handle special characters
            escaped = obj.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
            return f'"{escaped}"'
        elif obj is None:
            return "null"
        elif isinstance(obj, bool):
            return "true" if obj else "false"
        else:
            return str(obj)
    
    # Create the new JavaScript content
    js_data = python_to_js(data)
    new_content = f"window.ENHANCED_DASHBOARD_DATA = {js_data};"
    
    # Write the updated file
    with open('html_dashboard/dashboard_complete_enhanced.js', 'w') as f:
        f.write(new_content)
    
    print(f"\n✅ Updated dashboard data with corrected summary")
    
    # Verify the fix
    print(f"\n=== VERIFICATION ===")
    print(f"Rogers Authentication: {rogers_categories.get('Authentication', 0)}")
    print(f"Bell Authentication: {bell_categories.get('Authentication', 0)}")
    print(f"Rogers Pricing/Value: {rogers_categories.get('Pricing/Value Comments', 0)}")
    print(f"Bell Pricing/Value: {bell_categories.get('Pricing/Value Comments', 0)}")
    
    # Show top 8 for each provider
    rogers_top = sorted(rogers_categories.items(), key=lambda x: x[1], reverse=True)[:8]
    bell_top = sorted(bell_categories.items(), key=lambda x: x[1], reverse=True)[:8]
    
    print(f"\n📱 Rogers Top 8:")
    for i, (cat, count) in enumerate(rogers_top):
        if cat != 'App Praise':
            print(f"  {i+1}. {cat}: {count}")
    
    print(f"\n🔔 Bell Top 8:")
    for i, (cat, count) in enumerate(bell_top):
        if cat != 'App Praise':
            print(f"  {i+1}. {cat}: {count}")

if __name__ == "__main__":
    main()