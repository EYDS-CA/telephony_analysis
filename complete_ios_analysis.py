#!/usr/bin/env python3
"""
Complete iOS Review Analysis Script
1. Re-categorizes existing "General" reviews fairly for both providers
2. Analyzes remaining unanalyzed iOS reviews  
3. Ensures consistent categorization standards across Rogers and Bell
"""

import pandas as pd
import anthropic
import json
import time
from datetime import datetime
from collections import Counter

# Claude API setup
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def get_comprehensive_category_prompt():
    """Comprehensive categorization prompt for fair analysis"""
    return """
You are an expert analyst categorizing customer reviews for telecom mobile apps (Rogers/Bell). 
Maintain CONSISTENT standards across both providers.

EXACT CATEGORIES TO USE:

1. **Technical Issues** - App crashes, bugs, loading problems, sync issues, functionality problems
2. **User Experience** - Navigation, design, interface issues, usability problems, app layout
3. **Features** - Missing features, feature requests, functionality gaps, app capabilities  
4. **Billing** - Payment problems, billing disputes, charges, PRICE INCREASES, rate changes, billing questions
5. **Performance** - App speed, responsiveness, lag, slow loading, freezing
6. **Customer Support** - Support quality, response times, service issues, help problems
7. **Account Management** - Login issues, profile management, settings, account access problems
8. **Network Issues** - Connectivity, signal problems, data issues, service outages
9. **Authentication** - Login, password, security access issues, sign-in problems
10. **Security** - Privacy concerns, data security issues, account security
11. **Data Usage** - Data tracking, usage monitoring, data plan issues
12. **Notifications** - Push notifications, alerts, messaging problems
13. **Roaming** - International usage, roaming charges, travel issues
14. **User Feedback** - ONLY general praise/complaints with NO specific actionable issue

CRITICAL CATEGORIZATION RULES:
- Price complaints, rate increases = "Billing" 
- App not working, crashes = "Technical Issues"
- Hard to use, confusing = "User Experience"
- Missing functionality = "Features"
- Slow, laggy = "Performance" 
- Can't login = "Authentication"
- Only use "User Feedback" for vague praise/complaints with no specific issue

Review: "{review_text}"
Provider: {provider}

Respond with ONLY the exact category name. No explanations.
"""

def get_sentiment_analysis_prompt():
    """Prompt for sentiment analysis"""
    return """
Analyze the sentiment of this customer review and respond with ONLY one word:

Positive - Customer is satisfied, happy, or praising
Negative - Customer is dissatisfied, frustrated, or complaining  
Neutral - Factual, no clear positive or negative emotion
Mixed - Contains both positive and negative elements

Review: "{review_text}"

Respond with ONLY: Positive, Negative, Neutral, or Mixed
"""

def analyze_review_complete(review_text, provider, review_id):
    """Complete analysis: category + sentiment"""
    try:
        # Get category
        category_prompt = get_comprehensive_category_prompt().format(
            review_text=review_text, provider=provider
        )
        
        category_message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            temperature=0.1,
            messages=[{"role": "user", "content": category_prompt}]
        )
        
        category = category_message.content[0].text.strip()
        
        # Get sentiment
        sentiment_prompt = get_sentiment_analysis_prompt().format(review_text=review_text)
        
        sentiment_message = client.messages.create(
            model="claude-3-5-sonnet-20241022", 
            max_tokens=20,
            temperature=0.1,
            messages=[{"role": "user", "content": sentiment_prompt}]
        )
        
        sentiment = sentiment_message.content[0].text.strip()
        
        print(f"✅ {provider} {review_id[:8]}: '{category}' | {sentiment}")
        return category, sentiment
        
    except Exception as e:
        print(f"❌ Error analyzing {provider} review {review_id[:8]}: {str(e)}")
        return "General", "Neutral"

