import pandas as pd
import json
from datetime import datetime
import re
from collections import Counter, defaultdict

# Load the original dataset
print("Loading reviews...")
df = pd.read_csv('telecom_app_reviews_complete.csv')
print(f"Total reviews: {len(df):,}")

# Convert date to datetime
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year

def categorize_review_enhanced(row):
    """
    Enhanced categorization based on the new comprehensive system
    Returns: primary_focus, category, subcategory
    """
    text = (str(row['text']) + ' ' + str(row['claude_summary'])).lower()
    
    # Initialize
    primary_focus = "UNCLEAR"
    category = ""
    subcategory = ""
    
    # App-related keywords and patterns
    app_patterns = {
        'crashes': r'crash|keeps closing|stops working|force close|shut down|shuts off',
        'login': r'log\s?in|sign\s?in|password|authentication|verify device|can\'t access|locked out',
        'performance': r'slow|lag|freeze|loading|takes forever|spinning|unresponsive',
        'ui_navigation': r'confusing|hard to use|can\'t find|navigation|design|interface|menu|layout',
        'bugs': r'bug|glitch|error|not working|doesn\'t work|broken|fail',
        'installation': r'install|update|download|compatible|version',
        'features': r'feature|function|option|missing|want|need|request',
        'notifications': r'notification|alert|reminder',
        'data_sync': r'sync|refresh|update data|wrong information|not updating'
    }
    
    # Service-related keywords
    service_patterns = {
        'billing': r'bill|charge|payment|invoice|overcharge|fee|cost|price',
        'network': r'network|coverage|signal|connection|data plan|roaming',
        'customer_service': r'customer service|support|help|contact|representative|agent|call center',
        'account': r'account|plan|upgrade|cancel|subscription|contract'
    }
    
    # Check for app-related issues
    app_matches = []
    for pattern_name, pattern in app_patterns.items():
        if re.search(pattern, text):
            app_matches.append(pattern_name)
    
    # Check for service-related issues
    service_matches = []
    for pattern_name, pattern in service_patterns.items():
        if re.search(pattern, text):
            service_matches.append(pattern_name)
    
    # Determine primary focus
    if app_matches and not service_matches:
        primary_focus = "APP-RELATED"
    elif service_matches and not app_matches:
        primary_focus = "SERVICE-RELATED"
    elif app_matches and service_matches:
        primary_focus = "MIXED"
    
    # Assign specific categories based on matches
    if app_matches:
        # Prioritize critical app issues
        if 'crashes' in app_matches:
            category = "App Stability"
            subcategory = "Crashes & Freezes"
        elif 'login' in app_matches:
            category = "Authentication"
            subcategory = "Login & Access Issues"
        elif 'performance' in app_matches:
            category = "Performance"
            subcategory = "Speed & Responsiveness"
        elif 'ui_navigation' in app_matches:
            category = "User Experience"
            subcategory = "Navigation & Design"
        elif 'bugs' in app_matches:
            category = "Functionality"
            subcategory = "Bugs & Errors"
        elif 'installation' in app_matches:
            category = "App Management"
            subcategory = "Installation & Updates"
        else:
            category = "App Features"
            subcategory = app_matches[0].replace('_', ' ').title()
    
    elif service_matches:
        # Prioritize service issues
        if 'billing' in service_matches:
            category = "Billing & Charges"
            subcategory = "Payment & Invoice Issues"
        elif 'network' in service_matches:
            category = "Network & Connectivity"
            subcategory = "Service Quality"
        elif 'customer_service' in service_matches:
            category = "Customer Support"
            subcategory = "Service Experience"
        elif 'account' in service_matches:
            category = "Account Management"
            subcategory = "Plans & Services"
    
    # Handle sentiment-based categorization for unclear cases
    if primary_focus == "UNCLEAR":
        if row['claude_sentiment'] == 'Positive':
            primary_focus = "GENERAL-POSITIVE"
            category = "Positive Feedback"
            subcategory = "General Satisfaction"
        elif row['claude_sentiment'] == 'Negative':
            primary_focus = "GENERAL-NEGATIVE"
            category = "General Complaints"
            subcategory = "Overall Dissatisfaction"
    
    return primary_focus, category, subcategory

