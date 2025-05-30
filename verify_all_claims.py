#!/usr/bin/env python3

import pandas as pd
import numpy as np
import re
from collections import Counter

def verify_claims_against_data():
    """Comprehensive verification of all claims made in reports against actual filtered data"""
    
    print("=== COMPREHENSIVE CLAIMS VERIFICATION ===")
    print("Checking all statistical claims against filtered dataset...\n")
    
    # Load the filtered dataset
    df = pd.read_csv('telecom_app_reviews_filtered_current.csv')
    
    # Convert date column
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    print(f"Dataset loaded: {len(df):,} reviews")
    print(f"Date range: {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")
    print(f"Providers: {df['app_name'].value_counts().to_dict()}")
    print(f"Platforms: {df['platform'].value_counts().to_dict()}\n")
    
    # Initialize verification results
    verified_claims = []
    incorrect_claims = []
    
    # ================================================================
    # 1. EXECUTIVE SUMMARY CLAIMS VERIFICATION
    # ================================================================
    print("=" * 60)
    print("1. EXECUTIVE SUMMARY VERIFICATION")
    print("=" * 60)
    
    # Claim: Technical Issues 94.9% negative
    print("\n📊 TECHNICAL ISSUES SENTIMENT")
    if 'primary_category' in df.columns and 'claude_sentiment' in df.columns:
        tech_issues = df[df['primary_category'] == 'Technical Issues']
        if len(tech_issues) > 0:
            tech_negative_pct = (tech_issues['claude_sentiment'] == 'Negative').sum() / len(tech_issues) * 100
            print(f"Technical Issues negative sentiment: {tech_negative_pct:.1f}%")
            print(f"Total Technical Issues reviews: {len(tech_issues):,}")
            
            if abs(tech_negative_pct - 94.9) < 5:
                verified_claims.append(f"Technical Issues ~{tech_negative_pct:.1f}% negative (claimed 94.9%)")
            else:
                incorrect_claims.append(f"Technical Issues: Found {tech_negative_pct:.1f}% negative, claimed 94.9%")
        else:
            print("⚠️  No Technical Issues found in primary_category")
    
    # Claim: Billing 77.6% negative
    print("\n📊 BILLING SENTIMENT")
    billing_reviews = df[df['primary_category'] == 'Billing']
    if len(billing_reviews) > 0:
        billing_negative_pct = (billing_reviews['claude_sentiment'] == 'Negative').sum() / len(billing_reviews) * 100
        print(f"Billing negative sentiment: {billing_negative_pct:.1f}%")
        print(f"Total Billing reviews: {len(billing_reviews):,}")
        
        if abs(billing_negative_pct - 77.6) < 5:
            verified_claims.append(f"Billing ~{billing_negative_pct:.1f}% negative (claimed 77.6%)")
        else:
            incorrect_claims.append(f"Billing: Found {billing_negative_pct:.1f}% negative, claimed 77.6%")
    
    # Claim: Both apps score 2.64/5
    print("\n📊 AVERAGE RATINGS")
    overall_avg = df['rating'].mean()
    rogers_avg = df[df['app_name'] == 'Rogers']['rating'].mean() 
    bell_avg = df[df['app_name'] == 'Bell']['rating'].mean()
    
    print(f"Overall average rating: {overall_avg:.2f}")
    print(f"Rogers average rating: {rogers_avg:.2f}")
    print(f"Bell average rating: {bell_avg:.2f}")
    
    if abs(overall_avg - 2.64) < 0.1:
        verified_claims.append(f"Overall rating ~{overall_avg:.2f} (claimed 2.64)")
    else:
        incorrect_claims.append(f"Overall rating: Found {overall_avg:.2f}, claimed 2.64")
    
    # ================================================================
    # 2. PLATFORM PERFORMANCE GAP CLAIMS
    # ================================================================
    print("\n" + "=" * 60)
    print("2. PLATFORM PERFORMANCE GAP VERIFICATION")  
    print("=" * 60)
    
    # Claim: iOS 84.2% negative, Android 58.1% negative
    print("\n📊 PLATFORM SENTIMENT BREAKDOWN")
    ios_reviews = df[df['platform'] == 'iOS']
    android_reviews = df[df['platform'] == 'Android']
    
    ios_negative_pct = (ios_reviews['claude_sentiment'] == 'Negative').sum() / len(ios_reviews) * 100
    android_negative_pct = (android_reviews['claude_sentiment'] == 'Negative').sum() / len(android_reviews) * 100
    
    print(f"iOS negative sentiment: {ios_negative_pct:.1f}% (n={len(ios_reviews):,})")
    print(f"Android negative sentiment: {android_negative_pct:.1f}% (n={len(android_reviews):,})")
    print(f"Gap: {ios_negative_pct - android_negative_pct:.1f} percentage points")
    
    if abs(ios_negative_pct - 84.2) < 5:
        verified_claims.append(f"iOS negative ~{ios_negative_pct:.1f}% (claimed 84.2%)")
    else:
        incorrect_claims.append(f"iOS negative: Found {ios_negative_pct:.1f}%, claimed 84.2%")
        
    if abs(android_negative_pct - 58.1) < 5:
        verified_claims.append(f"Android negative ~{android_negative_pct:.1f}% (claimed 58.1%)")
    else:
        incorrect_claims.append(f"Android negative: Found {android_negative_pct:.1f}%, claimed 58.1%")
    
    # ================================================================
    # 3. PAYMENT SENTIMENT VERIFICATION
    # ================================================================
    print("\n" + "=" * 60)
    print("3. PAYMENT SENTIMENT VERIFICATION")
    print("=" * 60)
    
    # Search for payment-related mentions in review text
    payment_keywords = ['payment', 'pay', 'billing', 'bill', 'charge', 'fee', 'cost']
    payment_pattern = '|'.join(payment_keywords)
    
    payment_mentions = df[df['text'].str.contains(payment_pattern, case=False, na=False)]
    print(f"\nPayment-related mentions: {len(payment_mentions):,}")
    
    if len(payment_mentions) > 0:
        payment_negative_pct = (payment_mentions['claude_sentiment'] == 'Negative').sum() / len(payment_mentions) * 100
        payment_positive_count = (payment_mentions['claude_sentiment'] == 'Positive').sum()
        
        print(f"Payment mentions negative sentiment: {payment_negative_pct:.1f}%")
        print(f"Payment mentions positive count: {payment_positive_count}")
        print(f"Total payment mentions: {len(payment_mentions)}")
        
        # Verify claim: 70% negative (712 positive out of 2,377)
        claimed_total = 2377
        claimed_positive = 712
        claimed_negative_pct = (1 - claimed_positive/claimed_total) * 100
        
        print(f"Claimed: {claimed_positive} positive out of {claimed_total} = {100-claimed_negative_pct:.1f}% positive, {claimed_negative_pct:.1f}% negative")
        
        if abs(len(payment_mentions) - claimed_total) < 200:  # Allow some variance
            verified_claims.append(f"Payment mentions ~{len(payment_mentions)} (claimed {claimed_total})")
        else:
            incorrect_claims.append(f"Payment mentions: Found {len(payment_mentions)}, claimed {claimed_total}")
    
    # ================================================================
    # 4. CHATBOT COMPLAINTS VERIFICATION
    # ================================================================
    print("\n" + "=" * 60)
    print("4. CHATBOT COMPLAINTS VERIFICATION")
    print("=" * 60)
    
    # Search for chatbot/AI related complaints
    chatbot_keywords = ['chatbot', 'chat bot', 'anna', 'ai', 'automated', 'bot', 'virtual assistant']
    chatbot_pattern = '|'.join(chatbot_keywords)
    
    chatbot_mentions = df[df['text'].str.contains(chatbot_pattern, case=False, na=False)]
    
    print(f"\nChatbot-related mentions: {len(chatbot_mentions):,}")
    
    if len(chatbot_mentions) > 0:
        rogers_chatbot = chatbot_mentions[chatbot_mentions['app_name'] == 'Rogers']
        bell_chatbot = chatbot_mentions[chatbot_mentions['app_name'] == 'Bell']
        
        rogers_chatbot_negative = (rogers_chatbot['claude_sentiment'] == 'Negative').sum()
        bell_chatbot_negative = (bell_chatbot['claude_sentiment'] == 'Negative').sum()
        
        print(f"Rogers chatbot complaints (negative): {rogers_chatbot_negative}")
        print(f"Bell chatbot complaints (negative): {bell_chatbot_negative}")
        
        if bell_chatbot_negative > 0:
            ratio = rogers_chatbot_negative / bell_chatbot_negative
            print(f"Rogers vs Bell chatbot complaint ratio: {ratio:.1f}x")
            
            # Verify claim: Bell has 8x fewer (33 vs 4)
            if abs(rogers_chatbot_negative - 33) < 10 and abs(bell_chatbot_negative - 4) < 3:
                verified_claims.append(f"Chatbot complaints: Rogers {rogers_chatbot_negative}, Bell {bell_chatbot_negative}")
            else:
                incorrect_claims.append(f"Chatbot complaints: Found Rogers {rogers_chatbot_negative}, Bell {bell_chatbot_negative}; claimed Rogers 33, Bell 4")
        else:
            print("⚠️  No Bell chatbot complaints found")
    
    # ================================================================
    # 5. ADDITIONAL CLAIMS VERIFICATION
    # ================================================================
    print("\n" + "=" * 60)
    print("5. ADDITIONAL CLAIMS VERIFICATION")
    print("=" * 60)
    
    # App ratings claim: "identical 4.4/5 app ratings"
    print(f"\n📊 APP STORE RATINGS vs REVIEW RATINGS")
    print(f"Our dataset average rating: {df['rating'].mean():.2f}")
    print(f"Rogers average in our data: {df[df['app_name'] == 'Rogers']['rating'].mean():.2f}")
    print(f"Bell average in our data: {df[df['app_name'] == 'Bell']['rating'].mean():.2f}")
    print(f"Note: 4.4/5 claim refers to overall app store ratings, not review subset")
    
    # Category breakdown verification
    print(f"\n📊 CATEGORY BREAKDOWN")
    category_counts = df['primary_category'].value_counts()
    print("Top categories:")
    for i, (cat, count) in enumerate(category_counts.head(5).items()):
        pct = count / len(df) * 100
        print(f"  {i+1}. {cat}: {count:,} ({pct:.1f}%)")
    
    # ================================================================
    # 6. SUMMARY REPORT
    # ================================================================
    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    
    print(f"\n✅ VERIFIED CLAIMS ({len(verified_claims)}):")
    for claim in verified_claims:
        print(f"  ✓ {claim}")
    
    print(f"\n❌ INCORRECT CLAIMS ({len(incorrect_claims)}):")
    for claim in incorrect_claims:
        print(f"  ✗ {claim}")
    
    print(f"\n📊 CORRECTED STATISTICS FOR REPORTS:")
    print(f"  • Total reviews: {len(df):,}")
    print(f"  • Rogers: {len(df[df['app_name'] == 'Rogers']):,} ({len(df[df['app_name'] == 'Rogers'])/len(df)*100:.1f}%)")
    print(f"  • Bell: {len(df[df['app_name'] == 'Bell']):,} ({len(df[df['app_name'] == 'Bell'])/len(df)*100:.1f}%)")
    print(f"  • Average rating: {df['rating'].mean():.2f}")
    print(f"  • Negative sentiment: {(df['claude_sentiment'] == 'Negative').sum()/len(df)*100:.1f}%")
    print(f"  • iOS negative: {ios_negative_pct:.1f}%")
    print(f"  • Android negative: {android_negative_pct:.1f}%")
    if len(billing_reviews) > 0:
        print(f"  • Billing negative: {billing_negative_pct:.1f}%")
    if len(tech_issues) > 0:
        print(f"  • Technical Issues negative: {tech_negative_pct:.1f}%")
    
    return {
        'verified_claims': verified_claims,
        'incorrect_claims': incorrect_claims,
        'corrected_stats': {
            'total_reviews': len(df),
            'rogers_count': len(df[df['app_name'] == 'Rogers']),
            'bell_count': len(df[df['app_name'] == 'Bell']),
            'average_rating': round(df['rating'].mean(), 2),
            'negative_sentiment_pct': round((df['claude_sentiment'] == 'Negative').sum()/len(df)*100, 1),
            'ios_negative_pct': round(ios_negative_pct, 1),
            'android_negative_pct': round(android_negative_pct, 1),
            'billing_negative_pct': round(billing_negative_pct, 1) if len(billing_reviews) > 0 else None,
            'tech_negative_pct': round(tech_negative_pct, 1) if 'tech_issues' in locals() and len(tech_issues) > 0 else None
        }
    }

if __name__ == "__main__":
    results = verify_claims_against_data()