#!/usr/bin/env python3
"""
Apply Customer Support categorization fixes to dashboard data
"""

import pandas as pd
import json
import re
import os
from datetime import datetime

def apply_customer_support_fixes():
    """Apply the categorization fixes to the dashboard data"""
    
    print("Applying Customer Support categorization fixes...")
    
    # Load the suggested changes
    changes_file = 'customer_support_analysis_20250529_144309.csv'
    if not os.path.exists(changes_file):
        print(f"Changes file not found: {changes_file}")
        return
    
    changes_df = pd.read_csv(changes_file)
    print(f"Loaded {len(changes_df)} suggested changes")
    
    # Load the dashboard data
    dashboard_file = 'html_dashboard/dashboard_complete_enhanced.js'
    if not os.path.exists(dashboard_file):
        print(f"Dashboard file not found: {dashboard_file}")
        return
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the data object
    match = re.search(r'window\.ENHANCED_DASHBOARD_DATA = ({.*?});', content, re.DOTALL)
    if not match:
        print("Could not extract dashboard data from JavaScript file")
        return
    
    try:
        data = json.loads(match.group(1))
        reviews = data.get('reviews', [])
        print(f"Loaded {len(reviews)} reviews from dashboard data")
        
        # Create a mapping for quick lookups
        changes_map = {}
        for _, change in changes_df.iterrows():
            key = (change['id'], change['content'][:100])  # Use ID and first 100 chars as key
            changes_map[key] = change['new_category']
        
        # Apply changes
        changes_applied = 0
        category_changes = {}
        
        for review in reviews:
            review_id = review.get('id', '')
            content = review.get('content', '')
            current_category = review.get('category', '')
            
            if current_category == 'Customer Support':
                key = (review_id, content[:100])
                if key in changes_map:
                    new_category = changes_map[key]
                    review['category'] = new_category
                    changes_applied += 1
                    
                    # Track category changes for summary update
                    if new_category not in category_changes:
                        category_changes[new_category] = 0
                    category_changes[new_category] += 1
                    
                    if changes_applied <= 5:  # Show first 5 changes
                        print(f"✅ {changes_applied}. {review.get('app', '')} | {content[:60]}... → {new_category}")
        
        # Update summary statistics
        summary = data.get('summary', {})
        enhanced_category_dist = summary.get('enhanced_category_distribution', {})
        
        # Reduce Customer Support count
        if 'Customer Support' in enhanced_category_dist:
            enhanced_category_dist['Customer Support'] -= changes_applied
        
        # Increase counts for new categories
        for new_category, count in category_changes.items():
            if new_category in enhanced_category_dist:
                enhanced_category_dist[new_category] += count
            else:
                enhanced_category_dist[new_category] = count
        
        # Generate updated JavaScript content
        js_content = f'''// Enhanced Dashboard Data with Refined Customer Support Categorization
// Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
// Dataset: {len(reviews)} reviews with refined categories
// Customer Support refined: {changes_applied} reviews recategorized

window.ENHANCED_DASHBOARD_DATA = {json.dumps(data, indent=4, ensure_ascii=False)};

// Export for global access
if (typeof window !== 'undefined') {{
    window.DASHBOARD_DATA = window.ENHANCED_DASHBOARD_DATA; // Legacy compatibility
    window.COMPLETE_DASHBOARD_DATA = window.ENHANCED_DASHBOARD_DATA; // Alternative name
}}

// For Node.js environments
if (typeof module !== 'undefined' && module.exports) {{
    module.exports = window.ENHANCED_DASHBOARD_DATA;
}}'''
        
        # Save the updated file
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"\n=== CHANGES APPLIED SUCCESSFULLY ===")
        print(f"Total changes applied: {changes_applied}")
        print(f"Reviews remaining as Customer Support: {enhanced_category_dist.get('Customer Support', 0)}")
        
        print(f"\nCategory increases:")
        for category, count in sorted(category_changes.items(), key=lambda x: x[1], reverse=True):
            print(f"  {category}: +{count}")
        
        print(f"\nUpdated dashboard data saved to: {dashboard_file}")
        
        return changes_applied, category_changes
        
    except Exception as e:
        print(f"Error applying fixes: {e}")
        return None, None

def update_html_filter_dropdown(category_changes, total_changes):
    """Update the HTML filter dropdown with new category counts"""
    
    if not category_changes:
        return
    
    html_file = 'html_dashboard/dashboard.html'
    if not os.path.exists(html_file):
        print(f"HTML file not found: {html_file}")
        return
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Update specific category counts
    updates_made = 0
    
    # Customer Support: reduce by total changes
    current_customer_support = 828  # Current count
    new_customer_support = current_customer_support - total_changes
    
    html_content = html_content.replace(
        f'<option value="Customer Support">Customer Support (828)</option>',
        f'<option value="Customer Support">Customer Support ({new_customer_support:,})</option>'
    )
    updates_made += 1
    
    # Update other categories that increased
    category_current_counts = {
        'Service Quality': 267,
        'Billing': 162,
        'Authentication': 682,
        'Pricing/Value Comments': 515,
        'Technical Issues': 656,
        'Service Issues': 155
    }
    
    for category, increase in category_changes.items():
        if category in category_current_counts:
            current_count = category_current_counts[category]
            new_count = current_count + increase
            
            old_pattern = f'<option value="{category}">{category} ({current_count:,})</option>'
            new_pattern = f'<option value="{category}">{category} ({new_count:,})</option>'
            
            if old_pattern in html_content:
                html_content = html_content.replace(old_pattern, new_pattern)
                updates_made += 1
    
    # Save updated HTML
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Updated {updates_made} category counts in HTML filter dropdown")

if __name__ == "__main__":
    changes_applied, category_changes = apply_customer_support_fixes()
    if changes_applied and category_changes:
        update_html_filter_dropdown(category_changes, changes_applied)
        print(f"\n🎯 Customer Support category refinement complete!")
        print(f"   Before: 828 reviews")  
        print(f"   After: {828 - changes_applied} reviews")
        print(f"   Refined: {changes_applied} reviews ({round(changes_applied/828*100, 1)}%)")