# Apply enhanced categorization
print("\nApplying enhanced categorization...")
categorization_results = df.apply(categorize_review_enhanced, axis=1)
df['enhanced_primary_focus'] = categorization_results.apply(lambda x: x[0])
df['enhanced_category'] = categorization_results.apply(lambda x: x[1])
df['enhanced_subcategory'] = categorization_results.apply(lambda x: x[2])

# Generate statistics
print("\nCategorization Statistics:")
print(df['enhanced_primary_focus'].value_counts())
print("\nTop Categories:")
print(df['enhanced_category'].value_counts().head(10))

# Analyze critical user flows
def analyze_critical_flows(df):
    """Identify critical user stories and flows based on review patterns"""
    
    # Define critical flows in telecom apps
    critical_flows = {
        "Bill Payment Flow": ['bill', 'payment', 'pay', 'invoice'],
        "Usage Monitoring": ['usage', 'data', 'minutes', 'balance'],
        "Plan Management": ['plan', 'upgrade', 'change', 'add-on'],
        "Account Access": ['login', 'sign in', 'password', 'access'],
        "Customer Support": ['help', 'support', 'contact', 'chat'],
        "Service Activation": ['activate', 'setup', 'new', 'start']
    }
    
    flow_analysis = {}
    for flow_name, keywords in critical_flows.items():
        pattern = '|'.join(keywords)
        matching_reviews = df[df['text'].str.contains(pattern, case=False, na=False)]
        
        flow_analysis[flow_name] = {
            'total_mentions': len(matching_reviews),
            'negative_percentage': (matching_reviews['claude_sentiment'] == 'Negative').sum() / len(matching_reviews) * 100 if len(matching_reviews) > 0 else 0,
            'avg_rating': matching_reviews['rating'].mean() if len(matching_reviews) > 0 else 0
        }
    
    return flow_analysis

# Analyze by provider and platform
rogers_ios = df[(df['app_name'] == 'Rogers') & (df['platform'] == 'iOS')]
rogers_android = df[(df['app_name'] == 'Rogers') & (df['platform'] == 'Android')]
bell_ios = df[(df['app_name'] == 'Bell') & (df['platform'] == 'iOS')]
bell_android = df[(df['app_name'] == 'Bell') & (df['platform'] == 'Android')]

print(f"\nPlatform Distribution:")
print(f"Rogers iOS: {len(rogers_ios):,}")
print(f"Rogers Android: {len(rogers_android):,}")
print(f"Bell iOS: {len(bell_ios):,}")
print(f"Bell Android: {len(bell_android):,}")

# Get example reviews for each major issue
def get_example_reviews(df_subset, category, n=3):
    """Get example reviews for a specific category"""
    examples = df_subset[df_subset['enhanced_category'] == category].nlargest(n, 'thumbs_up')
    if len(examples) == 0:
        examples = df_subset[df_subset['enhanced_category'] == category].head(n)
    
    return examples[['text', 'rating', 'date', 'platform']].to_dict('records')

