#!/usr/bin/env python3

import re
import os

def fix_search_functionality():
    """Fix the search functionality in the Reviews tab"""
    
    print("=== FIXING SEARCH FUNCTIONALITY ===\n")
    
    dashboard_file = 'html_dashboard/dashboard.html'
    
    if not os.path.exists(dashboard_file):
        print(f"❌ Dashboard file not found: {dashboard_file}")
        return
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Fix the search filter to use the correct field name
    search_fixes = [
        # Fix the field name from 'content' to 'review' or 'text'
        (r'\(review\.content \|\| ""\)\.toLowerCase\(\)\.includes\(searchTerm\)', 
         '((review.review || review.text || "").toLowerCase().includes(searchTerm))'),
        
        # Also search in title and summary fields for better results
        (r'filteredReviews = filteredReviews\.filter\(\(review\) =>\s*\(\(review\.review \|\| review\.text \|\| ""\)\.toLowerCase\(\)\.includes\(searchTerm\)\)\);',
         '''filteredReviews = filteredReviews.filter((review) => {
            const searchText = (
              (review.review || "") + " " + 
              (review.text || "") + " " + 
              (review.title || "") + " " + 
              (review.claude_summary || "")
            ).toLowerCase();
            return searchText.includes(searchTerm);
          });'''),
    ]
    
    fixes_made = 0
    
    for old_pattern, new_code in search_fixes:
        if re.search(old_pattern, content, re.DOTALL):
            content = re.sub(old_pattern, new_code, content, flags=re.DOTALL)
            fixes_made += 1
            print(f"✅ Fixed search pattern: {old_pattern[:50]}...")
    
    # If the more complex pattern didn't match, try the simpler fix
    if fixes_made == 0:
        simple_fix = (
            r'\(review\.content \|\| ""\)',
            '(review.review || review.text || "")'
        )
        
        if re.search(simple_fix[0], content):
            content = re.sub(simple_fix[0], simple_fix[1], content)
            fixes_made += 1
            print(f"✅ Applied simple search field fix")
    
    # Enhanced search functionality - make it search multiple fields
    enhanced_search = '''
      // Enhanced search functionality for Reviews tab
      function applyFilters() {
        const category = document.getElementById("categoryFilter").value;
        const provider = document.getElementById("appFilter").value;
        const platform = document.getElementById("platformFilter").value;
        const searchTerm = document
          .getElementById("searchFilter")
          .value.toLowerCase();

        // Update filter status
        let activeFilters = [];
        if (category !== "all") activeFilters.push(category);
        if (provider !== "all") activeFilters.push(provider);
        if (platform !== "all") activeFilters.push(platform);
        if (searchTerm) activeFilters.push("Search: " + searchTerm);

        document.getElementById("filterStatus").textContent =
          activeFilters.length > 0
            ? "Active filters: " + activeFilters.join(", ")
            : "";

        // Get reviews data
        let filteredReviews = [];
        
        if (typeof window.DASHBOARD_DATA !== "undefined" && window.DASHBOARD_DATA.reviews) {
          filteredReviews = [...window.DASHBOARD_DATA.reviews];
        } else if (typeof telecomReviews !== "undefined") {
          filteredReviews = [...telecomReviews];
        } else {
          console.error("No review data available for filtering");
          return;
        }

        // Apply filters
        if (category !== "all") {
          filteredReviews = filteredReviews.filter(
            (review) =>
              (review.category || review.primary_category || "").toLowerCase() === category.toLowerCase()
          );
        }
        if (provider !== "all") {
          filteredReviews = filteredReviews.filter(
            (review) =>
              (review.app || review.app_name || "").toLowerCase() === provider.toLowerCase()
          );
        }
        if (platform !== "all") {
          filteredReviews = filteredReviews.filter(
            (review) =>
              (review.platform || "").toLowerCase() === platform.toLowerCase()
          );
        }
        
        // Enhanced search - search across multiple fields
        if (searchTerm) {
          filteredReviews = filteredReviews.filter((review) => {
            const searchableText = [
              review.review || review.text || "",
              review.title || "",
              review.claude_summary || "",
              review.author || "",
              review.issue_tags || "",
              review.feature_tags || "",
              review.primary_category || "",
              review.claude_sentiment || ""
            ].join(" ").toLowerCase();
            
            return searchableText.includes(searchTerm);
          });
        }

        // Update table with filtered results
        updateTableWithReviews(filteredReviews.slice(0, 100));
        
        // Update result count
        const resultCount = document.getElementById("resultCount");
        if (resultCount) {
          resultCount.textContent = `Showing ${Math.min(filteredReviews.length, 100)} of ${filteredReviews.length} reviews`;
        }
      }
    '''
    
    # Find and replace the existing applyFilters function
    apply_filters_pattern = r'function applyFilters\(\)\s*\{[^}]+\}(?:\s*\{[^}]+\})*'
    
    if re.search(apply_filters_pattern, content, re.DOTALL):
        # Find the complete function including nested braces
        start_pos = content.find('function applyFilters()')
        if start_pos != -1:
            brace_count = 0
            pos = content.find('{', start_pos)
            end_pos = pos
            
            while pos < len(content) and (brace_count > 0 or content[pos] == '{'):
                if content[pos] == '{':
                    brace_count += 1
                elif content[pos] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = pos + 1
                        break
                pos += 1
            
            if end_pos > start_pos:
                old_function = content[start_pos:end_pos]
                content = content[:start_pos] + enhanced_search.strip() + content[end_pos:]
                fixes_made += 1
                print(f"✅ Replaced applyFilters function with enhanced search")
    
    # Add result count display if not present
    if 'resultCount' not in content:
        result_count_html = '''
          <div id="resultCount" style="margin: 1rem 0; color: var(--ey-gray-dark); font-size: 0.9rem;">
            Loading reviews...
          </div>
        '''
        
        # Insert after the filter status
        filter_status_pattern = r'(<div id="filterStatus"[^>]*></div>)'
        if re.search(filter_status_pattern, content):
            content = re.sub(filter_status_pattern, r'\1' + result_count_html, content)
            fixes_made += 1
            print(f"✅ Added result count display")
    
    # Write back if changes were made
    if content != original_content:
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n📝 Saved {fixes_made} search functionality fixes")
    else:
        print(f"\n⚪ No search fixes needed")
    
    return fixes_made

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis')
    fixes = fix_search_functionality()
    print(f"\nSearch functionality fixes: {fixes}")