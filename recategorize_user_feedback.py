#!/usr/bin/env python3
"""
User Feedback Re-categorization Script
Re-categorizes 7,131 "User Feedback" reviews into specific actionable categories
Updates existing enhanced_category column (no new columns)
"""

import pandas as pd
import anthropic
import time
import json
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# Claude API setup
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

# Progress tracking
PROGRESS_FILE = "recategorization_progress.json"
RESULTS_FILE = "recategorization_results.json"

def get_recategorization_prompt():
    """Prompt for re-categorizing User Feedback into specific categories"""
    return """Re-categorize this User Feedback review into ONE specific category:

1. **Customer Support** - Customer service experiences, support quality, representatives, help desk
2. **Performance** - App speed, loading, lag, responsiveness, crashes, freezing
3. **Brand Loyalty** - Long-term customer expressions, "years with", loyalty statements, advocacy
4. **UX Complaints** - Interface problems, navigation issues, confusing design, usability complaints
5. **UX Praise** - Easy to use, user-friendly, intuitive, good interface, simple navigation
6. **General Dissatisfaction** - Vague negative feedback without specific actionable issues
7. **Pricing/Value Comments** - Cost concerns, expensive, cheap, value for money, pricing feedback
8. **Service Quality** - Network service, reliability, coverage quality (not customer support)
9. **Competitive Comparisons** - Comparing to other providers, switching mentions, "better than"

Review: "{review_text}"
Rating: {rating} stars

Respond with ONLY the category name."""

def recategorize_single_review(review_data):
    """Re-categorize a single User Feedback review"""
    try:
        review_text, review_id, rating, index = review_data
        
        prompt = get_recategorization_prompt().format(
            review_text=review_text[:300],  # Truncate for efficiency
            rating=rating
        )
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",  # Fast and cheap
            max_tokens=20,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        new_category = response.content[0].text.strip()
        
        return {
            'review_id': review_id,
            'index': index,
            'old_category': 'User Feedback',
            'new_category': new_category,
            'success': True
        }
        
    except Exception as e:
        print(f"❌ Error recategorizing {review_id[:8]}: {str(e)}")
        return {
            'review_id': review_id,
            'index': index,
            'old_category': 'User Feedback',
            'new_category': 'General Dissatisfaction',  # Fallback
            'success': False
        }

def load_progress():
    """Load existing recategorization progress"""
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
    """Save recategorization progress"""
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

