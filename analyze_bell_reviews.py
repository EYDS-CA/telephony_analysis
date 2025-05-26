#!/usr/bin/env python3
"""
Analyze all Bell reviews specifically to improve coverage.
"""

import pandas as pd
import asyncio
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from analyze_with_correct_limits import *

async def analyze_bell_reviews():
    """Focus on analyzing Bell reviews."""
    
    print("=" * 60)
    print("ANALYZING BELL REVIEWS FOR BETTER COVERAGE")
    print("=" * 60)
    
    # Load unanalyzed reviews
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv')
    
    # Filter for Bell only
    bell_df = df[df['app_name'] == 'Bell']
    
    print(f"Found {len(bell_df)} unanalyzed Bell reviews")
    print(f"This will improve Bell coverage from 25.1% to ~100%")
    
    # Convert to dict
    reviews = bell_df.to_dict('records')
    
    # Process in batches
    batch_size = 500
    rate_limiter = OptimizedRateLimiter()
    all_results = []
    
    total_batches = (len(reviews) + batch_size - 1) // batch_size
    start_time = time.time()
    
    print(f"\nProcessing in {total_batches} batches of {batch_size}")
    print(f"Estimated time: {len(reviews) / 30 / 60:.1f} minutes")
    
    for i in range(0, len(reviews), batch_size):
        batch_num = (i // batch_size) + 1
        batch = reviews[i:i + batch_size]
        
        try:
            results = await process_batch_optimized(batch, batch_num, total_batches, rate_limiter)
            all_results.extend(results)
            
            # Save checkpoint every 2000 reviews
            if len(all_results) % 2000 == 0 or batch_num == total_batches:
                checkpoint_df = pd.DataFrame(all_results)
                checkpoint_file = f'bell_checkpoint_{len(all_results)}.csv'
                checkpoint_df.to_csv(checkpoint_file, index=False)
                print(f"✓ Checkpoint: {checkpoint_file}")
                
                # Progress update
                elapsed = time.time() - start_time
                rate = len(all_results) / elapsed
                eta = (len(reviews) - len(all_results)) / rate if rate > 0 else 0
                
                print(f"Progress: {len(all_results)}/{len(reviews)} ({len(all_results)/len(reviews)*100:.1f}%)")
                print(f"ETA: {eta/60:.1f} minutes\n")
                
        except Exception as e:
            print(f"\nError in batch {batch_num}: {e}")
            # Save what we have
            if all_results:
                emergency_df = pd.DataFrame(all_results)
                emergency_df.to_csv(f'bell_emergency_{len(all_results)}.csv', index=False)
            raise
    
    # Save final results
    final_df = pd.DataFrame(all_results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'bell_analysis_complete_{timestamp}.csv'
    final_df.to_csv(output_file, index=False)
    
    # Summary
    elapsed_total = time.time() - start_time
    successes = (final_df['analysis_status'] == 'success').sum()
    
    print("\n" + "=" * 60)
    print("BELL ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"Total time: {elapsed_total/60:.1f} minutes")
    print(f"Reviews analyzed: {len(final_df)}")
    print(f"Successful: {successes} ({successes/len(final_df)*100:.1f}%)")
    print(f"Output file: {output_file}")
    
    # Combine with existing data
    print("\nCombining with existing analyzed data...")
    try:
        # Load most recent complete dataset
        existing = pd.read_csv('telecom_app_reviews_complete_with_new.csv')
        
        # Add new Bell reviews
        combined = pd.concat([existing, final_df[final_df['analysis_status'] == 'success']], 
                           ignore_index=True)
        
        # Save combined dataset
        combined_file = f'telecom_app_reviews_complete_final_{timestamp}.csv'
        combined.to_csv(combined_file, index=False)
        
        print(f"\nFinal combined dataset: {combined_file}")
        print(f"Total reviews: {len(combined)}")
        print(f"Rogers: {(combined['app_name'] == 'Rogers').sum()}")
        print(f"Bell: {(combined['app_name'] == 'Bell').sum()}")
        
        # Calculate new coverage
        rogers_total = 14506  # From cleaned data
        bell_total = 14936    # From cleaned data
        
        rogers_analyzed = (combined['app_name'] == 'Rogers').sum()
        bell_analyzed = (combined['app_name'] == 'Bell').sum()
        
        print(f"\nFinal Coverage:")
        print(f"Rogers: {rogers_analyzed}/{rogers_total} ({rogers_analyzed/rogers_total*100:.1f}%)")
        print(f"Bell: {bell_analyzed}/{bell_total} ({bell_analyzed/bell_total*100:.1f}%)")
        
    except Exception as e:
        print(f"\nCould not combine datasets: {e}")
        print("New Bell analyses saved separately")
    
    return final_df

if __name__ == "__main__":
    asyncio.run(analyze_bell_reviews())