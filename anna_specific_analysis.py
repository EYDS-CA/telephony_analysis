#!/usr/bin/env python3
"""
Specific analysis of Anna (Rogers AI assistant) mentions.
"""

import pandas as pd

def analyze_anna_specifically():
    """Deep dive into Anna mentions."""
    
    df = pd.read_csv('telecom_app_reviews_complete.csv')
    
    # Find Anna mentions
    anna_mask = (
        (df['app_name'] == 'Rogers') & 
        (df['text'].fillna('').str.contains('anna', case=False) | 
         df['claude_summary'].fillna('').str.contains('anna', case=False))
    )
    
    anna_reviews = df[anna_mask].copy()
    
    print(f"=== ANNA (Rogers Virtual Assistant) DETAILED ANALYSIS ===")
    print(f"Total Anna mentions: {len(anna_reviews)}")
    
    # Sentiment analysis
    print(f"\nSentiment Distribution:")
    sentiment_counts = anna_reviews['claude_sentiment'].value_counts()
    for sentiment, count in sentiment_counts.items():
        pct = count / len(anna_reviews) * 100
        print(f"  {sentiment}: {count} ({pct:.1f}%)")
    
    # Rating analysis
    print(f"\nRating Distribution:")
    rating_counts = anna_reviews['rating'].value_counts().sort_index()
    for rating, count in rating_counts.items():
        print(f"  {rating} stars: {count}")
    
    print(f"\nAverage rating: {anna_reviews['rating'].mean():.2f}/5")
    
    # Specific complaints about Anna
    print(f"\n=== SPECIFIC ANNA COMPLAINTS ===")
    
    # Extract Anna-specific text
    anna_specific_complaints = []
    
    for idx, row in anna_reviews.iterrows():
        text = str(row['text']).lower()
        
        # Find sentences mentioning Anna
        sentences = text.split('.')
        anna_sentences = [s for s in sentences if 'anna' in s]
        
        if anna_sentences:
            anna_specific_complaints.extend(anna_sentences)
    
    # Common themes
    themes = {
        'useless': ['useless', 'pointless', 'waste', 'no help'],
        'crashes': ['crash', 'freeze', 'stop working', 'not working'],
        'loops': ['loop', 'circle', 'round and round', 'repeat'],
        'understanding': ['understand', 'comprehend', 'get it'],
        'human_preference': ['real person', 'human', 'agent', 'representative']
    }
    
    theme_counts = {theme: 0 for theme in themes}
    
    for complaint in anna_specific_complaints:
        for theme, keywords in themes.items():
            if any(keyword in complaint for keyword in keywords):
                theme_counts[theme] += 1
    
    print("\nCommon complaint themes:")
    for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {theme.replace('_', ' ').title()}: {count} mentions")
    
    # Show actual Anna complaints
    print(f"\n=== SAMPLE ANNA-SPECIFIC COMPLAINTS ===")
    
    negative_anna = anna_reviews[anna_reviews['claude_sentiment'] == 'Negative'].head(10)
    
    for idx, row in negative_anna.iterrows():
        text = str(row['text'])
        # Find Anna-specific part
        anna_part = ""
        for sentence in text.split('.'):
            if 'anna' in sentence.lower():
                anna_part = sentence.strip()
                break
        
        if anna_part:
            print(f"\n- Rating: {row['rating']}/5")
            print(f"  \"{anna_part}\"")
            if pd.notna(row['claude_summary']):
                print(f"  Context: {row['claude_summary']}")
    
    # Compare to overall Rogers sentiment
    all_rogers = df[df['app_name'] == 'Rogers']
    rogers_negative_pct = (all_rogers['claude_sentiment'] == 'Negative').sum() / len(all_rogers) * 100
    anna_negative_pct = (anna_reviews['claude_sentiment'] == 'Negative').sum() / len(anna_reviews) * 100
    
    print(f"\n=== IMPACT ANALYSIS ===")
    print(f"Rogers overall negative sentiment: {rogers_negative_pct:.1f}%")
    print(f"Anna-related negative sentiment: {anna_negative_pct:.1f}%")
    print(f"Anna is {anna_negative_pct / rogers_negative_pct:.1f}x more negative than Rogers average")
    
    # Save Anna reviews
    anna_reviews[['rating', 'claude_sentiment', 'text', 'claude_summary', 'date']].to_csv('anna_reviews.csv', index=False)
    print(f"\n✓ All Anna reviews saved to anna_reviews.csv")
    
    return anna_reviews

if __name__ == "__main__":
    anna_df = analyze_anna_specifically()