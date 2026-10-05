# Analysis of Tutoring Class Effect on Student Score Gains

## Research Question
For the students who attended the tutoring class, did attending the tutoring class increase their score gain? If so, by how much?

## Answer
**YES: Attending the tutoring class increased score gains by approximately 1.16 points (statistically significant, p < 0.001).**

## Key Findings

### Sample Composition
- Total students: 2,000
- Students who attended tutoring: 600
- Students who did not attend: 1,400

### Descriptive Statistics
Students who attended tutoring had:
- Mean start-of-term score: 67.07 (SD: 4.92)
- Mean score gain: 13.02 points (SD: 3.78)

Students who did not attend tutoring had:
- Mean start-of-term score: 56.86 (SD: 8.12)
- Mean score gain: 9.39 points (SD: 4.06)

### Statistical Analysis

#### Unadjusted Comparison
The simple difference in mean score gains was 3.63 points (13.02 − 9.39), with a highly significant p-value (p < 0.001). However, this comparison is misleading because of **confounding**.

#### Confounding Issue
The selection process created a confound: students selected for tutoring had substantially higher start-of-term scores (mean difference: 10.21 points). Because there is a positive correlation between start-of-term scores and score gains (r = 0.55), the tutored students would naturally have larger gains even without the tutoring class. This confounding artificially inflates the estimated tutoring effect.

#### Adjusted Analysis (Regression)
To account for confounding, I used multiple regression analysis: 
```
Score gain = −4.35 + 1.16 × (attended tutoring) + 0.24 × (start-of-term score)
```

**Adjusted tutoring effect: 1.16 points** (standard error: 0.21, t-statistic: 5.61, p < 0.001)

This estimate is smaller than the unadjusted difference because it accounts for the students' baseline ability (start-of-term scores). The start-of-term score coefficient of 0.24 indicates that students gain approximately 0.24 additional points for each point higher their initial score was.

### Model Fit
- Unadjusted model R²: 0.149
- Adjusted model R²: 0.316

The adjusted model explains substantially more variance, confirming that the start-of-term score is an important predictor of score gains.

## Conclusion
The data provide clear evidence that attending the tutoring class resulted in an increase in score gains of approximately **1.16 points**. This effect remained highly statistically significant after accounting for differences in students' baseline abilities (start-of-term scores). The study design using random components in the assignment process, combined with the adjustment for baseline ability, provides reasonable grounds for inferring that this difference represents the causal effect of the tutoring class.
