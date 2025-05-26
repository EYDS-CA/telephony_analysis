#!/usr/bin/env python3
"""
Test Claude Haiku API connection with a small sample.
"""

import asyncio
import aiohttp
import json
import pandas as pd

# API Configuration
API_KEY = "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"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-3-haiku-20240307"

async def test_single_review():
    """Test API with a single review."""
    
    # Load one review for testing
    df = pd.read_csv('telecom_app_reviews_unanalyzed.csv', nrows=1)
    review = df.iloc[0]
    
    print("Testing with review:")
    print(f"App: {review['app_name']}")
    print(f"Rating: {review['rating']}")
    print(f"Text: {review['text'][:100]}...")
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY,
        "anthropic-version": "2023-06-01"
    }
    
    prompt = f"""Analyze this mobile app review and provide structured information.

Review:
App: {review['app_name']}
Platform: {review['platform']}
Rating: {review['rating']}/5
Text: {review['text'][:500]}

Provide a JSON response with:
1. "summary": Brief summary of the review
2. "sentiment": "Positive", "Negative", "Neutral", or "Mixed"
3. "primary_category": Main issue category

Return ONLY valid JSON."""
    
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 200,
        "temperature": 0.1
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            print("\nSending request to Claude API...")
            async with session.post(API_URL, headers=headers, json=payload) as response:
                print(f"Response status: {response.status}")
                
                if response.status == 200:
                    result = await response.json()
                    print("\nAPI Response:")
                    print(json.dumps(result, indent=2))
                    
                    # Extract the analysis
                    analysis_text = result['content'][0]['text']
                    analysis = json.loads(analysis_text)
                    
                    print("\nParsed Analysis:")
                    print(json.dumps(analysis, indent=2))
                    
                    print("\n✅ API connection successful!")
                    return True
                else:
                    error_text = await response.text()
                    print(f"\n❌ API Error: {error_text}")
                    return False
                    
        except Exception as e:
            print(f"\n❌ Exception: {str(e)}")
            return False

if __name__ == "__main__":
    success = asyncio.run(test_single_review())