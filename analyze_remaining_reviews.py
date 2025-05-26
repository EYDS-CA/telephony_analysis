#!/usr/bin/env python3
"""
Analyze remaining reviews using Claude Haiku API with concurrent processing.
"""

import pandas as pd
import asyncio
import aiohttp
import json
from datetime import datetime
import os
from typing import List, Dict, Any
import time
from tqdm.asyncio import tqdm

# API Configuration
API_KEY = "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"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-3-haiku-20240307"

# Tier 4 rate limits for Haiku
MAX_CONCURRENT_REQUESTS = 50  # Conservative for tier 4
REQUESTS_PER_MINUTE = 10000  # Tier 4 limit for Haiku
TOKENS_PER_MINUTE = 4000000  # Tier 4 limit for Haiku

# Analysis prompt
ANALYSIS_PROMPT = """Analyze this mobile app review and provide structured information.

Review:
App: {app_name}
Platform: {platform}
Rating: {rating}/5
Text: {review_text}

Provide a JSON response with:
1. "summary": Brief summary of the review (max 100 words)
2. "sentiment": "Positive", "Negative", "Neutral", or "Mixed"
3. "sentiment_score": Float between -1 (very negative) and 1 (very positive)
4. "primary_category": Main issue category from this list:
   - App Crashes
   - Login Issues
   - Performance
   - User Experience
   - Features
   - Billing
   - Customer Support
   - Installation Problems
   - Loading Problems
   - Account Management
   - Connectivity Issues
   - User Feedback
   - Other
5. "sub_category": More specific categorization
6. "technical_issues": List of specific technical problems mentioned
7. "complaint_severity": "Critical", "Major", "Minor", or "None"
8. "is_app_related": true/false (is this about the app or the service?)

Return ONLY valid JSON, no additional text."""

class RateLimiter:
    """Simple rate limiter for API requests."""
    
    def __init__(self, requests_per_minute):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
    
    async def wait_if_needed(self):
        """Wait if we're exceeding rate limit."""
        now = time.time()
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.requests_per_minute:
            # Wait until the oldest request is older than 1 minute
            wait_time = 60 - (now - self.request_times[0]) + 0.1
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.request_times.append(now)

async def analyze_review(session: aiohttp.ClientSession, review: Dict[str, Any], 
                        rate_limiter: RateLimiter, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """Analyze a single review using Claude Haiku."""
    
    async with semaphore:
        await rate_limiter.wait_if_needed()
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        prompt = ANALYSIS_PROMPT.format(
            app_name=review['app_name'],
            platform=review['platform'],
            rating=review['rating'],
            review_text=review.get('text', '')[:1000]  # Limit text length
        )
        
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        try:
            async with session.post(API_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    analysis = json.loads(result['content'][0]['text'])
                    
                    # Merge analysis with original review data
                    review['claude_summary'] = analysis.get('summary', '')
                    review['claude_sentiment'] = analysis.get('sentiment', 'Unknown')
                    review['sentiment_score'] = analysis.get('sentiment_score', 0)
                    review['primary_category'] = analysis.get('primary_category', 'Other')
                    review['sub_category'] = analysis.get('sub_category', '')
                    review['technical_issues'] = ', '.join(analysis.get('technical_issues', []))
                    review['complaint_severity'] = analysis.get('complaint_severity', 'None')
                    review['is_app_related'] = analysis.get('is_app_related', True)
                    review['analysis_status'] = 'success'
                    
                    return review
                else:
                    error_text = await response.text()
                    print(f"API Error {response.status}: {error_text}")
                    review['analysis_status'] = f'error_{response.status}'
                    return review
                    
        except Exception as e:
            print(f"Error analyzing review: {str(e)}")
            review['analysis_status'] = 'exception'
            return review

async def analyze_batch(reviews: List[Dict[str, Any]], batch_num: int, total_batches: int) -> List[Dict[str, Any]]:
    """Analyze a batch of reviews concurrently."""
    
    print(f"\nProcessing batch {batch_num}/{total_batches} ({len(reviews)} reviews)")
    
    rate_limiter = RateLimiter(REQUESTS_PER_MINUTE)
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async with aiohttp.ClientSession() as session:
        tasks = [analyze_review(session, review, rate_limiter, semaphore) for review in reviews]
        
        # Use tqdm for progress bar
        results = []
        for task in tqdm.as_completed(tasks, desc=f"Batch {batch_num}"):
            result = await task
            results.append(result)
        
        return results

def prepare_reviews(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert dataframe to list of dictionaries for processing."""
    reviews = df.to_dict('records')
    for review in reviews:
        # Ensure all required fields exist
        review['text'] = str(review.get('text', ''))
        review['app_name'] = str(review.get('app_name', ''))
        review['platform'] = str(review.get('platform', ''))
        review['rating'] = float(review.get('rating', 0))
    return reviews

async def main():
    """Main function to orchestrate the analysis."""
    
    print("Loading unanalyzed reviews...")
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv')
    print(f"Loaded {len(df)} reviews to analyze")
    
    # Convert to list of dictionaries
    reviews = prepare_reviews(df)
    
    # Process in batches to manage memory and allow checkpointing
    batch_size = 500
    all_results = []
    
    total_batches = (len(reviews) + batch_size - 1) // batch_size
    
    for i in range(0, len(reviews), batch_size):
        batch_num = (i // batch_size) + 1
        batch = reviews[i:i + batch_size]
        
        # Analyze batch
        results = await analyze_batch(batch, batch_num, total_batches)
        all_results.extend(results)
        
        # Save checkpoint every 5 batches
        if batch_num % 5 == 0:
            checkpoint_df = pd.DataFrame(all_results)
            checkpoint_df.to_csv(f'analysis_checkpoint_{batch_num}.csv', index=False)
            print(f"Checkpoint saved: analysis_checkpoint_{batch_num}.csv")
    
    # Save final results
    print("\nSaving final results...")
    final_df = pd.DataFrame(all_results)
    
    # Save newly analyzed reviews
    final_df.to_csv('telecom_app_reviews_newly_analyzed.csv', index=False)
    
    # Combine with existing analyzed reviews
    existing_df = pd.read_csv('telecom_app_reviews_complete.csv')
    combined_df = pd.concat([existing_df, final_df], ignore_index=True)
    combined_df.to_csv('telecom_app_reviews_complete_updated.csv', index=False)
    
    # Generate summary statistics
    print("\n=== Analysis Summary ===")
    print(f"Total reviews analyzed: {len(final_df)}")
    print(f"Successful analyses: {(final_df['analysis_status'] == 'success').sum()}")
    print(f"Failed analyses: {(final_df['analysis_status'] != 'success').sum()}")
    
    print("\nSentiment distribution:")
    print(final_df['claude_sentiment'].value_counts())
    
    print("\nTop categories:")
    print(final_df['primary_category'].value_counts().head(10))
    
    print("\nComplaint severity:")
    print(final_df['complaint_severity'].value_counts())
    
    print("\nFiles created:")
    print("- telecom_app_reviews_newly_analyzed.csv (new analyses only)")
    print("- telecom_app_reviews_complete_updated.csv (all reviews combined)")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())