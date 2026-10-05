# Final report: effect of arrangement Q on change `z`

## Answer
Yes. For the 600 units that received arrangement Q, receiving it increased their change `z` (follow-up minus baseline, 0–100 scale) by an estimated **1.21 points (95% CI 0.85 to 1.58; HC2 robust SE 0.18; p < 0.001)**.

**Adopted result:** the effect on the treated (ATT) estimated by regressing `z` on `x`, baseline `y` (centred at the treated-group mean of `y`) and their interaction, with HC2 robust standard errors: **+1.21 points [0.85, 1.58]**.

## Basis
- Assignment was a simple random draw of 600 of 2000 units, with full compliance, no attrition, no interference and blinded outcome recording (study description §3–4). The untreated group therefore gives a valid estimate of what the treated units' change would have been without Q, and the ATT is identified. Baseline `y` was measured before assignment, so adjusting for it cannot introduce bias; it only improves precision.
- Data checks: 2000 rows, no missing values, 600 treated / 1400 untreated. Baseline is balanced (treated mean 59.85 vs 60.28; Welch p = 0.31). All baseline and follow-up values lie well inside 0–100 (follow-up 46.3–97.3), so no floor/ceiling issue.
- `z` is strongly related to baseline (slope ≈ 0.25 per baseline point), so baseline adjustment reduces the standard error from 0.22 to 0.18.

## Estimates (all in points of `z`)
| Method | Estimate | 95% CI |
|---|---|---|
| Unadjusted difference in means (Neyman SE) | 1.11 | 0.69 – 1.53 |
| ANCOVA, `z ~ x + y`, HC2 | 1.22 | 0.86 – 1.58 |
| Interacted (Lin), centred at overall mean of `y` (ATE) | 1.23 | 0.87 – 1.59 |
| **Interacted, centred at treated mean of `y` (ATT) — adopted** | **1.21** | **0.85 – 1.58** |

Randomization (permutation) tests with 10,000 re-draws: p < 0.0001 for both the unadjusted and the baseline-residualised difference. The estimates agree closely; the unadjusted estimate is slightly lower because the treated group happened to have a marginally lower baseline, which is associated with smaller change.

## Supporting observations
- The increase appears across the distribution: quantile differences of `z` (treated − untreated) range from about 0.9 to 1.6 points at the 10th–90th percentiles, and the treated group's mean is higher in every baseline tercile (≈ +0.9, +0.8, +1.7).
- There is weak, non-significant evidence that the effect is larger at higher baselines (interaction 0.038 per baseline point, p = 0.075). This does not change the average answer, and I do not claim heterogeneity.

## Limits
- The estimate refers to the change measured at the single follow-up time, after Q had ended; nothing in the data speaks to effects at other times or for other populations.
- Because the baseline was fixed before assignment, the effect on change equals the effect on the follow-up measurement itself.
- Whether 1.2 points is practically important on this scale cannot be judged from the supplied material.
