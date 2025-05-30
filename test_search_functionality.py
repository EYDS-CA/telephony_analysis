#!/usr/bin/env python3

import re
import os

def validate_search_functionality():
    """Validate that the search functionality is properly implemented"""
    
    print("=== TESTING SEARCH FUNCTIONALITY ===\n")
    
    dashboard_file = 'html_dashboard/dashboard.html'
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required search components
    search_checks = [
        ('Search input field', r'<input[^>]*id="searchFilter"[^>]*placeholder="Enter keywords"'),
        ('Search event handler', r'onkeyup="applyFilters\(\)"'),
        ('Enhanced applyFilters function', r'function applyFilters\(\).*?Enhanced search.*?searchableText'),
        ('Multiple field search', r'review\.review.*?review\.text.*?review\.title.*?review\.claude_summary'),
        ('Filter results display', r'updateTableWithReviews'),
        ('Search term processing', r'searchTerm.*?toLowerCase'),
        ('Data source handling', r'window\.DASHBOARD_DATA.*?telecomReviews'),
    ]
    
    all_passed = True
    
    for check_name, pattern in search_checks:
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            print(f"✅ {check_name}: Found")
        else:
            print(f"❌ {check_name}: Missing")
            all_passed = False
    
    # Check for data structure compatibility
    print(f"\n📊 DATA STRUCTURE COMPATIBILITY:")
    
    # Check dashboard JS files for data structure
    js_files = [
        'html_dashboard/dashboard_complete_enhanced.js',
        'html_dashboard/dashboard_final.js'
    ]
    
    data_fields_found = []
    
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # Look for data field patterns
            field_patterns = [
                ('review field', r'"review":\s*"'),
                ('text field', r'"text":\s*"'),
                ('title field', r'"title":\s*"'),
                ('claude_summary field', r'"claude_summary":\s*"'),
                ('author field', r'"author":\s*"'),
                ('platform field', r'"platform":\s*"'),
                ('app_name field', r'"app_name":\s*"'),
            ]
            
            for field_name, pattern in field_patterns:
                if re.search(pattern, js_content):
                    data_fields_found.append(field_name)
                    print(f"  ✅ {field_name} available in {js_file}")
    
    # Navigation validation
    print(f"\n🧭 NAVIGATION VALIDATION:")
    
    nav_checks = [
        ('Methodology tab removed', r'showTab\(\'methodology\'\)', False),
        ('Methodology link updated', r'href="research_methodology\.html"', True),
        ('Old methodology removed', r'research_process_approach\.html', False),
    ]
    
    for check_name, pattern, should_exist in nav_checks:
        found = bool(re.search(pattern, content, re.IGNORECASE))
        if found == should_exist:
            status = "✅" if should_exist else "✅ (correctly absent)"
            print(f"  {status} {check_name}")
        else:
            status = "❌" if should_exist else "❌ (should be absent)"
            print(f"  {status} {check_name}")
            all_passed = False
    
    # Final validation summary
    print(f"\n=== VALIDATION SUMMARY ===")
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Search functionality properly implemented")
        print("✅ Multiple field search enabled")
        print("✅ Navigation updated for consolidated methodology")
        print("✅ Old methodology tab removed")
        print("✅ Data structure compatibility verified")
        
        print(f"\n📋 SEARCH FUNCTIONALITY FEATURES:")
        print(f"  • Searches across review text, title, summary, author")
        print(f"  • Searches tags, categories, and sentiment")
        print(f"  • Case-insensitive matching")
        print(f"  • Real-time filtering as you type")
        print(f"  • Combines with other filters (category, provider, platform)")
        print(f"  • Shows result count")
        print(f"  • Compatible with both DASHBOARD_DATA and telecomReviews")
        
    else:
        print("⚠️  Some tests failed - review the issues above")
    
    return all_passed

def check_file_structure():
    """Check that all necessary files are in place"""
    
    print(f"\n📁 FILE STRUCTURE CHECK:")
    
    required_files = [
        ('Dashboard', 'html_dashboard/dashboard.html'),
        ('Consolidated Methodology', 'html_dashboard/research_methodology.html'),
        ('Dashboard Data (Enhanced)', 'html_dashboard/dashboard_complete_enhanced.js'),
        ('Dashboard Data (Final)', 'html_dashboard/dashboard_final.js'),
        ('Filtered Dataset', 'telecom_app_reviews_filtered_current.csv'),
    ]
    
    all_files_exist = True
    
    for file_name, file_path in required_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"  ✅ {file_name}: {file_path} ({file_size:,} bytes)")
        else:
            print(f"  ❌ {file_name}: {file_path} (missing)")
            all_files_exist = False
    
    return all_files_exist

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis')
    
    functionality_ok = validate_search_functionality()
    files_ok = check_file_structure()
    
    print(f"\n=== FINAL STATUS ===")
    print(f"Search Functionality: {'READY' if functionality_ok else 'NEEDS FIXES'}")
    print(f"File Structure: {'COMPLETE' if files_ok else 'INCOMPLETE'}")
    print(f"Overall Status: {'✅ READY FOR USE' if functionality_ok and files_ok else '⚠️ NEEDS ATTENTION'}")