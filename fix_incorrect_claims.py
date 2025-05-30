#!/usr/bin/env python3

import re
import os

def fix_incorrect_claims():
    """Fix all incorrect statistical claims based on verification results"""
    
    print("=== FIXING INCORRECT CLAIMS BASED ON VERIFICATION ===\n")
    
    # Based on verification results, these are the corrections needed:
    corrections = [
        # iOS/Android platform performance corrections
        (r'84\.2% negative reviews on iOS', '75.4% negative reviews on iOS'),
        (r'58\.1% on Android', '59.2% on Android'),
        (r'26-point gap', '16.2-point gap'),
        (r'84\.2% negative.*?58\.1%', '75.4% negative sentiment versus 59.2% on Android'),
        
        # Chatbot complaints correction (major fix needed)
        (r'8x fewer chatbot complaints', '2x fewer chatbot complaints'),
        (r'Bell has 8x fewer', 'Bell has 2x fewer'),
        (r'8x fewer chatbot', '2x fewer chatbot'),
        (r'Bell generates 8x fewer', 'Bell generates 2x fewer'),
        (r'\(4 vs 33\)', '(407 vs 822 negative mentions)'),
        (r'33 vs 4', '407 vs 822'),
        
        # Billing sentiment (minor adjustment)
        (r'77\.6% negative.*?billing', '81.5% negative sentiment in billing'),
        (r'77\.6% have negative billing', '81.5% have negative billing'),
        
        # Payment mentions correction
        (r'712 positive out of 2,377', '418 positive out of 2,139'),
        (r'2,377 mentions', '2,139 mentions'),
        (r'70% of payment-related mentions are negative', '72.9% of payment-related mentions are negative'),
        (r'\(712 positive out of 2,377 mentions\)', '(418 positive out of 2,139 mentions)'),
        
        # Average rating corrections (keep consistent)
        (r'both apps score 2\.64/5', 'apps average 2.58/5 overall (Rogers 2.60, Bell 2.53)'),
        (r'identical.*?2\.64/5', 'similar performance at 2.58/5 average'),
        
        # Technical Issues verification (already accurate)
        (r'94\.9% negative for Technical Issues', '95.1% negative for Technical Issues'),
        
        # General accuracy improvements
        (r'catastrophic failure rates.*?70%', 'high failure rates with 72.9% negative payment experiences'),
        (r'Despite identical 4\.4/5 app ratings and 2\.64/5 written reviews', 'Despite similar app store ratings, written reviews average 2.58/5'),
        
        # Rogers vs Bell ratio updates
        (r'Rogers.*?0\.37%.*?Bell.*?0\.11%', 'Rogers shows higher complaint volumes than Bell'),
        (r'8\.25x fewer AI frustrations', '2x fewer chatbot-related complaints'),
        
        # Platform-specific updates
        (r'iOS users experience significantly worse', 'iOS users experience moderately worse'),
        (r'disproportionately affect iOS users', 'affect iOS users more than Android users'),
    ]
    
    # Files to update
    html_files = [
        'html_dashboard/dashboard.html',
        'html_dashboard/executive_summary.html',
        'html_dashboard/rogers_cx_transformation_report.html',
        'html_dashboard/bell_smart_cx_report.html',
        'html_dashboard/cx_ux_assessment_report.html',
        'html_dashboard/research_methodology.html'
    ]
    
    total_fixes = 0
    
    for html_file in html_files:
        if not os.path.exists(html_file):
            continue
            
        print(f"📄 Fixing claims in {html_file}...")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_fixes = 0
        
        # Apply all corrections
        for old_pattern, new_text in corrections:
            matches = len(re.findall(old_pattern, content, re.IGNORECASE))
            if matches > 0:
                content = re.sub(old_pattern, new_text, content, flags=re.IGNORECASE)
                file_fixes += matches
                print(f"  ✅ Fixed: '{old_pattern}' → '{new_text}' ({matches} instances)")
        
        # Write back if changes were made
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  📝 Saved {file_fixes} claim corrections")
        else:
            print(f"  ⚪ No corrections needed")
        
        total_fixes += file_fixes
        print()
    
    print(f"=== CLAIM CORRECTIONS COMPLETE ===")
    print(f"Fixed {total_fixes} incorrect claims across {len(html_files)} files")
    
    # Generate corrected executive summary text
    print(f"\n=== CORRECTED EXECUTIVE SUMMARY TEXT ===")
    corrected_summary = """
Executive Summary

The Telecom App Hierarchy of Needs
Our analysis reveals a clear hierarchy:

95.1% negative for Technical Issues and 81.5% negative for Billing show that core function reliability matters most.

Apps average 2.58/5 overall (Rogers 2.60, Bell 2.53)—both struggle with the same core issues.

The winning formula: Build a "banking app that pays telecom bills" with bulletproof reliability.

Platform Performance Gap
iOS users experience moderately worse app performance than Android users, with 75.4% negative reviews on iOS versus 59.2% on Android.

This 16.2-point gap suggests platform-specific technical issues that affect iOS users more than Android users, who often represent premium customer segments.

CCTS Prevention Opportunity
42.4% of CCTS complaints are billing-related, while our data shows 81.5% negative sentiment in billing category reviews.

Additionally, 72.9% of payment-related mentions are negative (418 positive out of 2,139 mentions).

Fixing these app issues could prevent thousands of regulatory complaints.

Analysis Impact
From 30,000+ app store reviews, we analyzed 10,103 in detail using AI to categorize issues.

This revealed that frustrated users who write reviews experience high failure rates with 72.9% negative payment experiences and 81.5% negative billing sentiment.

These breaking points directly correlate with CCTS data showing 42.4% of formal complaints are billing-related—proving that fixing app billing functions could prevent thousands of regulatory escalations worth $2,500-6,500 each².

Bell's Smart CX Decisions: Evidence from App Design
Visual analysis confirms Bell's strategic advantages:

1) Hidden complexity - Chat requires 3 taps but delivers humans immediately (vs Rogers' instant chat that deflects).

2) Priority hierarchy - Core functions (usage/billing) above promotions (vs Rogers' credit card ads competing with bill payment).

3) Payment transparency - Shows current payment method before asking for alternatives (vs Rogers' confusing credit-first approach).

Despite similar app store ratings, written reviews average 2.58/5, and Bell has 2x fewer chatbot-related complaints (407 vs 822 negative mentions).
"""
    
    print(corrected_summary)
    
    return total_fixes

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis')
    fix_incorrect_claims()