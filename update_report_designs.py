#!/usr/bin/env python3
"""
Update all report HTML files to use consistent EY dashboard design
"""

import os
import re
from pathlib import Path

# Template for the new report structure
REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | CX Insights Dashboard</title>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=EYInterstate:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    
    <!-- EY Report Styles -->
    <link href="{styles_path}ey-report-styles.css" rel="stylesheet">
</head>
<body>
    <!-- Professional Header -->
    <header class="header">
        <div class="header-top">
            <a href="{dashboard_path}dashboard.html" class="ey-logo">EY</a>
            <div class="header-meta">Digital & Emerging Technologies</div>
        </div>
        <div class="header-main">
            <h1 class="header-title">{header_title}</h1>
            <p class="header-subtitle">{header_subtitle}</p>
        </div>
    </header>

    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb">
        <a href="{dashboard_path}dashboard.html">Dashboard</a>
        <span>›</span>
        <a href="{dashboard_path}dashboard.html#reports">Reports</a>
        <span>›</span>
        <span>{breadcrumb_title}</span>
    </nav>

    <!-- Main Content -->
    <div class="report-container">
        <div class="report-section">
            <div class="report-header">
                <h1 class="report-title">{report_title}</h1>
                <p class="report-subtitle">{report_subtitle}</p>
            </div>
            
            <div class="report-content">
                {content}
            </div>
        </div>
    </div>

    <!-- Footer -->
    <footer class="footer">
        <nav class="footer-nav">
            <a href="{dashboard_path}dashboard.html">Dashboard</a>
            <a href="{dashboard_path}executive_summary.html">Executive Summary</a>
            <a href="{dashboard_path}rogers_cx_transformation_report.html">CX Transformation</a>
            <a href="{methodology_path}research_methodology_report.html">Methodology</a>
        </nav>
        <p>&copy; 2024 EY. All rights reserved.</p>
    </footer>

    <!-- Back to Dashboard Button -->
    <a href="{dashboard_path}dashboard.html" class="back-to-dashboard">
        <i class="fas fa-arrow-left"></i> Back to Dashboard
    </a>
