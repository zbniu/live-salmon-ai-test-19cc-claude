# Analysis of Tutoring Class Effect on Score Gains

## Research Question
For the students who attended the tutoring class, did attending the tutoring class increase their score gain z? If so, by how much?

## Answer

**Yes, attending the tutoring class increased students' score gains.** The estimated effect size is **3.7 points** (on a 0–100 scale).

### Key Evidence

1. **Adjusted Treatment Effect**: 3.7132 points
   - Statistical significance: p < 0.000001
   - Standard error: 0.1957
   - This estimate controls for students' start-of-term test scores and thus accounts for the selection mechanism by which students were admitted to the tutoring class.

2. **Raw Difference**: For context, the unadjusted comparison showed students who attended tutoring gained 5.4 points more on average than those who did not. However, this raw difference is confounded because higher-scoring students at the start of the term were preferentially admitted to the tutoring class.

### Study Design and Selection Mechanism

The study used a selection procedure based on start-of-term test scores:
- Applications were ranked by start-of-term score plus other factors plus random variation
- The 900 highest-ranked applicants were selected
- Admitted students (600 of them) were chosen in descending order of start-of-term score until all 600 places were filled
- This created a systematic difference between the two groups

**Selection Bias in the Data:**
- Students who attended tutoring had a mean start-of-term score of 65.71
- Students who did not attend had a mean start-of-term score of 56.89
- Difference: 8.82 points

This difference in baseline ability is important because start-of-term test score is also predictive of score gain (each additional point on the start-of-term score is associated with 0.1918 additional points of score gain).

### Analytical Approach

Two regression models were fitted to the complete dataset (n = 2000):

**Model 1 (Unadjusted):** z = β₀ + β₁(x)
- Tutoring effect: 5.4051 points
- R² = 0.293

**Model 2 (Adjusted):** z = β₀ + β₁(x) + β₂(y)
- Tutoring effect: 3.7132 points
- Start-of-term score effect: 0.1918 points per point
- R² = 0.398

The adjusted model (Model 2) is more credible because it accounts for the selection mechanism documented in the study protocol. The inclusion of start-of-term test score reduces the tutoring effect estimate from 5.4 to 3.7 points, reflecting the removal of confounding bias.

### Robustness Checks

1. **Stratified Analysis**: Within each quartile of start-of-term scores, the tutoring effect remained consistent at approximately 3.7–3.9 points, consistent with the adjusted model estimate.

2. **Nonparametric Test**: A Mann-Whitney U test on unadjusted score gains confirmed that median gains differed significantly between groups (p < 0.000001).

3. **Model Fit**: The adjusted model explains 39.8% of the variance in score gain, a substantial improvement over the unadjusted model (29.3%), indicating that the inclusion of start-of-term score substantially improves model fit.

## Conclusion

**The tutoring class increased score gains by approximately 3.7 points.** This is a modest but statistically significant and consistent effect. Students who attended the tutoring class gained about 3.7 additional points on the 0–100 scale compared to what they would have gained based on their starting ability level alone.

The effect was estimated using regression adjustment for start-of-term test scores to remove selection bias created by the admission procedure. All robustness checks support this conclusion.
