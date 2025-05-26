#!/usr/bin/env python3
"""
Analyze reviews with correct Tier 4 rate limits.
Optimized for 80k output tokens/minute constraint.
"""

import pandas as pd
import asyncio
import aiohttp
import json
import time
from datetime import datetime
from typing import List, Dict, Any
import sys
import os

# API Configuration
API_KEY = "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"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-3-haiku-20240307"

# Tier 4 Rate Limits
REQUESTS_PER_MINUTE = 4000
INPUT_TOKENS_PER_MINUTE = 400000
OUTPUT_TOKENS_PER_MINUTE = 80000

# Strategy: With ~85 output tokens per review, we can do ~940 reviews/minute
# But let's be conservative and aim for 800 reviews/minute
MAX_CONCURRENT_REQUESTS = 50  # Can handle many concurrent requests
OUTPUT_TOKENS_PER_REQUEST = 100  # Keep responses short

# Even shorter prompt to minimize tokens
ANALYSIS_PROMPT = """Analyze this app review and return only a JSON object:
App: {app_name}, Rating: {rating}/5
Review: {review_text}

Required JSON fields:
- summary: brief summary (max 30 words)
- sentiment: one of "Positive", "Negative", "Neutral", "Mixed"  
- category: one of "App Crashes", "Login Issues", "Performance", "User Experience", "Features", "Billing", "Support", "Other"
- severity: one of "Critical", "Major", "Minor", "None"
"""

class OptimizedRateLimiter:
    """Rate limiter optimized for high throughput within token limits."""
    
    def __init__(self):
        self.request_times = []
        self.token_window = []
        self.token_counts = []
        self.lock = asyncio.Lock()
        
    async def acquire(self, estimated_tokens=85):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time.time()
            minute_ago = now - 60
            
            # Clean old data
            self.request_times = [t for t in self.request_times if t > minute_ago]
            valid_indices = [i for i, t in enumerate(self.token_window) if t > minute_ago]
            self.token_window = [self.token_window[i] for i in valid_indices]
            self.token_counts = [self.token_counts[i] for i in valid_indices]
            
            # Check request rate (4000/min)
            if len(self.request_times) >= REQUESTS_PER_MINUTE - 100:  # Leave some buffer
                wait_time = 60 - (now - self.request_times[0]) + 0.1
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    return await self.acquire(estimated_tokens)
            
            # Check token rate (80k output tokens/min)
            current_tokens = sum(self.token_counts)
            if current_tokens + estimated_tokens > OUTPUT_TOKENS_PER_MINUTE - 5000:  # Leave buffer
                wait_time = 60 - (now - self.token_window[0]) + 0.1
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                    return await self.acquire(estimated_tokens)
            
            # Record request
            self.request_times.append(now)
            return True
    
    async def record_tokens(self, tokens_used):
        """Record actual token usage."""
        async with self.lock:
            self.token_window.append(time.time())
            self.token_counts.append(tokens_used)

