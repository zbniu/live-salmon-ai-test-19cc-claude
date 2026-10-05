# Effect of the tutoring class on score gain among students who attended

## Answer

Yes. Attending the tutoring class increased the score gain `z` of the students who attended it by an estimated **1.01 points** on the 0–100 scale (95% CI 0.65 to 1.38; HC2 robust SE 0.185; p < 0.001). This is the effect on the treated (ATT) for the 600 attendees. It corresponds to about a 10% increase over the gain these students would be expected to have made without tutoring (about 9.7 points).

The adopted number is the ATT from the regression of `z` on attendance, the start-of-term score `y`, and their interaction, with `y` centred at the attendees' mean (Lin's estimator; estimator C below).

## Why this answer is credible

Attendance was assigned by a simple random draw of 600 out of 2000 students, using no information about them. All selected students attended and no others did. There were no switches, no interference, identical measurement, blinded scoring, and no missing data (study description, sections 3–4). The difference between attendees and non-attendees is therefore a causal effect of the class. Under random selection, the attendees are a random subset of the students, so the ATT and the ATE coincide in expectation. The estimated ATE here is 1.04, almost the same.

## Data checks

There are 2000 rows: 600 attended and 1400 did not. Nothing is missing and there are no duplicates. `y` ranges from 45.0 to 75.0, and the implied end-of-term score `y + z` ranges from 44.9 to 97.1. No score is at the 0 or 100 bound, so floor and ceiling effects are not a concern.

The start-of-term score is strongly related to the gain: the correlation is 0.48, and the gain rises about 0.23 points per pre-test point. By chance, the attendees started 0.75 points lower (59.16 vs 59.91; p = 0.08). The relationship between `z` and `y` is linear in both groups: a cubic term adds nothing (p = 0.88 for controls, p = 0.23 for attendees).

## Estimates (all from `results/02_estimate.txt`)

| Estimator | Estimate | SE | 95% CI |
|---|---|---|---|
| A. Unadjusted difference in mean `z` | 0.85 | 0.21 | 0.43 – 1.27 |
| B. ANCOVA `z ~ x + y` | 1.02 | 0.19 | 0.66 – 1.39 |
| **C. Interacted, centred at attendees' mean `y` (ATT) — adopted** | **1.01** | **0.185** | **0.65 – 1.38** |
| C′. Interacted, centred at full-sample mean `y` (ATE) | 1.04 | 0.19 | 0.67 – 1.40 |
| D. Imputation ATT, linear control model (bootstrap SE) | 1.01 | 0.19 | 0.65 – 1.38 |
| D. Imputation ATT, cubic control model (bootstrap SE) | 1.02 | 0.19 | 0.65 – 1.38 |

A Fisher randomization test of the sharp null hypothesis of no effect for any student gave p ≈ 0.0002 (5000 permutations). None of the permuted ANCOVA coefficients reached the observed value.

The unadjusted difference (0.85) is lower than the adjusted estimates. This is because the attendees happened to start slightly lower, and lower starters gain less. The covariate-adjusted estimators correct for this chance imbalance and are also more precise. I therefore adopt the adjusted ATT. All adjusted variants agree to within about 0.02 points.

## Heterogeneity (secondary)

There is modest evidence that the effect grows with the start-of-term score. The difference in slopes on `y` between attendees and non-attendees is 0.041 points per pre-test point (SE 0.021, p = 0.048). The within-quintile effects are 0.32, 0.98, 1.05, 1.41 and 1.31 points, from the lowest to the highest quintile of `y`. Each has an SE of about 0.4. The residual spread is also slightly larger among attendees (Levene p = 0.04), which fits with some variation in the effect.

This pattern is suggestive, not firmly established. It does not change the headline result, which is the average effect over the attendees.

## Limitations

The estimate applies to the gain on this test over this term for these 2000 students. The data do not show how long the effect lasts or how well it generalises to other students or settings. The CI reflects sampling and randomization uncertainty only.
