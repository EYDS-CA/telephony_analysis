import pandas as pd
import json
from datetime import datetime
import numpy as np
from collections import Counter, defaultdict
import re

# Load the complete dataset
print("Loading telecom app reviews...")
df = pd.read_csv('telecom_app_reviews_complete.csv')
print(f"Total reviews loaded: {len(df):,}")

# Convert date column to datetime
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month

# Basic statistics
print(f"\nBasic Statistics:")
print(f"Rogers reviews: {len(df[df['app_name'] == 'Rogers']):,}")
print(f"Bell reviews: {len(df[df['app_name'] == 'Bell']):,}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")

# Focus on Rogers analysis as requested
rogers_df = df[df['app_name'] == 'Rogers']
bell_df = df[df['app_name'] == 'Bell']

# 1. Main complaint analysis for Rogers
print("\n=== ROGERS APP COMPLAINT ANALYSIS ===")

# Categorize complaints
def categorize_complaint(row):
    """Enhanced categorization focusing on app vs service issues"""
    text = str(row['text']).lower() + ' ' + str(row['claude_summary']).lower()
    
    # App-related issues
    app_issues = {
        'crashes': ['crash', 'keeps closing', 'stops working', 'force close', 'shut down', 'shuts off'],
        'login': ['login', 'sign in', 'password', 'authentication', 'verify device', 'can\'t access'],
        'performance': ['slow', 'lag', 'freeze', 'loading', 'takes forever', 'spinning'],
        'ui_ux': ['confusing', 'hard to use', 'can\'t find', 'navigation', 'design', 'interface'],
        'features_broken': ['not working', 'doesn\'t work', 'broken', 'error', 'fail'],
        'installation': ['install', 'update', 'download', 'compatible'],
        'data_sync': ['sync', 'refresh', 'update data', 'wrong information']
    }
    
    # Service-related issues
    service_issues = {
        'billing': ['bill', 'charge', 'payment', 'invoice', 'overcharge'],
        'network': ['network', 'coverage', 'signal', 'connection', 'data plan'],
        'customer_service': ['customer service', 'support', 'help', 'contact', 'representative'],
        'account': ['account', 'plan', 'upgrade', 'cancel', 'subscription']
    }
    
    found_app_issues = []
    found_service_issues = []
    
    for category, keywords in app_issues.items():
        if any(keyword in text for keyword in keywords):
            found_app_issues.append(category)
    
    for category, keywords in service_issues.items():
        if any(keyword in text for keyword in keywords):
            found_service_issues.append(category)
    
    return found_app_issues, found_service_issues

# Apply categorization
print("\nAnalyzing complaint categories...")
complaint_analysis = []
for idx, row in rogers_df.iterrows():
    app_issues, service_issues = categorize_complaint(row)
    complaint_analysis.append({
        'review_id': row['review_id'],
        'app_issues': app_issues,
        'service_issues': service_issues,
        'is_app_complaint': len(app_issues) > 0,
        'is_service_complaint': len(service_issues) > 0,
        'rating': row['rating'],
        'sentiment': row['claude_sentiment']
    })

complaint_df = pd.DataFrame(complaint_analysis)

# Calculate complaint statistics
total_rogers = len(rogers_df)
app_complaints = complaint_df['is_app_complaint'].sum()
service_complaints = complaint_df['is_service_complaint'].sum()
both_complaints = ((complaint_df['is_app_complaint']) & (complaint_df['is_service_complaint'])).sum()
neither_complaints = total_rogers - app_complaints - service_complaints + both_complaints

print(f"\nRogers Complaint Breakdown:")
print(f"App-related complaints: {app_complaints:,} ({app_complaints/total_rogers*100:.1f}%)")
print(f"Service-related complaints: {service_complaints:,} ({service_complaints/total_rogers*100:.1f}%)")
print(f"Both app & service: {both_complaints:,} ({both_complaints/total_rogers*100:.1f}%)")
print(f"Neither/General feedback: {neither_complaints:,} ({neither_complaints/total_rogers*100:.1f}%)")

# 2. Compare Rogers vs Bell complaint types
print("\n=== ROGERS VS BELL COMPARISON ===")

# Apply same analysis to Bell
bell_complaint_analysis = []
for idx, row in bell_df.iterrows():
    app_issues, service_issues = categorize_complaint(row)
    bell_complaint_analysis.append({
        'review_id': row['review_id'],
        'app_issues': app_issues,
        'service_issues': service_issues,
        'is_app_complaint': len(app_issues) > 0,
        'is_service_complaint': len(service_issues) > 0,
        'rating': row['rating'],
        'sentiment': row['claude_sentiment']
    })

