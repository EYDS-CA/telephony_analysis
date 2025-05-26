#!/usr/bin/env python3
"""Test Bell analysis with 1000 reviews."""

import pandas as pd
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_with_correct_limits import *

async def test_bell():
    # Load unanalyzed reviews
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv')
    bell_df = df[df['app_name'] == 'Bell'].head(1000)
    
    print(f"Testing with {len(bell_df)} Bell reviews")
    
    reviews = bell_df.to_dict('records')
    batch_size = 500
    rate_limiter = OptimizedRateLimiter()
    all_results = []
    
    total_batches = (len(reviews) + batch_size - 1) // batch_size
    
    for i in range(0, len(reviews), batch_size):
        batch_num = (i // batch_size) + 1
        batch = reviews[i:i + batch_size]
        
        results = await process_batch_optimized(batch, batch_num, total_batches, rate_limiter)
        all_results.extend(results)
    
    # Save results
    result_df = pd.DataFrame(all_results)
    result_df.to_csv('bell_test_1000.csv', index=False)
    
    print(f"\nResults saved to bell_test_1000.csv")
    print(f"Success rate: {(result_df['analysis_status'] == 'success').mean()*100:.1f}%")
    
    if 'claude_sentiment' in result_df.columns:
        print("\nSentiment distribution:")
        print(result_df['claude_sentiment'].value_counts())

asyncio.run(test_bell())