#!/usr/bin/env python3
"""
Analyze a small batch of reviews to test the process before full run.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyze_remaining_reviews import *
import pandas as pd

async def analyze_small_batch():
    """Analyze just 100 reviews as a test."""
    
    print("Loading unanalyzed reviews...")
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv', nrows=100)
    print(f"Loaded {len(df)} reviews for test batch")
    
    # Show distribution
    print("\nTest batch distribution:")
    print(f"By app: {df['app_name'].value_counts().to_dict()}")
    print(f"By platform: {df['platform'].value_counts().to_dict()}")
    
    # Convert to list of dictionaries
    reviews = prepare_reviews(df)
    
    # Analyze batch
    print("\nAnalyzing test batch...")
    rate_limiter = RateLimiter(REQUESTS_PER_MINUTE)
    semaphore = asyncio.Semaphore(10)  # Use fewer concurrent requests for test
    
    async with aiohttp.ClientSession() as session:
        tasks = [analyze_review(session, review, rate_limiter, semaphore) for review in reviews]
        
        results = []
        for task in tqdm.as_completed(tasks, desc="Analyzing"):
            result = await task
            results.append(result)
    
    # Save results
    print("\nSaving test results...")
    results_df = pd.DataFrame(results)
    results_df.to_csv('test_batch_analyzed.csv', index=False)
    
    # Show summary
    print("\n=== Test Batch Summary ===")
    print(f"Total analyzed: {len(results_df)}")
    print(f"Successful: {(results_df['analysis_status'] == 'success').sum()}")
    print(f"Failed: {(results_df['analysis_status'] != 'success').sum()}")
    
    if 'claude_sentiment' in results_df.columns:
        print("\nSentiment distribution:")
        print(results_df['claude_sentiment'].value_counts())
    
    if 'primary_category' in results_df.columns:
        print("\nTop categories:")
        print(results_df['primary_category'].value_counts().head())
    
    print("\nTest batch saved to: test_batch_analyzed.csv")
    
    # Show a few examples
    print("\n=== Sample Results ===")
    for i, row in results_df.head(3).iterrows():
        print(f"\nReview {i+1}:")
        print(f"App: {row['app_name']}, Rating: {row['rating']}")
        print(f"Summary: {row.get('claude_summary', 'N/A')[:100]}...")
        print(f"Sentiment: {row.get('claude_sentiment', 'N/A')}")
        print(f"Category: {row.get('primary_category', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(analyze_small_batch())