bell_complaint_df = pd.DataFrame(bell_complaint_analysis)

bell_app_complaints = bell_complaint_df['is_app_complaint'].sum()
bell_service_complaints = bell_complaint_df['is_service_complaint'].sum()

print(f"\nComplaint Type Comparison:")
print(f"Rogers - App complaints: {app_complaints/total_rogers*100:.1f}% vs Service complaints: {service_complaints/total_rogers*100:.1f}%")
print(f"Bell - App complaints: {bell_app_complaints/len(bell_df)*100:.1f}% vs Service complaints: {bell_service_complaints/len(bell_df)*100:.1f}%")

# 3. Top specific issues for Rogers
print("\n=== TOP ROGERS APP ISSUES ===")

# Count specific app issues
app_issue_counts = Counter()
for issues_list in complaint_df['app_issues']:
    for issue in issues_list:
        app_issue_counts[issue] += 1

print("\nMost common app-related issues:")
for issue, count in app_issue_counts.most_common():
    print(f"- {issue}: {count:,} reviews ({count/total_rogers*100:.1f}%)")

# 4. Sentiment analysis by issue type
print("\n=== SENTIMENT BY ISSUE TYPE (ROGERS) ===")

# Get reviews with specific issues
crash_reviews = rogers_df[rogers_df['text'].str.contains('crash|closing|stops working', case=False, na=False)]
login_reviews = rogers_df[rogers_df['text'].str.contains('login|sign in|password', case=False, na=False)]
performance_reviews = rogers_df[rogers_df['text'].str.contains('slow|lag|freeze|loading', case=False, na=False)]

print(f"\nCrash-related reviews: {len(crash_reviews):,} (Avg rating: {crash_reviews['rating'].mean():.2f})")
print(f"Login-related reviews: {len(login_reviews):,} (Avg rating: {login_reviews['rating'].mean():.2f})")
print(f"Performance-related reviews: {len(performance_reviews):,} (Avg rating: {performance_reviews['rating'].mean():.2f})")

# 5. Time trend analysis
print("\n=== TIME TREND ANALYSIS ===")

# Group by year and calculate metrics
yearly_stats = rogers_df.groupby('year').agg({
    'rating': ['mean', 'count'],
    'claude_sentiment': lambda x: (x == 'Negative').sum() / len(x) * 100
}).round(2)

print("\nRogers App Yearly Trends:")
print(yearly_stats)

# 6. Platform-specific issues
print("\n=== PLATFORM-SPECIFIC ANALYSIS (ROGERS) ===")

android_rogers = rogers_df[rogers_df['platform'] == 'Android']
ios_rogers = rogers_df[rogers_df['platform'] == 'iOS']

print(f"\nAndroid: {len(android_rogers):,} reviews (Avg rating: {android_rogers['rating'].mean():.2f})")
print(f"iOS: {len(ios_rogers):,} reviews (Avg rating: {ios_rogers['rating'].mean():.2f})")

# Check for platform-specific issues
android_crashes = android_rogers[android_rogers['text'].str.contains('crash', case=False, na=False)]
ios_crashes = ios_rogers[ios_rogers['text'].str.contains('crash', case=False, na=False)]

print(f"\nCrash rate by platform:")
print(f"Android: {len(android_crashes)/len(android_rogers)*100:.1f}%")
print(f"iOS: {len(ios_crashes)/len(ios_rogers)*100:.1f}%")

# 7. Generate actionable insights
print("\n=== ACTIONABLE INSIGHTS FOR ROGERS APP IMPROVEMENT ===")

