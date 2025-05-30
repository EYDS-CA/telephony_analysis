#!/usr/bin/env python3
"""
Customer Support Category Refinement Script
Analyzes reviews categorized as "Customer Support" to identify
more specific, actionable categories they should belong to.
"""

import pandas as pd
import re
import os
import json
from datetime import datetime

def categorize_customer_support_review(content):
    """
    Categorize a review currently labeled as 'Customer Support'
    Returns the most appropriate specific category
    """
    content_lower = content.lower()
    
    # Keywords for Billing issues (specific billing problems vs general CS)
    billing_keywords = [
        'bill', 'billing', 'invoice', 'charge', 'charged', 'payment',
        'autopay', 'auto pay', 'statement', 'balance', 'overcharge',
        'wrong charge', 'billing error', 'billing issue', 'credit',
        'refund', 'dispute', 'billing department', 'account balance'
    ]
    
    # Keywords for Authentication/Account Access issues
    authentication_keywords = [
        'login', 'log in', 'sign in', 'signin', 'password', 'username',
        'can\'t login', 'cant login', 'cannot login', 'access', 'locked out',
        'account locked', 'reset password', 'forgot password', 'verification',
        'account access', 'two factor', '2fa', 'security question'
    ]
    
    # Keywords for Service Quality/Reliability issues
    service_quality_keywords = [
        'service', 'outage', 'down', 'interruption', 'reliability', 'quality',
        'service problems', 'poor service', 'service issues', 'connection',
        'signal', 'coverage', 'network', 'internet down', 'phone service'
    ]
    
    # Keywords for Pricing/Value concerns (pricing discussions with CS)
    pricing_keywords = [
        'price', 'cost', 'expensive', 'cheap', 'rate', 'plan', 'package',
        'promotion', 'deal', 'discount', 'pricing', 'better deal',
        'competitive', 'quote', 'estimate', 'package deal'
    ]
    
    # Keywords for Technical Issues (technical problems discussed with CS)
    technical_keywords = [
        'technical', 'tech support', 'technical support', 'error', 'bug',
        'glitch', 'not working', 'broken', 'malfunction', 'trouble',
        'technical issue', 'technical problem', 'device', 'equipment'
    ]
    
    # Keywords for Wait Times/Phone Support specific issues
    wait_time_keywords = [
        'wait', 'waiting', 'hold', 'on hold', 'wait time', 'queue',
        'phone', 'call', 'calling', 'phone support', 'call center',
        'transferred', 'transfer', 'hung up', 'disconnect', 'busy'
    ]
    
    # Keywords for Staff/Agent Quality issues
    staff_quality_keywords = [
        'rude', 'unhelpful', 'helpful', 'polite', 'impolite', 'nice',
        'representative', 'rep', 'agent', 'staff', 'employee',
        'customer service rep', 'service rep', 'friendly', 'unfriendly',
        'professional', 'unprofessional', 'attitude', 'supervisor'
    ]
    
    # Keywords for Resolution/Follow-up issues
    resolution_keywords = [
        'resolve', 'solved', 'unsolved', 'fixed', 'unfixed', 'follow up',
        'follow-up', 'callback', 'call back', 'promised', 'never called',
        'no resolution', 'unresolved', 'escalate', 'escalated'
    ]
    
    # Keywords for Installation/Setup support
    installation_keywords = [
        'install', 'installation', 'setup', 'technician', 'appointment',
        'service call', 'home visit', 'installer', 'schedule', 'reschedule'
    ]
    
    # Check for specific categories in order of specificity
    
    # Billing issues (most specific business category)
    if any(keyword in content_lower for keyword in billing_keywords):
        return 'Billing'
    
    # Authentication/Account access
    if any(keyword in content_lower for keyword in authentication_keywords):
        return 'Authentication'
    
    # Service Quality/Reliability
    if any(keyword in content_lower for keyword in service_quality_keywords):
        return 'Service Quality'
    
    # Pricing/Value discussions
    if any(keyword in content_lower for keyword in pricing_keywords):
        return 'Pricing/Value Comments'
    
    # Technical support
    if any(keyword in content_lower for keyword in technical_keywords):
        return 'Technical Issues'
    
    # Installation/Setup
    if any(keyword in content_lower for keyword in installation_keywords):
        return 'Service Issues'
    
    # Wait times (specific CS process issue)
    if any(keyword in content_lower for keyword in wait_time_keywords):
        return 'Customer Support'  # Keep as CS for wait time issues
    
    # Staff quality (specific CS experience issue)
    if any(keyword in content_lower for keyword in staff_quality_keywords):
        return 'Customer Support'  # Keep as CS for staff quality issues
    
    # Resolution issues (specific CS process issue)
    if any(keyword in content_lower for keyword in resolution_keywords):
        return 'Customer Support'  # Keep as CS for resolution issues
    
    # If no specific keywords found, keep as Customer Support
    return 'Customer Support'

