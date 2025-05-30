#!/usr/bin/env python3
"""
Resilient Enhanced Analysis - Full 10K review analysis with resume capability
Can pickup from where it left off if interrupted
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

# Progress tracking files
PROGRESS_FILE = "analysis_progress.json"
RESULTS_FILE = "analysis_results.json"

def get_enhanced_category_prompt():
    """Enhanced categorization prompt"""
    return """
Categorize this telecom app review into ONE category:

1. **App Crashes** - App crashes, freezing, force close
2. **Technical Issues** - Bugs, glitches, sync issues, malfunctions  
3. **Performance** - Slow loading, lag, speed issues
4. **User Experience** - Navigation, design, interface problems
5. **Features** - Missing features, functionality gaps
6. **Authentication** - Login, password, sign-in problems
7. **Price Increases** - Rate hikes, cost complaints, billing changes
8. **Payment Issues** - Payment failures, card problems
9. **Billing** - General billing disputes, charges
10. **Coverage Issues** - Signal problems, poor reception, dead zones
11. **Roaming Issues** - International roaming, travel connectivity
12. **Network Issues** - Data connectivity, outages
13. **Service Issues** - General service quality, disruptions
14. **Customer Support** - Support quality, response times
15. **Account Management** - Profile, settings, account access
16. **Security** - Privacy, data security, account security
17. **Data Usage** - Data tracking, usage monitoring
18. **Notifications** - Push notifications, alerts
19. **User Feedback** - General praise/complaints with no specific issue

Review: "{review_text}"

