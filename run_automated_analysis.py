#!/usr/bin/env python3
"""
Automated analysis of remaining reviews with rate limiting.
Runs without user interaction.
"""

import pandas as pd
import asyncio
import sys
import os
from datetime import datetime

# Import from the fixed script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_remaining_reviews_fixed import *

async def run_automated_analysis(max_reviews=None):
    """Run analysis automatically without user prompts."""
    
    start_time = datetime.now()
    
    print("=" * 60)
    print("AUTOMATED ANALYSIS OF REMAINING REVIEWS")
    print("=" * 60)
    print(f"Start time: {start_time}")
    print(f"Rate limits: {OUTPUT_TOKENS_PER_MINUTE} output tokens/minute")
    print(f"Concurrent requests: {MAX_CONCURRENT_REQUESTS}")
    
    # Load unanalyzed reviews
    print("\nLoading unanalyzed reviews...")
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv')
    
    if max_reviews:
        df = df.head(max_reviews)
        print(f"Limited to {max_reviews} reviews for this run")
    
    total_reviews = len(df)
    print(f"Total reviews to analyze: {total_reviews:,}")
    
    # Show distribution
    print("\nDistribution:")
    for app, count in df['app_name'].value_counts().items():
        print(f"  {app}: {count:,} ({count/total_reviews*100:.1f}%)")
    
    # Estimate time
    # With 5 concurrent requests and ~1 second per request, we get ~5 reviews/second
    # But with rate limiting, expect closer to 2-3 reviews/second
    estimated_time = total_reviews / 2.5
    print(f"\nEstimated time: {estimated_time/60:.1f} minutes")
    
    # Convert to list
    reviews = prepare_reviews(df)
    
    # Create rate limiter
    rate_limiter = TokenAwareRateLimiter(SAFE_REQUESTS_PER_MINUTE, OUTPUT_TOKENS_PER_MINUTE)
    
    # Process in batches
    batch_size = 100
    all_results = []
    failed_count = 0
    
    total_batches = (len(reviews) + batch_size - 1) // batch_size
    
    for i in range(0, len(reviews), batch_size):
        batch_num = (i // batch_size) + 1
        batch = reviews[i:i + batch_size]
        
        print(f"\n{'='*60}")
        print(f"BATCH {batch_num}/{total_batches}")
        print(f"{'='*60}")
        
        try:
            # Analyze batch
            results = await analyze_batch_conservative(batch, batch_num, total_batches, rate_limiter)
            
            # Count successes
            batch_successes = sum(1 for r in results if r.get('analysis_status') == 'success')
            batch_failures = len(results) - batch_successes
            failed_count += batch_failures
            
            all_results.extend(results)
            
            print(f"\nBatch {batch_num} complete: {batch_successes} success, {batch_failures} failed")
            
            # Save checkpoint every 10 batches
            if batch_num % 10 == 0 or batch_num == total_batches:
                checkpoint_df = pd.DataFrame(all_results)
                checkpoint_file = f'automated_checkpoint_batch_{batch_num}.csv'
                checkpoint_df.to_csv(checkpoint_file, index=False)
                print(f"✓ Checkpoint saved: {checkpoint_file}")
                
                # Show progress
                elapsed = (datetime.now() - start_time).total_seconds()
                reviews_done = len(all_results)
                rate = reviews_done / elapsed if elapsed > 0 else 0
                
                print(f"\nProgress: {reviews_done:,}/{total_reviews:,} ({reviews_done/total_reviews*100:.1f}%)")
                print(f"Success rate: {(reviews_done-failed_count)/reviews_done*100:.1f}%")
                print(f"Rate: {rate:.1f} reviews/second")
                
                if rate > 0:
                    eta = (total_reviews - reviews_done) / rate
                    print(f"ETA: {eta/60:.1f} minutes")
                
        except Exception as e:
            print(f"\n❌ Error in batch {batch_num}: {str(e)}")
            # Save emergency checkpoint
            if all_results:
                emergency_df = pd.DataFrame(all_results)
                emergency_df.to_csv(f'emergency_automated_batch_{batch_num}.csv', index=False)
                print(f"Emergency checkpoint saved")
            raise
    
    # Save final results
    print("\n" + "="*60)
    print("SAVING FINAL RESULTS")
    print("="*60)
    
    final_df = pd.DataFrame(all_results)
    
    # Save newly analyzed reviews
    output_file = f'automated_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    final_df.to_csv(output_file, index=False)
    print(f"✓ Results saved to: {output_file}")
    
    # Show summary
    end_time = datetime.now()
    total_time = (end_time - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    print(f"End time: {end_time}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average rate: {len(all_results)/total_time:.2f} reviews/second")
    
    print(f"\nResults:")
    print(f"  Total processed: {len(final_df):,}")
    print(f"  Successful: {(final_df['analysis_status'] == 'success').sum():,}")
    print(f"  Failed: {(final_df['analysis_status'] != 'success').sum():,}")
    
    if 'claude_sentiment' in final_df.columns:
        print("\nSentiment distribution:")
        for sentiment, count in final_df['claude_sentiment'].value_counts().items():
            print(f"  {sentiment}: {count:,} ({count/len(final_df)*100:.1f}%)")
    
    if 'primary_category' in final_df.columns:
        print("\nTop 5 categories:")
        for category, count in final_df['primary_category'].value_counts().head().items():
            print(f"  {category}: {count:,}")
    
    if 'output_tokens' in final_df.columns:
        total_tokens = final_df['output_tokens'].sum()
        avg_tokens = final_df['output_tokens'].mean()
        print(f"\nToken usage:")
        print(f"  Total: {total_tokens:,}")
        print(f"  Average per review: {avg_tokens:.1f}")
        print(f"  Estimated cost: ${total_tokens * 1.25 / 1_000_000:.2f}")
    
    return final_df

if __name__ == "__main__":
    # Check command line arguments
    max_reviews = None
    if len(sys.argv) > 1:
        try:
            max_reviews = int(sys.argv[1])
            print(f"Limiting analysis to {max_reviews} reviews")
        except ValueError:
            print("Usage: python run_automated_analysis.py [max_reviews]")
            sys.exit(1)
    
    # Run the analysis
    asyncio.run(run_automated_analysis(max_reviews))