def analyze_customer_support_reviews():
    """Extract and analyze Customer Support reviews"""
    
    print("Analyzing Customer Support reviews for better categorization...")
    
    # Load the current dashboard data file to get the reviews
    dashboard_file = 'html_dashboard/dashboard_complete_enhanced.js'
    if not os.path.exists(dashboard_file):
        print(f"Dashboard file not found: {dashboard_file}")
        return
    
    # Extract reviews from the JavaScript file
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the ENHANCED_DASHBOARD_DATA object
    match = re.search(r'window\.ENHANCED_DASHBOARD_DATA = ({.*?});', content, re.DOTALL)
    if not match:
        print("Could not extract dashboard data from JavaScript file")
        return
    
    try:
        data = json.loads(match.group(1))
        reviews = data.get('reviews', [])
        print(f"Loaded {len(reviews)} reviews from dashboard data")
        
        # Filter for Customer Support reviews
        customer_support_reviews = [r for r in reviews if r.get('category') == 'Customer Support']
        print(f"Found {len(customer_support_reviews)} Customer Support reviews")
        
        if len(customer_support_reviews) == 0:
            print("No Customer Support reviews found")
            return
        
        # Analyze and categorize
        changes = []
        
        for review in customer_support_reviews:
            content = review.get('content', '')
            current_category = review.get('category', '')
            
            # Get new category suggestion
            new_category = categorize_customer_support_review(content)
            
            if new_category != current_category:
                changes.append({
                    'id': review.get('id', ''),
                    'app': review.get('app', ''),
                    'platform': review.get('platform', ''),
                    'rating': review.get('rating', ''),
                    'date': review.get('date', ''),
                    'content': content,
                    'old_category': current_category,
                    'new_category': new_category
                })
        
        # Summary
        print(f"\n=== CUSTOMER SUPPORT ANALYSIS SUMMARY ===")
        print(f"Total Customer Support reviews analyzed: {len(customer_support_reviews)}")
        print(f"Reviews that could be recategorized: {len(changes)}")
        print(f"Reviews remaining as Customer Support: {len(customer_support_reviews) - len(changes)}")
        
        if changes:
            # Save changes report
            changes_df = pd.DataFrame(changes)
            changes_file = f'customer_support_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            changes_df.to_csv(changes_file, index=False)
            print(f"Potential changes saved to: {changes_file}")
            
            # Show category distribution of suggested changes
            print(f"\nSuggested new category distribution:")
            new_categories = changes_df['new_category'].value_counts()
            for category, count in new_categories.items():
                print(f"  {category}: {count}")
            
            # Show sample changes by new category
            print(f"\n=== SAMPLE SUGGESTED CHANGES ===")
            for new_cat in new_categories.index[:6]:
                sample_changes = changes_df[changes_df['new_category'] == new_cat].head(2)
                print(f"\n{new_cat} ({new_categories[new_cat]} suggested changes):")
                for _, change in sample_changes.iterrows():
                    print(f"  • {change['app']} | {change['platform']} | Rating: {change['rating']}")
                    print(f"    \"{change['content'][:100]}...\"")
                    
            # Show highly specific examples
            print(f"\n=== HIGHLY SPECIFIC EXAMPLES THAT SHOULD BE RECATEGORIZED ===")
            
            # Billing examples
            billing_examples = changes_df[changes_df['new_category'] == 'Billing'].head(3)
            if not billing_examples.empty:
                print(f"\nBilling examples:")
                for _, ex in billing_examples.iterrows():
                    print(f"  • \"{ex['content'][:120]}...\"")
            
            # Service Quality examples  
            service_examples = changes_df[changes_df['new_category'] == 'Service Quality'].head(3)
            if not service_examples.empty:
                print(f"\nService Quality examples:")
                for _, ex in service_examples.iterrows():
                    print(f"  • \"{ex['content'][:120]}...\"")
                    
            # Authentication examples
            auth_examples = changes_df[changes_df['new_category'] == 'Authentication'].head(3)
            if not auth_examples.empty:
                print(f"\nAuthentication examples:")
                for _, ex in auth_examples.iterrows():
                    print(f"  • \"{ex['content'][:120]}...\"")
        
        else:
            print("No recategorization suggestions found - all Customer Support reviews are appropriately categorized!")
            
        return changes
        
    except Exception as e:
        print(f"Error analyzing dashboard data: {e}")
        return None

