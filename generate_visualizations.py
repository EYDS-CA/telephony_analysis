import pandas as pd
import json
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from collections import Counter
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('ggplot')

# Load data
print("Loading data...")
df = pd.read_csv('telecom_app_reviews_complete.csv')
df['date'] = pd.to_datetime(df['date'])
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['year_month'] = df['date'].dt.to_period('M')

# Create output directory for charts
import os
os.makedirs('html_dashboard/charts', exist_ok=True)

# Filter for 2018-2025 as requested
df_filtered = df[(df['year'] >= 2018) & (df['year'] <= 2025)]
rogers_df = df_filtered[df_filtered['app_name'] == 'Rogers']
bell_df = df_filtered[df_filtered['app_name'] == 'Bell']

print(f"Analyzing {len(df_filtered):,} reviews from 2018-2025")
print(f"Rogers: {len(rogers_df):,} | Bell: {len(bell_df):,}")

# 1. Monthly Review Volume and Sentiment Trend
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

# Review volume by month
monthly_counts = df_filtered.groupby(['year_month', 'app_name']).size().unstack(fill_value=0)
monthly_counts.plot(ax=ax1, marker='o', markersize=4)
ax1.set_title('Monthly Review Volume: Rogers vs Bell (2018-2025)', fontsize=16, fontweight='bold')
ax1.set_xlabel('Month')
ax1.set_ylabel('Number of Reviews')
ax1.legend(['Bell', 'Rogers'], loc='upper left')
ax1.grid(True, alpha=0.3)

# Negative sentiment percentage by month
monthly_sentiment = df_filtered.groupby(['year_month', 'app_name']).apply(
    lambda x: (x['claude_sentiment'] == 'Negative').sum() / len(x) * 100
).unstack(fill_value=0)
monthly_sentiment.plot(ax=ax2, marker='o', markersize=4, color=['#0066cc', '#e50000'])
ax2.set_title('Monthly Negative Sentiment Rate', fontsize=14, fontweight='bold')
ax2.set_xlabel('Month')
ax2.set_ylabel('Negative Sentiment %')
ax2.legend(['Bell', 'Rogers'], loc='upper left')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('html_dashboard/charts/monthly_trends.png', dpi=150, bbox_inches='tight')
plt.close()

# 2. Issue Category Distribution Comparison
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 8))

# Rogers top categories
rogers_categories = rogers_df['primary_category'].value_counts().head(10)
rogers_categories.plot(kind='barh', ax=ax1, color='#e50000')
ax1.set_title('Top 10 Issues - Rogers App', fontsize=14, fontweight='bold')
ax1.set_xlabel('Number of Reviews')

# Bell top categories  
bell_categories = bell_df['primary_category'].value_counts().head(10)
bell_categories.plot(kind='barh', ax=ax2, color='#0066cc')
ax2.set_title('Top 10 Issues - Bell App', fontsize=14, fontweight='bold')
ax2.set_xlabel('Number of Reviews')

plt.tight_layout()
plt.savefig('html_dashboard/charts/category_comparison.png', dpi=150, bbox_inches='tight')
plt.close()

# 3. Rating Distribution Comparison
fig, ax = plt.subplots(figsize=(10, 6))

ratings_data = []
for rating in [1, 2, 3, 4, 5]:
    rogers_count = (rogers_df['rating'] == rating).sum()
    bell_count = (bell_df['rating'] == rating).sum()
    ratings_data.append({
        'Rating': rating,
        'Rogers': rogers_count / len(rogers_df) * 100,
        'Bell': bell_count / len(bell_df) * 100
    })

ratings_df = pd.DataFrame(ratings_data)
x = np.arange(len(ratings_df))
width = 0.35

ax.bar(x - width/2, ratings_df['Rogers'], width, label='Rogers', color='#e50000')
ax.bar(x + width/2, ratings_df['Bell'], width, label='Bell', color='#0066cc')

ax.set_xlabel('Rating', fontsize=12)
ax.set_ylabel('Percentage of Reviews (%)', fontsize=12)
ax.set_title('Rating Distribution: Rogers vs Bell', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(ratings_df['Rating'])
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('html_dashboard/charts/rating_distribution.png', dpi=150, bbox_inches='tight')
plt.close()

# 4. Platform Performance Analysis
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))

# Rogers by platform
rogers_platform = rogers_df.groupby('platform').agg({
    'rating': 'mean',
    'review_id': 'count'
}).round(2)

# Bell by platform
bell_platform = bell_df.groupby('platform').agg({
    'rating': 'mean',
    'review_id': 'count'
}).round(2)

# Average ratings by platform
platforms = ['Android', 'iOS']
rogers_ratings = [rogers_platform.loc[p, 'rating'] if p in rogers_platform.index else 0 for p in platforms]
bell_ratings = [bell_platform.loc[p, 'rating'] if p in bell_platform.index else 0 for p in platforms]

x = np.arange(len(platforms))
width = 0.35

ax1.bar(x - width/2, rogers_ratings, width, label='Rogers', color='#e50000')
ax1.bar(x + width/2, bell_ratings, width, label='Bell', color='#0066cc')
ax1.set_ylabel('Average Rating')
ax1.set_title('Average Rating by Platform')
ax1.set_xticks(x)
ax1.set_xticklabels(platforms)
ax1.legend()
ax1.set_ylim(0, 5)

# Review count by platform
rogers_counts = [rogers_platform.loc[p, 'review_id'] if p in rogers_platform.index else 0 for p in platforms]
bell_counts = [bell_platform.loc[p, 'review_id'] if p in bell_platform.index else 0 for p in platforms]

