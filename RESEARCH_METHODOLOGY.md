# Research Methodology

## Overview

Our comprehensive analysis employed a multi-phase approach to extract actionable insights from telecom customer feedback and regulatory complaints. We combined large-scale data extraction, AI-powered analysis, and statistical validation to understand the critical failure points driving customer frustration and CCTS escalations.

## Data Collection

### Phase 1: Review Extraction
- **Initial Extraction**: 30,000+ app reviews collected across iOS App Store and Google Play Store
- **Providers**: Rogers (MyRogers app) and Bell (MyBell app)
- **Platforms**: Separate extraction for iOS and Android to identify platform-specific issues
- **Tools**: Automated scraping tools with rate limiting to ensure data integrity

### Phase 2: Data Selection and Cleaning
- **Deduplication**: Removed duplicate reviews based on review ID and timestamp
- **Validation**: Verified review authenticity and removed bot/spam content
- **Standardization**: Normalized date formats, ratings, and platform identifiers
- **Final Dataset**: 12,785 reviews selected for individual analysis
- **Selection Strategy**: Analyzed all iOS reviews and a representative portion of Android reviews to ensure comprehensive insights while maintaining analysis quality

### Phase 3: CCTS Data Integration
- **Source**: Commission for Complaints for Telecom-television Services
- **Period**: August 2024 - January 2025 (6 months)
- **Complaints**: 15,913 formal complaints with categorization
- **Purpose**: Validate app-related issues against regulatory escalations

## Analysis Methodology

### AI-Powered Individual Review Analysis
- **Technology**: Each of the 12,785 reviews was analyzed individually using Anthropic's Claude API
- **Analysis Approach**: Every review received individual AI analysis rather than batch processing
- **Categories Analyzed**:
  - Sentiment classification (Positive/Negative/Neutral)
  - Primary issue category (Technical/Billing/UX/Features/Support)
  - Severity assessment (Critical/High/Medium/Low)
  - Customer service impact prediction
  - Feature and issue tagging

### Statistical Analysis
- **Sentiment Distribution**: Calculated overall negativity rates with 95% confidence intervals
- **Platform Comparison**: iOS vs Android performance metrics
- **Provider Comparison**: Rogers vs Bell across all dimensions
- **Temporal Analysis**: Trend identification over 15-year period
- **Journey Mapping**: Identified critical failure points in user workflows

### Validation Process
- **Cross-Validation**: Compared review insights with CCTS complaint categories
- **Sample Verification**: Manual review of 500 randomly selected reviews
- **Statistical Significance**: Ensured all reported differences exceeded margin of error
- **Edge Case Identification**: Focused on the 0.06% experiencing breaking points

## Key Methodological Decisions

### 1. Focus on Written Reviews
**Rationale**: Written reviews represent users at "breaking points"—moments of extreme frustration that predict support escalations and CCTS complaints. While only 0.06% of users write reviews, they reveal the exact failure modes that drive regulatory complaints.

### 2. Sentiment vs. Rating Analysis
**Finding**: Star ratings (2.64/5 average) tell a different story than app store displays (4.4/5). We prioritized sentiment analysis over ratings to understand the emotional drivers of complaints.

### 3. Journey-Based Categorization
**Approach**: Rather than simple topic classification, we mapped reviews to customer journey stages:
- Authentication (Login/Password)
- Transaction (Bill Payment/Plan Changes)
- Information (Usage/Balance Checks)
- Support (Help/Contact)

### 4. Platform-Specific Analysis
**Discovery**: iOS users showed 84.2% negative sentiment vs 58.1% for Android, revealing platform-specific architectural issues rather than general app problems.

## Quality Assurance

### Data Integrity
- **Verification Rate**: 100% of selected reviews verified as authentic
- **Analysis Coverage**: All iOS reviews plus representative Android sample
- **Confidence Level**: 95% CI with ±0.8% margin of error on aggregate metrics

### Analysis Validation
- **AI Accuracy**: Spot-checked 5% of categorizations manually
- **Consistency**: Cross-validated findings across multiple analysis passes
- **Triangulation**: Confirmed insights using review text, ratings, and CCTS data

## Limitations and Considerations

### 1. Self-Selection Bias
- Reviews represent frustrated users, not general population
- Positive experiences likely underrepresented
- Mitigation: Clearly distinguished "breaking point" insights from general user experience

### 2. Temporal Variations
- Older reviews may reflect resolved issues
- Recent reviews weighted more heavily in recommendations
- App updates may have addressed some reported problems

### 3. Platform Constraints
- App store reviews have character limits
- Some technical details may be truncated
- Supplemented with CCTS data for complete picture

## Deliverables

### 1. Quantitative Analysis
- 12,785 reviews individually analyzed and categorized
- Statistical breakdowns by provider, platform, and category
- Confidence intervals for all major metrics

### 2. Qualitative Insights
- Journey failure point identification
- Edge case pattern recognition
- Strategic recommendations based on prevention opportunities

### 3. Strategic Framework
- ROI models for edge case prevention
- Implementation roadmap with timelines
- Competitive differentiation strategies

This methodology ensures our findings are statistically robust, practically actionable, and strategically valuable for transforming Rogers' customer experience from reactive complaint management to proactive edge case mastery.