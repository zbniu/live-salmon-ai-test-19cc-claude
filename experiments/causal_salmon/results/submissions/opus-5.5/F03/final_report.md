# Final report: effect of the tutoring class on score gain `z`

## Answer

**Yes. For the students who attended, the tutoring class increased the score gain `z` by about 1.2 points (0–100 scale).**

**Adopted result (answers the research question):** average effect on the treated (ATT) = **+1.21 points**, 95% CI **[0.85, 1.58]**
(regression-adjusted difference in means, Lin interacted estimator with baseline score `y` centred at the attenders' mean, HC2 robust SE 0.184; randomization test p < 0.001).

The effect is modest: roughly a quarter of a standard deviation of `z` (SD ≈ 4.4), against an average control-group gain of about 10.0 points.

## Why this is identified

Per the study description, 600 of 2000 students were selected by a simple random draw using no student information, with full compliance, no switching, no interference, identical measurement, blinded end-of-term scoring, and no missing data. The non-attenders are therefore a valid comparison group for the attenders, and the difference in mean `z` estimates the effect for the attenders. Because `y` was measured before assignment, an effect on the gain `z` is the same as an effect on the end-of-term score.

## Data checks (results/01_inspect.txt)

2000 rows, 600 attenders and 1400 non-attenders, no missing values or duplicates. `y` ranges 45.0–75.0; `z` ranges −0.4 to 22.9; all implied end-of-term scores (y+z) lie within 0–100. Baseline `y` is balanced: attenders 59.85 vs non-attenders 60.28 (difference −0.42, p = 0.31; SMD −0.05).

## Estimates (results/02_analysis.txt)

| Method | Estimate | 95% CI |
|---|---|---|
| Unadjusted difference in means (Neyman SE) | 1.110 | [0.686, 1.535] |
| ANCOVA z ~ x + y (HC2) | 1.219 | [0.858, 1.580] |
| **Lin interacted, y centred at attenders' mean (ATT) — adopted** | **1.214** | **[0.854, 1.575]** |
| Same, bootstrap (5000, stratified) | 1.214 | [0.862, 1.578] |
| Lin interacted, y centred at full sample (ATE) | 1.226 | [0.865, 1.587] |

Randomization inference (10,000 re-draws of 600 of 2000): p ≈ 0.0001 (the smallest attainable value) for both the unadjusted and the ANCOVA estimate.

Adjustment for `y` is preferred because `z` rises with baseline score (slope ≈ 0.25 per point, R² ≈ 0.25 within arms), so it removes noise (SE 0.217 → 0.184) and corrects for the chance imbalance in which attenders started 0.42 points lower. The unadjusted estimate (1.11) is the design-based benchmark and leads to the same conclusion.

## Heterogeneity and robustness

The effect appears in every quintile of baseline score (0.57 to 2.17 points, each with SE ≈ 0.4) and across the distribution of `z` (quantile differences 0.9–1.6; median difference 1.09). There is weak, non-significant evidence that the effect is larger for students with higher baseline scores (interaction 0.038 per point, p = 0.075), so the conclusion is about the average effect for attenders, not a claim that every attender gained the same amount.

## Limitations

This is a single randomized comparison; the confidence interval reflects sampling and assignment uncertainty only. The data say nothing about why the class worked or whether the effect would persist or generalise beyond these 2000 students.
