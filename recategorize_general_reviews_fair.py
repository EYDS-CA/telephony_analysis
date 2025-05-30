#!/usr/bin/env python3
"""
Fair General Category Re-categorization Script
Analyzes both Rogers and Bell "General" reviews using consistent categorization standards
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

def analyze_existing_categories(df):
    """Analyze how Rogers reviews are currently categorized to ensure fairness"""
    
    rogers_reviews = df[df['app_name'] == 'Rogers']
    bell_reviews = df[df['app_name'] == 'Bell']
    
    print("📊 Current categorization analysis:")
    print(f"\nRogers category distribution:")
    rogers_cats = rogers_reviews['primary_category'].value_counts()
    for cat, count in rogers_cats.head(10).items():
        print(f"   {cat}: {count}")
    
    print(f"\nBell category distribution:")
    bell_cats = bell_reviews['primary_category'].value_counts()
    for cat, count in bell_cats.head(10).items():
        print(f"   {cat}: {count}")
    
    return rogers_cats, bell_cats

def get_enhanced_category_prompt():
    """Enhanced categorization prompt based on existing Rogers categorizations"""
    return """
You are an expert analyst categorizing customer reviews for telecom mobile apps. You must maintain CONSISTENT categorization standards across providers.

IMPORTANT: Use these EXACT category names and criteria based on existing successful categorizations:

1. **Technical Issues** - App crashes, bugs, loading problems, sync issues, app functionality problems
2. **User Experience** - Navigation, design, interface complaints, usability, app layout issues  
3. **Features** - Missing features, feature requests, functionality issues, app capabilities
4. **Billing** - Payment problems, billing disputes, account charges, PRICE INCREASES, billing questions, payment methods
5. **Performance** - App speed, responsiveness, lag issues, slow loading
6. **Customer Support** - Support quality, response times, helpfulness, service issues
7. **Account Management** - Login issues, profile management, settings, account access
8. **Network Issues** - Connectivity, signal, data problems, service outages
9. **Authentication** - Login, password, security access issues
10. **Security** - Privacy concerns, data security issues
11. **Data Usage** - Data tracking, usage monitoring issues, data plans
12. **Notifications** - Push notifications, alerts, messaging issues
13. **Roaming** - International usage, roaming charges
14. **User Feedback** - ONLY for general praise/complaints with no specific issue mentioned

CRITICAL RULES:
- Price complaints, rate increases, billing changes = "Billing" (NOT General)
- Any specific functionality issue = appropriate technical category (NOT General) 
- Only use "User Feedback" for vague praise/complaints with no actionable issue
- Be consistent: similar complaints should get same category regardless of provider

Review to categorize: "{review_text}"

Provider: {provider} (for context only - categorize consistently)

Respond with ONLY the category name (e.g., "Billing" or "Technical Issues").
No explanations or additional text.
"""

def categorize_review(review_text, provider, review_id):
    """Send review to Claude for categorization with enhanced prompt"""
    try:
        prompt = get_enhanced_category_prompt().format(
            review_text=review_text, 
            provider=provider
        )
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        category = message.content[0].text.strip()
        print(f"✅ {provider} {review_id[:8]}: '{category}'")
        return category
        
    except Exception as e:
        print(f"❌ Error categorizing {provider} review {review_id[:8]}: {str(e)}")
        return "General"  # Keep as General if API fails

def main():
    """Main fair categorization process"""
    
    print("🔄 Loading filtered dataset...")
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    
    # Analyze current categorizations for fairness baseline
    rogers_cats, bell_cats = analyze_existing_categories(df)
    
    # Find all "General" reviews from both providers
    general_reviews = df[df['primary_category'] == 'General'].copy()
    
    rogers_general = general_reviews[general_reviews['app_name'] == 'Rogers']
    bell_general = general_reviews[general_reviews['app_name'] == 'Bell']
    
    print(f"\n📊 General reviews to recategorize:")
    print(f"   Rogers: {len(rogers_general)}")
    print(f"   Bell: {len(bell_general)}")
    print(f"   Total: {len(general_reviews)}")
    
    if len(general_reviews) == 0:
        print("✅ No 'General' reviews to recategorize!")
        return
    
    # Create backup
    backup_file = f'Data/general_reviews_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    general_reviews.to_csv(backup_file, index=False)
    print(f"💾 Backup created: {backup_file}")
    
    # Process each review with fair categorization
    print(f"\n🤖 Starting fair categorization with enhanced prompt...")
    updated_categories = []
    
    for idx, (_, review) in enumerate(general_reviews.iterrows(), 1):
        provider = review['app_name']
        print(f"\n[{idx}/{len(general_reviews)}] Processing {provider} review {review['review_id'][:8]}...")
        
        # Get new category from Claude
        new_category = categorize_review(
            review['text'], 
            provider, 
            review['review_id']
        )
        updated_categories.append(new_category)
        
        # Rate limiting
        if idx % 10 == 0:
            print(f"⏸️  Processed {idx} reviews, pausing 2 seconds...")
            time.sleep(2)
        else:
            time.sleep(0.5)
    
    # Add new categories to dataframe
    general_reviews['new_category'] = updated_categories
    
    # Analyze results by provider
    print(f"\n📈 Fair Recategorization Results:")
    
    rogers_results = general_reviews[general_reviews['app_name'] == 'Rogers']['new_category'].value_counts()
    bell_results = general_reviews[general_reviews['app_name'] == 'Bell']['new_category'].value_counts()
    
    print(f"\nRogers recategorization:")
    for category, count in rogers_results.items():
        print(f"   {category}: {count}")
    
    print(f"\nBell recategorization:")
    for category, count in bell_results.items():
        print(f"   {category}: {count}")
    
    # Update main dataset
    print(f"\n🔄 Updating main dataset...")
    for idx, (orig_idx, row) in enumerate(general_reviews.iterrows()):
        df.loc[orig_idx, 'primary_category'] = updated_categories[idx]
    
    # Save updated dataset
    output_file = 'Data/analyzed_reviews_filtered_clean_fair_updated.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Fair updated dataset saved: {output_file}")
    
    # Save detailed results
    results_file = f'fair_general_recategorization_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    general_reviews[['review_id', 'app_name', 'text', 'primary_category', 'new_category']].to_csv(results_file, index=False)
    print(f"📋 Detailed results saved: {results_file}")
    
    # Show fairness analysis
    print(f"\n⚖️  Fairness Analysis:")
    print(f"   Processed {len(rogers_general)} Rogers + {len(bell_general)} Bell reviews")
    print(f"   Used consistent categorization standards")
    print(f"   Enhanced prompt focuses on specific issues vs general feedback")
    
    print(f"""
🎯 Fair Recategorization Complete!

📊 Summary:
   • Rogers General → Specific: {len(rogers_general)} reviews
   • Bell General → Specific: {len(bell_general)} reviews  
   • Total processed: {len(general_reviews)} reviews
   • Backup: {backup_file}
   • Results: {results_file}
   
🔄 Next Steps:
   1. Review results for fairness and accuracy
   2. Replace dataset: cp {output_file} Data/analyzed_reviews_filtered_clean.csv
   3. Regenerate dashboard JS files
""")

if __name__ == "__main__":
    main()