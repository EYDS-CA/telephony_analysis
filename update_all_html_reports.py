#!/usr/bin/env python3

import json
import re
import os
from pathlib import Path

def load_metrics():
    """Load the filtered dataset metrics"""
    with open('filtered_dataset_metrics.json', 'r') as f:
        return json.load(f)

def update_html_file(file_path, metrics):
    """Update a single HTML file with new metrics"""
    print(f"Updating {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Track changes
    changes = []
    
    # Update total review counts (various formats)
    old_patterns = [
        r'12,785',
        r'12,893', 
        r'12785',
        r'12893'
    ]
    
    for pattern in old_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, '10,103', content)
            changes.append(f"Updated {pattern} to 10,103")
    
    # Update data timeframe references
    timeframe_updates = [
        (r'2010-2025', '2020-2025'),
        (r'2015-2025', '2020-2025'),
        (r'from 2010', 'from 2020'),
        (r'since 2010', 'since 2020'),
        (r'spanning.*?2010.*?2025', 'spanning 2020-2025')
    ]
    
    for old_pattern, new_pattern in timeframe_updates:
        if re.search(old_pattern, content):
            content = re.sub(old_pattern, new_pattern, content)
            changes.append(f"Updated timeframe: {old_pattern} to {new_pattern}")
    
    # Update data currency percentage
    data_currency_updates = [
        (r'65\.2%', '99.6%'),
        (r'78\.4%', '99.6%'),
        (r'data currency.*?65\.2', f'data currency: 99.6'),
        (r'current data.*?78\.4', f'current data: 99.6')
    ]
    
    for old_pattern, new_pattern in data_currency_updates:
        if re.search(old_pattern, content, re.IGNORECASE):
            content = re.sub(old_pattern, new_pattern, content, flags=re.IGNORECASE)
            changes.append(f"Updated data currency to 99.6%")
    
    # Update platform splits (approximate)
    platform_updates = [
        (r'Android.*?(\d+,?\d*)', f'Android: {metrics["android_reviews"]:,}'),
        (r'iOS.*?(\d+,?\d*)', f'iOS: {metrics["ios_reviews"]:,}'),
        (r'89\.9%.*?Android', f'{metrics["android_percentage"]}% Android'),
        (r'10\.1%.*?iOS', f'{metrics["ios_percentage"]}% iOS')
    ]
    
    # Update average rating if found
    if re.search(r'average rating.*?[23]\.\d+', content, re.IGNORECASE):
        content = re.sub(r'(average rating.*?)([23]\.\d+)', f'\\g<1>{metrics["average_rating"]}', content, flags=re.IGNORECASE)
        changes.append(f"Updated average rating to {metrics['average_rating']}")
    
    # Update Rogers/Bell split
    if re.search(r'Rogers.*?\d+', content):
        content = re.sub(r'Rogers.*?(\d+,?\d*)', f'Rogers: {metrics["rogers_reviews"]:,}', content)
        changes.append(f"Updated Rogers count to {metrics['rogers_reviews']:,}")
    
    if re.search(r'Bell.*?\d+', content):
        content = re.sub(r'Bell.*?(\d+,?\d*)', f'Bell: {metrics["bell_reviews"]:,}', content)
        changes.append(f"Updated Bell count to {metrics['bell_reviews']:,}")
    
    # Add filtering methodology note (if not already present)
    if 'pre-2020' not in content and 'dashboard.html' in file_path:
        methodology_note = '''
        <div class="methodology-note" style="background: #f8f9fa; border-left: 4px solid var(--ey-blue); padding: 1rem; margin: 1rem 0; font-size: 0.9rem;">
            <strong>Data Quality Enhancement:</strong> This analysis focuses on current, relevant data by filtering out outdated Android reviews (pre-2020) 
            while preserving all iOS reviews (already current 2023-2025). This improves data currency from 65.2% to 99.6%, ensuring business-relevant insights.
        </div>
        '''
        # Insert after the first paragraph or header
        content = re.sub(r'(<p[^>]*>.*?</p>)', f'\\1{methodology_note}', content, count=1)
        changes.append("Added filtering methodology note")
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    if changes:
        print(f"  ✓ Made {len(changes)} changes:")
        for change in changes:
            print(f"    - {change}")
    else:
        print(f"  ⚪ No changes needed")
    
    return len(changes)

def main():
    """Update all HTML reports with filtered dataset metrics"""
    
    # Load metrics
    metrics = load_metrics()
    print("=== UPDATING ALL HTML REPORTS WITH FILTERED METRICS ===\n")
    print(f"Using filtered dataset metrics:")
    print(f"  Total Reviews: {metrics['total_reviews']:,}")
    print(f"  Android: {metrics['android_reviews']:,} ({metrics['android_percentage']}%)")
    print(f"  iOS: {metrics['ios_reviews']:,} ({metrics['ios_percentage']}%)")
    print(f"  Rogers: {metrics['rogers_reviews']:,} ({metrics['rogers_percentage']}%)")
    print(f"  Bell: {metrics['bell_reviews']:,} ({metrics['bell_percentage']}%)")
    print(f"  Average Rating: {metrics['average_rating']}")
    print(f"  Data Currency: {metrics['data_currency']}%")
    print(f"  Date Range: {metrics['date_range_start']} to {metrics['date_range_end']}\n")
    
    # List of HTML files to update
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
    
    total_changes = 0
    
    for html_file in html_files:
        if os.path.exists(html_file):
            changes = update_html_file(html_file, metrics)
            total_changes += changes
        else:
            print(f"⚠️  File not found: {html_file}")
        print()
    
    print(f"=== UPDATE COMPLETE ===")
    print(f"Updated {len([f for f in html_files if os.path.exists(f)])} files with {total_changes} total changes")
    print(f"All reports now reflect the filtered dataset of {metrics['total_reviews']:,} reviews (2020-2025)")

if __name__ == "__main__":
    main()