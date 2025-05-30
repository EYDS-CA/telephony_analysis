#!/usr/bin/env python3
"""
User Feedback Trend Analysis - Identify actual content themes and patterns
Analyzes what customers are actually talking about in User Feedback reviews
"""

import pandas as pd
import re
from collections import Counter, defaultdict
import numpy as np

def extract_themes(reviews_list, rating_filter=None):
    """Extract common themes and patterns from reviews"""
    
    if rating_filter:
        reviews_list = [r for r in reviews_list if r['rating'] in rating_filter]
    
    # Combine text and analyze
    all_text = ' '.join([r['text'].lower() for r in reviews_list if isinstance(r['text'], str)])
    
    # Common words (filter out basic words)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text)
    stop_words = {'the', 'and', 'for', 'with', 'this', 'that', 'have', 'are', 'was', 'but', 'not', 'can', 'had', 'has', 'get', 'all', 'you', 'app', 'bell', 'rogers', 'very', 'good', 'bad', 'use', 'work', 'works', 'just', 'like', 'one', 'only', 'now', 'new', 'old', 'best', 'worst', 'great', 'terrible', 'love', 'hate'}
    
    filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
    word_counts = Counter(filtered_words)
    
    # Extract specific patterns
    patterns = {
        'switching': len([r for r in reviews_list if any(word in r['text'].lower() for word in ['switch', 'switching', 'change provider', 'leaving'])]),
        'customer_service': len([r for r in reviews_list if any(word in r['text'].lower() for word in ['customer service', 'support', 'representative', 'agent', 'help desk'])]),
        'money_cost': len([r for r in reviews_list if any(word in r['text'].lower() for word in ['money', 'cost', 'expensive', 'cheap', 'price', 'pricing', 'bill', 'charge'])]),
        'easy_simple': len([r for r in reviews_list if any(word in r['text'].lower() for word in ['easy', 'simple', 'user friendly', 'intuitive'])]),
        'recommend': len([r for r in reviews_list if any(word in r['text'].lower() for word in ['recommend', 'suggest', 'advise'])]),
        'years_customer': len([r for r in reviews_list if any(word in r['text'].lower() for word in ['years', 'year', 'longtime', 'long time', 'customer for'])]),
        'comparison': len([r for r in reviews_list if any(word in r['text'].lower() for word in ['than', 'better', 'compared', 'versus', 'vs'])]),
        'satisfaction': len([r for r in reviews_list if any(word in r['text'].lower() for word in ['satisfied', 'happy', 'pleased', 'disappointed', 'frustrated'])]),
    }
    
    return word_counts, patterns

