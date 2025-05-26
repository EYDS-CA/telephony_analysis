#!/usr/bin/env python3
"""
Run full analysis of remaining reviews with progress tracking and error recovery.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analyze_remaining_reviews import *
import pandas as pd
import json
from datetime import datetime

async def run_full_analysis(start_from_batch=0):
    """Run full analysis with ability to resume from a specific batch."""
    
    print("=" * 60)
    print("FULL ANALYSIS OF REMAINING TELECOM APP REVIEWS")
    print("=" * 60)
    
    # Load unanalyzed reviews
    print("\nLoading unanalyzed reviews...")
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv')
    total_reviews = len(df)
    print(f"Total reviews to analyze: {total_reviews:,}")
    
    # Show distribution
    print("\nDistribution by app:")
    for app, count in df['app_name'].value_counts().items():
        print(f"  {app}: {count:,} ({count/total_reviews*100:.1f}%)")
    
    # Estimate time and cost
    batch_size = 500
    total_batches = (total_reviews + batch_size - 1) // batch_size
    
    # Haiku pricing: $0.25 per million input tokens, $1.25 per million output tokens
    # Estimate ~200 tokens input, ~100 tokens output per review
    estimated_input_tokens = total_reviews * 200
    estimated_output_tokens = total_reviews * 100
    estimated_cost = (estimated_input_tokens * 0.25 / 1_000_000) + (estimated_output_tokens * 1.25 / 1_000_000)
    
    print(f"\nAnalysis plan:")
    print(f"  Batch size: {batch_size}")
    print(f"  Total batches: {total_batches}")
    print(f"  Starting from batch: {start_from_batch + 1}")
    print(f"  Concurrent requests: {MAX_CONCURRENT_REQUESTS}")
    print(f"  Estimated cost: ${estimated_cost:.2f}")
    print(f"  Estimated time: {total_reviews / 7:.0f} seconds ({total_reviews / 7 / 60:.1f} minutes)")
    
    # Confirm before proceeding
    response = input("\nProceed with full analysis? (yes/no): ")
    if response.lower() != 'yes':
        print("Analysis cancelled.")
        return
    
    # Convert to list of dictionaries
    reviews = prepare_reviews(df)
    
    # Track progress
    all_results = []
    failed_reviews = []
    start_time = datetime.now()
    
    # Load previous checkpoint if resuming
    if start_from_batch > 0:
        checkpoint_file = f'analysis_checkpoint_{start_from_batch * 5}.csv'
        if os.path.exists(checkpoint_file):
            print(f"\nLoading checkpoint from {checkpoint_file}...")
            checkpoint_df = pd.read_csv(checkpoint_file)
            all_results = checkpoint_df.to_dict('records')
            print(f"Loaded {len(all_results)} previously analyzed reviews")
    
    # Process batches
    for i in range(start_from_batch * batch_size, len(reviews), batch_size):
        batch_num = (i // batch_size) + 1
        batch = reviews[i:i + batch_size]
        
        print(f"\n{'='*60}")
        print(f"BATCH {batch_num}/{total_batches}")
        print(f"{'='*60}")
        
        try:
            # Analyze batch
            results = await analyze_batch(batch, batch_num, total_batches)
            
            # Track successes and failures
            batch_successes = sum(1 for r in results if r.get('analysis_status') == 'success')
            batch_failures = len(results) - batch_successes
            
            all_results.extend(results)
            failed_reviews.extend([r for r in results if r.get('analysis_status') != 'success'])
            
            print(f"Batch {batch_num} complete: {batch_successes} success, {batch_failures} failed")
            
            # Save checkpoint every 5 batches
            if batch_num % 5 == 0:
                checkpoint_df = pd.DataFrame(all_results)
                checkpoint_file = f'analysis_checkpoint_{batch_num}.csv'
                checkpoint_df.to_csv(checkpoint_file, index=False)
                print(f"✓ Checkpoint saved: {checkpoint_file}")
                
                # Show progress
                elapsed = (datetime.now() - start_time).total_seconds()
                reviews_done = len(all_results)
                rate = reviews_done / elapsed if elapsed > 0 else 0
                eta = (total_reviews - reviews_done) / rate if rate > 0 else 0
                
                print(f"\nProgress: {reviews_done:,}/{total_reviews:,} ({reviews_done/total_reviews*100:.1f}%)")
                print(f"Rate: {rate:.1f} reviews/second")
                print(f"ETA: {eta/60:.1f} minutes")
                
        except Exception as e:
            print(f"\n❌ Error in batch {batch_num}: {str(e)}")
            print("Saving emergency checkpoint...")
            emergency_df = pd.DataFrame(all_results)
            emergency_df.to_csv(f'emergency_checkpoint_batch_{batch_num}.csv', index=False)
            raise
    
    # Save final results
    print("\n" + "="*60)
    print("SAVING FINAL RESULTS")
    print("="*60)
    
    final_df = pd.DataFrame(all_results)
    
    # Save newly analyzed reviews
    final_df.to_csv('telecom_app_reviews_newly_analyzed.csv', index=False)
    print("✓ Saved newly analyzed reviews")
    
    # Save failed reviews for retry
    if failed_reviews:
        failed_df = pd.DataFrame(failed_reviews)
        failed_df.to_csv('failed_reviews.csv', index=False)
        print(f"✓ Saved {len(failed_reviews)} failed reviews for retry")
    
    # Combine with existing analyzed reviews
    print("\nCombining with existing analyzed reviews...")
    existing_df = pd.read_csv('telecom_app_reviews_complete.csv')
    combined_df = pd.concat([existing_df, final_df], ignore_index=True)
    combined_df.to_csv('telecom_app_reviews_complete_updated.csv', index=False)
    print(f"✓ Combined dataset saved: {len(combined_df):,} total reviews")
    
    # Generate final report
    elapsed_total = (datetime.now() - start_time).total_seconds()
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)
    
    print(f"\nTime taken: {elapsed_total/60:.1f} minutes")
    print(f"Average rate: {len(all_results)/elapsed_total:.1f} reviews/second")
    
    print(f"\nTotal reviews analyzed: {len(final_df):,}")
    print(f"Successful analyses: {(final_df['analysis_status'] == 'success').sum():,}")
    print(f"Failed analyses: {(final_df['analysis_status'] != 'success').sum():,}")
    
    print("\nSentiment distribution:")
    if 'claude_sentiment' in final_df.columns:
        for sentiment, count in final_df['claude_sentiment'].value_counts().items():
            print(f"  {sentiment}: {count:,} ({count/len(final_df)*100:.1f}%)")
    
    print("\nTop categories:")
    if 'primary_category' in final_df.columns:
        for category, count in final_df['primary_category'].value_counts().head(10).items():
            print(f"  {category}: {count:,}")
    
    print("\nComplaint severity:")
    if 'complaint_severity' in final_df.columns:
        for severity, count in final_df['complaint_severity'].value_counts().items():
            print(f"  {severity}: {count:,}")
    
    # Estimate actual cost
    if 'usage' in locals():
        actual_input_tokens = sum(r.get('input_tokens', 0) for r in all_results)
        actual_output_tokens = sum(r.get('output_tokens', 0) for r in all_results)
        actual_cost = (actual_input_tokens * 0.25 / 1_000_000) + (actual_output_tokens * 1.25 / 1_000_000)
        print(f"\nActual API cost: ${actual_cost:.2f}")
    
    print("\n✅ Analysis complete! Check these files:")
    print("  - telecom_app_reviews_newly_analyzed.csv")
    print("  - telecom_app_reviews_complete_updated.csv")
    if failed_reviews:
        print("  - failed_reviews.csv (for retry)")

if __name__ == "__main__":
    # Check if resuming from a specific batch
    start_batch = 0
    if len(sys.argv) > 1:
        try:
            start_batch = int(sys.argv[1])
            print(f"Resuming from batch {start_batch}")
        except ValueError:
            print("Invalid batch number. Starting from beginning.")
    
    asyncio.run(run_full_analysis(start_batch))