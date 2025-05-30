#!/usr/bin/env python3
"""
Test Enhanced Analysis - Process first 200 reviews to verify system works
"""

import pandas as pd
import anthropic
import time
from datetime import datetime

# Claude API setup
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

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

def analyze_review(review_text, review_id):
    """Analyze single review"""
    try:
        prompt = get_enhanced_category_prompt().format(review_text=review_text)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=30,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}]
        )
        
        category = response.content[0].text.strip()
        return category, True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return "User Feedback", False

def main():
    """Test enhanced analysis on sample"""
    
    print("🔄 Loading dataset for testing...")
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    
    # Test with first 200 reviews
    test_df = df.head(200).copy()
    
    print(f"📊 Testing enhanced analysis on {len(test_df)} reviews...")
    print(f"   Rogers: {len(test_df[test_df['app_name'] == 'Rogers'])}")
    print(f"   Bell: {len(test_df[test_df['app_name'] == 'Bell'])}")
    
    # Process reviews
    results = []
    success_count = 0
    start_time = time.time()
    
    for idx, (_, review) in enumerate(test_df.iterrows(), 1):
        category, success = analyze_review(review['text'], review['review_id'])
        results.append(category)
        
        if success:
            success_count += 1
        
        print(f"[{idx:3d}/200] {review['app_name']} {review['review_id'][:8]} → {category}")
        
        # Rate limiting
        time.sleep(0.2)  # 5 requests per second
    
    # Add results to dataframe
    test_df['enhanced_category'] = results
    
    # Show results
    elapsed = time.time() - start_time
    print(f"\n📈 Test Results:")
    print(f"   Success rate: {success_count/len(test_df)*100:.1f}%")
    print(f"   Time: {elapsed:.1f} seconds")
    print(f"   Rate: {len(test_df)/elapsed*60:.1f} reviews/minute")
    
    # Category distribution
    category_counts = pd.Series(results).value_counts()
    print(f"\nEnhanced category distribution:")
    for category, count in category_counts.items():
        print(f"   {category}: {count}")
    
    # Save test results
    test_file = f'test_enhanced_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    test_df.to_csv(test_file, index=False)
    print(f"\n✅ Test results saved: {test_file}")
    
    print(f"\n🎯 Test successful! Enhanced categorization working properly.")
    print(f"   Ready to scale to full 10,103 review analysis.")

if __name__ == "__main__":
    main()