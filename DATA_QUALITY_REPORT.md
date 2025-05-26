# Data Quality Report: Telecom App Reviews

## Summary of Data Quality Issues Fixed

### Original Raw Data Issues (telecom_app_reviews_raw.csv)
- **Total rows**: 34,245 (including header)
- **Corrupted app_name fields**: ~4,500 rows with dates, version numbers, or empty values
- **Invalid entries**: Many rows had extraction metadata in wrong columns
- **Duplicate reviews**: 319 exact duplicates found

### Cleaning Process Applied

1. **App Name Validation**
   - Validated app_name field must be "Rogers" or "Bell"
   - Attempted recovery from text content when app_name was corrupted
   - Removed rows where app provider couldn't be determined

2. **Platform Validation**
   - Ensured platform is either "Android" or "iOS"
   - Removed rows with invalid platform values

3. **Rating Validation**
   - Converted ratings to numeric (0-5 scale)
   - Removed rows with invalid rating values

4. **Duplicate Removal**
   - Removed 319 duplicate reviews based on text, author, and rating

5. **Date Parsing**
   - Standardized date formats
   - Maintained original timestamps where valid

### Cleaned Data Results (telecom_app_reviews_cleaned.csv)

**Total cleaned reviews**: 29,442

**Distribution by App**:
- Bell: 14,936 reviews (50.7%)
- Rogers: 14,506 reviews (49.3%)

**Distribution by Platform**:
- Android: 28,450 reviews (96.6%)
- iOS: 992 reviews (3.4%)

**Rating Distribution**:
- 5 stars: 8,129 (27.6%)
- 4 stars: 3,010 (10.2%)
- 3 stars: 2,179 (7.4%)
- 2 stars: 2,516 (8.5%)
- 1 star: 13,597 (46.2%)
- 0 stars: 11 (0.04%)

### Complaint Pattern Analysis

Using keywords: complaint, complain, ccts, escalat, regulatory, ombudsman, rip off, file a complaint

**Results**:
- Rogers: 87 complaints (0.6% of 14,506 reviews)
- Bell: 130 complaints (0.9% of 14,936 reviews)

### Comparison with LLM-Analyzed Dataset

**Our LLM-analyzed dataset (telecom_app_reviews_complete.csv)**:
- Total: 12,785 reviews (43% of cleaned raw data)
- Rogers: 9,038 (70.7%)
- Bell: 3,747 (29.3%)
- Complaint rates: Both at 2.2%

**Key Differences**:
1. **Dataset Size**: LLM analysis has fewer reviews, suggesting additional filtering/quality checks
2. **App Distribution**: Raw data is 50/50, but LLM data is 70/30 Rogers/Bell
3. **Complaint Detection**: LLM found 3-4x more complaints through semantic analysis
4. **Platform Split**: Raw shows 97% Android, LLM shows 93% Android

### Conclusions

1. **Data Quality**: Successfully cleaned 29,442 valid reviews from 34,245 raw entries
2. **Complaint Patterns**: Basic keyword search finds fewer complaints (0.6-0.9%) vs LLM semantic analysis (2.2%)
3. **Distribution Shift**: The LLM dataset appears to have additional filtering or selection criteria that resulted in:
   - Fewer total reviews
   - Higher proportion of Rogers reviews
   - Better complaint detection through understanding context

The cleaned raw data is now available in `telecom_app_reviews_cleaned.csv` for further analysis or comparison.