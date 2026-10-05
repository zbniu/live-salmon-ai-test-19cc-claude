# Did the tutoring class increase score gain `z`? — Final report

## Answer
**Yes. Among the 600 students who attended the tutoring class, attending raised their score gain by about 1.0 point on the 0–100 scale** (adopted estimate: **+1.01 points, 95% CI ≈ 0.65 to 1.37**; regression-adjusted effect on the treated, bootstrap CI). The evidence that the effect is positive is strong (p < 0.001 in every analysis).

## Basis for causal interpretation
Per the study description, 600 of 2000 students were chosen by a uniform random draw using no student information, all chosen students attended and nobody else did, no switching, no interference between students, identical measurement, blinded end-of-term scoring, and no missing data. The comparison of attendees with non-attendees therefore estimates a causal effect, and for a randomized assignment the effect on attendees equals (in expectation) the average effect over all students.

## Data checks
2000 rows, 3 columns, no missing values. x=1: 600, x=0: 1400. Mean start score `y`: 59.16 (treated) vs 59.91 (control); difference −0.75, p = 0.08 (KS p = 0.13). This is consistent with chance imbalance under randomization, but it matters because `y` is a strong predictor of `z` (slope ≈ 0.22 gain points per start-score point, control arm).

## Results (outcome `z`)
| Analysis | Estimate | 95% CI |
|---|---|---|
| Raw difference in means (10.76 − 9.91) | 0.848 | 0.428, 1.268 (Welch t p = 8e-5; permutation p < 1e-4; Mann–Whitney p = 1e-4) |
| OLS z ~ x + y | 1.023 | 0.659, 1.387 |
| Lin-adjusted ATE (x, centered y, interaction) | 1.036 | 0.671, 1.400 |
| **Regression-adjusted effect on the treated (adopted)** | **1.014** | **0.651, 1.370** |

**Why the adjusted figure is adopted:** `y` was measured before assignment, so adjusting for it cannot introduce bias in a randomized design. It removes the small chance imbalance in `y` (treated students started slightly lower and so would be expected to gain slightly less) and reduces residual SD of `z` from 4.25 to 3.71, giving tighter intervals. The raw difference (0.85) is also valid and unbiased on average, but in this particular sample it is pulled down by the imbalance. The two are statistically compatible; the substantive conclusion (a gain of roughly 1 point) is the same.

## Heterogeneity (secondary, exploratory)
The effect is positive in every start-score quintile, from 0.32 (lowest quintile, CI −0.47 to 1.10) to ≈1.3–1.4 in the top two quintiles. The linear x×y interaction is 0.041 per point (p = 0.048), borderline; cubic interaction terms are null (all p > 0.38). This is weak evidence that the benefit may be larger for higher starters, not a firm finding, and it was not a pre-specified question. The treated group's `z` is also somewhat more variable (SD 4.50 vs 4.11; Levene p = 0.001), consistent with some variation in effect across students. Outcome distributions are roughly symmetric with no outliers, so mean-based inference is appropriate.

## Limitations
The study description does not say how `z` was generated, so the functional form of heterogeneity is not established. The estimate is for the supplied 2000 students and the single tutoring class described; it says nothing beyond that. The effect size (~1 point, about a quarter of the SD of `z`) is modest.
