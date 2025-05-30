#!/usr/bin/env python3

import re
import os

def fix_html_structure():
    """Fix broken HTML structure from title replacements"""
    
    print("=== FIXING HTML STRUCTURE ISSUES ===\n")
    
    # Files to process
    html_files = [
        'bell_smart_cx_report.html',
        'cx_ux_assessment_report.html', 
        'dashboard.html',
        'executive_summary.html',
        'rogers_cx_transformation_report.html'
    ]
    
    # Common HTML structure fixes
    structure_fixes = [
        # Fix missing closing tags
        (r'<h1 class="header-title">([^<]+)$', r'<h1 class="header-title">\1</h1>'),
        (r'<h1 class="report-title">([^<]+)$', r'<h1 class="report-title">\1</h1>'),
        (r'<h2>([^<]+)$', r'<h2>\1</h2>'),
        (r'<h3>([^<]+)$', r'<h3>\1</h3>'),
        
        # Fix broken content that was cut off
        (r'Bell\.64/5', 'Bell achieves 2.64/5'),
        (r'Bell\.7%', 'Bell: 58.7%'),
        (r'Rogers\.1%', 'Rogers: 64.1%'),
        (r'Rogers\.079%', 'Rogers: 0.079%'),
        (r'Bell\.037%', 'Bell: 0.037%'),
        (r'Bell\.11%', 'Bell: 0.11%'),
        (r'Rogers\.37%', 'Rogers: 0.37%'),
        (r'Bell\.70/5', 'Bell: 3.70/5'),
        (r'Bell \(0\.11%', 'Bell: 0.11%'),
        (r'Rogers \(0\.37%', 'Rogers: 0.37%'),
        (r'Rogers% of viewport', 'Rogers: 45% of viewport'),
        (r'Bellx fewer', 'Bell generates 8x fewer'),
        
        # Fix incomplete sentences
        (r'Despite superior UI, Bell\.', 'Despite superior UI, Bell achieves the same 2.64/5 rating as Rogers.'),
        (r'How Bellx fewer chatbot', 'How Bell generates 8x fewer chatbot'),
    ]
    
    total_fixes = 0
    
    for html_file in html_files:
        if not os.path.exists(html_file):
            continue
            
        print(f"📄 Fixing HTML structure in {html_file}...")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_fixes = 0
        
        # Apply all structure fixes
        for pattern, replacement in structure_fixes:
            matches = len(re.findall(pattern, content, re.MULTILINE))
            if matches > 0:
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                file_fixes += matches
                print(f"  ✅ Fixed: '{pattern}' ({matches} instances)")
        
        # Write back if changes were made
        if content != original_content:
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  📝 Saved {file_fixes} structure fixes")
        else:
            print(f"  ⚪ No structure fixes needed")
        
        total_fixes += file_fixes
        print()
    
    return total_fixes

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis/html_dashboard')
    fix_html_structure()