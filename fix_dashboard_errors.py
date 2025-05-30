#!/usr/bin/env python3

import re
import os

def fix_dashboard_javascript_errors():
    """Fix JavaScript errors and restore missing search functionality"""
    
    print("=== FIXING DASHBOARD JAVASCRIPT ERRORS ===\n")
    
    dashboard_file = 'html_dashboard/dashboard.html'
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    fixes_made = 0
    
    # Fix 1: Ensure search input field exists in Reviews tab
    if 'id="searchFilter"' not in content:
        # Find the Reviews tab content and add search input
        reviews_tab_pattern = r'(<div id="analysis" class="tab-content">.*?<div class="filter-group">.*?</div>)'
        
        search_input_html = '''
              <div class="filter-group">
                <label class="filter-label">Search Reviews</label>
                <input
                  type="text"
                  class="filter-input"
                  id="searchFilter"
                  placeholder="Enter keywords..."
                  onkeyup="applyFilters()"
                />
              </div>
        '''
        
        if re.search(reviews_tab_pattern, content, re.DOTALL):
            # Insert search input after the last filter group
            insertion_point = content.find('</div>', content.find('class="filter-group"')) + 6
            if insertion_point > 5:
                content = content[:insertion_point] + search_input_html + content[insertion_point:]
                fixes_made += 1
                print(f"✅ Added search input field to Reviews tab")
    
    # Fix 2: Add null checks for DOM elements
    null_check_fixes = [
        # Fix addEventListener on null element
        (r'(\w+)\.addEventListener\(', r'if (\1) \1.addEventListener('),
        
        # Fix innerHTML on null element  
        (r'(\w+)\.innerHTML\s*=', r'if (\1) \1.innerHTML ='),
        
        # Fix specific populateDataTable error
        (r'document\.getElementById\("reviewsTableBody"\)\.innerHTML', 
         'const tbody = document.getElementById("reviewsTableBody"); if (tbody) tbody.innerHTML'),
    ]
    
    for old_pattern, new_pattern in null_check_fixes:
        matches = re.findall(old_pattern, content)
        if matches:
            content = re.sub(old_pattern, new_pattern, content)
            fixes_made += len(matches)
            print(f"✅ Added null checks for DOM operations ({len(matches)} instances)")
    
    # Fix 3: Ensure Reviews tab structure is complete
    reviews_tab_structure = '''
        <!-- Reviews Analysis Tab -->
        <div id="analysis" class="tab-content">
          <div class="container" style="max-width: 1200px">
            <h2 style="margin-bottom: 2rem">Reviews Analysis</h2>

            <!-- Filters -->
            <div class="filters-container" style="margin-bottom: 2rem">
              <div class="filter-group">
                <label class="filter-label">Category</label>
                <select class="filter-select" id="categoryFilter" onchange="applyFilters()">
                  <option value="all">All Categories</option>
                  <option value="technical issues">Technical Issues</option>
                  <option value="billing">Billing</option>
                  <option value="user experience">User Experience</option>
                  <option value="features">Features</option>
                  <option value="performance">Performance</option>
                  <option value="customer support">Customer Support</option>
                </select>
              </div>

              <div class="filter-group">
                <label class="filter-label">Provider</label>
                <select class="filter-select" id="appFilter" onchange="applyFilters()">
                  <option value="all">All Providers</option>
                  <option value="rogers">Rogers</option>
                  <option value="bell">Bell</option>
                </select>
              </div>

              <div class="filter-group">
                <label class="filter-label">Platform</label>
                <select class="filter-select" id="platformFilter" onchange="applyFilters()">
                  <option value="all">All Platforms</option>
                  <option value="android">Android</option>
                  <option value="ios">iOS</option>
                </select>
              </div>
              
              <div class="filter-group">
                <label class="filter-label">Search Reviews</label>
                <input
                  type="text"
                  class="filter-input"
                  id="searchFilter"
                  placeholder="Enter keywords..."
                  onkeyup="applyFilters()"
                />
              </div>
            </div>

            <!-- Filter Status -->
            <div id="filterStatus" style="margin-bottom: 1rem; color: var(--ey-gray-dark); font-size: 0.9rem;"></div>
            
            <!-- Result Count -->
            <div id="resultCount" style="margin: 1rem 0; color: var(--ey-gray-dark); font-size: 0.9rem; font-weight: 500;">
              Loading reviews...
            </div>

            <!-- Reviews Table -->
            <div class="table-container">
              <table class="reviews-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Provider</th>
                    <th>Platform</th>
                    <th>Rating</th>
                    <th>Review</th>
                    <th>Sentiment</th>
                    <th>Category</th>
                  </tr>
                </thead>
                <tbody id="reviewsTableBody">
                  <tr>
                    <td colspan="7" style="text-align: center; padding: 2rem;">
                      Loading reviews...
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
    '''
    
    # Check if Reviews tab exists and is properly structured
    if 'id="analysis"' not in content or 'id="searchFilter"' not in content:
        # Replace or add the complete Reviews tab
        analysis_tab_pattern = r'<div id="analysis" class="tab-content">.*?</div>\s*</div>'
        
        if re.search(analysis_tab_pattern, content, re.DOTALL):
            content = re.sub(analysis_tab_pattern, reviews_tab_structure.strip(), content, flags=re.DOTALL)
            fixes_made += 1
            print(f"✅ Replaced incomplete Reviews tab with complete structure")
        else:
            # Insert before the Strategic Report tab if Reviews tab is missing
            report_tab_pattern = r'(<div id="report" class="tab-content">)'
            if re.search(report_tab_pattern, content):
                content = re.sub(report_tab_pattern, reviews_tab_structure + '\n\n        ' + r'\1', content)
                fixes_made += 1
                print(f"✅ Added complete Reviews tab structure")
    
    # Fix 4: Update populateDataTable function to handle null elements
    populate_data_table_fix = '''
      function populateDataTable(reviews) {
        const tbody = document.getElementById("reviewsTableBody");
        if (!tbody) {
          console.error("Reviews table body not found");
          return;
        }
        
        if (!reviews || reviews.length === 0) {
          tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 2rem;">No reviews found</td></tr>';
          return;
        }

        const rows = reviews.slice(0, 100).map(review => {
          const date = review.date || 'N/A';
          const provider = review.app_name || review.app || 'N/A';
          const platform = review.platform || 'N/A';
          const rating = review.rating || 'N/A';
          const reviewText = (review.review || review.text || '').substring(0, 200) + '...';
          const sentiment = review.claude_sentiment || review.sentiment || 'N/A';
          const category = review.primary_category || review.category || 'N/A';
          
          return `
            <tr>
              <td>${date}</td>
              <td>${provider}</td>
              <td>${platform}</td>
              <td>${rating}</td>
              <td style="max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${reviewText}</td>
              <td>${sentiment}</td>
              <td>${category}</td>
            </tr>
          `;
        }).join('');
        
        tbody.innerHTML = rows;
      }
    '''
    
    # Replace populateDataTable function if it exists
    populate_pattern = r'function populateDataTable\([^}]+\{[^}]+\}'
    if re.search(populate_pattern, content, re.DOTALL):
        # Find the complete function including nested braces
        start_pos = content.find('function populateDataTable(')
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
                content = content[:start_pos] + populate_data_table_fix.strip() + content[end_pos:]
                fixes_made += 1
                print(f"✅ Fixed populateDataTable function with null checks")
    
    # Write back if changes were made
    if content != original_content:
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n📝 Saved {fixes_made} JavaScript fixes")
    else:
        print(f"\n⚪ No JavaScript fixes needed")
    
    return fixes_made

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis')
    
    fixes = fix_dashboard_javascript_errors()
    print(f"\nJavaScript fixes applied: {fixes}")