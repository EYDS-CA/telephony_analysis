#!/usr/bin/env python3

import re
import os

def add_complete_reviews_tab():
    """Add complete Reviews tab with search functionality"""
    
    print("=== ADDING COMPLETE REVIEWS TAB ===\n")
    
    dashboard_file = 'html_dashboard/dashboard.html'
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Complete Reviews tab HTML
    reviews_tab_html = '''
        <!-- Reviews Analysis Tab -->
        <div id="analysis" class="tab-content">
          <div class="container" style="max-width: 1200px">
            <h2 style="margin-bottom: 2rem">Reviews Analysis</h2>

            <!-- Filters -->
            <div class="filters-container" style="margin-bottom: 2rem; display: flex; gap: 1rem; flex-wrap: wrap;">
              <div class="filter-group" style="display: flex; flex-direction: column; min-width: 150px;">
                <label class="filter-label" style="margin-bottom: 0.5rem; font-weight: 500; color: var(--ey-gray-dark);">Category</label>
                <select class="filter-select" id="categoryFilter" onchange="applyFilters()" style="padding: 0.5rem; border: 1px solid var(--ey-gray-medium); border-radius: 4px;">
                  <option value="all">All Categories</option>
                  <option value="technical issues">Technical Issues</option>
                  <option value="billing">Billing</option>
                  <option value="user experience">User Experience</option>
                  <option value="features">Features</option>
                  <option value="performance">Performance</option>
                  <option value="customer support">Customer Support</option>
                </select>
              </div>

              <div class="filter-group" style="display: flex; flex-direction: column; min-width: 150px;">
                <label class="filter-label" style="margin-bottom: 0.5rem; font-weight: 500; color: var(--ey-gray-dark);">Provider</label>
                <select class="filter-select" id="appFilter" onchange="applyFilters()" style="padding: 0.5rem; border: 1px solid var(--ey-gray-medium); border-radius: 4px;">
                  <option value="all">All Providers</option>
                  <option value="rogers">Rogers</option>
                  <option value="bell">Bell</option>
                </select>
              </div>

              <div class="filter-group" style="display: flex; flex-direction: column; min-width: 150px;">
                <label class="filter-label" style="margin-bottom: 0.5rem; font-weight: 500; color: var(--ey-gray-dark);">Platform</label>
                <select class="filter-select" id="platformFilter" onchange="applyFilters()" style="padding: 0.5rem; border: 1px solid var(--ey-gray-medium); border-radius: 4px;">
                  <option value="all">All Platforms</option>
                  <option value="android">Android</option>
                  <option value="ios">iOS</option>
                </select>
              </div>
              
              <div class="filter-group" style="display: flex; flex-direction: column; min-width: 200px; flex: 1;">
                <label class="filter-label" style="margin-bottom: 0.5rem; font-weight: 500; color: var(--ey-gray-dark);">Search Reviews</label>
                <input
                  type="text"
                  class="filter-input"
                  id="searchFilter"
                  placeholder="Enter keywords..."
                  onkeyup="applyFilters()"
                  style="padding: 0.5rem; border: 1px solid var(--ey-gray-medium); border-radius: 4px; font-size: 0.9rem;"
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
            <div class="table-container" style="background: white; border-radius: 8px; box-shadow: var(--shadow-sm); overflow: hidden;">
              <table class="reviews-table" style="width: 100%; border-collapse: collapse;">
                <thead style="background: var(--ey-gray-light);">
                  <tr>
                    <th style="padding: 1rem; text-align: left; font-weight: 600; border-bottom: 1px solid var(--ey-gray-medium);">Date</th>
                    <th style="padding: 1rem; text-align: left; font-weight: 600; border-bottom: 1px solid var(--ey-gray-medium);">Provider</th>
                    <th style="padding: 1rem; text-align: left; font-weight: 600; border-bottom: 1px solid var(--ey-gray-medium);">Platform</th>
                    <th style="padding: 1rem; text-align: left; font-weight: 600; border-bottom: 1px solid var(--ey-gray-medium);">Rating</th>
                    <th style="padding: 1rem; text-align: left; font-weight: 600; border-bottom: 1px solid var(--ey-gray-medium); max-width: 400px;">Review</th>
                    <th style="padding: 1rem; text-align: left; font-weight: 600; border-bottom: 1px solid var(--ey-gray-medium);">Sentiment</th>
                    <th style="padding: 1rem; text-align: left; font-weight: 600; border-bottom: 1px solid var(--ey-gray-medium);">Category</th>
                  </tr>
                </thead>
                <tbody id="reviewsTableBody">
                  <tr>
                    <td colspan="7" style="text-align: center; padding: 2rem; color: var(--ey-gray-dark);">
                      Loading reviews...
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
    '''
    
    # Check if Reviews tab already exists
    if '<div id="analysis" class="tab-content">' in content:
        # Replace existing incomplete tab
        analysis_tab_pattern = r'<div id="analysis" class="tab-content">.*?</div>\s*</div>'
        
        if re.search(analysis_tab_pattern, content, re.DOTALL):
            content = re.sub(analysis_tab_pattern, reviews_tab_html.strip(), content, flags=re.DOTALL)
            print("✅ Replaced existing incomplete Reviews tab")
        else:
            print("⚠️  Found analysis tab but couldn't match pattern for replacement")
    else:
        # Add new tab before Strategic Report tab
        report_tab_pattern = r'(\s*<!-- Strategic Report Tab -->|<div id="report" class="tab-content">)'
        
        if re.search(report_tab_pattern, content):
            content = re.sub(report_tab_pattern, reviews_tab_html + '\n\n        ' + r'\1', content)
            print("✅ Added new complete Reviews tab")
        else:
            print("❌ Could not find insertion point for Reviews tab")
            return False
    
    # Write back the updated content
    with open(dashboard_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("📝 Saved updated dashboard with complete Reviews tab")
    return True

def verify_search_components():
    """Verify that all search components are now present"""
    
    dashboard_file = 'html_dashboard/dashboard.html'
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    components = [
        ('Search input field', r'id="searchFilter"'),
        ('Search event handler', r'onkeyup="applyFilters\(\)"'),
        ('Category filter', r'id="categoryFilter"'),
        ('Provider filter', r'id="appFilter"'),
        ('Platform filter', r'id="platformFilter"'),
        ('Reviews table', r'id="reviewsTableBody"'),
        ('Filter status', r'id="filterStatus"'),
        ('Result count', r'id="resultCount"'),
        ('ApplyFilters function', r'function applyFilters\(\)'),
    ]
    
    print("\n=== VERIFYING SEARCH COMPONENTS ===")
    
    all_present = True
    for component_name, pattern in components:
        if re.search(pattern, content):
            print(f"✅ {component_name}: Found")
        else:
            print(f"❌ {component_name}: Missing")
            all_present = False
    
    return all_present

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis')
    
    added = add_complete_reviews_tab()
    verified = verify_search_components()
    
    print(f"\n=== SUMMARY ===")
    print(f"Reviews tab added/updated: {added}")
    print(f"All components verified: {verified}")
    print(f"Status: {'✅ READY' if added and verified else '⚠️ NEEDS ATTENTION'}")