def process_batch_concurrent(batch_data, max_workers=50):
    """Process batch with concurrent requests"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(recategorize_single_review, batch_data))
    return results

def main():
    """Main re-categorization process"""
    
    print("🔄 USER FEEDBACK RE-CATEGORIZATION")
    print("🎯 Converting vague 'User Feedback' into actionable categories")
    print("=" * 60)
    
    # Load dataset
    df = pd.read_csv('Data/enhanced_analysis_final_clean.csv')
    
    # Filter for User Feedback reviews only
    user_feedback_reviews = df[df['enhanced_category'] == 'User Feedback'].copy()
    user_feedback_reviews['text'] = user_feedback_reviews['text'].fillna('').astype(str)
    
    print(f"📊 Dataset Overview:")
    print(f"   Total reviews: {len(df):,}")
    print(f"   User Feedback reviews: {len(user_feedback_reviews):,}")
    print(f"   Percentage: {len(user_feedback_reviews)/len(df)*100:.1f}%")
    
    # Load progress
    start_index, existing_results = load_progress()
    
    remaining_reviews = user_feedback_reviews.iloc[start_index:].copy()
    
    print(f"\n🔄 Re-categorization Status:")
    print(f"   Starting from: {start_index:,}")
    print(f"   Remaining: {len(remaining_reviews):,}")
    print(f"   Already completed: {len(existing_results):,}")
    
    if len(remaining_reviews) == 0:
        print("✅ All User Feedback reviews already re-categorized!")
        # Apply existing results and generate final dataset
        print("🔄 Applying existing results to dataset...")
        for result in existing_results.values():
            if result['success']:
                df.loc[result['index'], 'enhanced_category'] = result['new_category']
        
        output_file = 'Data/recategorized_analysis_final.csv'
        df.to_csv(output_file, index=False)
        print(f"✅ Final dataset saved: {output_file}")
        return
    
    # Calculate batch optimization
    batch_size = 100  # Reviews per batch
    total_batches = (len(remaining_reviews) + batch_size - 1) // batch_size
    estimated_time = total_batches * 3 / 60  # 3 seconds per batch
    
    print(f"\n⏱️  Processing Plan:")
    print(f"   Batch size: {batch_size}")
    print(f"   Total batches: {total_batches}")
    print(f"   Estimated time: {estimated_time:.1f} minutes")
    print(f"   Expected rate: ~2000 reviews/min")
    
    # Process batches
    start_time = time.time()
    success_count = len([r for r in existing_results.values() if r['success']])
    
    try:
        for batch_num in range(total_batches):
            batch_start = batch_num * batch_size
            batch_end = min(batch_start + batch_size, len(remaining_reviews))
            batch_reviews = remaining_reviews.iloc[batch_start:batch_end]
            
            print(f"\n📦 Batch {batch_num + 1}/{total_batches} ({start_index + batch_start + 1}-{start_index + batch_end})")
            
            # Prepare batch data
            batch_data = []
            for idx, (df_idx, review) in enumerate(batch_reviews.iterrows()):
                actual_index = df_idx  # Use original dataframe index
                batch_data.append((
                    review['text'],
                    review['review_id'],
                    review['rating'],
                    actual_index
                ))
            
            # Process batch
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
            completed = start_index + batch_end
            elapsed = time.time() - start_time
            current_rate = (completed - start_index) / elapsed * 60 if elapsed > 0 else 0
            
            print(f"   ✅ Processed {len(batch_results)} reviews in {batch_time:.1f}s")
            print(f"   📈 Batch success: {batch_success}/{len(batch_results)}")
            print(f"   ⚡ Current rate: {current_rate:.0f} reviews/min")
            
            # Save progress
            save_progress(completed, len(user_feedback_reviews), existing_results)
            
            # Rate limiting
            if batch_num < total_batches - 1:
                time.sleep(2)  # 2 second delay between batches
    
    except KeyboardInterrupt:
        print(f"\n⏸️  Re-categorization interrupted - progress saved")
        return
    except Exception as e:
        print(f"\n❌ Error: {e} - progress saved")
        return
    
    # Apply results to dataset
    print(f"\n🔄 Applying re-categorization results to dataset...")
    
    for result in existing_results.values():
        if result['success']:
            df.loc[result['index'], 'enhanced_category'] = result['new_category']
    
    # Generate final dataset
    output_file = f'Data/recategorized_analysis_final_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(output_file, index=False)
    
    # Results analysis
    total_time = time.time() - start_time
    final_rate = len(remaining_reviews) / total_time * 60
    
    # Category distribution
    new_categories = [r['new_category'] for r in existing_results.values() if r['success']]
    category_counts = pd.Series(new_categories).value_counts()
    
    print(f"\n🎯 RE-CATEGORIZATION COMPLETE!")
    print(f"   📊 Processed: {len(remaining_reviews):,} User Feedback reviews")
    print(f"   ⏱️  Total time: {total_time/60:.1f} minutes")
    print(f"   ⚡ Final rate: {final_rate:.0f} reviews/min")
    print(f"   ✅ Success: {success_count:,}/{len(existing_results):,}")
    
    print(f"\n📈 New Category Distribution:")
    for category, count in category_counts.items():
        pct = count/len(existing_results)*100
        print(f"   {category}: {count:,} ({pct:.1f}%)")
    
    # Final dataset summary
    final_category_dist = df['enhanced_category'].value_counts()
    print(f"\n📊 Final Enhanced Dataset ({len(df):,} reviews):")
    print(f"   Categories: {len(final_category_dist)}")
    print(f"   Top categories:")
    for category, count in final_category_dist.head(10).items():
        print(f"     {category}: {count:,}")
    
    # Cleanup progress files
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
    
    print(f"""
🏁 USER FEEDBACK RE-CATEGORIZATION SUCCESS!

📁 Final dataset: {output_file}
🎯 Actionable categories: {len(category_counts)}
📊 Total reviews: {len(df):,}

✨ Key achievements:
   • Converted vague 'User Feedback' into {len(category_counts)} actionable categories
   • {category_counts.get('Customer Support', 0):,} Customer Support insights
   • {category_counts.get('UX Praise', 0):,} UX Praise + {category_counts.get('UX Complaints', 0):,} UX Complaints
   • {category_counts.get('Brand Loyalty', 0):,} Brand Loyalty expressions
   • {category_counts.get('Performance', 0):,} Performance feedback
   
🔄 Ready for dashboard regeneration with enhanced insights!
""")

if __name__ == "__main__":
    main()