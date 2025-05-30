#!/usr/bin/env python3
"""
Clean Category Results - Fix verbose category responses
"""

import pandas as pd
import re

def clean_category_name(category):
    """Clean verbose category responses to just the category name"""
    if not isinstance(category, str):
        return "User Feedback"
    
    # Map of standard categories
    standard_categories = [
        "App Crashes", "Technical Issues", "Performance", "User Experience", 
        "Features", "Authentication", "Price Increases", "Payment Issues", 
        "Billing", "Coverage Issues", "Roaming Issues", "Network Issues", 
        "Service Issues", "Customer Support", "Account Management", 
        "Security", "Data Usage", "Notifications", "User Feedback"
    ]
    
    # Check if category contains any standard category name
    category_lower = category.lower()
    for std_cat in standard_categories:
        if std_cat.lower() in category_lower:
            return std_cat
    
    # If no match found, return User Feedback as fallback
    return "User Feedback"

def main():
    """Clean the optimized dataset categories"""
    
    print("🧹 Cleaning category results...")
    
    # Load the optimized dataset
    df = pd.read_csv('Data/optimized_enhanced_analysis_20250529_122345.csv')
    
    print(f"📊 Dataset loaded: {len(df):,} reviews")
    
    # Show current category distribution
    current_cats = df['enhanced_category'].value_counts()
    print(f"\n❌ Current (messy) categories:")
    for cat, count in current_cats.head(10).items():
        print(f"   {cat[:60]}...: {count}")
    
    # Clean categories
    df['enhanced_category'] = df['enhanced_category'].apply(clean_category_name)
    
    # Show cleaned distribution
    cleaned_cats = df['enhanced_category'].value_counts()
    print(f"\n✅ Cleaned categories:")
    for cat, count in cleaned_cats.items():
        print(f"   {cat}: {count:,}")
    
    # Save cleaned dataset
    output_file = 'Data/enhanced_analysis_final_clean.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n🎯 Final Enhanced Analysis Complete!")
    print(f"   📁 Clean dataset: {output_file}")
    print(f"   📊 Total reviews: {len(df):,}")
    print(f"   📈 Categories: {len(cleaned_cats)}")
    
    print(f"\n🏆 Top Enhanced Categories:")
    for cat, count in cleaned_cats.head(10).items():
        print(f"   {cat}: {count:,}")

if __name__ == "__main__":
    main()