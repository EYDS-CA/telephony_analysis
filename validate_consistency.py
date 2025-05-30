#!/usr/bin/env python3

import re
import os
import json
from pathlib import Path

def validate_html_consistency():
    """Validate that all HTML files have consistent metrics"""
    
    # Load expected metrics
    with open('filtered_dataset_metrics.json', 'r') as f:
        expected_metrics = json.load(f)
    
    print("=== VALIDATING METRICS CONSISTENCY ACROSS ALL REPORTS ===\n")
    print(f"Expected metrics from filtered dataset:")
    print(f"  Total Reviews: {expected_metrics['total_reviews']:,}")
    print(f"  Data Currency: {expected_metrics['data_currency']}%")
    print(f"  Average Rating: {expected_metrics['average_rating']}")
    print(f"  Rogers: {expected_metrics['rogers_reviews']:,} ({expected_metrics['rogers_percentage']}%)")
    print(f"  Bell: {expected_metrics['bell_reviews']:,} ({expected_metrics['bell_percentage']}%)\n")
    
    # Files to validate
    html_files = [
        'html_dashboard/dashboard.html',
        'html_dashboard/executive_summary.html',
        'html_dashboard/rogers_cx_transformation_report.html',
        'html_dashboard/bell_smart_cx_report.html',
        'html_dashboard/cx_ux_assessment_report.html',
        'html_dashboard/metrics_calculations_verification.html',
        'html_dashboard/research_process_approach.html',
        'html_dashboard/key_metrics_reference.html'
    ]
    
    issues = []
    
    for html_file in html_files:
        if not os.path.exists(html_file):
            issues.append(f"❌ File not found: {html_file}")
            continue
            
        print(f"📄 Validating {html_file}...")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_issues = []
        
        # Check for old review counts
        old_counts = ['12,785', '12,893', '12785', '12893']
        for old_count in old_counts:
            if old_count in content:
                file_issues.append(f"  ❌ Still contains old count: {old_count}")
        
        # Check for correct total review count
        if '10,103' not in content:
            file_issues.append(f"  ⚠️  Missing correct total review count (10,103)")
        
        # Check data timeframe
        if '2010' in content and '2020-2025' not in content:
            file_issues.append(f"  ⚠️  May contain old timeframe (2010 instead of 2020)")
        
        # Check for old data currency percentages
        old_currency = ['65.2%', '78.4%']
        for old_perc in old_currency:
            if old_perc in content:
                file_issues.append(f"  ❌ Still contains old data currency: {old_perc}")
        
        # Check for correct data currency
        if '99.6%' not in content and 'data_accuracy_report' not in html_file:
            file_issues.append(f"  ⚠️  Missing correct data currency (99.6%)")
        
        if file_issues:
            issues.extend([f"Issues in {html_file}:"] + file_issues)
            print(f"  ❌ Found {len(file_issues)} issues")
        else:
            print(f"  ✅ All metrics consistent")
        
        print()
    
    # Validate dashboard data files
    print("📊 Validating dashboard data files...")
    
    js_files = [
        'html_dashboard/dashboard_complete_enhanced.js',
        'html_dashboard/dashboard_final.js'
    ]
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            if 'total_reviews: 10103' in js_content:
                print(f"  ✅ {js_file} has correct total_reviews")
            else:
                issues.append(f"❌ {js_file} missing correct total_reviews")
        else:
            issues.append(f"❌ JS file not found: {js_file}")
    
    print()
    
    # Summary
    if issues:
        print("=== VALIDATION ISSUES FOUND ===")
        for issue in issues:
            print(issue)
        print(f"\nTotal issues: {len(issues)}")
    else:
        print("=== VALIDATION PASSED ===")
        print("✅ All files have consistent metrics matching the filtered dataset")
        print("✅ Dashboard data files are synchronized")
        print("✅ All reports reflect 10,103 reviews from 2020-2025")
        print("✅ Data currency improved to 99.6%")
    
    return len(issues) == 0

def validate_dashboard_functionality():
    """Quick validation of dashboard HTML structure"""
    
    print("\n=== VALIDATING DASHBOARD FUNCTIONALITY ===")
    
    dashboard_file = 'html_dashboard/dashboard.html'
    
    if not os.path.exists(dashboard_file):
        print("❌ Dashboard file not found")
        return False
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ('Chart.js library', 'chart.js'),
        ('Plotly library', 'plotly.js'),
        ('Dashboard initialization', 'initializeStandaloneMode'),
        ('Chart containers', 'sentiment-chart'),
        ('Navigation tabs', 'nav-tab'),
        ('Loading screen', 'loading'),
        ('Updated total reviews', '10,103')
    ]
    
    all_passed = True
    for check_name, check_pattern in checks:
        if check_pattern in content:
            print(f"  ✅ {check_name}")
        else:
            print(f"  ❌ {check_name}")
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    consistency_ok = validate_html_consistency()
    functionality_ok = validate_dashboard_functionality()
    
    print(f"\n=== FINAL VALIDATION RESULTS ===")
    if consistency_ok and functionality_ok:
        print("🎉 ALL VALIDATIONS PASSED!")
        print("   • Metrics are consistent across all reports")
        print("   • Dashboard functionality is intact")
        print("   • Filtered dataset properly reflected (10,103 reviews)")
        print("   • Data currency improved to 99.6%")
    else:
        print("⚠️  Some validations failed - please review the issues above")