def analyze_trends():
    """Analyze actual trends and themes in User Feedback"""
    
    print("🔍 TREND ANALYSIS: User Feedback Content Themes")
    print("=" * 60)
    
    # Load dataset
    df = pd.read_csv('Data/enhanced_analysis_final_clean.csv')
    user_feedback = df[df['enhanced_category'] == 'User Feedback'].copy()
    user_feedback['text'] = user_feedback['text'].fillna('').astype(str)
    
    # Convert to list of dicts for easier analysis
    reviews_data = []
    for _, row in user_feedback.iterrows():
        reviews_data.append({
            'text': row['text'],
            'rating': row['rating'],
            'provider': row['app_name'],
            'platform': row['platform']
        })
    
    print(f"📊 Analyzing {len(reviews_data):,} User Feedback reviews")
    
    # Analyze by rating groups
    print(f"\n🔍 THEME ANALYSIS BY RATING:")
    
    rating_groups = {
        'Highly Positive (5⭐)': [5],
        'Positive (4⭐)': [4], 
        'Neutral (3⭐)': [3],
        'Negative (2⭐)': [2],
        'Highly Negative (1⭐)': [1]
    }
    
    for group_name, ratings in rating_groups.items():
        group_reviews = [r for r in reviews_data if r['rating'] in ratings]
        if len(group_reviews) < 50:  # Skip small groups
            continue
            
        print(f"\n📈 {group_name} ({len(group_reviews):,} reviews):")
        
        word_counts, patterns = extract_themes(group_reviews)
        
        # Top words
        print(f"   Top themes:")
        for word, count in word_counts.most_common(12):
            if count > 10:  # Only significant themes
                print(f"     '{word}': {count}")
        
        # Patterns
        print(f"   Behavioral patterns:")
        for pattern, count in patterns.items():
            if count > 5:
                pct = count/len(group_reviews)*100
                print(f"     {pattern.replace('_', ' ').title()}: {count} ({pct:.1f}%)")
    
    # Provider comparison
    print(f"\n🏢 PROVIDER-SPECIFIC THEMES:")
    
    for provider in ['Rogers', 'Bell']:
        provider_reviews = [r for r in reviews_data if r['provider'] == provider]
        print(f"\n📱 {provider} ({len(provider_reviews):,} reviews):")
        
        # Positive themes
        positive = [r for r in provider_reviews if r['rating'] >= 4]
        if positive:
            word_counts, _ = extract_themes(positive)
            print(f"   Positive themes:")
            for word, count in word_counts.most_common(8):
                if count > 5:
                    print(f"     '{word}': {count}")
        
        # Negative themes  
        negative = [r for r in provider_reviews if r['rating'] <= 2]
        if negative:
            word_counts, _ = extract_themes(negative)
            print(f"   Negative themes:")
            for word, count in word_counts.most_common(8):
                if count > 5:
                    print(f"     '{word}': {count}")
    
    # Specific content analysis
    print(f"\n📋 CONTENT CATEGORY ANALYSIS:")
    
    # Service quality mentions
    service_reviews = [r for r in reviews_data if any(word in r['text'].lower() 
                      for word in ['service', 'customer service', 'support', 'help', 'representative', 'agent'])]
    print(f"\n🎧 Service Quality Mentions ({len(service_reviews):,} reviews):")
    print("   Sample quotes:")
    for r in service_reviews[:8]:
        print(f"     {r['rating']}⭐ '{r['text'][:80]}...'")
    
    # Brand loyalty expressions
    loyalty_reviews = [r for r in reviews_data if any(word in r['text'].lower() 
                      for word in ['years', 'longtime', 'always', 'never leave', 'loyal', 'faithful'])]
    print(f"\n💝 Brand Loyalty Expressions ({len(loyalty_reviews):,} reviews):")
    print("   Sample quotes:")
    for r in loyalty_reviews[:6]:
        print(f"     {r['rating']}⭐ '{r['text'][:80]}...'")
    
    # Competitive comparisons
    comparison_reviews = [r for r in reviews_data if any(word in r['text'].lower() 
                         for word in ['better than', 'worse than', 'compared to', 'versus', 'switch from', 'switch to'])]
    print(f"\n⚖️ Competitive Comparisons ({len(comparison_reviews):,} reviews):")
    print("   Sample quotes:")
    for r in comparison_reviews[:6]:
        print(f"     {r['rating']}⭐ '{r['text'][:80]}...'")
    
    # Pricing/value mentions
    pricing_reviews = [r for r in reviews_data if any(word in r['text'].lower() 
                      for word in ['price', 'pricing', 'cost', 'expensive', 'cheap', 'value', 'money', 'afford'])]
    print(f"\n💰 Pricing/Value Mentions ({len(pricing_reviews):,} reviews):")
    print("   Sample quotes:")
    for r in pricing_reviews[:6]:
        print(f"     {r['rating']}⭐ '{r['text'][:80]}...'")
    
    # App usability feedback
    usability_reviews = [r for r in reviews_data if any(word in r['text'].lower() 
                        for word in ['easy', 'simple', 'user friendly', 'intuitive', 'confusing', 'complicated', 'interface'])]
    print(f"\n📱 App Usability Feedback ({len(usability_reviews):,} reviews):")
    print("   Sample quotes:")
    for r in usability_reviews[:6]:
        print(f"     {r['rating']}⭐ '{r['text'][:80]}...'")
    
    # Recommended sub-categories based on trends
    print(f"\n🎯 RECOMMENDED SUB-CATEGORIES BASED ON TRENDS:")
    
    categories = {
        'Service Quality Feedback': len(service_reviews),
        'Brand Loyalty/Advocacy': len(loyalty_reviews), 
        'Competitive Comparisons': len(comparison_reviews),
        'Pricing/Value Comments': len(pricing_reviews),
        'App Usability Feedback': len(usability_reviews),
        'General Satisfaction': len([r for r in reviews_data if r['rating'] >= 4 and len(r['text'].split()) <= 10]),
        'General Dissatisfaction': len([r for r in reviews_data if r['rating'] <= 2 and len(r['text'].split()) <= 10]),
        'Non-Specific Feedback': 0  # Calculate remaining
    }
    
    # Calculate overlap and remaining
    categorized_count = 0
    overlap_ids = set()
    
    print(f"\n📊 Trend-Based Sub-Categories:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            pct = count/len(reviews_data)*100
            print(f"   {category}: {count:,} ({pct:.1f}%)")
    
    total_theme_reviews = len(service_reviews) + len(loyalty_reviews) + len(comparison_reviews) + len(pricing_reviews) + len(usability_reviews)
    
    print(f"\n✨ KEY INSIGHTS:")
    print(f"   • {total_theme_reviews:,} reviews ({total_theme_reviews/len(reviews_data)*100:.1f}%) have identifiable themes")
    print(f"   • Service Quality is major theme ({len(service_reviews):,} mentions)")
    print(f"   • Pricing/Value concerns significant ({len(pricing_reviews):,} mentions)")
    print(f"   • Brand loyalty expressions common ({len(loyalty_reviews):,} mentions)")
    print(f"   • App usability feedback valuable ({len(usability_reviews):,} mentions)")
    
    print(f"\n🎯 ACTIONABLE CATEGORIES:")
    print(f"   1. Service Quality Feedback - Understand service strengths/weaknesses")
    print(f"   2. Pricing/Value Comments - Price sensitivity and value perception")
    print(f"   3. App Usability Feedback - Interface and user experience insights")
    print(f"   4. Competitive Comparisons - Competitive positioning insights")
    print(f"   5. Brand Loyalty/Advocacy - Customer retention insights")
    print(f"   6. General Satisfaction - Short positive feedback")
    print(f"   7. General Dissatisfaction - Short negative feedback")

if __name__ == "__main__":
    analyze_trends()