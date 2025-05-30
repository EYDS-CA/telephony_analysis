#!/usr/bin/env python3

import re
import os

def update_navigation_for_methodology():
    """Update navigation to use consolidated research methodology and remove old tab"""
    
    print("=== UPDATING NAVIGATION FOR CONSOLIDATED METHODOLOGY ===\n")
    
    # Files to update
    files_to_update = [
        'html_dashboard/dashboard.html',
        'html_dashboard/executive_summary.html', 
        'html_dashboard/rogers_cx_transformation_report.html',
        'html_dashboard/bell_smart_cx_report.html',
        'html_dashboard/cx_ux_assessment_report.html',
        'html_dashboard/key_metrics_reference.html',
        'html_dashboard/metrics_calculations_verification.html'
    ]
    
    navigation_updates = [
        # Remove the Research Methodology tab from main navigation
        (r'<button[^>]*onclick="[^"]*showTab\(\'methodology\'\)[^"]*"[^>]*>\s*Research Methodology\s*</button>\s*', ''),
        
        # Update Reports section to include consolidated methodology
        (r'(<h3[^>]*>.*?Data Analysis & Research Methodology.*?</h3>)', 
         r'\1'),  # Keep the section title
        
        # Replace old methodology links with consolidated one
        (r'href="research_process_approach\.html"', 'href="research_methodology.html"'),
        (r'href="metrics_calculations_verification\.html"', 'href="research_methodology.html"'),
        
        # Update any references to old methodology files
        (r'Research Process & Approach', 'Research Methodology'),
        (r'Metrics Calculations & Verification', 'Research Methodology'),
        
        # Update methodology section content
        (r'(<div class="card"[^>]*>.*?)(<div class="card-header">.*?<h3 class="card-title">)Research Process & Approach(</h3>.*?<p class="card-subtitle">)([^<]*)(</p>.*?</div>.*?<p[^>]*>)([^<]*)(</p>.*?<a[^>]*href=")[^"]*(".*?</a>)', 
         r'\1\2Research Methodology\3Comprehensive approach to data collection, AI analysis, and validation\4\5Complete methodology covering extraction of 30,000+ reviews, AI-powered analysis of 10,103 filtered reviews, and cross-validation with CCTS complaints\6\7research_methodology.html\8'),
        
        # Remove the duplicate methodology card 
        (r'<div class="card"[^>]*>.*?<h3 class="card-title">Metrics Calculations & Verification</h3>.*?</div>\s*</div>', ''),
    ]
    
    total_updates = 0
    
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            continue
            
        print(f"📄 Updating navigation in {file_path}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_updates = 0
        
        for old_pattern, new_content in navigation_updates:
            matches = len(re.findall(old_pattern, content, re.DOTALL | re.IGNORECASE))
            if matches > 0:
                content = re.sub(old_pattern, new_content, content, flags=re.DOTALL | re.IGNORECASE)
                file_updates += matches
                print(f"  ✅ Updated: {old_pattern[:40]}... ({matches} instances)")
        
        # Special handling for dashboard.html to remove methodology tab content
        if 'dashboard.html' in file_path:
            # Remove the methodology tab content section
            methodology_tab_pattern = r'<!-- Research Methodology Tab -->.*?</div>\s*</div>\s*<!-- End methodology tab -->'
            if not re.search(methodology_tab_pattern, content, re.DOTALL):
                # Try alternative pattern
                methodology_tab_pattern = r'<div id="methodology" class="tab-content">.*?</div>\s*</div>'
                
            if re.search(methodology_tab_pattern, content, re.DOTALL):
                content = re.sub(methodology_tab_pattern, '', content, flags=re.DOTALL)
                file_updates += 1
                print(f"  ✅ Removed methodology tab content section")
            
            # Remove methodology from tab switching logic
            methodology_switch_patterns = [
                (r'case "methodology":\s*shouldActivate = tabText === "Research Methodology";\s*break;', ''),
                (r'"methodology"[^}]*}', ''),
            ]
            
            for pattern, replacement in methodology_switch_patterns:
                if re.search(pattern, content, re.DOTALL):
                    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
                    file_updates += 1
                    print(f"  ✅ Removed methodology from tab switching logic")
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  📝 Saved {file_updates} navigation updates")
        else:
            print(f"  ⚪ No navigation updates needed")
        
        total_updates += file_updates
        print()
    
    # Update the consolidated methodology file navigation
    methodology_file = 'html_dashboard/research_methodology.html'
    if os.path.exists(methodology_file):
        print(f"📄 Updating navigation links in {methodology_file}...")
        
        with open(methodology_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure it has proper navigation back to dashboard
        nav_links = [
            (r'href="dashboard\.html\?tab=reports"', 'href="dashboard.html?tab=reports"'),
            (r'href="\.\.\/research_process_approach\.html"', 'href="dashboard.html?tab=reports"'),
        ]
        
        for old_link, new_link in nav_links:
            if re.search(old_link, content):
                content = re.sub(old_link, new_link, content)
                total_updates += 1
        
        with open(methodology_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✅ Updated methodology file navigation")
    
    print(f"=== NAVIGATION UPDATES COMPLETE ===")
    print(f"Total updates: {total_updates}")
    print(f"✅ Consolidated research methodology integrated")
    print(f"✅ Old methodology tab removed")
    print(f"✅ All report links point to research_methodology.html")
    
    return total_updates

def create_shared_navigation_update():
    """Update shared navigation if it exists"""
    
    shared_nav_file = 'html_dashboard/shared-navigation.js'
    
    if os.path.exists(shared_nav_file):
        print(f"\n📄 Updating shared navigation file...")
        
        with open(shared_nav_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update any methodology references
        updates = [
            (r'research_process_approach\.html', 'research_methodology.html'),
            (r'metrics_calculations_verification\.html', 'research_methodology.html'),
            (r'Research Process.*?Approach', 'Research Methodology'),
            (r'Metrics Calculations.*?Verification', 'Research Methodology'),
        ]
        
        updates_made = 0
        for old_pattern, new_content in updates:
            if re.search(old_pattern, content, re.IGNORECASE):
                content = re.sub(old_pattern, new_content, content, flags=re.IGNORECASE)
                updates_made += 1
        
        if updates_made > 0:
            with open(shared_nav_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated shared navigation with {updates_made} changes")
        else:
            print(f"  ⚪ No shared navigation updates needed")
        
        return updates_made
    
    return 0

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis')
    
    nav_updates = update_navigation_for_methodology()
    shared_updates = create_shared_navigation_update()
    
    print(f"\n=== SUMMARY ===")
    print(f"Navigation updates: {nav_updates}")
    print(f"Shared navigation updates: {shared_updates}")
    print(f"Total: {nav_updates + shared_updates}")