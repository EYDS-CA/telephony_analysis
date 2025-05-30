#!/usr/bin/env python3
"""
Comprehensive 10K Review Re-analysis Script
Enhanced category system based on review patterns
Optimized for API rate limits: 4,000 requests/minute, 400K tokens/minute
"""

import pandas as pd
import anthropic
import time
from datetime import datetime
import math

# Claude API setup
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def get_enhanced_category_system():
    """Enhanced category system based on review analysis patterns"""
    return {
        # Core technical categories
        "App Crashes": "App crashes, freezing, force close, app stops working",
        "Technical Issues": "Bugs, glitches, sync issues, general app malfunctions", 
        "Performance": "Slow loading, lag, responsiveness issues, app speed",
        "User Experience": "Navigation, design, interface usability, confusing layout",
        "Features": "Missing features, feature requests, functionality gaps",
        "Authentication": "Login issues, password problems, sign-in failures",
        
        # Financial categories  
        "Price Increases": "Rate increases, price hikes, cost complaints, billing changes",
        "Payment Issues": "Payment failures, card problems, payment method issues",
        "Billing": "General billing disputes, charges, account billing questions",
        
        # Service categories
        "Coverage Issues": "Signal problems, dead zones, poor reception, network coverage",
        "Roaming Issues": "International roaming, roaming charges, travel connectivity",
        "Network Issues": "Data connectivity, network outages, service interruptions", 
        "Service Issues": "General service quality, service disruptions, provider issues",
        
        # Support categories
        "Customer Support": "Support quality, response times, help issues, service representatives",
        "Account Management": "Profile management, settings, account access problems",
        
        # Security & Privacy
        "Security": "Privacy concerns, data security, account security issues",
        
        # Specialized
        "Data Usage": "Data tracking, usage monitoring, data plan issues",
        "Notifications": "Push notifications, alerts, messaging problems",
        
        # General
        "User Feedback": "General praise, satisfaction, vague complaints with no specific issue"
    }

def get_comprehensive_analysis_prompt():
    """Comprehensive prompt with enhanced categories"""
    categories = get_enhanced_category_system()
    
    category_list = ""
    for i, (category, description) in enumerate(categories.items(), 1):
        category_list += f"{i}. **{category}** - {description}\n"
    
    return f"""
You are an expert analyst categorizing telecom app reviews with enhanced precision.

ENHANCED CATEGORY SYSTEM:
{category_list}

CRITICAL RULES:
- Price complaints, rate increases = "Price Increases" (NOT billing)
- App crashes, force close = "App Crashes" (NOT technical issues)  
- Payment card failures = "Payment Issues" (NOT billing)
- Signal, reception problems = "Coverage Issues" (NOT network issues)
- International/travel issues = "Roaming Issues" (NOT network issues)
- Only use "User Feedback" for vague praise/complaints with no specific actionable issue

Review: "{{review_text}}"

Respond with ONLY the exact category name. No explanations.
"""

def get_sentiment_prompt():
    """Sentiment analysis prompt"""
    return """
Analyze sentiment. Respond with ONLY one word:
Positive - Satisfied, happy, praising
Negative - Dissatisfied, frustrated, complaining
Neutral - Factual, no clear emotion
Mixed - Both positive and negative elements

Review: "{review_text}"

Respond ONLY: Positive, Negative, Neutral, or Mixed
"""

def analyze_single_review(review_text, review_id, provider):
    """Analyze one review with rate limiting"""
    try:
        # Category analysis
        category_prompt = get_comprehensive_analysis_prompt().format(review_text=review_text)
        
        category_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=30,
            temperature=0.1,
            messages=[{"role": "user", "content": category_prompt}]
        )
        
        category = category_response.content[0].text.strip()
        
        # Sentiment analysis  
        sentiment_prompt = get_sentiment_prompt().format(review_text=review_text)
        
        sentiment_response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=15, 
            temperature=0.1,
            messages=[{"role": "user", "content": sentiment_prompt}]
        )
        
        sentiment = sentiment_response.content[0].text.strip()
        
        return category, sentiment, True
        
    except Exception as e:
        print(f"❌ Error analyzing {provider} {review_id[:8]}: {str(e)}")
        return "User Feedback", "Neutral", False

def calculate_batch_timing():
    """Calculate optimal batch timing for rate limits"""
    # Rate limits: 4,000 requests/minute, 400K tokens/minute
    # Each review = 2 requests (~1000 tokens total)
    # Safe limit: 1,800 reviews per minute (3,600 requests, ~360K tokens)
    
    reviews_per_minute = 1800
    reviews_per_batch = 100
    batches_per_minute = reviews_per_minute / reviews_per_batch
    seconds_between_batches = 60 / batches_per_minute
    
    return reviews_per_batch, seconds_between_batches