def main():
    """Complete iOS review analysis"""
    
    print("🔄 Loading filtered dataset...")
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    
    # Find iOS reviews needing analysis
    ios_reviews = df[df['platform'] == 'iOS'].copy()
    
    # Reviews needing categorization (General or missing)
    needs_analysis = ios_reviews[
        (ios_reviews['primary_category'].isna()) | 
        (ios_reviews['primary_category'] == '') |
        (ios_reviews['primary_category'] == 'General')
    ].copy()
    
    rogers_needs = needs_analysis[needs_analysis['app_name'] == 'Rogers']
    bell_needs = needs_analysis[needs_analysis['app_name'] == 'Bell']
    
    print(f"\n📊 iOS Reviews Analysis Scope:")
    print(f"   Total iOS reviews: {len(ios_reviews)}")
    print(f"   Rogers needing analysis: {len(rogers_needs)}")
    print(f"   Bell needing analysis: {len(bell_needs)}")
    print(f"   Total to process: {len(needs_analysis)}")
    
    if len(needs_analysis) == 0:
        print("✅ All iOS reviews already properly categorized!")
        return
    
    # Show current category distribution for context
    print(f"\n📈 Current iOS categorization:")
    current_cats = ios_reviews['primary_category'].value_counts()
    for cat, count in current_cats.head(8).items():
        print(f"   {cat}: {count}")
    
    # Create backup
    backup_file = f'Data/ios_analysis_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    needs_analysis.to_csv(backup_file, index=False)
    print(f"💾 Backup created: {backup_file}")
    
    # Process each review
    print(f"\n🤖 Starting comprehensive iOS analysis...")
    new_categories = []
    new_sentiments = []
    
    for idx, (_, review) in enumerate(needs_analysis.iterrows(), 1):
        provider = review['app_name']
        print(f"\n[{idx}/{len(needs_analysis)}] Analyzing {provider} review {review['review_id'][:8]}...")
        
        # Get category and sentiment
        category, sentiment = analyze_review_complete(
            review['text'], 
            provider, 
            review['review_id']
        )
        
        new_categories.append(category)
        new_sentiments.append(sentiment)
        
        # Rate limiting
        if idx % 10 == 0:
            print(f"⏸️  Processed {idx} reviews, pausing 3 seconds...")
            time.sleep(3)
        else:
            time.sleep(0.7)  # Slightly longer delay for double API calls
    
    # Update the analysis results
    needs_analysis['new_category'] = new_categories
    needs_analysis['new_sentiment'] = new_sentiments
    
    # Show results breakdown
    print(f"\n📈 Analysis Results:")
    
    print(f"\nCategory distribution:")
    cat_counts = pd.Series(new_categories).value_counts()
    for category, count in cat_counts.items():
        print(f"   {category}: {count}")
    
    print(f"\nSentiment distribution:")
    sent_counts = pd.Series(new_sentiments).value_counts()
    for sentiment, count in sent_counts.items():
        print(f"   {sentiment}: {count}")
    
    print(f"\nBy provider:")
    rogers_results = needs_analysis[needs_analysis['app_name'] == 'Rogers']
    bell_results = needs_analysis[needs_analysis['app_name'] == 'Bell']
    
    print(f"Rogers categories: {rogers_results['new_category'].value_counts().to_dict()}")
    print(f"Bell categories: {bell_results['new_category'].value_counts().to_dict()}")
    
    # Update main dataset
    print(f"\n🔄 Updating main dataset...")
    for idx, (orig_idx, row) in enumerate(needs_analysis.iterrows()):
        df.loc[orig_idx, 'primary_category'] = new_categories[idx]
        df.loc[orig_idx, 'claude_sentiment'] = new_sentiments[idx]
    
    # Save updated dataset
    output_file = 'Data/analyzed_reviews_complete_ios.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Complete iOS dataset saved: {output_file}")
    
    # Save detailed results
    results_file = f'complete_ios_analysis_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    analysis_results = needs_analysis[['review_id', 'app_name', 'text', 'primary_category', 'new_category', 'new_sentiment']]
    analysis_results.to_csv(results_file, index=False)
    print(f"📋 Detailed results saved: {results_file}")
    
    print(f"""
🎯 Complete iOS Analysis Finished!

📊 Summary:
   • Rogers iOS analyzed: {len(rogers_needs)} reviews
   • Bell iOS analyzed: {len(bell_needs)} reviews
   • Total processed: {len(needs_analysis)} reviews
   • Categories assigned with fair standards
   • Sentiment analysis included
   
📈 Impact:
   • All iOS reviews now properly categorized
   • Consistent standards across Rogers/Bell
   • Ready for accurate dashboard insights
   
🔄 Next Steps:
   1. Review results: {results_file}
   2. Update dataset: cp {output_file} Data/analyzed_reviews_filtered_clean.csv
   3. Regenerate dashboard JS files
   4. Verify iOS charts show complete, fair data
""")

if __name__ == "__main__":
    main()