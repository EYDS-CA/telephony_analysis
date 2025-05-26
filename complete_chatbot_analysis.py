#!/usr/bin/env python3
"""
Complete chatbot analysis across all datasets.
"""

import pandas as pd

def analyze_all_chatbot_mentions():
    """Analyze chatbot mentions across analyzed, unanalyzed, and cleaned datasets."""
    
    print("=== COMPLETE CHATBOT ANALYSIS ACROSS ALL DATASETS ===\n")
    
    # Load all datasets
    analyzed = pd.read_csv('telecom_app_reviews_complete.csv')
    unanalyzed = pd.read_csv('telecom_app_reviews_unanalyzed.csv')
    cleaned = pd.read_csv('telecom_app_reviews_cleaned.csv')
    
    # Define search pattern
    chatbot_pattern = 'anna|chatbot|chat bot|live chat|ai chat|virtual assistant|automated chat|chat support|chat agent|chat help'
    
    # Search in each dataset
    datasets = {
        'Analyzed': analyzed,
        'Unanalyzed': unanalyzed,
        'Total Cleaned': cleaned
    }
    
    results = {}
    
    for name, df in datasets.items():
        # Create combined text field
        df['combined_text'] = df['text'].fillna('').str.lower()
        if 'claude_summary' in df.columns:
            df['combined_text'] += ' ' + df['claude_summary'].fillna('').str.lower()
        
        # Find mentions
        df['mentions_chatbot'] = df['combined_text'].str.contains(chatbot_pattern, case=False, na=False)
        
        # Count by app
        rogers_count = len(df[(df['app_name'] == 'Rogers') & df['mentions_chatbot']])
        bell_count = len(df[(df['app_name'] == 'Bell') & df['mentions_chatbot']])
        
        # Anna specific (Rogers)
        df['mentions_anna'] = df['combined_text'].str.contains('anna', case=False, na=False)
        anna_count = len(df[(df['app_name'] == 'Rogers') & df['mentions_anna']])
        
        results[name] = {
            'total_reviews': len(df),
            'rogers_reviews': len(df[df['app_name'] == 'Rogers']),
            'bell_reviews': len(df[df['app_name'] == 'Bell']),
            'rogers_chatbot': rogers_count,
            'bell_chatbot': bell_count,
            'rogers_anna': anna_count
        }
    
    # Display results
    print("Dataset Coverage:")
    print(f"{'Dataset':<15} {'Total Reviews':<15} {'Rogers':<15} {'Bell':<15}")
    print("-" * 60)
    for name, stats in results.items():
        print(f"{name:<15} {stats['total_reviews']:<15,} {stats['rogers_reviews']:<15,} {stats['bell_reviews']:<15,}")
    
    print("\n\nChatbot Mentions:")
    print(f"{'Dataset':<15} {'Rogers Chatbot':<20} {'Bell Chatbot':<20} {'Anna Specific':<20}")
    print("-" * 75)
    for name, stats in results.items():
        print(f"{name:<15} {stats['rogers_chatbot']:<20} {stats['bell_chatbot']:<20} {stats['rogers_anna']:<20}")
    
    # Calculate true proportions
    total_rogers_reviews = results['Total Cleaned']['rogers_reviews']
    total_bell_reviews = results['Total Cleaned']['bell_reviews']
    total_rogers_chatbot = results['Total Cleaned']['rogers_chatbot']
    total_bell_chatbot = results['Total Cleaned']['bell_chatbot']
    
    print("\n\n=== TRUE COMPARISON (from complete cleaned dataset) ===")
    print(f"\nTotal Reviews:")
    print(f"  Rogers: {total_rogers_reviews:,}")
    print(f"  Bell: {total_bell_reviews:,}")
    
    print(f"\nChatbot Mentions:")
    print(f"  Rogers: {total_rogers_chatbot} ({total_rogers_chatbot/total_rogers_reviews*100:.2f}% of Rogers reviews)")
    print(f"  Bell: {total_bell_chatbot} ({total_bell_chatbot/total_bell_reviews*100:.2f}% of Bell reviews)")
    
    print(f"\nTrue Ratio:")
    ratio = total_rogers_chatbot / total_bell_chatbot if total_bell_chatbot > 0 else 0
    print(f"  Rogers has {ratio:.1f}x more chatbot mentions than Bell")
    
    # Adjust for review volume
    rogers_rate = total_rogers_chatbot / total_rogers_reviews
    bell_rate = total_bell_chatbot / total_bell_reviews
    adjusted_ratio = rogers_rate / bell_rate if bell_rate > 0 else 0
    
    print(f"\nAdjusted for review volume:")
    print(f"  Rogers users are {adjusted_ratio:.1f}x more likely to mention chatbots")
    
    # Anna specific analysis
    total_anna = results['Total Cleaned']['rogers_anna']
    print(f"\n\nAnna (Rogers AI) Specific:")
    print(f"  Total Anna mentions: {total_anna}")
    print(f"  {total_anna/total_rogers_reviews*100:.2f}% of Rogers reviews mention Anna")
    print(f"  {total_anna/total_rogers_chatbot*100:.1f}% of Rogers chatbot mentions are specifically about Anna")
    
    # Sample unanalyzed Bell chatbot mentions
    print("\n\n=== SAMPLE UNANALYZED BELL CHATBOT MENTIONS ===")
    bell_chatbot_unanalyzed = unanalyzed[
        (unanalyzed['app_name'] == 'Bell') & 
        (unanalyzed['combined_text'].str.contains(chatbot_pattern, case=False, na=False))
    ]
    
    if len(bell_chatbot_unanalyzed) > 0:
        print(f"\nFound {len(bell_chatbot_unanalyzed)} Bell chatbot mentions in unanalyzed data:")
        for idx, row in bell_chatbot_unanalyzed.head(5).iterrows():
            print(f"\n- Rating: {row['rating']}/5")
            print(f"  Text: {row['text'][:200]}...")
    
    return results

if __name__ == "__main__":
    results = analyze_all_chatbot_mentions()