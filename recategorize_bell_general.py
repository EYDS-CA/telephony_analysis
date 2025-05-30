#!/usr/bin/env python3
"""
Bell General Category Re-categorization Script
Uses Claude API to individually analyze and re-categorize Bell reviews currently marked as "General"
"""

import pandas as pd
import anthropic
import json
import time
from datetime import datetime
import os

# Claude API setup
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY', '')
client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

def get_category_prompt():
    """Define the categorization prompt for Claude"""
    return """
You are an expert analyst categorizing customer reviews for Bell's mobile app. 

Please analyze this review and categorize it into ONE of these primary categories:

1. **Technical Issues** - App crashes, bugs, loading problems, sync issues
2. **User Experience** - Navigation, design, interface complaints, usability
3. **Features** - Missing features, feature requests, functionality issues
4. **Billing** - Payment problems, billing disputes, account charges
5. **Performance** - App speed, responsiveness, lag issues
6. **Customer Support** - Support quality, response times, helpfulness
7. **Account Management** - Login issues, profile management, settings
8. **Network Issues** - Connectivity, signal, data problems
9. **Authentication** - Login, password, security access issues
10. **Security** - Privacy concerns, data security issues
11. **Data Usage** - Data tracking, usage monitoring issues
12. **Notifications** - Push notifications, alerts, messaging
13. **Roaming** - International usage, roaming charges
14. **User Feedback** - General praise, satisfaction, positive comments

Review to categorize: "{review_text}"

Respond with ONLY the category name (e.g., "Technical Issues" or "User Experience").
Do not include explanations or additional text.
"""

def categorize_review(review_text, review_id):
    """Send review to Claude for categorization"""
    try:
        prompt = get_category_prompt().format(review_text=review_text)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=50,
            temperature=0.1,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        category = message.content[0].text.strip()
        print(f"✅ Review {review_id[:8]}: '{category}'")
        return category
        
    except Exception as e:
        print(f"❌ Error categorizing review {review_id[:8]}: {str(e)}")
        return "General"  # Keep as General if API fails

def main():
    """Main categorization process"""
    
    print("🔄 Loading filtered dataset...")
    df = pd.read_csv('Data/analyzed_reviews_filtered_clean.csv')
    
    # Filter for Bell reviews with "General" category
    bell_general = df[
        (df['app_name'] == 'Bell') & 
        (df['primary_category'] == 'General')
    ].copy()
    
    print(f"📊 Found {len(bell_general)} Bell reviews categorized as 'General'")
    
    if len(bell_general) == 0:
        print("✅ No Bell 'General' reviews to recategorize!")
        return
    
    # Create backup of original data
    backup_file = f'Data/bell_general_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    bell_general.to_csv(backup_file, index=False)
    print(f"💾 Backup created: {backup_file}")
    
    # Process each review
    print(f"\n🤖 Starting Claude API categorization...")
    updated_categories = []
    
    for idx, (_, review) in enumerate(bell_general.iterrows(), 1):
        print(f"\n[{idx}/{len(bell_general)}] Processing review {review['review_id'][:8]}...")
        
        # Get new category from Claude
        new_category = categorize_review(review['text'], review['review_id'])
        updated_categories.append(new_category)
        
        # Rate limiting - be respectful to API
        if idx % 10 == 0:
            print(f"⏸️  Processed {idx} reviews, pausing 2 seconds...")
            time.sleep(2)
        else:
            time.sleep(0.5)  # Small delay between requests
    
    # Update the categories
    bell_general['new_category'] = updated_categories
    
    # Show categorization results
    print(f"\n📈 Recategorization Results:")
    category_counts = pd.Series(updated_categories).value_counts()
    for category, count in category_counts.items():
        print(f"   {category}: {count}")
    
    # Update the main dataset
    print(f"\n🔄 Updating main dataset...")
    for idx, (orig_idx, row) in enumerate(bell_general.iterrows()):
        df.loc[orig_idx, 'primary_category'] = updated_categories[idx]
    
    # Save updated dataset
    output_file = 'Data/analyzed_reviews_filtered_clean_updated.csv'
    df.to_csv(output_file, index=False)
    print(f"✅ Updated dataset saved: {output_file}")
    
    # Save detailed results
    results_file = f'bell_general_recategorization_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    bell_general[['review_id', 'text', 'primary_category', 'new_category']].to_csv(results_file, index=False)
    print(f"📋 Detailed results saved: {results_file}")
    
    print(f"""
🎯 Recategorization Complete!

📊 Summary:
   • Processed: {len(bell_general)} Bell 'General' reviews
   • Categories updated in main dataset
   • Backup created: {backup_file}
   • Results saved: {results_file}
   
🔄 Next Steps:
   1. Review the results in {results_file}
   2. If satisfied, regenerate dashboard JS files
   3. Replace original dataset with updated version
""")

if __name__ == "__main__":
    main()