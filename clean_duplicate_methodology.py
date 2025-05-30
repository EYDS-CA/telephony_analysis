#!/usr/bin/env python3

import re
import os

def clean_duplicate_methodology_cards():
    """Remove duplicate methodology cards and clean up navigation"""
    
    print("=== CLEANING DUPLICATE METHODOLOGY CARDS ===\n")
    
    dashboard_file = 'html_dashboard/dashboard.html'
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Find and remove the second methodology card (keep the first one)
    # Pattern to match the entire second methodology card
    second_card_pattern = r'(<div class="card" style="display: flex; flex-direction: column">\s*<div class="card-header">\s*<div>\s*<h3 class="card-title">Research Methodology</h3>\s*<p class="card-subtitle">\s*Data collection, AI analysis methodology, and validation[^}]*?</div>\s*</div>\s*</div>)'
    
    matches = re.findall(second_card_pattern, content, re.DOTALL)
    
    if len(matches) > 1:
        # Remove all but the first occurrence
        for i in range(1, len(matches)):
            content = content.replace(matches[i], '', 1)
        print(f"✅ Removed {len(matches) - 1} duplicate methodology cards")
    
    # Update the grid to single column if only one card remains
    if 'grid grid-2' in content and len(matches) <= 1:
        content = content.replace('grid grid-2', 'grid grid-1')
        print(f"✅ Updated grid layout for single methodology card")
    
    # Make sure there's only one methodology card with updated content
    methodology_card_updated = '''
                <div class="card" style="display: flex; flex-direction: column">
                  <div class="card-header">
                    <div>
                      <h3 class="card-title">Research Methodology</h3>
                      <p class="card-subtitle">
                        Comprehensive data collection, AI analysis, and validation approach
                      </p>
                    </div>
                  </div>
                  <div
                    style="
                      padding: 1.5rem;
                      display: flex;
                      flex-direction: column;
                      height: 100%;
                    "
                  >
                    <p style="margin-bottom: 1.5rem; flex: 1">
                      Complete methodology covering extraction of 30,000+ reviews, 
                      AI-powered analysis of 10,103 filtered reviews, cross-validation 
                      with 15,913 CCTS complaints, and statistical verification of all key metrics.
                    </p>
                    <div style="margin-top: auto">
                      <a
                        href="research_methodology.html"
                        style="
                          display: inline-block;
                          background: var(--ey-blue);
                          color: white;
                          border: none;
                          padding: 0.75rem 1.5rem;
                          border-radius: 4px;
                          font-weight: 600;
                          text-decoration: none;
                          transition: background 0.2s;
                        "
                        >View Complete Methodology</a
                      >
                    </div>
                  </div>
                </div>
    '''
    
    # Replace any remaining methodology card with the updated version
    methodology_card_pattern = r'<div class="card"[^>]*>.*?<h3 class="card-title">Research Methodology</h3>.*?</div>\s*</div>\s*</div>'
    
    if re.search(methodology_card_pattern, content, re.DOTALL):
        content = re.sub(methodology_card_pattern, methodology_card_updated.strip(), content, flags=re.DOTALL, count=1)
        print(f"✅ Updated methodology card content")
    
    # Remove any leftover empty methodology tab content
    empty_methodology_patterns = [
        r'<!-- Research Methodology Tab -->\s*</div>',
        r'<div id="methodology" class="tab-content">\s*</div>',
    ]
    
    for pattern in empty_methodology_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, '', content)
            print(f"✅ Cleaned up empty methodology tab remnants")
    
    # Write back if changes were made
    if content != original_content:
        with open(dashboard_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n📝 Saved cleanup changes to dashboard")
    else:
        print(f"\n⚪ No cleanup needed")
    
    return len(content) != len(original_content)

def add_result_count_to_reviews():
    """Add result count display to Reviews tab if not present"""
    
    dashboard_file = 'html_dashboard/dashboard.html'
    
    with open(dashboard_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add result count display after filter status if not present
    if 'resultCount' not in content:
        result_count_html = '''
          <div id="resultCount" style="margin: 1rem 0; color: var(--ey-gray-dark); font-size: 0.9rem; font-weight: 500;">
            Loading reviews...
          </div>
        '''
        
        # Find the filter status div and add result count after it
        filter_status_pattern = r'(<div id="filterStatus"[^>]*></div>)'
        if re.search(filter_status_pattern, content):
            content = re.sub(filter_status_pattern, r'\1' + result_count_html, content)
            
            with open(dashboard_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Added result count display to Reviews tab")
            return True
    
    return False

if __name__ == "__main__":
    os.chdir('/Users/amirshayegh/Developer/temp/review_analysis')
    
    cleaned = clean_duplicate_methodology_cards()
    result_count_added = add_result_count_to_reviews()
    
    print(f"\n=== CLEANUP SUMMARY ===")
    print(f"Methodology duplicates cleaned: {cleaned}")
    print(f"Result count added: {result_count_added}")