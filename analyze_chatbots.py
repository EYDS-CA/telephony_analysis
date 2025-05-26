#!/usr/bin/env python3
"""
Analyze mentions of AI chatbots (Anna for Rogers, AI chat for Bell) in reviews.
"""

import pandas as pd
import re

def analyze_chatbot_mentions():
    """Extract and analyze all chatbot-related reviews."""
    
    print("Loading analyzed reviews...")
    df = pd.read_csv('telecom_app_reviews_complete.csv')
    
    # Define search patterns
    chatbot_keywords = [
        'anna', 'chatbot', 'chat bot', 'live chat', 'ai chat', 
        'virtual assistant', 'automated chat', 'chat support',
        'chat agent', 'chat help'
    ]
    
    # Create regex pattern
    pattern = '|'.join(chatbot_keywords)
    
    # Find reviews mentioning chatbots
    df['text_lower'] = df['text'].fillna('').str.lower() + ' ' + df['claude_summary'].fillna('').str.lower()
    df['mentions_chatbot'] = df['text_lower'].str.contains(pattern, case=False, na=False)
    
    chatbot_reviews = df[df['mentions_chatbot']].copy()
    
    print(f"\nFound {len(chatbot_reviews)} reviews mentioning chatbots")
    print(f"Rogers: {len(chatbot_reviews[chatbot_reviews['app_name'] == 'Rogers'])} reviews")
    print(f"Bell: {len(chatbot_reviews[chatbot_reviews['app_name'] == 'Bell'])} reviews")
    
    # Analyze Anna (Rogers) specifically
    anna_reviews = chatbot_reviews[
        (chatbot_reviews['app_name'] == 'Rogers') & 
        (chatbot_reviews['text_lower'].str.contains('anna', case=False, na=False))
    ]
    
    print(f"\n=== ANNA (Rogers Virtual Assistant) ===")
    print(f"Total mentions: {len(anna_reviews)}")
    
    if len(anna_reviews) > 0:
        print(f"Sentiment breakdown:")
        print(anna_reviews['claude_sentiment'].value_counts())
        print(f"\nAverage rating: {anna_reviews['rating'].mean():.2f}")
        
        print("\nSample Anna reviews:")
        for idx, row in anna_reviews.head(5).iterrows():
            print(f"\n- Rating: {row['rating']}/5 | Sentiment: {row['claude_sentiment']}")
            print(f"  Text: {row['text'][:200]}...")
            if pd.notna(row['claude_summary']):
                print(f"  Summary: {row['claude_summary']}")
    
    # Analyze Bell AI chat
    bell_chat_reviews = chatbot_reviews[chatbot_reviews['app_name'] == 'Bell']
    
    print(f"\n=== BELL AI/LIVE CHAT ===")
    print(f"Total mentions: {len(bell_chat_reviews)}")
    
    if len(bell_chat_reviews) > 0:
        print(f"Sentiment breakdown:")
        print(bell_chat_reviews['claude_sentiment'].value_counts())
        print(f"\nAverage rating: {bell_chat_reviews['rating'].mean():.2f}")
        
        print("\nSample Bell chat reviews:")
        for idx, row in bell_chat_reviews.head(5).iterrows():
            print(f"\n- Rating: {row['rating']}/5 | Sentiment: {row['claude_sentiment']}")
            print(f"  Text: {row['text'][:200]}...")
            if pd.notna(row['claude_summary']):
                print(f"  Summary: {row['claude_summary']}")
    
    # Compare effectiveness
    print(f"\n=== COMPARISON ===")
    
    # Calculate metrics for each
    rogers_chat_all = chatbot_reviews[chatbot_reviews['app_name'] == 'Rogers']
    bell_chat_all = chatbot_reviews[chatbot_reviews['app_name'] == 'Bell']
    
    rogers_negative_pct = (rogers_chat_all['claude_sentiment'] == 'Negative').sum() / len(rogers_chat_all) * 100 if len(rogers_chat_all) > 0 else 0
    bell_negative_pct = (bell_chat_all['claude_sentiment'] == 'Negative').sum() / len(bell_chat_all) * 100 if len(bell_chat_all) > 0 else 0
    
    print(f"Rogers chatbot negative sentiment: {rogers_negative_pct:.1f}%")
    print(f"Bell chatbot negative sentiment: {bell_negative_pct:.1f}%")
    
    # Look for specific complaints
    print(f"\n=== COMMON COMPLAINTS ===")
    
    complaint_patterns = {
        'useless': 'useless|pointless|waste of time|doesn\'t help',
        'doesnt_understand': 'doesn\'t understand|can\'t understand|not understanding',
        'loop': 'loop|circle|round and round|going nowhere',
        'want_human': 'real person|human|actual person|speak to someone',
        'frustrating': 'frustrat|annoying|terrible|awful'
    }
    
    for complaint_type, pattern in complaint_patterns.items():
        rogers_count = rogers_chat_all[rogers_chat_all['text_lower'].str.contains(pattern, case=False, na=False)].shape[0]
        bell_count = bell_chat_all[bell_chat_all['text_lower'].str.contains(pattern, case=False, na=False)].shape[0]
        
        print(f"\n{complaint_type.replace('_', ' ').title()}:")
        print(f"  Rogers: {rogers_count} mentions")
        print(f"  Bell: {bell_count} mentions")
    
    # Save detailed results
    chatbot_reviews_output = chatbot_reviews[['app_name', 'rating', 'claude_sentiment', 'text', 'claude_summary', 'primary_category']]
    chatbot_reviews_output.to_csv('chatbot_analysis.csv', index=False)
    print(f"\n✓ Detailed analysis saved to chatbot_analysis.csv")
    
    return chatbot_reviews

if __name__ == "__main__":
    chatbot_reviews_df = analyze_chatbot_mentions()