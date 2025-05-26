#!/usr/bin/env python3
"""
Analyze remaining reviews using Claude Haiku API with proper rate limiting.
Fixed for 80,000 output tokens per minute limit.
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

# Adjusted rate limits based on actual limits
MAX_CONCURRENT_REQUESTS = 5  # Much more conservative
OUTPUT_TOKENS_PER_MINUTE = 80000  # Your actual limit
MAX_OUTPUT_TOKENS_PER_REQUEST = 200  # Reduced from 500

# Calculate safe request rate
# 80,000 tokens/min ÷ 200 tokens/request = 400 requests/min max
# Use 300 to be safe
SAFE_REQUESTS_PER_MINUTE = 300

# Analysis prompt (shortened to reduce tokens)
ANALYSIS_PROMPT = """Analyze this app review. Return JSON only.

App: {app_name}
Rating: {rating}/5
Text: {review_text}

JSON format:
{{
  "summary": "Brief summary (max 50 words)",
  "sentiment": "Positive|Negative|Neutral|Mixed",
  "sentiment_score": -1.0 to 1.0,
  "primary_category": "App Crashes|Login Issues|Performance|User Experience|Features|Billing|Customer Support|Other",
  "complaint_severity": "Critical|Major|Minor|None",
  "is_app_related": true/false
}}"""

class TokenAwareRateLimiter:
    """Rate limiter that tracks both requests and tokens."""
    
    def __init__(self, requests_per_minute, tokens_per_minute):
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        self.request_times = []
        self.token_times = []
        self.token_counts = []
        
    async def wait_if_needed(self, estimated_tokens=200):
        """Wait if we're exceeding rate limits."""
        now = time.time()
        
        # Clean old data
        minute_ago = now - 60
        self.request_times = [t for t in self.request_times if t > minute_ago]
        self.token_times = [t for t in self.token_times if t > minute_ago]
        self.token_counts = [c for i, c in enumerate(self.token_counts) 
                           if i < len(self.token_times) and self.token_times[i] > minute_ago]
        
        # Check request rate
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (now - self.request_times[0]) + 0.1
            if wait_time > 0:
                print(f"Request rate limit reached, waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                now = time.time()
        
        # Check token rate
        current_tokens = sum(self.token_counts)
        if current_tokens + estimated_tokens > self.tokens_per_minute:
            wait_time = 60 - (now - self.token_times[0]) + 0.1
            if wait_time > 0:
                print(f"Token rate limit reached ({current_tokens} tokens used), waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
                # Recalculate after wait
                minute_ago = time.time() - 60
                self.token_times = [t for t in self.token_times if t > minute_ago]
                self.token_counts = [c for i, c in enumerate(self.token_counts) 
                                   if i < len(self.token_times) and self.token_times[i] > minute_ago]
        
        self.request_times.append(time.time())
        
    def record_tokens(self, token_count):
        """Record actual token usage."""
        self.token_times.append(time.time())
        self.token_counts.append(token_count)

async def analyze_review_with_retry(session: aiohttp.ClientSession, review: Dict[str, Any], 
                                  rate_limiter: TokenAwareRateLimiter, semaphore: asyncio.Semaphore,
                                  max_retries: int = 3) -> Dict[str, Any]:
    """Analyze a single review with retry logic for rate limits."""
    
    async with semaphore:
        for attempt in range(max_retries):
            await rate_limiter.wait_if_needed(MAX_OUTPUT_TOKENS_PER_REQUEST)
            
            headers = {
                "Content-Type": "application/json",
                "X-API-Key": API_KEY,
                "anthropic-version": "2023-06-01"
            }
            
            # Truncate text to reduce tokens
            review_text = str(review.get('text', ''))[:500]
            
            prompt = ANALYSIS_PROMPT.format(
                app_name=review['app_name'],
                rating=review['rating'],
                review_text=review_text
            )
            
            payload = {
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": MAX_OUTPUT_TOKENS_PER_REQUEST,
                "temperature": 0.1
            }
            
            try:
                async with session.post(API_URL, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        # Record actual token usage
                        output_tokens = result.get('usage', {}).get('output_tokens', MAX_OUTPUT_TOKENS_PER_REQUEST)
                        rate_limiter.record_tokens(output_tokens)
                        
                        # Parse response
                        try:
                            analysis = json.loads(result['content'][0]['text'])
                        except:
                            # If JSON parsing fails, use defaults
                            analysis = {
                                'summary': 'Failed to parse response',
                                'sentiment': 'Unknown',
                                'sentiment_score': 0,
                                'primary_category': 'Other',
                                'complaint_severity': 'None',
                                'is_app_related': True
                            }
                        
                        # Merge analysis with original review data
                        review['claude_summary'] = analysis.get('summary', '')
                        review['claude_sentiment'] = analysis.get('sentiment', 'Unknown')
                        review['sentiment_score'] = analysis.get('sentiment_score', 0)
                        review['primary_category'] = analysis.get('primary_category', 'Other')
                        review['complaint_severity'] = analysis.get('complaint_severity', 'None')
                        review['is_app_related'] = analysis.get('is_app_related', True)
                        review['analysis_status'] = 'success'
                        review['output_tokens'] = output_tokens
                        
                        return review
                        
                    elif response.status == 429:
                        # Rate limit hit - wait longer
                        wait_time = min(60 * (attempt + 1), 300)  # Max 5 minutes
                        print(f"Rate limit 429 on attempt {attempt + 1}, waiting {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                        
                    else:
                        error_text = await response.text()
                        print(f"API Error {response.status}: {error_text[:200]}")
                        review['analysis_status'] = f'error_{response.status}'
                        review['error_message'] = error_text[:200]
                        return review
                        
            except Exception as e:
                print(f"Error analyzing review: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(5 * (attempt + 1))
                    continue
                review['analysis_status'] = 'exception'
                review['error_message'] = str(e)[:200]
                return review
        
        # If all retries failed
        review['analysis_status'] = 'max_retries_exceeded'
        return review

async def analyze_batch_conservative(reviews: List[Dict[str, Any]], batch_num: int, 
                                   total_batches: int, rate_limiter: TokenAwareRateLimiter) -> List[Dict[str, Any]]:
    """Analyze a batch with conservative rate limiting."""
    
    print(f"\nProcessing batch {batch_num}/{total_batches} ({len(reviews)} reviews)")
    print(f"Using max {MAX_CONCURRENT_REQUESTS} concurrent requests")
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async with aiohttp.ClientSession() as session:
        tasks = [analyze_review_with_retry(session, review, rate_limiter, semaphore) 
                for review in reviews]
        
        results = []
        with tqdm(total=len(tasks), desc=f"Batch {batch_num}") as pbar:
            for task in asyncio.as_completed(tasks):
                result = await task
                results.append(result)
                pbar.update(1)
                
                # Show token usage periodically
                if len(results) % 10 == 0:
                    current_tokens = sum(rate_limiter.token_counts)
                    pbar.set_postfix({
                        'tokens/min': f"{current_tokens}/{OUTPUT_TOKENS_PER_MINUTE}",
                        'success': sum(1 for r in results if r.get('analysis_status') == 'success')
                    })
        
        return results

def prepare_reviews(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Convert dataframe to list of dictionaries for processing."""
    reviews = df.to_dict('records')
    for review in reviews:
        review['text'] = str(review.get('text', ''))
        review['app_name'] = str(review.get('app_name', ''))
        review['platform'] = str(review.get('platform', ''))
        review['rating'] = float(review.get('rating', 0))
    return reviews

async def main():
    """Main function with conservative rate limiting."""
    
    print("Loading unanalyzed reviews...")
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv')
    print(f"Loaded {len(df)} reviews to analyze")
    
    # Start with a small batch to test
    print("\nStarting with small test batch of 50 reviews...")
    test_df = df.head(50)
    test_reviews = prepare_reviews(test_df)
    
    # Create rate limiter
    rate_limiter = TokenAwareRateLimiter(SAFE_REQUESTS_PER_MINUTE, OUTPUT_TOKENS_PER_MINUTE)
    
    # Test batch
    test_results = await analyze_batch_conservative(test_reviews, 1, 1, rate_limiter)
    
    # Check results
    successes = sum(1 for r in test_results if r.get('analysis_status') == 'success')
    print(f"\nTest batch results: {successes}/{len(test_results)} successful")
    
    if successes < len(test_results) * 0.8:
        print("⚠️ High failure rate in test batch. Check your API limits.")
        print("Failed reviews:")
        for r in test_results:
            if r.get('analysis_status') != 'success':
                print(f"  - Status: {r.get('analysis_status')}, Error: {r.get('error_message', 'N/A')}")
    
    # Save test results
    test_df_results = pd.DataFrame(test_results)
    test_df_results.to_csv('test_batch_with_rate_limits.csv', index=False)
    print(f"\nTest results saved to test_batch_with_rate_limits.csv")
    
    # Ask to continue
    response = input("\nContinue with full analysis? (yes/no): ")
    if response.lower() != 'yes':
        return
    
    # Process remaining reviews
    remaining_reviews = prepare_reviews(df.iloc[50:])
    batch_size = 100  # Smaller batches for better control
    all_results = test_results.copy()
    
    for i in range(0, len(remaining_reviews), batch_size):
        batch_num = (i // batch_size) + 2
        total_batches = (len(df) + batch_size - 1) // batch_size
        batch = remaining_reviews[i:i + batch_size]
        
        results = await analyze_batch_conservative(batch, batch_num, total_batches, rate_limiter)
        all_results.extend(results)
        
        # Save checkpoint
        if batch_num % 10 == 0:
            checkpoint_df = pd.DataFrame(all_results)
            checkpoint_df.to_csv(f'checkpoint_batch_{batch_num}.csv', index=False)
            print(f"Checkpoint saved: checkpoint_batch_{batch_num}.csv")
    
    # Save final results
    print("\nSaving final results...")
    final_df = pd.DataFrame(all_results)
    final_df.to_csv('telecom_app_reviews_newly_analyzed_rate_limited.csv', index=False)
    
    print("\n=== Analysis Summary ===")
    print(f"Total analyzed: {len(final_df)}")
    print(f"Successful: {(final_df['analysis_status'] == 'success').sum()}")
    print(f"Failed: {(final_df['analysis_status'] != 'success').sum()}")
    
    if 'output_tokens' in final_df.columns:
        total_tokens = final_df['output_tokens'].sum()
        print(f"Total output tokens used: {total_tokens:,}")

if __name__ == "__main__":
    asyncio.run(main())