# Generate comprehensive insights data
insights_data = {
    'metadata': {
        'analysis_date': datetime.now().isoformat(),
        'total_reviews': len(df),
        'date_range': f"{df['date'].min()} to {df['date'].max()}"
    },
    
    'categorization_summary': {
        'primary_focus_distribution': df['enhanced_primary_focus'].value_counts().to_dict(),
        'top_categories': df['enhanced_category'].value_counts().head(15).to_dict(),
        'app_vs_service_breakdown': {
            'rogers': {
                'app_related': len(df[(df['app_name'] == 'Rogers') & (df['enhanced_primary_focus'] == 'APP-RELATED')]),
                'service_related': len(df[(df['app_name'] == 'Rogers') & (df['enhanced_primary_focus'] == 'SERVICE-RELATED')]),
                'mixed': len(df[(df['app_name'] == 'Rogers') & (df['enhanced_primary_focus'] == 'MIXED')])
            },
            'bell': {
                'app_related': len(df[(df['app_name'] == 'Bell') & (df['enhanced_primary_focus'] == 'APP-RELATED')]),
                'service_related': len(df[(df['app_name'] == 'Bell') & (df['enhanced_primary_focus'] == 'SERVICE-RELATED')]),
                'mixed': len(df[(df['app_name'] == 'Bell') & (df['enhanced_primary_focus'] == 'MIXED')])
            }
        }
    },
    
    'platform_comparison': {
        'rogers': {
            'ios': {
                'total_reviews': len(rogers_ios),
                'avg_rating': float(rogers_ios['rating'].mean()),
                'negative_percentage': float((rogers_ios['claude_sentiment'] == 'Negative').sum() / len(rogers_ios) * 100) if len(rogers_ios) > 0 else 0,
                'top_issues': rogers_ios['enhanced_category'].value_counts().head(5).to_dict(),
                'examples': {}
            },
            'android': {
                'total_reviews': len(rogers_android),
                'avg_rating': float(rogers_android['rating'].mean()),
                'negative_percentage': float((rogers_android['claude_sentiment'] == 'Negative').sum() / len(rogers_android) * 100) if len(rogers_android) > 0 else 0,
                'top_issues': rogers_android['enhanced_category'].value_counts().head(5).to_dict(),
                'examples': {}
            }
        },
        'bell': {
            'ios': {
                'total_reviews': len(bell_ios),
                'avg_rating': float(bell_ios['rating'].mean()) if len(bell_ios) > 0 else 0,
                'negative_percentage': float((bell_ios['claude_sentiment'] == 'Negative').sum() / len(bell_ios) * 100) if len(bell_ios) > 0 else 0,
                'top_issues': bell_ios['enhanced_category'].value_counts().head(5).to_dict() if len(bell_ios) > 0 else {},
                'examples': {}
            },
            'android': {
                'total_reviews': len(bell_android),
                'avg_rating': float(bell_android['rating'].mean()),
                'negative_percentage': float((bell_android['claude_sentiment'] == 'Negative').sum() / len(bell_android) * 100) if len(bell_android) > 0 else 0,
                'top_issues': bell_android['enhanced_category'].value_counts().head(5).to_dict(),
                'examples': {}
            }
        }
    },
    
    'critical_flows': analyze_critical_flows(df),
    
    'category_examples': {}
}

# Add example reviews for top categories
top_categories = df['enhanced_category'].value_counts().head(10).index
for category in top_categories:
    insights_data['category_examples'][category] = {
        'rogers': get_example_reviews(df[df['app_name'] == 'Rogers'], category, 2),
        'bell': get_example_reviews(df[df['app_name'] == 'Bell'], category, 2)
    }

# Save enhanced dataset
print("\nSaving enhanced dataset...")
df.to_csv('telecom_reviews_enhanced.csv', index=False)

# Save insights data
with open('html_dashboard/enhanced_insights_data.json', 'w') as f:
    json.dump(insights_data, f, indent=2, default=str)

print("\n✅ Recategorization complete!")
print(f"Enhanced dataset saved to: telecom_reviews_enhanced.csv")
print(f"Insights data saved to: html_dashboard/enhanced_insights_data.json")

# Generate summary statistics for dashboard
summary_stats = {
    'total_reviews': len(df),
    'rogers_reviews': len(df[df['app_name'] == 'Rogers']),
    'bell_reviews': len(df[df['app_name'] == 'Bell']),
    'categories': list(df['enhanced_category'].unique()),
    'years': sorted(list(df['year'].unique())),
    'platforms': list(df['platform'].unique())
}

with open('html_dashboard/dashboard_metadata.json', 'w') as f:
    json.dump(summary_stats, f, indent=2)

print("\nTop issues by provider:")
print("\nRogers:")
print(df[df['app_name'] == 'Rogers']['enhanced_category'].value_counts().head(5))
print("\nBell:")
print(df[df['app_name'] == 'Bell']['enhanced_category'].value_counts().head(5))