</body>
</html>"""

# Report configurations
REPORTS = {
    'rogers_cx_transformation_report.html': {
        'title': 'Rogers CX Transformation Report',
        'header_title': 'Rogers CX Transformation',
        'header_subtitle': 'From Edge Case Mastery to Market Leadership',
        'breadcrumb_title': 'CX Transformation Report',
        'report_title': 'Rogers CX Transformation: From Edge Case Mastery to Market Leadership',
        'report_subtitle': 'Strategic roadmap for achieving market leadership through core reliability'
    },
    'executive_summary.html': {
        'title': 'Executive Summary',
        'header_title': 'Executive Summary',
        'header_subtitle': 'Rogers CX Transformation Analysis - Key Findings and Strategic Recommendations',
        'breadcrumb_title': 'Executive Summary',
        'report_title': 'Executive Summary: Rogers CX Transformation Analysis',
        'report_subtitle': 'From Edge Case Mastery to Market Leadership'
    },
    'cx_ux_assessment_report.html': {
        'title': 'CX/UX Assessment Report',
        'header_title': 'Customer Experience Assessment',
        'header_subtitle': 'Rogers vs Bell Mobile Applications',
        'breadcrumb_title': 'CX/UX Assessment',
        'report_title': 'Customer Experience Assessment: Rogers vs Bell Mobile Applications',
        'report_subtitle': 'Comprehensive analysis of mobile app failures and CX orchestration issues'
    },
    'data_methodology_report.html': {
        'title': 'Data Methodology Report',
        'header_title': 'Data Methodology & Derivations',
        'header_subtitle': 'How we calculated every metric',
        'breadcrumb_title': 'Data Methodology',
        'report_title': 'Data Methodology and Number Derivations',
        'report_subtitle': 'Detailed explanations of all calculations and statistical methods'
    },
    'research_methodology_report.html': {
        'title': 'Research Methodology',
        'header_title': 'Research Methodology',
        'header_subtitle': 'Comprehensive analysis approach',
        'breadcrumb_title': 'Research Methodology',
        'report_title': 'Research Methodology',
        'report_subtitle': 'How we analyzed 12,785 reviews to derive actionable insights'
    },
    'bell_smart_cx_report.html': {
        'title': "Bell's Smart CX Decisions",
        'header_title': "Bell's Smart CX Decisions",
        'header_subtitle': 'Visual analysis of Bell\'s UX advantage',
        'breadcrumb_title': 'Bell CX Analysis',
        'report_title': "Bell's Smart CX Decisions: Evidence from App Design",
        'report_subtitle': 'How Bell generates 8x fewer chatbot complaints through deliberate UX choices'
    }
}

def extract_content_from_html(html_content):
    """Extract the main content from existing HTML"""
    # Try to find content between common markers
    patterns = [
        r'<div class="content"[^>]*>(.*?)</div>\s*</body>',
        r'<main[^>]*>(.*?)</main>',
        r'<article[^>]*>(.*?)</article>',
        r'<div class="report-content"[^>]*>(.*?)</div>\s*</div>\s*</body>',
        r'<body[^>]*>(.*?)</body>'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
        if match:
            content = match.group(1)
            # Clean up the content
            content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
            content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)
            content = re.sub(r'<header[^>]*>.*?</header>', '', content, flags=re.DOTALL)
            content = re.sub(r'<nav[^>]*>.*?</nav>', '', content, flags=re.DOTALL)
            content = re.sub(r'<footer[^>]*>.*?</footer>', '', content, flags=re.DOTALL)
            return content.strip()
    
    return "<p>Content extraction failed. Please check the original file.</p>"

def update_report_file(file_path, config):
    """Update a single report file with new design"""
    try:
        # Read existing content
        with open(file_path, 'r', encoding='utf-8') as f:
            existing_html = f.read()
        
        # Extract content
        content = extract_content_from_html(existing_html)
        
        # Determine relative paths based on file location
        file_dir = os.path.dirname(file_path)
        if 'html_dashboard' in file_dir:
            styles_path = ''
            dashboard_path = ''
            methodology_path = '../'
        else:
            styles_path = 'html_dashboard/'
            dashboard_path = 'html_dashboard/'
            methodology_path = ''
        
        # Generate new HTML
        new_html = REPORT_TEMPLATE.format(
            title=config['title'],
            header_title=config['header_title'],
            header_subtitle=config['header_subtitle'],
            breadcrumb_title=config['breadcrumb_title'],
            report_title=config['report_title'],
            report_subtitle=config['report_subtitle'],
            content=content,
            styles_path=styles_path,
            dashboard_path=dashboard_path,
            methodology_path=methodology_path
        )
        
        # Save updated file
        output_path = file_path.replace('.html', '_updated.html')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        
        print(f"✅ Updated: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {str(e)}")
        return False

def main():
    """Update all report files"""
    base_dir = Path('/Users/amirshayegh/Developer/temp/review_analysis')
    
    print("🎨 Updating report designs to match dashboard...")
    print(f"📁 Base directory: {base_dir}")
    
    success_count = 0
    
    for filename, config in REPORTS.items():
        # Check multiple possible locations
        possible_paths = [
            base_dir / 'html_dashboard' / filename,
            base_dir / filename
        ]
        
        for path in possible_paths:
            if path.exists():
                print(f"\n📄 Processing: {filename}")
                if update_report_file(str(path), config):
                    success_count += 1
                break
        else:
            print(f"\n⚠️  Not found: {filename}")
    
    print(f"\n✨ Complete! Updated {success_count}/{len(REPORTS)} reports")
    print("\nNote: Updated files have '_updated.html' suffix. Review and rename as needed.")

if __name__ == "__main__":
    main()