Respond with ONLY the category name.
"""

def save_progress(current_index, total_reviews, results):
    """Save current progress to file"""
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

def load_progress():
    """Load previous progress if exists"""
    if os.path.exists(PROGRESS_FILE) and os.path.exists(RESULTS_FILE):
        try:
            with open(PROGRESS_FILE, 'r') as f:
                progress = json.load(f)
            
            with open(RESULTS_FILE, 'r') as f:
                results = json.load(f)
            
            return progress['current_index'], results
        except Exception as e:
            print(f"⚠️  Error loading progress: {e}")
            return 0, {}
    
    return 0, {}

def analyze_review(review_text, review_id, provider):
    """Analyze single review with error handling"""
    try:
        prompt = get_enhanced_category_prompt().format(review_text=review_text)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=30,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        category = response.content[0].text.strip()
        return category, "Neutral", True  # Default sentiment for now
        
    except Exception as e:
        print(f"❌ Error analyzing {provider} {review_id[:8]}: {str(e)}")
        return "User Feedback", "Neutral", False

def main():
    """Resilient enhanced analysis with resume capability"""
    
    print("🔄 Loading dataset...")
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    
    # Load previous progress
    start_index, existing_results = load_progress()
    
    if start_index > 0:
        print(f"📂 Found previous progress: resuming from review {start_index + 1}/{len(df)}")
        print(f"   Already completed: {len(existing_results)} reviews")
    else:
        print(f"🆕 Starting fresh analysis of {len(df):,} reviews")
        # Create backup on fresh start
        backup_file = f'Data/full_dataset_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        df.to_csv(backup_file, index=False)
        print(f"💾 Backup created: {backup_file}")
    
    print(f"\n📊 Dataset Overview:")
    print(f"   Total reviews: {len(df):,}")
    print(f"   Rogers: {len(df[df['app_name'] == 'Rogers']):,}")
    print(f"   Bell: {len(df[df['app_name'] == 'Bell']):,}")
    print(f"   Remaining to process: {len(df) - start_index:,}")
    
    # Process reviews starting from where we left off
    success_count = len([r for r in existing_results.values() if r['success']])
    error_count = len(existing_results) - success_count
    start_time = time.time()
    
    print(f"\n🤖 Starting enhanced analysis...")
    
    try:
        for idx in range(start_index, len(df)):
            review = df.iloc[idx]
            provider = review['app_name']
            review_id = review['review_id']
            
            # Analyze review
            category, sentiment, success = analyze_review(
                review['text'], 
                review_id, 
                provider
            )
            
            # Store result
            existing_results[review_id] = {
                'index': idx,
                'provider': provider,
                'category': category,
                'sentiment': sentiment,
                'success': success
            }
            
            if success:
                success_count += 1
            else:
                error_count += 1
            
            # Progress reporting
            completed = idx + 1
            if completed % 25 == 0 or completed <= 10:
                elapsed = time.time() - start_time
                rate = (completed - start_index) / elapsed * 60 if elapsed > 0 else 0
                remaining = len(df) - completed
                eta = remaining / rate if rate > 0 else 0
                
                print(f"[{completed:,}/{len(df):,}] {provider} {review_id[:8]} → {category}")
                print(f"   Rate: {rate:.1f}/min | Success: {success_count}/{completed} | ETA: {eta:.1f}min")
            
            # Save progress every 50 reviews
            if completed % 50 == 0:
                save_progress(completed, len(df), existing_results)
                print(f"💾 Progress saved at {completed:,} reviews")
            
            # Rate limiting - 42 reviews/minute based on test
            time.sleep(1.5)  # ~40 reviews per minute
    
    except KeyboardInterrupt:
        print(f"\n⏸️  Analysis interrupted by user at review {idx + 1}")
        save_progress(idx, len(df), existing_results)
        print(f"💾 Progress saved. Resume by running script again.")
        return
    
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        save_progress(idx, len(df), existing_results)
        print(f"💾 Progress saved. Resume by running script again.")
        return
    
    # Analysis complete - save final results
    save_progress(len(df), len(df), existing_results)
    
    # Generate final dataset
    print(f"\n🔄 Generating final enhanced dataset...")
    
    # Apply results to dataframe
    for review_id, result in existing_results.items():
        if result['success']:
            idx = result['index']
            df.loc[idx, 'enhanced_category'] = result['category']
            df.loc[idx, 'enhanced_sentiment'] = result['sentiment']
    
    # Save enhanced dataset
    output_file = f'Data/enhanced_analysis_complete_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(output_file, index=False)
    
    # Generate summary
    elapsed_total = time.time() - start_time
    categories = [r['category'] for r in existing_results.values() if r['success']]
    category_counts = pd.Series(categories).value_counts()
    
    print(f"\n🎯 Enhanced Analysis Complete!")
    print(f"\n📊 Final Results:")
    print(f"   Total reviews: {len(df):,}")
    print(f"   Successfully analyzed: {success_count:,} ({success_count/len(df)*100:.1f}%)")
    print(f"   Errors: {error_count:,}")
    print(f"   Total time: {elapsed_total/3600:.1f} hours")
    
    print(f"\n📈 Enhanced Category Distribution:")
    for category, count in category_counts.head(15).items():
        print(f"   {category}: {count:,}")
    
    # Save summary report
    summary_file = f'enhanced_analysis_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(summary_file, 'w') as f:
        f.write(f"Enhanced 10K Review Analysis - Final Report\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        f.write(f"Dataset: {len(df):,} reviews\n")
        f.write(f"Success rate: {success_count/len(df)*100:.1f}%\n")
        f.write(f"Analysis time: {elapsed_total/3600:.1f} hours\n\n")
        f.write("Enhanced Category Distribution:\n")
        for category, count in category_counts.items():
            f.write(f"  {category}: {count:,}\n")
    
    # Cleanup progress files
    if os.path.exists(PROGRESS_FILE):
        os.remove(PROGRESS_FILE)
    if os.path.exists(RESULTS_FILE):
        os.remove(RESULTS_FILE)
    
    print(f"""
🏁 Analysis Complete!

📁 Files generated:
   • Enhanced dataset: {output_file}
   • Summary report: {summary_file}
   
🔄 Next steps:
   1. Review the enhanced categories
   2. Update main dataset: cp {output_file} Data/analyzed_reviews_filtered_clean.csv
   3. Regenerate dashboard with enhanced insights
   4. Analyze new category patterns for strategic insights
   
✨ Key insights now available:
   • Price Increases: {category_counts.get('Price Increases', 0):,} reviews
   • App Crashes: {category_counts.get('App Crashes', 0):,} reviews
   • Coverage Issues: {category_counts.get('Coverage Issues', 0):,} reviews
   • Payment Issues: {category_counts.get('Payment Issues', 0):,} reviews
""")

if __name__ == "__main__":
    main()