# Data Methodology and Number Derivations

## How We Calculated Every Key Metric

### 1. The 0.06% Review Rate

**Claim**: "0.06% of users write reviews"

**Derivation**:
```
We DON'T have the actual calculation because we lack total user base numbers.
This is an ESTIMATE that needs citation or should be marked as (E).

What we DO know:
- Rogers: 9,038 reviews collected over multiple years
- Bell: 3,747 reviews collected over multiple years
- Industry benchmarks suggest 0.01-0.1% of app users write reviews

The 0.06% is the midpoint of our claimed rates:
- Rogers: 0.079% (needs verification)
- Bell: 0.037% (needs verification)
- Average: (0.079% + 0.037%) / 2 = 0.058% ≈ 0.06%

STATUS: NEEDS CITATION OR USER BASE DATA
```

### 2. The 99.94% Silent Majority

**Claim**: "99.94% are the silent majority"

**Derivation**:
```
Simple calculation: 100% - 0.06% = 99.94%

This assumes the 0.06% review rate is accurate.
STATUS: DEPENDENT ON REVIEW RATE VERIFICATION
```

### 3. Review Sentiment Analysis

**Claim**: "60% negative sentiment"

**Derivation**:
```python
Total reviews analyzed: 12,785
Negative sentiment reviews: 7,669
Calculation: 7,669 / 12,785 = 0.5996 = 60.0%

95% Confidence Interval: ±0.8%
Formula: 1.96 * sqrt(p(1-p)/n) = 1.96 * sqrt(0.6*0.4/12785) = 0.0085 = 0.8%

STATUS: VERIFIED FROM DATA
```

### 4. Login Success Rate (7.7%)

**Claim**: "Only 7.7% positive login experiences"

**Derivation**:
```python
Reviews mentioning login: 1,290
Positive sentiment login reviews: 99
Calculation: 99 / 1,290 = 0.0767 = 7.7%

Note: This is among reviews that mention login, NOT all users
STATUS: VERIFIED FROM DATA
```

**Actual verification from our data shows**:
```
Login mentions: 1,290
Negative login reviews: 1,191 (92.3%)
Positive login reviews: 99 (7.7%)
```

### 5. Payment Success Rate (25.7%)

**Claim**: "Only 25.7% positive payment experiences"

**Derivation**:
```python
Reviews mentioning bill/payment: 2,084
Positive sentiment payment reviews: 536
Calculation: 536 / 2,084 = 0.2572 = 25.7%

STATUS: VERIFIED FROM DATA
```

### 6. Platform-Specific Negativity

**Claim**: "iOS 84.2% negative, Android 58.1% negative"

**Derivation**:
```python
iOS reviews: 4,028
iOS negative: 3,392
iOS negative rate: 3,392 / 4,028 = 0.8421 = 84.2%

Android reviews: 8,757
Android negative: 5,089
Android negative rate: 5,089 / 8,757 = 0.5811 = 58.1%

STATUS: VERIFIED FROM DATA
```

### 7. Average Rating (2.64/5)

**Claim**: "Reviews average 2.64/5 stars"

**Derivation**:
```python
Sum of all ratings: 33,733
Number of reviews: 12,785
Average: 33,733 / 12,785 = 2.638 = 2.64

STATUS: VERIFIED FROM DATA
```

### 8. CCTS Complaint Counts

**Claim**: "15,913 CCTS complaints"

**Derivation**:
```
Direct count from CCTS data file
Time period: Aug 2024 - Jan 2025 (6 months)

Breakdown:
- Billing: 6,752 (42.4%)
- Service Delivery: 3,707 (23.3%)
- Contract Dispute: 4,756 (29.9%)
- Credit Management: 698 (4.4%)

STATUS: VERIFIED FROM DATA
```

### 9. The 32,000 Annual CCTS Complaints

**Claim**: "32,000 annual CCTS complaints industry-wide"

**Derivation**:
```
This is NOT from our data.
Our data shows 15,913 in 6 months for specific providers.
The 32,000 figure would need to be:
- Extrapolated (15,913 × 2 = 31,826 ≈ 32,000) OR
- Cited from CCTS annual report

STATUS: NEEDS CITATION
```

### 10. Channel Switching (12%)

**Claim**: "12% mention needing human help"

**Derivation**:
```python
Rogers reviews mentioning support: 1,074
Rogers total reviews: 9,038
Rogers rate: 1,074 / 9,038 = 0.1188 = 11.9%

Bell reviews mentioning support: 451
Bell total reviews: 3,747
Bell rate: 451 / 3,747 = 0.1203 = 12.0%

Average: ≈12%
STATUS: VERIFIED FROM DATA
```

### 11. Chatbot Mentions

**Claim**: "Bell 4 mentions, Rogers 33 mentions"

**Derivation**:
```python
Search terms: 'chatbot|chat bot|virtual assistant|Anna|ROGie'
Bell matches: 4
Rogers matches: 33

Bell percentage: 4 / 3,747 = 0.11%
Rogers percentage: 33 / 9,038 = 0.37%

STATUS: VERIFIED FROM DATA
```

### 12. CCTS Complaint Costs

**Claim**: "$2,500-6,500 per complaint"

**Derivation**:
```
NOT from our data.
This is an industry estimate that needs citation.
Possible sources: CCTS reports, industry studies, telecom financial reports

STATUS: NEEDS CITATION
```

### 13. Support Cost Reduction (30-60%)

**Claim**: "30-60% support cost reduction possible"

**Derivation**:
```
NOT from our data.
Referenced from case studies:
- DBX Bank: 30% reduction
- Magicpin: 60% ticket deflection
- Need specific citations for these cases

STATUS: NEEDS CITATIONS
```

### 14. ROI Calculations (125-430%)

**Claim**: "ROI ranges from 125-430%"

**Derivation**:
```
Conservative: 
- Prevention: 1,000 complaints × $2,500 = $2.5M
- Investment: $2M
- ROI: ($2.5M - $2M) / $2M = 125%

Aggressive:
- Prevention: 2,000 complaints × $6,500 = $13M
- Investment: $3M  
- ROI: ($13M - $3M) / $3M = 333%

Note: These assume the $2,500-6,500 costs are accurate
STATUS: CALCULATION BASED ON UNVERIFIED COSTS
```

## Summary of Data Sources

### Verified from Our Data ✓
- Total review counts and breakdown
- Sentiment analysis percentages
- Login/payment success rates
- Platform-specific metrics
- Average ratings
- CCTS complaint categories
- Channel switching rates
- Chatbot mention counts

### Needs External Verification ⚠️
- 0.06% review generation rate (need user base)
- $2,500-6,500 CCTS complaint costs
- 32,000 annual industry CCTS complaints
- 30-60% support reduction benchmarks
- App Store ratings of 4.4/5

### Calculated/Derived 🧮
- 99.94% silent majority (100% - 0.06%)
- ROI projections (based on cost assumptions)
- Breaking point interpretations

## Recommendations for Report Accuracy

1. **Add footnotes** for all unverified claims
2. **Mark estimates** with (E) notation
3. **Include this methodology** as an appendix
4. **Request client data** for:
   - Total app user base
   - Actual support costs
   - Historical CCTS complaint costs
5. **Add confidence levels** to projections