async def analyze_review_optimized(session: aiohttp.ClientSession, review: Dict[str, Any], 
                                 rate_limiter: OptimizedRateLimiter, semaphore: asyncio.Semaphore) -> Dict[str, Any]:
    """Analyze a single review with optimized settings."""
    
    async with semaphore:
        # Wait for rate limit clearance
        await rate_limiter.acquire()
        
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": API_KEY,
            "anthropic-version": "2023-06-01"
        }
        
        # Truncate text aggressively to save tokens
        review_text = str(review.get('text', ''))[:300]
        
        prompt = ANALYSIS_PROMPT.format(
            app_name=review['app_name'],
            rating=review['rating'],
            review_text=review_text
        )
        
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": OUTPUT_TOKENS_PER_REQUEST,
            "temperature": 0
        }
        
        try:
            async with session.post(API_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    
                    # Record token usage
                    output_tokens = result.get('usage', {}).get('output_tokens', 0)
                    await rate_limiter.record_tokens(output_tokens)
                    
                    # Parse response
                    try:
                        analysis = json.loads(result['content'][0]['text'])
                    except:
                        analysis = {}
                    
                    # Update review
                    review['claude_summary'] = analysis.get('summary', '')
                    review['claude_sentiment'] = analysis.get('sentiment', 'Unknown')
                    review['primary_category'] = analysis.get('category', 'Other')
                    review['complaint_severity'] = analysis.get('severity', 'None')
                    review['analysis_status'] = 'success'
                    review['output_tokens'] = output_tokens
                    
                elif response.status == 429:
                    # Rate limit - this shouldn't happen with our limiter
                    review['analysis_status'] = 'rate_limited'
                    await asyncio.sleep(5)
                else:
                    review['analysis_status'] = f'error_{response.status}'
                    
        except Exception as e:
            review['analysis_status'] = 'exception'
            review['error'] = str(e)[:100]
            
        return review

async def process_batch_optimized(reviews: List[Dict[str, Any]], batch_num: int, 
                                total_batches: int, rate_limiter: OptimizedRateLimiter):
    """Process a batch with optimized concurrency."""
    
    print(f"\nBatch {batch_num}/{total_batches} ({len(reviews)} reviews)")
    start_time = time.time()
    
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    
    async with aiohttp.ClientSession() as session:
        tasks = [analyze_review_optimized(session, review, rate_limiter, semaphore) 
                for review in reviews]
        
        # Process all tasks
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                reviews[i]['analysis_status'] = 'exception'
                reviews[i]['error'] = str(result)[:100]
                processed_results.append(reviews[i])
            else:
                processed_results.append(result)
        
        # Stats
        elapsed = time.time() - start_time
        successes = sum(1 for r in processed_results if r.get('analysis_status') == 'success')
        rate = len(reviews) / elapsed if elapsed > 0 else 0
        
        print(f"  Completed in {elapsed:.1f}s ({rate:.1f} reviews/sec)")
        print(f"  Success: {successes}/{len(reviews)} ({successes/len(reviews)*100:.1f}%)")
        
        return processed_results

async def analyze_remaining_optimized(limit=None):
    """Analyze remaining reviews with optimized settings."""
    
    print("=" * 60)
    print("OPTIMIZED ANALYSIS WITH CORRECT RATE LIMITS")
    print("=" * 60)
    print(f"Limits: {REQUESTS_PER_MINUTE} req/min, {OUTPUT_TOKENS_PER_MINUTE} output tokens/min")
    print(f"Concurrency: {MAX_CONCURRENT_REQUESTS}")
    
    # Load unanalyzed reviews
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv')
    
    if limit:
        df = df.head(limit)
    
    print(f"\nAnalyzing {len(df)} reviews")
    print(f"Distribution: Rogers {(df['app_name']=='Rogers').sum()}, Bell {(df['app_name']=='Bell').sum()}")
    
    # Focus on Bell reviews first since they're underrepresented
    bell_df = df[df['app_name'] == 'Bell']
    rogers_df = df[df['app_name'] == 'Rogers']
    
    print(f"\nPrioritizing {len(bell_df)} Bell reviews...")
    
    # Combine with Bell first
    df_ordered = pd.concat([bell_df, rogers_df], ignore_index=True)
    reviews = df_ordered.to_dict('records')
    
    # Process in larger batches since we can handle more concurrency
    batch_size = 500
    rate_limiter = OptimizedRateLimiter()
    all_results = []
    
    total_batches = (len(reviews) + batch_size - 1) // batch_size
    start_time = time.time()
    
    for i in range(0, len(reviews), batch_size):
        batch_num = (i // batch_size) + 1
        batch = reviews[i:i + batch_size]
        
        results = await process_batch_optimized(batch, batch_num, total_batches, rate_limiter)
        all_results.extend(results)
        
        # Checkpoint every 5000 reviews
        if len(all_results) % 5000 == 0:
            checkpoint_df = pd.DataFrame(all_results)
            checkpoint_df.to_csv(f'optimized_checkpoint_{len(all_results)}.csv', index=False)
            print(f"✓ Checkpoint saved at {len(all_results)} reviews")
    
    # Save final results
    final_df = pd.DataFrame(all_results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_df.to_csv(f'optimized_analysis_{timestamp}.csv', index=False)
    
    # Summary
    elapsed_total = time.time() - start_time
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Total time: {elapsed_total/60:.1f} minutes")
    print(f"Average rate: {len(all_results)/elapsed_total:.1f} reviews/second")
    print(f"\nResults:")
    print(f"  Total: {len(final_df)}")
    print(f"  Success: {(final_df['analysis_status'] == 'success').sum()}")
    print(f"  Failed: {(final_df['analysis_status'] != 'success').sum()}")
    
    # Bell vs Rogers breakdown
    bell_results = final_df[final_df['app_name'] == 'Bell']
    rogers_results = final_df[final_df['app_name'] == 'Rogers']
    
    print(f"\nBell: {len(bell_results)} ({(bell_results['analysis_status'] == 'success').sum()} successful)")
    print(f"Rogers: {len(rogers_results)} ({(rogers_results['analysis_status'] == 'success').sum()} successful)")
    
    return final_df

if __name__ == "__main__":
    limit = None
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    
    asyncio.run(analyze_remaining_optimized(limit))