def main():
    """Comprehensive 10K review re-analysis"""
    
    print("🔄 Loading complete dataset...")
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    
    print(f"📊 Dataset Analysis:")
    print(f"   Total reviews: {len(df):,}")
    print(f"   Rogers: {len(df[df['app_name'] == 'Rogers']):,}")
    print(f"   Bell: {len(df[df['app_name'] == 'Bell']):,}")
    print(f"   iOS: {len(df[df['platform'] == 'iOS']):,}")
    print(f"   Android: {len(df[df['platform'] == 'Android']):,}")
    
    # Show enhanced category system
    categories = get_enhanced_category_system()
    print(f"\n📋 Enhanced Category System ({len(categories)} categories):")
    for category, description in categories.items():
        print(f"   • {category}: {description}")
    
    # Calculate timing for rate limits
    batch_size, batch_delay = calculate_batch_timing()
    total_batches = math.ceil(len(df) / batch_size)
    estimated_time = (total_batches * batch_delay) / 60  # minutes
    
    print(f"\n⏱️  Rate Limit Optimization:")
    print(f"   Batch size: {batch_size} reviews")
    print(f"   Batch delay: {batch_delay:.1f} seconds")
    print(f"   Total batches: {total_batches}")
    print(f"   Estimated time: {estimated_time:.1f} minutes")
    
    # Auto-proceed with analysis
    print(f"\n▶️  Starting re-analysis of {len(df):,} reviews with enhanced categories...")
    
    # Create backup
    backup_file = f'Data/full_dataset_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(backup_file, index=False)
    print(f"💾 Backup created: {backup_file}")
    
    # Prepare results storage
    new_categories = []
    new_sentiments = []
    success_count = 0
    error_count = 0
    
    print(f"\n🤖 Starting comprehensive re-analysis...")
    start_time = time.time()
    
    # Process in batches
    for batch_num in range(total_batches):
        batch_start = batch_num * batch_size
        batch_end = min((batch_num + 1) * batch_size, len(df))
        batch_df = df.iloc[batch_start:batch_end]
        
        print(f"\n📦 Batch {batch_num + 1}/{total_batches} ({batch_start+1}-{batch_end})")
        
        batch_categories = []
        batch_sentiments = []
        
        for idx, (_, review) in enumerate(batch_df.iterrows()):
            review_num = batch_start + idx + 1
            provider = review['app_name']
            
            # Analyze review
            category, sentiment, success = analyze_single_review(
                review['text'], 
                review['review_id'], 
                provider
            )
            
            batch_categories.append(category)
            batch_sentiments.append(sentiment)
            
            if success:
                success_count += 1
            else:
                error_count += 1
            
            # Progress indicator
            if review_num % 50 == 0:
                elapsed = time.time() - start_time
                rate = review_num / elapsed * 60  # reviews per minute
                print(f"   [{review_num:,}/{len(df):,}] {provider} {review['review_id'][:8]} → {category} | {sentiment} ({rate:.0f}/min)")
            
            # Mini delay between requests
            time.sleep(0.02)  # 20ms between requests
        
        # Add batch results
        new_categories.extend(batch_categories)
        new_sentiments.extend(batch_sentiments)
        
        # Batch delay for rate limiting
        if batch_num < total_batches - 1:  # Don't delay after last batch
            print(f"⏸️  Batch complete. Pausing {batch_delay:.1f}s for rate limiting...")
            time.sleep(batch_delay)
    
    # Update dataset
    print(f"\n🔄 Updating dataset with enhanced categories...")
    df['enhanced_category'] = new_categories
    df['enhanced_sentiment'] = new_sentiments
    
    # Analysis results
    print(f"\n📈 Re-analysis Results:")
    print(f"   Successful: {success_count:,}")
    print(f"   Errors: {error_count:,}")
    print(f"   Total time: {(time.time() - start_time)/60:.1f} minutes")
    
    # Category distribution
    category_counts = pd.Series(new_categories).value_counts()
    print(f"\nEnhanced category distribution:")
    for category, count in category_counts.head(15).items():
        print(f"   {category}: {count:,}")
    
    # Sentiment distribution
    sentiment_counts = pd.Series(new_sentiments).value_counts()
    print(f"\nSentiment distribution:")
    for sentiment, count in sentiment_counts.items():
        print(f"   {sentiment}: {count:,}")
    
    # Save enhanced dataset
    output_file = f'Data/enhanced_analysis_complete_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Enhanced dataset saved: {output_file}")
    
    # Save summary report
    summary_file = f'enhanced_analysis_summary_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
    with open(summary_file, 'w') as f:
        f.write(f"Enhanced 10K Review Analysis Summary\n")
        f.write(f"Generated: {datetime.now()}\n\n")
        f.write(f"Dataset: {len(df):,} reviews\n")
        f.write(f"Success rate: {success_count/len(df)*100:.1f}%\n\n")
        f.write("Enhanced Categories:\n")
        for category, count in category_counts.items():
            f.write(f"  {category}: {count:,}\n")
        f.write(f"\nSentiment:\n")
        for sentiment, count in sentiment_counts.items():
            f.write(f"  {sentiment}: {count:,}\n")
    
    print(f"""
🎯 Comprehensive Re-analysis Complete!

📊 Enhanced Insights:
   • {len(categories)} specialized categories
   • Price Increases: {category_counts.get('Price Increases', 0):,} reviews
   • App Crashes: {category_counts.get('App Crashes', 0):,} reviews  
   • Coverage Issues: {category_counts.get('Coverage Issues', 0):,} reviews
   • Payment Issues: {category_counts.get('Payment Issues', 0):,} reviews
   
🔄 Next Steps:
   1. Review: {summary_file}
   2. Update dataset: cp {output_file} Data/analyzed_reviews_filtered_clean.csv
   3. Regenerate dashboard with enhanced categories
   4. Analyze new insights for strategic recommendations
""")

if __name__ == "__main__":
    main()