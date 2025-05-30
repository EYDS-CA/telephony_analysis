#!/usr/bin/env python3

import re
import os

def fix_corrupted_titles():
    """Fix all corrupted titles in HTML reports"""
    
    print("=== FIXING CORRUPTED REPORT TITLES ===\n")
    
    # Define proper title mappings
    title_fixes = [
        # Bell report fixes
        (r'Bell: 3,048>', 'Bell\'s Smart CX Decisions'),
        (r'Bell: 3,048', 'Bell'),
        
        # Rogers report fixes  
        (r'Rogers: 7,055>', 'Rogers CX Transformation Strategy'),
        (r'Rogers: 7,055', 'Rogers'),
        
        # Executive summary fixes
        (r'Executive Summary: Rogers: 7,055>', 'Executive Summary'),
        
        # CX Assessment fixes
        (r'Customer Experience Assessment: Rogers: 7,055>', 'Customer Experience Assessment'),
        (r'Where Bell: 3,048>', 'Where Bell Excels'),
        (r'Why Bell: 3,048>', 'Why Bell Outperforms'),
        
        # Dashboard fixes
        (r'<h1 class="report-title">Rogers: 7,055>', '<h1 class="report-title">Rogers CX Transformation Strategy'),
        (r'<h3 class="card-title">Rogers: 7,055>', '<h3 class="card-title">Rogers Strategic Report'),
        (r'<h3 class="card-title">Bell: 3,048>', '<h3 class="card-title">Bell CX Analysis'),
        
        # Generic section headers
        (r'<h2>Rogers: 7,055>', '<h2>Rogers Analysis'),
        (r'<h2>Bell: 3,048>', '<h2>Bell Analysis'),
        (r'<h3>Rogers: 7,055>', '<h3>Rogers Insights'),
        (r'<h3>Bell: 3,048>', '<h3>Bell Insights'),
        
        # Recommendation fixes
        (r'Recommendation for Rogers: 7,055>', 'Recommendations for Rogers'),
    ]
    
    # Files to process
    html_files = [
        'bell_smart_cx_report.html',
        'cx_ux_assessment_report.html', 
        'dashboard.html',
        'executive_summary.html',
        'rogers_cx_transformation_report.html'
    ]
    
    total_fixes = 0
    
    for html_file in html_files:
        if not os.path.exists(html_file):
            print(f"⚠️  File not found: {html_file}")
            continue
            
        print(f"📄 Processing {html_file}...")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_fixes = 0
        
        # Apply all title fixes
        for pattern, replacement in title_fixes:
            matches = len(re.findall(pattern, content))
            if matches > 0:
                content = re.sub(pattern, replacement, content)
                file_fixes += matches
                print(f"  ✅ Fixed: '{pattern}' → '{replacement}' ({matches} instances)")
        
        # Write back if changes were made
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  📝 Saved {file_fixes} fixes to {html_file}")
        else:
            print(f"  ⚪ No fixes needed")
        
        total_fixes += file_fixes
        print()
    
    print(f"=== TITLE FIXES COMPLETE ===")
    print(f"Fixed {total_fixes} corrupted titles across {len(html_files)} files")
    
    return total_fixes

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis/html_dashboard')
    fix_corrupted_titles()