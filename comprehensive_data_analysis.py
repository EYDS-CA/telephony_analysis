import pandas as pd
import numpy as np
from collections import Counter

def analyze_comprehensive_data():
    """Comprehensive analysis of CCTS and app review data"""
    
    print("COMPREHENSIVE TELECOM DATA ANALYSIS")
    print("=" * 60)
    
    # Load app review data
    app_df = pd.read_csv('/Users/amirshayegh/Developer/temp/review_analysis/Data/dashboard_current_data.csv')
    print(f"\nApp Reviews Analysis (N={len(app_df):,})")
    print("-" * 40)
    
    # App review category distribution
    app_categories = app_df['enhanced_category'].value_counts()
    print("Top App Review Categories:")
    for cat, count in app_categories.head(10).items():
        percentage = (count / len(app_df)) * 100
        print(f"  {cat}: {count:,} ({percentage:.1f}%)")
    
    # Provider breakdown
    provider_breakdown = app_df['app'].value_counts()
    print(f"\nProvider Distribution:")
    for provider, count in provider_breakdown.items():
        percentage = (count / len(app_df)) * 100
        print(f"  {provider}: {count:,} ({percentage:.1f}%)")
    
    # Platform breakdown
    platform_breakdown = app_df['platform'].value_counts()
    print(f"\nPlatform Distribution:")
    for platform, count in platform_breakdown.items():
        percentage = (count / len(app_df)) * 100
        print(f"  {platform}: {count:,} ({percentage:.1f}%)")
    
    # CCTS Analysis
    print(f"\n\nCCTS Regulatory Complaints Analysis (N=15,913)")
    print("-" * 40)
    
    # Read CCTS data properly
    ccts_df = pd.read_csv('/Users/amirshayegh/Developer/temp/review_analysis/Data/CCTS.csv', 
                         encoding='latin1', skiprows=6)
    
    # Primary categories
    primary_cats = ccts_df['Primary Category'].value_counts()
    print("CCTS Primary Categories:")
    for cat, count in primary_cats.items():
        percentage = (count / len(ccts_df)) * 100
        print(f"  {cat}: {count:,} ({percentage:.1f}%)")
    
    # Top issues
    top_issues = ccts_df['Issue'].value_counts()
    print(f"\nTop CCTS Issues:")
    for issue, count in top_issues.head(8).items():
        percentage = (count / len(ccts_df)) * 100
        print(f"  {issue}: {count:,} ({percentage:.1f}%)")
    
    # Provider analysis
    ccts_providers = ccts_df['Service Provider'].value_counts()
    print(f"\nCCTS Provider Distribution:")
    for provider, count in ccts_providers.head(8).items():
        percentage = (count / len(ccts_df)) * 100
        print(f"  {provider}: {count:,} ({percentage:.1f}%)")
    
    # Cross-analysis: Map categories
    print(f"\n\nCROSS-ANALYSIS: Regulatory vs App Feedback")
    print("-" * 50)
    
    # Hierarchy of Needs Analysis
    print(f"\nTelecom App Hierarchy of Needs Analysis:")
    print(f"Level 1 - Core Function Reliability:")
    
    # Core reliability issues from apps
    core_issues = ['App Crashes', 'Technical Issues', 'Performance', 'Authentication']
    core_total = sum(app_categories.get(cat, 0) for cat in core_issues)
    core_percentage = (core_total / len(app_df)) * 100
    print(f"  App Reviews: {core_total:,} issues ({core_percentage:.1f}%)")
    
    # Core reliability from CCTS
    service_delivery = ccts_df[ccts_df['Primary Category'] == 'Service Delivery']
    reliability_issues = ['Service not working', 'Service Not Working', 'Intermittent service', 
                         'Intermittent Service', 'Complete loss of service']
    reliability_total = sum(service_delivery['Secondary Category'].value_counts().get(issue, 0) 
                           for issue in reliability_issues)
    reliability_percentage = (reliability_total / len(ccts_df)) * 100
    print(f"  CCTS Complaints: {reliability_total:,} issues ({reliability_percentage:.1f}%)")
    
    print(f"\nLevel 2 - Human Support Access:")
    support_issues = ['Customer Support', 'Service Quality']
    support_total = sum(app_categories.get(cat, 0) for cat in support_issues)
    support_percentage = (support_total / len(app_df)) * 100
    print(f"  App Reviews: {support_total:,} issues ({support_percentage:.1f}%)")
    
    print(f"\nLevel 3 - Performance:")
    perf_issues = ['Performance', 'Network Issues', 'Coverage Issues']
    perf_total = sum(app_categories.get(cat, 0) for cat in perf_issues)
    perf_percentage = (perf_total / len(app_df)) * 100
    print(f"  App Reviews: {perf_total:,} issues ({perf_percentage:.1f}%)")
    
    print(f"\nLevel 4 - User Experience:")
    ux_issues = ['User Experience', 'Notifications', 'Features']
    ux_total = sum(app_categories.get(cat, 0) for cat in ux_issues)
    ux_percentage = (ux_total / len(app_df)) * 100
    print(f"  App Reviews: {ux_total:,} issues ({ux_percentage:.1f}%)")
    
    # Billing dominance analysis
    print(f"\n\nBILLING DOMINANCE ANALYSIS")
    print("-" * 30)
    
    # CCTS billing
    billing_ccts = 6752  # From earlier analysis
    billing_ccts_pct = (billing_ccts / len(ccts_df)) * 100
    print(f"CCTS Billing Complaints: {billing_ccts:,} ({billing_ccts_pct:.1f}%)")
    
    # App billing 
    app_billing = app_categories.get('Billing', 0)
    app_billing_pct = (app_billing / len(app_df)) * 100
    print(f"App Billing Reviews: {app_billing:,} ({app_billing_pct:.1f}%)")
    
    # Price increases
    price_issues = app_categories.get('Price Increases', 0)
    price_pct = (price_issues / len(app_df)) * 100
    print(f"App Price Increase Reviews: {price_issues:,} ({price_pct:.1f}%)")
    
    # Key insights
    print(f"\n\nKEY DATA INSIGHTS")
    print("-" * 20)
    print(f"1. Billing Crisis: 42.4% of regulatory complaints vs {app_billing_pct:.1f}% of app reviews")
    print(f"2. App Reliability: {core_percentage:.1f}% of reviews relate to basic functionality")
    print(f"3. Hidden Complexity: Authentication issues affect {app_categories.get('Authentication', 0):,} users")
    print(f"4. Performance Gap: {perf_percentage:.1f}% cite network/performance issues")
    print(f"5. UX Matters: {ux_percentage:.1f}% focus on user experience improvements")
    
    # Bell vs Rogers comparison
    print(f"\n\nPROVIDER COMPARISON")
    print("-" * 20)
    bell_reviews = app_df[app_df['app'] == 'Bell']
    rogers_reviews = app_df[app_df['app'] == 'Rogers']
    
    print(f"Bell Reviews: {len(bell_reviews):,}")
    print(f"Rogers Reviews: {len(rogers_reviews):,}")
    
    # Top issues by provider
    bell_cats = bell_reviews['enhanced_category'].value_counts()
    rogers_cats = rogers_reviews['enhanced_category'].value_counts()
    
    print(f"\nBell Top Issues:")
    for cat, count in bell_cats.head(5).items():
        percentage = (count / len(bell_reviews)) * 100
        print(f"  {cat}: {count:,} ({percentage:.1f}%)")
    
    print(f"\nRogers Top Issues:")
    for cat, count in rogers_cats.head(5).items():
        percentage = (count / len(rogers_reviews)) * 100
        print(f"  {cat}: {count:,} ({percentage:.1f}%)")

if __name__ == "__main__":
    analyze_comprehensive_data()