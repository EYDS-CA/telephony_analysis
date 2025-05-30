#!/usr/bin/env python3
"""
User Feedback Analysis - Fixed version
Analyzes 7,131 User Feedback reviews to identify meaningful sub-categories
"""

import pandas as pd
import re
from collections import Counter
import numpy as np

def analyze_user_feedback():
    """Comprehensive analysis of User Feedback category"""
    
    print("🔍 ANALYZING USER FEEDBACK CATEGORY")
    print("=" * 50)
    
    # Load the cleaned dataset
    df = pd.read_csv('Data/enhanced_analysis_final_clean.csv')
    
    # Filter for User Feedback reviews and clean text
    user_feedback = df[df['enhanced_category'] == 'User Feedback'].copy()
    user_feedback['text'] = user_feedback['text'].fillna('').astype(str)  # Fix NaN issue
    
    print(f"📊 User Feedback Reviews: {len(user_feedback):,}")
    print(f"   Percentage of total: {len(user_feedback)/len(df)*100:.1f}%")
    
    # Basic statistics
    print(f"\n📈 Basic Statistics:")
    print(f"   Average rating: {user_feedback['rating'].mean():.2f}")
    print(f"   Rating distribution:")
    for rating in [1,2,3,4,5]:
        count = len(user_feedback[user_feedback['rating'] == rating])
        pct = count/len(user_feedback)*100
        print(f"     {rating}⭐: {count:,} ({pct:.1f}%)")
    
    # Provider breakdown
    print(f"\n🏢 Provider Breakdown:")
    provider_counts = user_feedback['app_name'].value_counts()
    for provider, count in provider_counts.items():
        pct = count/len(user_feedback)*100
        print(f"   {provider}: {count:,} ({pct:.1f}%)")
    
    # Length analysis
    user_feedback['word_count'] = user_feedback['text'].str.split().str.len()
    
    print(f"\n📏 Review Length Analysis:")
    print(f"   Average words: {user_feedback['word_count'].mean():.1f}")
    
    # Sample analysis by length and rating
    print(f"\n📝 Pattern Analysis:")
    
    # Very short positive (1-3 words, 4-5 stars)
    short_positive = user_feedback[(user_feedback['word_count'] <= 3) & 
                                  (user_feedback['rating'] >= 4)]
    
    # Very short negative (1-3 words, 1-2 stars)
    short_negative = user_feedback[(user_feedback['word_count'] <= 3) & 
                                  (user_feedback['rating'] <= 2)]
    
    # Medium positive (4-20 words, 4-5 stars)
    medium_positive = user_feedback[(user_feedback['word_count'] >= 4) & 
                                   (user_feedback['word_count'] <= 20) &
                                   (user_feedback['rating'] >= 4)]
    
    # Medium negative (4-20 words, 1-2 stars)
    medium_negative = user_feedback[(user_feedback['word_count'] >= 4) & 
                                   (user_feedback['word_count'] <= 20) &
                                   (user_feedback['rating'] <= 2)]
    
    # Long reviews (20+ words)
    long_reviews = user_feedback[user_feedback['word_count'] > 20]
    
    # Neutral/moderate (3 stars or mixed short/medium)
    neutral_reviews = user_feedback[user_feedback['rating'] == 3]
    
    # Non-informative (very short, unclear)
    non_informative = user_feedback[(user_feedback['word_count'] <= 2) | 
                                   (user_feedback['text'].str.lower().isin(['', '.', 'none', 'n/a', 'na', '...']))]
    
    print(f"\n🎯 PROPOSED SUB-CATEGORIES:")
    
    categories = {
        '1. Brand Loyalty': {
            'count': len(short_positive),
            'description': 'Short positive feedback (1-3 words, 4-5 stars)',
            'examples': short_positive['text'].head(8).tolist()
        },
        '2. General Dissatisfaction': {
            'count': len(short_negative),
            'description': 'Short negative feedback (1-3 words, 1-2 stars)',
            'examples': short_negative['text'].head(8).tolist()
        },
        '3. App Praise': {
            'count': len(medium_positive),
            'description': 'Medium positive feedback (4-20 words, 4-5 stars)',
            'examples': medium_positive['text'].head(6).tolist()
        },
        '4. General Complaints': {
            'count': len(medium_negative),
            'description': 'Medium negative feedback (4-20 words, 1-2 stars)',
            'examples': medium_negative['text'].head(6).tolist()
        },
        '5. Detailed Feedback': {
            'count': len(long_reviews),
            'description': 'Long detailed reviews (20+ words)',
            'examples': [text[:80] + '...' for text in long_reviews['text'].head(4).tolist()]
        },
        '6. Neutral Comments': {
            'count': len(neutral_reviews),
            'description': '3-star moderate feedback',
            'examples': neutral_reviews['text'].head(6).tolist()
        },
        '7. Non-Informative': {
            'count': len(non_informative),
            'description': 'Minimal/unclear content',
            'examples': non_informative['text'].head(8).tolist()
        }
    }
    
    # Print categories
    total_categorized = 0
    for category, data in categories.items():
        count = data['count']
        pct = count/len(user_feedback)*100
        total_categorized += count
        
        print(f"\n{category}: {count:,} ({pct:.1f}%)")
        print(f"   {data['description']}")
        print(f"   Examples: {data['examples']}")
    
    # Account for overlap
    remaining = len(user_feedback) - total_categorized
    print(f"\n📊 Summary:")
    print(f"   Total analyzed: {len(user_feedback):,}")
    print(f"   Categories account for: {total_categorized:,}")
    print(f"   Overlap/remaining: {remaining:,}")
    
    # Business value assessment
    print(f"\n💼 BUSINESS VALUE ASSESSMENT:")
    
    high_value = len(medium_positive) + len(medium_negative) + len(long_reviews)
    medium_value = len(neutral_reviews)
    low_value = len(short_positive) + len(short_negative) + len(non_informative)
    
    print(f"   🟢 HIGH VALUE ({high_value:,} reviews - {high_value/len(user_feedback)*100:.1f}%):")
    print(f"      • App Praise: Understand what customers love")
    print(f"      • General Complaints: Identify improvement areas")  
    print(f"      • Detailed Feedback: Rich insights for strategy")
    
    print(f"   🟡 MEDIUM VALUE ({medium_value:,} reviews - {medium_value/len(user_feedback)*100:.1f}%):")
    print(f"      • Neutral Comments: Moderate feedback")
    
    print(f"   🔴 LOW VALUE ({low_value:,} reviews - {low_value/len(user_feedback)*100:.1f}%):")
    print(f"      • Brand Loyalty: Nice but not actionable")
    print(f"      • General Dissatisfaction: Vague negativity")
    print(f"      • Non-Informative: No business value")
    
    # Key insights
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"   • {len(user_feedback):,} reviews need sub-categorization")
    print(f"   • {high_value:,} reviews ({high_value/len(user_feedback)*100:.1f}%) have high business value")
    print(f"   • Rogers dominates User Feedback ({provider_counts['Rogers']:,} vs {provider_counts['Bell']:,})")
    print(f"   • Polarized ratings: {len(user_feedback[user_feedback['rating'] <= 2]):,} negative vs {len(user_feedback[user_feedback['rating'] >= 4]):,} positive")
    
    print(f"\n✅ RECOMMENDATION:")
    print(f"   Create sub-categorization script to split User Feedback into these 7 categories")
    print(f"   Focus analysis on High Value categories ({high_value:,} reviews)")
    print(f"   Filter out Low Value categories for strategic insights")

if __name__ == "__main__":
    analyze_user_feedback()