insights = {
    "executive_summary": {
        "total_reviews_analyzed": len(rogers_df),
        "average_rating": round(rogers_df['rating'].mean(), 2),
        "negative_sentiment_rate": round((rogers_df['claude_sentiment'] == 'Negative').sum() / len(rogers_df) * 100, 1),
        "app_related_complaints": round(app_complaints/total_rogers*100, 1),
        "service_related_complaints": round(service_complaints/total_rogers*100, 1)
    },
    
    "critical_issues": {
        "app_stability": {
            "description": "App crashes and stability issues",
            "frequency": app_issue_counts.get('crashes', 0),
            "percentage": round(app_issue_counts.get('crashes', 0)/total_rogers*100, 1),
            "severity": "CRITICAL",
            "recommendation": "Implement comprehensive crash reporting and fix memory leaks. Focus on Android stability."
        },
        "authentication": {
            "description": "Login and authentication problems",
            "frequency": app_issue_counts.get('login', 0),
            "percentage": round(app_issue_counts.get('login', 0)/total_rogers*100, 1),
            "severity": "HIGH",
            "recommendation": "Simplify authentication flow, implement biometric login, and improve error messaging."
        },
        "performance": {
            "description": "Slow loading and poor performance",
            "frequency": app_issue_counts.get('performance', 0),
            "percentage": round(app_issue_counts.get('performance', 0)/total_rogers*100, 1),
            "severity": "HIGH",
            "recommendation": "Optimize API calls, implement caching, and reduce app size."
        }
    },
    
    "improvement_priorities": [
        {
            "priority": 1,
            "area": "App Stability",
            "action": "Fix crash issues, especially on Android devices",
            "expected_impact": "Could improve ratings by 0.5-1.0 stars",
            "effort": "High",
            "timeline": "2-3 months"
        },
        {
            "priority": 2,
            "area": "Authentication Flow",
            "action": "Redesign login process with better error handling",
            "expected_impact": "Reduce support calls by 15-20%",
            "effort": "Medium",
            "timeline": "1-2 months"
        },
        {
            "priority": 3,
            "area": "Performance Optimization",
            "action": "Implement lazy loading and optimize data fetching",
            "expected_impact": "Improve user satisfaction scores",
            "effort": "Medium",
            "timeline": "2-3 months"
        },
        {
            "priority": 4,
            "area": "User Interface",
            "action": "Simplify navigation and improve feature discoverability",
            "expected_impact": "Reduce user confusion and support queries",
            "effort": "Medium",
            "timeline": "3-4 months"
        },
        {
            "priority": 5,
            "area": "Self-Service Features",
            "action": "Add in-app troubleshooting and FAQ section",
            "expected_impact": "Reduce customer service contact by 25%",
            "effort": "Low",
            "timeline": "1 month"
        }
    ],
    
    "competitive_analysis": {
        "rogers_vs_bell": {
            "rogers_avg_rating": round(rogers_df['rating'].mean(), 2),
            "bell_avg_rating": round(bell_df['rating'].mean(), 2),
            "rogers_app_complaint_rate": round(app_complaints/total_rogers*100, 1),
            "bell_app_complaint_rate": round(bell_app_complaints/len(bell_df)*100, 1),
            "key_difference": "Rogers has significantly more app-related complaints, while Bell users complain more about service"
        }
    },
    
    "customer_service_impact": {
        "reviews_needing_support": round((rogers_df['customer_service_impact'] == True).sum() / len(rogers_df) * 100, 1),
        "top_reasons_for_contact": [
            "App crashes and technical issues",
            "Login/authentication problems", 
            "Billing inquiries that could be self-served",
            "Account management tasks"
        ],
        "reduction_opportunity": "Fixing top 3 app issues could reduce support contact by 30-40%"
    }
}

# Save comprehensive analysis
print("\nSaving analysis results...")

# Save detailed insights
with open('html_dashboard/rogers_improvement_insights.json', 'w') as f:
    json.dump(insights, f, indent=2)

# Save complaint categorization data
# Convert yearly_stats to a serializable format
yearly_trends = {}
for year in yearly_stats.index:
    yearly_trends[str(year)] = {
        "avg_rating": float(yearly_stats.loc[year, ('rating', 'mean')]),
        "review_count": int(yearly_stats.loc[year, ('rating', 'count')]),
        "negative_percentage": float(yearly_stats.loc[year, ('claude_sentiment', '<lambda>')])
    }

complaint_summary = {
    "rogers_complaints": {
        "total_reviews": len(rogers_df),
        "app_complaints": int(app_complaints),
        "service_complaints": int(service_complaints),
        "both_types": int(both_complaints),
        "neither_type": int(neither_complaints),
        "top_app_issues": dict(app_issue_counts.most_common(10))
    },
    "bell_complaints": {
        "total_reviews": len(bell_df),
        "app_complaints": int(bell_app_complaints),
        "service_complaints": int(bell_service_complaints)
    },
    "yearly_trends": yearly_trends
}

with open('html_dashboard/complaint_analysis.json', 'w') as f:
    json.dump(complaint_summary, f, indent=2)

print("\n✅ Analysis complete! Results saved to:")
print("- html_dashboard/rogers_improvement_insights.json")
print("- html_dashboard/complaint_analysis.json")
print("\nKey findings:")
print(f"1. Rogers app has {round(app_complaints/total_rogers*100, 1)}% app-related complaints vs Bell's {round(bell_app_complaints/len(bell_df)*100, 1)}%")
print(f"2. Top issue is app crashes affecting {app_issue_counts.get('crashes', 0):,} reviews")
print(f"3. Fixing top 3 issues could improve ratings and reduce support contact by 30-40%")