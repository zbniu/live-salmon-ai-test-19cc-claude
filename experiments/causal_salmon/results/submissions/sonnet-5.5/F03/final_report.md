# Did the tutoring class increase score gain `z`?

## Answer
**Yes.** Attending the tutoring class increased the score gain by about **1.2 points** (0–100 scale) on average for the students who attended.

**Adopted result (answers the research question):** covariate-adjusted effect (OLS of `z` on `x` and start score `y`, robust HC2 SE) = **+1.22 points, 95% CI 0.86 to 1.58, p < 0.001**.
Effect among attendees specifically (regression-imputation ATT) = **+1.21, bootstrap 95% CI 0.83 to 1.57**. The effect is about 1.2 points on a typical control-group gain of about 10 points (roughly 12%), or about 0.28 SD of `z`.

## Why a causal reading is supported
- Per the study description, 600 of 2000 students were chosen by a uniform random draw using no information about the students; all selected attended, none of the others did; there was no switching or interference, and `y` was measured before assignment. The end-of-term scorers were blind to attendance, and there are no missing data.
- Randomization is consistent with the data: baseline `y` is balanced (mean 59.85 attended vs 60.28 not; Welch p = 0.31; KS p = 0.13).
- Because assignment was random, the simple difference in means is an unbiased estimate of the average effect; adjusting for the pre-treatment score `y` only increases precision.

## Results
| Estimator | Effect on `z` | 95% CI |
|---|---|---|
| Difference in means (unadjusted, Welch) | +1.110 (SE 0.217) | 0.69 to 1.53 |
| Permutation test (20,000 draws), unadjusted | p ≈ 0.00005 | — |
| Adjusted for `y` (**adopted**) | **+1.219** (SE 0.184) | **0.86 to 1.58** |
| Lin interacted adjustment (ATE) | +1.226 (SE 0.184) | 0.86 to 1.59 |
| Attendees' effect (ATT, regression imputation) | +1.214 (boot SE 0.186) | 0.83 to 1.57 |

Group means of `z`: 9.994 (control, n = 1400) vs 11.104 (attended, n = 600); difference 1.110.

All estimates agree. The adjusted estimates are slightly larger and tighter than the unadjusted one only because `y` is a strong predictor of `z` (correlation about 0.51; roughly +0.26 gain points per start-score point), and by chance the attended group started about 0.4 points lower. The unadjusted and adjusted estimates are statistically compatible.

## Heterogeneity and checks
- Effect by start-score quartile (unadjusted): 0.79, 1.39, 0.72, 1.94 (each SE about 0.37). The pattern is not monotone, and the formal interaction test with `y` (linear + quadratic terms) gives p = 0.14 (linear interaction alone p = 0.075). There is no solid evidence that the effect varies with the start score; it is not established whether it does.
- The relationship of `z` to `y` is linear (quadratic term p = 0.94). Residuals are roughly symmetric; variance is similar across arms (Levene p = 0.095). Bootstrap CIs (unadjusted 0.69 to 1.54; adjusted 0.87 to 1.57) match the analytic ones.

## Caveats
- The estimate is of the average effect; individual effects may differ. Results are based only on the supplied data (`x`, `y`, `z`), and no other variables could be checked.
- Which exact adjusted vs unadjusted estimator to use was my choice, made after seeing the data; the conclusion (about +1.1 to +1.2 points, clearly above zero) does not depend on that choice.
