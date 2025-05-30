#!/usr/bin/env python3
"""
User Feedback Analysis - Determine sub-categorization patterns
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
    
    # Filter for User Feedback reviews
    user_feedback = df[df['enhanced_category'] == 'User Feedback'].copy()
    
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
    user_feedback['text_length'] = user_feedback['text'].str.len()
    user_feedback['word_count'] = user_feedback['text'].str.split().str.len()
    
    print(f"\n📏 Review Length Analysis:")
    print(f"   Average characters: {user_feedback['text_length'].mean():.0f}")
    print(f"   Average words: {user_feedback['word_count'].mean():.1f}")
    
    # Word count distribution
    word_bins = [1, 2, 3, 5, 10, 20, 50, 1000]
    for i in range(len(word_bins)-1):
        count = len(user_feedback[(user_feedback['word_count'] >= word_bins[i]) & 
                                 (user_feedback['word_count'] < word_bins[i+1])])
        print(f"   {word_bins[i]}-{word_bins[i+1]-1} words: {count:,}")
    
    # Sample analysis by length and rating
    print(f"\n📝 Sample Analysis:")
    
    # Very short positive (1-3 words, 4-5 stars)
    short_positive = user_feedback[(user_feedback['word_count'] <= 3) & 
                                  (user_feedback['rating'] >= 4)]
    print(f"\n1️⃣ SHORT POSITIVE ({len(short_positive):,} reviews):")
    print("   Samples:")
    for text in short_positive['text'].head(10):
        print(f"     '{text}'")
    
    # Very short negative (1-3 words, 1-2 stars)
    short_negative = user_feedback[(user_feedback['word_count'] <= 3) & 
                                  (user_feedback['rating'] <= 2)]
    print(f"\n2️⃣ SHORT NEGATIVE ({len(short_negative):,} reviews):")
    print("   Samples:")
    for text in short_negative['text'].head(10):
        print(f"     '{text}'")
    
    # Medium positive (4-20 words, 4-5 stars)
    medium_positive = user_feedback[(user_feedback['word_count'] >= 4) & 
                                   (user_feedback['word_count'] <= 20) &
                                   (user_feedback['rating'] >= 4)]
    print(f"\n3️⃣ MEDIUM POSITIVE ({len(medium_positive):,} reviews):")
    print("   Samples:")
    for text in medium_positive['text'].head(8):
        print(f"     '{text}'")
    
    # Medium negative (4-20 words, 1-2 stars)
    medium_negative = user_feedback[(user_feedback['word_count'] >= 4) & 
                                   (user_feedback['word_count'] <= 20) &
                                   (user_feedback['rating'] <= 2)]
    print(f"\n4️⃣ MEDIUM NEGATIVE ({len(medium_negative):,} reviews):")
    print("   Samples:")
    for text in medium_negative['text'].head(8):
        print(f"     '{text}'")
    
    # Long reviews (20+ words)
    long_reviews = user_feedback[user_feedback['word_count'] > 20]
    print(f"\n5️⃣ LONG REVIEWS ({len(long_reviews):,} reviews):")
    print("   High-rated samples (4-5 stars):")
    long_positive = long_reviews[long_reviews['rating'] >= 4]
    for text in long_positive['text'].head(5):
        print(f"     '{text[:100]}...'")
    
    print("   Low-rated samples (1-2 stars):")
    long_negative = long_reviews[long_reviews['rating'] <= 2]
    for text in long_negative['text'].head(5):
        print(f"     '{text[:100]}...'")
    
    # Keyword analysis
    print(f"\n🔍 KEYWORD ANALYSIS:")
    
    # Combine all text for analysis
    all_text = ' '.join(user_feedback['text'].str.lower())
    
    # Common positive words
    positive_reviews = user_feedback[user_feedback['rating'] >= 4]['text'].str.lower()
    positive_text = ' '.join(positive_reviews)
    
    # Common negative words  
    negative_reviews = user_feedback[user_feedback['rating'] <= 2]['text'].str.lower()
    negative_text = ' '.join(negative_reviews)
    
    # Extract common patterns
    print(f"\n📊 Common Patterns in Positive Reviews:")
    positive_words = positive_text.split()
    positive_counter = Counter(positive_words)
    for word, count in positive_counter.most_common(15):
        if len(word) > 2 and word not in ['the', 'and', 'for', 'with', 'this', 'app', 'bell', 'rogers']:
            print(f"   '{word}': {count}")
    
    print(f"\n📊 Common Patterns in Negative Reviews:")
    negative_words = negative_text.split()
    negative_counter = Counter(negative_words)
    for word, count in negative_counter.most_common(15):
        if len(word) > 2 and word not in ['the', 'and', 'for', 'with', 'this', 'app', 'bell', 'rogers']:
            print(f"   '{word}': {count}")
    
    # Proposed sub-categories
    print(f"\n🎯 PROPOSED SUB-CATEGORIES:")
    print(f"""
Based on the analysis, here are recommended sub-categories:

1. **Brand Loyalty** ({len(short_positive):,} reviews)
   - Very short positive feedback (1-3 words, 4-5 stars)
   - Examples: "love it", "great", "excellent"
   
2. **General Dissatisfaction** ({len(short_negative):,} reviews)  
   - Very short negative feedback (1-3 words, 1-2 stars)
   - Examples: "terrible", "garbage", "hate it"
   
3. **App Praise** ({len(medium_positive):,} reviews)
   - Medium positive feedback (4-20 words, 4-5 stars)
   - Specific positive comments about app experience
   
4. **General Complaints** ({len(medium_negative):,} reviews)
   - Medium negative feedback (4-20 words, 1-2 stars) 
   - Vague complaints without specific actionable issues
   
5. **Detailed Feedback** ({len(long_reviews):,} reviews)
   - Long reviews (20+ words) with detailed opinions
   - Mixed or comprehensive feedback
   
6. **Non-Informative** (minimal content reviews)
   - Single characters, "none", "n/a", etc.
   - No actionable information
   """)
    
    # Calculate distribution
    categories = {
        'Brand Loyalty': len(short_positive),
        'General Dissatisfaction': len(short_negative), 
        'App Praise': len(medium_positive),
        'General Complaints': len(medium_negative),
        'Detailed Feedback': len(long_reviews)
    }
    
    # Remaining (neutral, non-informative)
    accounted = sum(categories.values())
    remaining = len(user_feedback) - accounted
    categories['Non-Informative'] = remaining
    
    print(f"\n📈 Sub-category Distribution:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        pct = count/len(user_feedback)*100
        print(f"   {category}: {count:,} ({pct:.1f}%)")
    
    print(f"\n✅ Total accounted: {sum(categories.values()):,} / {len(user_feedback):,}")

if __name__ == "__main__":
    analyze_user_feedback()