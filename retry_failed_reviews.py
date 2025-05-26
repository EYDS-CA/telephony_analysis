#!/usr/bin/env python3
"""
Retry failed reviews from checkpoint with more conservative rate limiting.
"""

import pandas as pd
import asyncio
import time
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_remaining_reviews_fixed import *

# Even more conservative settings
MAX_CONCURRENT_REQUESTS = 2  # Only 2 at a time
DELAY_BETWEEN_REQUESTS = 0.5  # Wait 0.5s between requests

async def retry_failed_reviews(checkpoint_file):
    """Retry only the failed reviews from a checkpoint."""
    
    print(f"Loading checkpoint: {checkpoint_file}")
    df = pd.read_csv(checkpoint_file)
    
    # Filter for failed reviews
    failed_df = df[df['analysis_status'] != 'success'].copy()
    success_df = df[df['analysis_status'] == 'success'].copy()
    
    print(f"\nCheckpoint summary:")
    print(f"Total reviews: {len(df)}")
    print(f"Successful: {len(success_df)}")
    print(f"Failed: {len(failed_df)}")
    
    if len(failed_df) == 0:
        print("No failed reviews to retry!")
        return df
    
    print(f"\nRetrying {len(failed_df)} failed reviews...")
    
    # Convert to list of dicts
    failed_reviews = failed_df.to_dict('records')
    
    # Create more conservative rate limiter
    rate_limiter = TokenAwareRateLimiter(60, OUTPUT_TOKENS_PER_MINUTE)  # Only 60 requests/minute
    
    # Process in smaller batches
    batch_size = 20
    retry_results = []
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
        
        for i in range(0, len(failed_reviews), batch_size):
            batch = failed_reviews[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(failed_reviews) + batch_size - 1) // batch_size
            
            print(f"\nRetry batch {batch_num}/{total_batches}")
            
            # Add delay between batches
            if i > 0:
                print("Waiting 5 seconds between batches...")
                await asyncio.sleep(5)
            
            # Process batch with delays
            tasks = []
            for j, review in enumerate(batch):
                if j > 0:
                    await asyncio.sleep(DELAY_BETWEEN_REQUESTS)
                
                # Clear previous analysis results
                for key in ['claude_summary', 'claude_sentiment', 'sentiment_score', 
                           'primary_category', 'complaint_severity', 'is_app_related',
                           'analysis_status', 'error_message', 'output_tokens']:
                    review.pop(key, None)
                
                task = analyze_review_with_retry(session, review, rate_limiter, semaphore, max_retries=5)
                tasks.append(task)
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*tasks)
            retry_results.extend(batch_results)
            
            # Show progress
            successes = sum(1 for r in batch_results if r.get('analysis_status') == 'success')
            print(f"Batch {batch_num}: {successes}/{len(batch)} successful")
            
            # If we're getting too many failures, slow down more
            if successes < len(batch) * 0.5:
                print("High failure rate detected, increasing delays...")
                DELAY_BETWEEN_REQUESTS = 1.0
    
    # Combine results
    retry_df = pd.DataFrame(retry_results)
    
    # Merge with successful reviews
    combined_df = pd.concat([success_df, retry_df], ignore_index=True)
    
    # Save updated checkpoint
    output_file = f'retry_checkpoint_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n=== Retry Summary ===")
    print(f"Original failures: {len(failed_df)}")
    print(f"Retry successes: {(retry_df['analysis_status'] == 'success').sum()}")
    print(f"Still failed: {(retry_df['analysis_status'] != 'success').sum()}")
    print(f"\nTotal successful: {(combined_df['analysis_status'] == 'success').sum()}/{len(combined_df)}")
    print(f"Success rate: {(combined_df['analysis_status'] == 'success').mean()*100:.1f}%")
    print(f"\nSaved to: {output_file}")
    
    return combined_df

if __name__ == "__main__":
    checkpoint = 'analysis_checkpoint_10.csv'
    if len(sys.argv) > 1:
        checkpoint = sys.argv[1]
    
    asyncio.run(retry_failed_reviews(checkpoint))