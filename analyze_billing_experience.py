#!/usr/bin/env python3
"""
Analyze billing experience mentions in telecom app reviews.
"""

import pandas as pd
import re
from datetime import datetime
import json

def analyze_billing_experience():
    """Analyze billing-related mentions in app reviews."""
    
    print("Loading cleaned review data...")
    df = pd.read_csv('telecom_app_reviews_cleaned.csv')
    
    # Define billing-related keywords
    billing_keywords = {
        'payment': ['pay', 'payment', 'paying', 'paid', 'pay bill', 'make payment', 'process payment'],
        'bill_access': ['view bill', 'see bill', 'check bill', 'bill amount', 'billing', 'invoice', 'statement'],
        'plan_info': ['plan', 'usage', 'data usage', 'minutes', 'balance', 'remaining', 'overage'],
        'payment_method': ['credit card', 'debit', 'bank account', 'payment method', 'auto pay', 'autopay', 'automatic payment'],
        'payment_issues': ['decline', 'rejected', 'failed', 'error', 'won\'t accept', 'can\'t pay', 'payment fail'],
        'billing_errors': ['overcharge', 'wrong amount', 'incorrect', 'double charge', 'billing error', 'mistake'],
        'ease_of_use': ['easy to pay', 'simple', 'convenient', 'quick', 'hassle', 'difficult', 'confusing', 'complicated']
    }
    
    # Function to check if review mentions billing
    def contains_billing_keywords(text):
        if pd.isna(text):
            return False
        text_lower = str(text).lower()
        
        # Check for any billing-related keyword
        for category, keywords in billing_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return True
        return False
    
    # Function to categorize billing mentions
    def categorize_billing_mention(text):
        if pd.isna(text):
            return []
        
        text_lower = str(text).lower()
        categories = []
        
        for category, keywords in billing_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    categories.append(category)
                    break
        
        return list(set(categories))
    
    # Filter reviews that mention billing
    print("Identifying billing-related reviews...")
    df['mentions_billing'] = df['text'].apply(contains_billing_keywords)
    df['billing_categories'] = df['text'].apply(categorize_billing_mention)
    
    billing_reviews = df[df['mentions_billing']].copy()
    
    print(f"\nFound {len(billing_reviews)} billing-related reviews out of {len(df)} total")
    print(f"Billing mention rate: {len(billing_reviews)/len(df)*100:.1f}%")
    
    # Analyze by provider
    rogers_billing = billing_reviews[billing_reviews['app_name'] == 'Rogers']
    bell_billing = billing_reviews[billing_reviews['app_name'] == 'Bell']
    
    print(f"\nBy Provider:")
    print(f"Rogers: {len(rogers_billing)} billing mentions ({len(rogers_billing)/len(df[df['app_name']=='Rogers'])*100:.1f}% of Rogers reviews)")
    print(f"Bell: {len(bell_billing)} billing mentions ({len(bell_billing)/len(df[df['app_name']=='Bell'])*100:.1f}% of Bell reviews)")
    
    # Sentiment analysis for billing reviews
    def calculate_sentiment(reviews):
        if len(reviews) == 0:
            return {}
        
        # Based on ratings
        very_negative = len(reviews[reviews['rating'] == 1])
        negative = len(reviews[reviews['rating'] == 2])
        neutral = len(reviews[reviews['rating'] == 3])
        positive = len(reviews[reviews['rating'] == 4])
        very_positive = len(reviews[reviews['rating'] == 5])
        
        total_negative = very_negative + negative
        total_positive = positive + very_positive
        
        return {
            'total': len(reviews),
            'negative_pct': total_negative / len(reviews) * 100,
            'neutral_pct': neutral / len(reviews) * 100,
            'positive_pct': total_positive / len(reviews) * 100,
            'avg_rating': reviews['rating'].mean()
        }
    
    rogers_sentiment = calculate_sentiment(rogers_billing)
    bell_sentiment = calculate_sentiment(bell_billing)
    
    print("\n=== SENTIMENT ANALYSIS ===")
    print(f"\nRogers Billing Sentiment:")
    print(f"  Negative: {rogers_sentiment['negative_pct']:.1f}%")
    print(f"  Neutral: {rogers_sentiment['neutral_pct']:.1f}%")
    print(f"  Positive: {rogers_sentiment['positive_pct']:.1f}%")
    print(f"  Average Rating: {rogers_sentiment['avg_rating']:.2f}/5")
    
    print(f"\nBell Billing Sentiment:")
    print(f"  Negative: {bell_sentiment['negative_pct']:.1f}%")
    print(f"  Neutral: {bell_sentiment['neutral_pct']:.1f}%")
    print(f"  Positive: {bell_sentiment['positive_pct']:.1f}%")
    print(f"  Average Rating: {bell_sentiment['avg_rating']:.2f}/5")
    
    # Analyze specific billing aspects
    print("\n=== BILLING ASPECT ANALYSIS ===")
    
    for provider, provider_billing in [('Rogers', rogers_billing), ('Bell', bell_billing)]:
        print(f"\n{provider} Billing Categories:")
        
        # Count mentions by category
        category_counts = {}
        for categories in provider_billing['billing_categories']:
            for cat in categories:
                category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Sort by frequency
        sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
        for cat, count in sorted_categories:
            pct = count / len(provider_billing) * 100
            print(f"  {cat}: {count} mentions ({pct:.1f}%)")
    
    # Extract specific payment issues
    print("\n=== PAYMENT ISSUES ANALYSIS ===")
    
    payment_issue_keywords = {
        'cant_pay': ['can\'t pay', 'cannot pay', 'unable to pay', 'won\'t let me pay'],
        'payment_failed': ['payment failed', 'payment error', 'declined', 'rejected'],
        'app_crashes': ['crash', 'crashes when', 'freezes', 'stops working'],
        'loading_issues': ['won\'t load', 'loading', 'blank screen', 'white screen'],
        'login_required': ['log in again', 'logged out', 'sign in', 'keeps asking'],
        'wrong_amount': ['wrong amount', 'incorrect', 'overcharge', 'double charge']
    }
    
    def find_payment_issues(text):
        if pd.isna(text):
            return []
        
        text_lower = str(text).lower()
        issues = []
        
        for issue, keywords in payment_issue_keywords.items():
            for keyword in keywords:
                if keyword in text_lower and 'pay' in text_lower:
                    issues.append(issue)
                    break
        
        return issues
    
    # Analyze payment issues
    rogers_billing['payment_issues'] = rogers_billing['text'].apply(find_payment_issues)
    bell_billing['payment_issues'] = bell_billing['text'].apply(find_payment_issues)
    
    print("\nRogers Payment Issues:")
    rogers_issue_counts = {}
    for issues in rogers_billing['payment_issues']:
        for issue in issues:
            rogers_issue_counts[issue] = rogers_issue_counts.get(issue, 0) + 1
    
    for issue, count in sorted(rogers_issue_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue}: {count} mentions")
    
    print("\nBell Payment Issues:")
    bell_issue_counts = {}
    for issues in bell_billing['payment_issues']:
        for issue in issues:
            bell_issue_counts[issue] = bell_issue_counts.get(issue, 0) + 1
    
    for issue, count in sorted(bell_issue_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {issue}: {count} mentions")
    
    # Sample reviews for each provider
    print("\n=== SAMPLE BILLING REVIEWS ===")
    
    # Get worst billing reviews
    print("\nWorst Rogers Billing Reviews (1 star):")
    worst_rogers = rogers_billing[rogers_billing['rating'] == 1].sample(min(3, len(rogers_billing[rogers_billing['rating'] == 1])))
    for idx, row in worst_rogers.iterrows():
        print(f"\n- {row['text'][:200]}...")
    
    print("\nWorst Bell Billing Reviews (1 star):")
    worst_bell = bell_billing[bell_billing['rating'] == 1].sample(min(3, len(bell_billing[bell_billing['rating'] == 1])))
    for idx, row in worst_bell.iterrows():
        print(f"\n- {row['text'][:200]}...")
    
    # Get best billing reviews
    print("\nBest Rogers Billing Reviews (5 stars):")
    best_rogers = rogers_billing[rogers_billing['rating'] == 5].sample(min(3, len(rogers_billing[rogers_billing['rating'] == 5])))
    for idx, row in best_rogers.iterrows():
        print(f"\n- {row['text'][:200]}...")
    
    print("\nBest Bell Billing Reviews (5 stars):")
    best_bell = bell_billing[bell_billing['rating'] == 5].sample(min(3, len(bell_billing[bell_billing['rating'] == 5])))
    for idx, row in best_bell.iterrows():
        print(f"\n- {row['text'][:200]}...")
    
    # Look for specific billing functionality mentions
    print("\n=== BILLING FUNCTIONALITY ANALYSIS ===")
    
    functionality_keywords = {
        'view_bill': ['view bill', 'see bill', 'check bill', 'look at bill'],
        'pay_bill': ['pay bill', 'make payment', 'pay my bill', 'payment'],
        'auto_pay': ['autopay', 'auto pay', 'automatic payment', 'recurring'],
        'payment_history': ['payment history', 'past payments', 'previous bill'],
        'plan_details': ['plan details', 'my plan', 'usage', 'data left'],
        'change_payment': ['change payment', 'update card', 'new card', 'payment method']
    }
    
    def analyze_functionality(reviews, provider_name):
        print(f"\n{provider_name} Billing Functionality Mentions:")
        
        functionality_counts = {}
        positive_counts = {}
        negative_counts = {}
        
        for _, review in reviews.iterrows():
            text_lower = str(review['text']).lower()
            
            for func, keywords in functionality_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        functionality_counts[func] = functionality_counts.get(func, 0) + 1
                        
                        if review['rating'] >= 4:
                            positive_counts[func] = positive_counts.get(func, 0) + 1
                        elif review['rating'] <= 2:
                            negative_counts[func] = negative_counts.get(func, 0) + 1
                        break
        
        # Display results
        for func in functionality_keywords.keys():
            total = functionality_counts.get(func, 0)
            if total > 0:
                positive = positive_counts.get(func, 0)
                negative = negative_counts.get(func, 0)
                print(f"  {func}: {total} mentions (Positive: {positive}, Negative: {negative})")
    
    analyze_functionality(rogers_billing, "Rogers")
    analyze_functionality(bell_billing, "Bell")
    
    # Generate summary report
    report = {
        'total_billing_mentions': len(billing_reviews),
        'billing_mention_rate': f"{len(billing_reviews)/len(df)*100:.1f}%",
        'rogers': {
            'total_mentions': len(rogers_billing),
            'mention_rate': f"{len(rogers_billing)/len(df[df['app_name']=='Rogers'])*100:.1f}%",
            'sentiment': rogers_sentiment,
            'top_issues': rogers_issue_counts
        },
        'bell': {
            'total_mentions': len(bell_billing),
            'mention_rate': f"{len(bell_billing)/len(df[df['app_name']=='Bell'])*100:.1f}%",
            'sentiment': bell_sentiment,
            'top_issues': bell_issue_counts
        }
    }
    
    # Save detailed billing reviews for further analysis
    billing_reviews.to_csv('billing_experience_reviews.csv', index=False)
    
    # Save summary report
    with open('billing_experience_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print("\n=== FILES SAVED ===")
    print("- billing_experience_reviews.csv (all billing-related reviews)")
    print("- billing_experience_report.json (summary statistics)")
    
    return billing_reviews, report

if __name__ == "__main__":
    billing_reviews, report = analyze_billing_experience()