def create_apply_script(changes):
    """Create a script to apply the suggested changes"""
    if not changes:
        return
        
    script_content = f'''#!/usr/bin/env python3
"""
Apply Customer Support categorization fixes to dashboard data
Generated automatically on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
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
    changes_file = 'customer_support_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    if not os.path.exists(changes_file):
        print(f"Changes file not found: {{changes_file}}")
        return
    
    changes_df = pd.read_csv(changes_file)
    print(f"Loaded {{len(changes_df)}} suggested changes")
    
    # Load the dashboard data
    dashboard_file = 'html_dashboard/dashboard_complete_enhanced.js'
    if not os.path.exists(dashboard_file):
        print(f"Dashboard file not found: {{dashboard_file}}")
        return
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract the data object
    match = re.search(r'window\\.ENHANCED_DASHBOARD_DATA = ({{.*?}});', content, re.DOTALL)
    if not match:
        print("Could not extract dashboard data from JavaScript file")
        return
    
    try:
        data = json.loads(match.group(1))
        reviews = data.get('reviews', [])
        print(f"Loaded {{len(reviews)}} reviews from dashboard data")
        
        # Create a mapping for quick lookups
        changes_map = {{}}
        for _, change in changes_df.iterrows():
            key = (change['id'], change['content'][:100])  # Use ID and first 100 chars as key
            changes_map[key] = change['new_category']
        
        # Apply changes
        changes_applied = 0
        category_changes = {{}}
        
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
                        print(f"✅ {{changes_applied}}. {{review.get('app', '')}} | {{content[:60]}}... → {{new_category}}")
        
        # Update summary statistics
        summary = data.get('summary', {{}})
        enhanced_category_dist = summary.get('enhanced_category_distribution', {{}})
        
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
        js_content = f\'\'\'// Enhanced Dashboard Data with Refined Customer Support Categorization
// Generated: {{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}}
// Dataset: {{len(reviews)}} reviews with refined categories
// Customer Support refined: {{changes_applied}} reviews recategorized

window.ENHANCED_DASHBOARD_DATA = {{json.dumps(data, indent=4, ensure_ascii=False)}};

// Export for global access
if (typeof window !== 'undefined') {{{{
    window.DASHBOARD_DATA = window.ENHANCED_DASHBOARD_DATA; // Legacy compatibility
    window.COMPLETE_DASHBOARD_DATA = window.ENHANCED_DASHBOARD_DATA; // Alternative name
}}}}

// For Node.js environments
if (typeof module !== 'undefined' && module.exports) {{{{
    module.exports = window.ENHANCED_DASHBOARD_DATA;
}}}}\'\'\'
        
        # Save the updated file
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"\\n=== CHANGES APPLIED SUCCESSFULLY ===")
        print(f"Total changes applied: {{changes_applied}}")
        print(f"Reviews remaining as Customer Support: {{enhanced_category_dist.get('Customer Support', 0)}}")
        
        print(f"\\nCategory increases:")
        for category, count in sorted(category_changes.items(), key=lambda x: x[1], reverse=True):
            print(f"  {{category}}: +{{count}}")
        
        print(f"\\nUpdated dashboard data saved to: {{dashboard_file}}")
        
        return changes_applied, category_changes
        
    except Exception as e:
        print(f"Error applying fixes: {{e}}")
        return None, None

if __name__ == "__main__":
    apply_customer_support_fixes()
'''
    
    script_file = f'apply_customer_support_fixes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
    with open(script_file, 'w') as f:
        f.write(script_content)
    
    print(f"\\nApply script created: {script_file}")
    print("Review the suggested changes and run the script if they look appropriate.")

if __name__ == "__main__":
    changes = analyze_customer_support_reviews()
    if changes:
        create_apply_script(changes)