#!/usr/bin/env python3
"""
Progress Checker - Monitor ongoing enhanced analysis
"""

import json
import os
from datetime import datetime

def check_progress():
    """Check current analysis progress"""
    
    if not os.path.exists('analysis_progress.json'):
        print("❌ No analysis in progress")
        return
    
    try:
        with open('analysis_progress.json', 'r') as f:
            progress = json.load(f)
        
        with open('analysis_results.json', 'r') as f:
            results = json.load(f)
        
        # Progress stats
        current = progress['current_index']
        total = progress['total_reviews']
        completed = progress['completed_count']
        
        print(f"📊 Enhanced Analysis Progress")
        print(f"   Current position: {current:,} / {total:,} reviews")
        print(f"   Completed: {completed:,} reviews ({completed/total*100:.1f}%)")
        print(f"   Remaining: {total - current:,} reviews")
        print(f"   Last update: {progress['timestamp']}")
        
        # Success rate
        success_count = sum(1 for r in results.values() if r['success'])
        error_count = len(results) - success_count
        
        print(f"\n✅ Quality Stats:")
        print(f"   Successful: {success_count:,}")
        print(f"   Errors: {error_count:,}")
        print(f"   Success rate: {success_count/len(results)*100:.1f}%")
        
        # Category distribution
        categories = {}
        providers = {'Rogers': 0, 'Bell': 0}
        
        for result in results.values():
            if result['success']:
                cat = result['category']
                categories[cat] = categories.get(cat, 0) + 1
                providers[result['provider']] += 1
        
        print(f"\n📈 Enhanced Categories (Top 10):")
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        for cat, count in sorted_cats[:10]:
            print(f"   {cat}: {count:,}")
        
        print(f"\n🏢 By Provider:")
        for provider, count in providers.items():
            print(f"   {provider}: {count:,}")
        
        # Time estimate
        if current > 0:
            timestamp = datetime.fromisoformat(progress['timestamp'])
            # Rough estimate based on current progress
            print(f"\n⏱️  Estimated completion: Analysis continues in background")
            print(f"   Rate: ~40-50 reviews per minute")
            remaining_time = (total - current) / 45  # minutes
            print(f"   ETA: ~{remaining_time:.0f} minutes remaining")
        
    except Exception as e:
        print(f"❌ Error reading progress: {e}")

if __name__ == "__main__":
    check_progress()