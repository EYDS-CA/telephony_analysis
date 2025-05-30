#!/usr/bin/env python3
"""
Optimized Enhanced Analysis - Fully utilizes Tier 4 Claude Haiku limits
4,000 requests/min, 400K input tokens/min, 80K output tokens/min
"""

import pandas as pd
import anthropic
import asyncio
import time
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import threading

# Claude API setup
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Progress tracking
PROGRESS_FILE = "analysis_progress.json"
RESULTS_FILE = "analysis_results.json"

# Rate limiting (conservative but fast)
MAX_CONCURRENT = 100  # Process 100 reviews concurrently
BATCH_SIZE = 200      # Process in batches of 200
BATCH_DELAY = 3       # 3 seconds between batches

def get_optimized_prompt():
    """Ultra-compact prompt for speed"""
    return """Categorize review:

App Crashes | Technical Issues | Performance | User Experience | Features | Authentication | Price Increases | Payment Issues | Billing | Coverage Issues | Roaming Issues | Network Issues | Service Issues | Customer Support | Account Management | Security | Data Usage | Notifications | User Feedback

Review: "{review_text}"

Category:"""

def analyze_single_review(review_data):
    """Optimized single review analysis"""
    try:
        review_text, review_id, provider, index = review_data
        
        prompt = get_optimized_prompt().format(review_text=review_text[:300])  # Truncate for speed
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Use faster Haiku model
            max_tokens=15,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        category = response.content[0].text.strip()
        
        return {
            'review_id': review_id,
            'index': index,
            'provider': provider,
            'category': category,
            'sentiment': 'Neutral',  # Skip sentiment for speed
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Error {provider} {review_id[:8]}: {str(e)}")
        return {
            'review_id': review_id,
            'index': index, 
            'provider': provider,
            'category': 'User Feedback',
            'sentiment': 'Neutral',
            'success': False
        }

def load_progress():
    """Load existing progress"""
    if os.path.exists(PROGRESS_FILE) and os.path.exists(RESULTS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
            return progress['current_index'], results
        except:
            return 0, {}
    return 0, {}

def save_progress(current_index, total_reviews, results):
    """Save progress"""
    progress_data = {
        "current_index": current_index,
        "total_reviews": total_reviews,
        "timestamp": datetime.now().isoformat(),
        "completed_count": len(results)
    }
    
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress_data, f)
    
    with open(RESULTS_FILE, 'w') as f:
        json.dump(results, f)

def process_batch_concurrent(batch_data):
    """Process a batch with concurrent requests"""
    with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
        results = list(executor.map(analyze_single_review, batch_data))
    return results

def main():
    """Optimized main analysis"""
    
    print("🚀 OPTIMIZED Enhanced Analysis - Using Full Tier 4 Capacity")
    print("⚡ Model: Claude Haiku (faster, cheaper)")
    print("🔄 Concurrency: 100 simultaneous requests")
    print("📦 Batch size: 200 reviews")
    
    # Load dataset
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    
    # Load progress
    start_index, existing_results = load_progress()
    
    print(f"\n📊 Dataset Status:")
    print(f"   Total reviews: {len(df):,}")
    print(f"   Starting from: {start_index:,}")
    print(f"   Remaining: {len(df) - start_index:,}")
    print(f"   Already completed: {len(existing_results):,}")
    
    # Calculate optimization
    remaining = len(df) - start_index
    total_batches = (remaining + BATCH_SIZE - 1) // BATCH_SIZE
    estimated_time = total_batches * BATCH_DELAY / 60  # minutes
    
    print(f"\n⏱️  Optimization Estimates:")
    print(f"   Batches needed: {total_batches}")
    print(f"   Estimated time: {estimated_time:.1f} minutes")
    print(f"   Expected rate: ~{remaining/estimated_time:.0f} reviews/min")
    
    # Process remaining reviews
    start_time = time.time()
    success_count = len([r for r in existing_results.values() if r['success']])
    
    try:
        for batch_num in range(total_batches):
            batch_start = start_index + (batch_num * BATCH_SIZE)
            batch_end = min(batch_start + BATCH_SIZE, len(df))
            
            if batch_start >= len(df):
                break
                
            batch_df = df.iloc[batch_start:batch_end]
            
            print(f"\n📦 Batch {batch_num + 1}/{total_batches} ({batch_start+1}-{batch_end})")
            
            # Prepare batch data
            batch_data = []
            for idx, (_, review) in enumerate(batch_df.iterrows()):
                actual_index = batch_start + idx
                batch_data.append((
                    review['text'],
                    review['review_id'], 
                    review['app_name'],
                    actual_index
                ))
            
            # Process batch concurrently
            batch_start_time = time.time()
            batch_results = process_batch_concurrent(batch_data)
            batch_time = time.time() - batch_start_time
            
            # Update results
            batch_success = 0
            for result in batch_results:
                existing_results[result['review_id']] = result
                if result['success']:
                    batch_success += 1
                    success_count += 1
            
            # Progress reporting
            completed = batch_end
            elapsed = time.time() - start_time
            current_rate = (completed - start_index) / elapsed * 60 if elapsed > 0 else 0
            
            print(f"   ✅ Processed {len(batch_results)} reviews in {batch_time:.1f}s")
            print(f"   📈 Batch success: {batch_success}/{len(batch_results)}")
            print(f"   ⚡ Current rate: {current_rate:.0f} reviews/min")
            print(f"   🏁 Overall progress: {completed:,}/{len(df):,} ({completed/len(df)*100:.1f}%)")
            
            # Save progress
            save_progress(completed, len(df), existing_results)
            
            # Rate limiting delay
            if batch_num < total_batches - 1:
                print(f"   ⏸️  Rate limit delay: {BATCH_DELAY}s...")
                time.sleep(BATCH_DELAY)
    
    except KeyboardInterrupt:
        print(f"\n⏸️  Analysis interrupted - progress saved")
        return
    except Exception as e:
        print(f"\n❌ Error: {e} - progress saved")
        return
    
    # Final results
    total_time = time.time() - start_time
    final_rate = (len(df) - start_index) / total_time * 60
    
    print(f"\n🎯 OPTIMIZED ANALYSIS COMPLETE!")
    print(f"   📊 Processed: {len(df) - start_index:,} reviews")
    print(f"   ⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"   ⚡ Final rate: {final_rate:.0f} reviews/min")
    print(f"   ✅ Success: {success_count:,}/{len(existing_results):,}")
    
    # Generate final dataset
    print(f"\n🔄 Generating optimized dataset...")
    
    for review_id, result in existing_results.items():
        if result['success']:
            idx = result['index']
            df.loc[idx, 'enhanced_category'] = result['category']
            df.loc[idx, 'enhanced_sentiment'] = result['sentiment']
    
    # Save final results
    output_file = f'Data/optimized_enhanced_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(output_file, index=False)
    
    # Category summary
    categories = [r['category'] for r in existing_results.values() if r['success']]
    category_counts = pd.Series(categories).value_counts()
    
    print(f"\n📈 Final Enhanced Categories:")
    for category, count in category_counts.head(15).items():
        print(f"   {category}: {count:,}")
    
    # Cleanup progress files
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
    
    print(f"""
🏁 OPTIMIZATION SUCCESS!

🚀 Performance:
   • Used Claude Haiku (faster + cheaper)
   • 100 concurrent requests per batch
   • {final_rate:.0f} reviews/min vs 40 reviews/min before
   • {final_rate/40:.1f}x speed improvement!

📁 Results:
   • Enhanced dataset: {output_file}
   • Ready for dashboard regeneration
   
🎯 Key Enhanced Categories:
   • Price Increases: {category_counts.get('Price Increases', 0):,}
   • App Crashes: {category_counts.get('App Crashes', 0):,}
   • Payment Issues: {category_counts.get('Payment Issues', 0):,}
   • Authentication: {category_counts.get('Authentication', 0):,}
""")

if __name__ == "__main__":
    main()