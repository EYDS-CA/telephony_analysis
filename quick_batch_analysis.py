#!/usr/bin/env python3
"""
Quick Batch Analysis - Process reviews in manageable batches
"""

import pandas as pd
import anthropic
import time
import json
import os
from datetime import datetime

# Claude API setup
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def get_category_prompt():
    """Optimized categorization prompt"""
    return """
Categorize this review into ONE category:

App Crashes | Technical Issues | Performance | User Experience | Features | Authentication | Price Increases | Payment Issues | Billing | Coverage Issues | Roaming Issues | Network Issues | Service Issues | Customer Support | Account Management | Security | Data Usage | Notifications | User Feedback

Review: "{review_text}"

Respond with ONLY the category name.
"""

def analyze_batch(reviews_batch):
    """Analyze a batch of reviews"""
    results = []
    
    for _, review in reviews_batch.iterrows():
        try:
            prompt = get_category_prompt().format(review_text=review['text'])
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=20,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            category = response.content[0].text.strip()
            results.append({
                'review_id': review['review_id'],
                'provider': review['app_name'],
                'category': category,
                'success': True
            })
            
            print(f"✅ {review['app_name']} {review['review_id'][:8]} → {category}")
            
        except Exception as e:
            print(f"❌ {review['app_name']} {review['review_id'][:8]} → Error: {str(e)}")
            results.append({
                'review_id': review['review_id'],
                'provider': review['app_name'],
                'category': 'User Feedback',
                'success': False
            })
        
        time.sleep(0.3)  # Rate limiting
    
    return results

def main():
    """Process reviews in batches"""
    
    print("🔄 Loading dataset...")
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    
    # Process first 500 reviews to start
    batch_size = 500
    total_batches = (len(df) + batch_size - 1) // batch_size
    
    print(f"📊 Processing first {batch_size} reviews...")
    print(f"   Total reviews: {len(df):,}")
    print(f"   This batch: {batch_size}")
    print(f"   Total batches available: {total_batches}")
    
    # Take first batch
    batch_df = df.head(batch_size)
    
    print(f"\n🤖 Starting batch analysis...")
    start_time = time.time()
    
    # Process batch
    results = analyze_batch(batch_df)
    
    # Calculate results
    success_count = sum(1 for r in results if r['success'])
    error_count = len(results) - success_count
    elapsed = time.time() - start_time
    
    print(f"\n📈 Batch Results:")
    print(f"   Processed: {len(results)} reviews")
    print(f"   Success: {success_count} ({success_count/len(results)*100:.1f}%)")
    print(f"   Errors: {error_count}")
    print(f"   Time: {elapsed/60:.1f} minutes")
    print(f"   Rate: {len(results)/elapsed*60:.1f} reviews/minute")
    
    # Category distribution
    categories = [r['category'] for r in results if r['success']]
    category_counts = pd.Series(categories).value_counts()
    
    print(f"\nCategory distribution (first {batch_size}):")
    for category, count in category_counts.items():
        print(f"   {category}: {count}")
    
    # Apply results to dataframe
    for result in results:
        if result['success']:
            mask = df['review_id'] == result['review_id']
            df.loc[mask, 'enhanced_category'] = result['category']
    
    # Save partial results
    output_file = f'batch_analysis_first_{batch_size}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    batch_df_enhanced = df.head(batch_size)
    batch_df_enhanced.to_csv(output_file, index=False)
    
    print(f"\n✅ Batch analysis complete!")
    print(f"   Results saved: {output_file}")
    print(f"   {len(df) - batch_size:,} reviews remaining")
    
    # Estimate full analysis time
    full_time_estimate = (elapsed / batch_size) * len(df) / 3600  # hours
    print(f"   Full analysis estimate: {full_time_estimate:.1f} hours")
    
    print(f"\n🔄 To continue with next batch, modify batch_size or start_index in script")

if __name__ == "__main__":
    main()