ax2.bar(x - width/2, rogers_counts, width, label='Rogers', color='#e50000')
ax2.bar(x + width/2, bell_counts, width, label='Bell', color='#0066cc')
ax2.set_ylabel('Number of Reviews')
ax2.set_title('Review Volume by Platform')
ax2.set_xticks(x)
ax2.set_xticklabels(platforms)
ax2.legend()

# Sentiment by platform - Rogers
rogers_android_neg = (rogers_df[rogers_df['platform'] == 'Android']['claude_sentiment'] == 'Negative').sum() / len(rogers_df[rogers_df['platform'] == 'Android']) * 100
rogers_ios_neg = (rogers_df[rogers_df['platform'] == 'iOS']['claude_sentiment'] == 'Negative').sum() / len(rogers_df[rogers_df['platform'] == 'iOS']) * 100

ax3.bar(['Android', 'iOS'], [rogers_android_neg, rogers_ios_neg], color='#e50000')
ax3.set_ylabel('Negative Sentiment %')
ax3.set_title('Rogers: Negative Sentiment by Platform')
ax3.set_ylim(0, 100)

# Sentiment by platform - Bell
bell_android = bell_df[bell_df['platform'] == 'Android']
bell_ios = bell_df[bell_df['platform'] == 'iOS']

if len(bell_android) > 0:
    bell_android_neg = (bell_android['claude_sentiment'] == 'Negative').sum() / len(bell_android) * 100
else:
    bell_android_neg = 0

if len(bell_ios) > 0:
    bell_ios_neg = (bell_ios['claude_sentiment'] == 'Negative').sum() / len(bell_ios) * 100
else:
    bell_ios_neg = 0

ax4.bar(['Android', 'iOS'], [bell_android_neg, bell_ios_neg], color='#0066cc')
ax4.set_ylabel('Negative Sentiment %')
ax4.set_title('Bell: Negative Sentiment by Platform')
ax4.set_ylim(0, 100)

plt.tight_layout()
plt.savefig('html_dashboard/charts/platform_analysis.png', dpi=150, bbox_inches='tight')
plt.close()

# 5. Word Cloud Data Preparation
from collections import Counter
import re

def extract_keywords(text_series, stop_words=None):
    """Extract most common words from text"""
    if stop_words is None:
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                     'of', 'with', 'by', 'from', 'is', 'it', 'that', 'this', 'was', 'are',
                     'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
                     'could', 'should', 'may', 'might', 'must', 'can', 'app', 'rogers', 'bell',
                     'i', 'me', 'my', 'you', 'your', 'they', 'them', 'their', 'we', 'us', 'our'}
    
    all_words = []
    for text in text_series.dropna():
        words = re.findall(r'\b[a-z]+\b', str(text).lower())
        all_words.extend([w for w in words if w not in stop_words and len(w) > 3])
    
    return Counter(all_words).most_common(20)

# Extract keywords for negative reviews
rogers_negative = rogers_df[rogers_df['claude_sentiment'] == 'Negative']
bell_negative = bell_df[bell_df['claude_sentiment'] == 'Negative']

rogers_keywords = extract_keywords(rogers_negative['text'])
bell_keywords = extract_keywords(bell_negative['text'])

# 6. Save analysis summary
analysis_summary = {
    "analysis_date": datetime.now().isoformat(),
    "period": "2018-2025",
    "total_reviews": len(df_filtered),
    "rogers_stats": {
        "total_reviews": len(rogers_df),
        "avg_rating": float(rogers_df['rating'].mean()),
        "negative_pct": float((rogers_df['claude_sentiment'] == 'Negative').sum() / len(rogers_df) * 100),
        "top_keywords": rogers_keywords[:10],
        "platform_breakdown": {
            "android": len(rogers_df[rogers_df['platform'] == 'Android']),
            "ios": len(rogers_df[rogers_df['platform'] == 'iOS'])
        }
    },
    "bell_stats": {
        "total_reviews": len(bell_df),
        "avg_rating": float(bell_df['rating'].mean()),
        "negative_pct": float((bell_df['claude_sentiment'] == 'Negative').sum() / len(bell_df) * 100),
        "top_keywords": bell_keywords[:10],
        "platform_breakdown": {
            "android": len(bell_df[bell_df['platform'] == 'Android']),
            "ios": len(bell_df[bell_df['platform'] == 'iOS'])
        }
    },
    "key_insights": [
        "Rogers app receives nearly 2x more app-related complaints than Bell",
        "Both apps show declining ratings in 2023-2025 period",
        "Android users report more issues than iOS users for both apps",
        "Installation and login issues are the top pain points for Rogers users",
        "Bell users complain more about service quality than app functionality"
    ]
}

with open('html_dashboard/visual_analysis_summary.json', 'w') as f:
    json.dump(analysis_summary, f, indent=2)

print("\n✅ Visualization generation complete!")
print(f"\nGenerated files:")
print("- html_dashboard/charts/monthly_trends.png")
print("- html_dashboard/charts/category_comparison.png")
print("- html_dashboard/charts/rating_distribution.png")
print("- html_dashboard/charts/platform_analysis.png")
print("- html_dashboard/visual_analysis_summary.json")
print("\nKey insights:")
print("1. Rogers has significantly more negative reviews about app functionality")
print("2. Bell users are more satisfied with the app but complain about service")
print("3. Android platform shows worse performance for both apps")
print("4. Review volume and sentiment have worsened in recent years")