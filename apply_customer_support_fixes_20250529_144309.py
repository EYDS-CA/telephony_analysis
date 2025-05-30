#!/usr/bin/env python3
"""
Apply Customer Support categorization fixes to dashboard data
Generated automatically on 2025-05-29 14:43:09
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

if __name__ == "__main__":
    apply_customer_support_fixes()
