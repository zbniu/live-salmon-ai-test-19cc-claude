# Final report: effect of arrangement Q on change `z` among units that received Q

## Answer

Yes. Among the 600 units that received arrangement Q, receiving it increased their change `z` by about **1.0 point** on the 0–100 scale.

**Adopted result (answers the research question):** average treatment effect on the treated (ATT) = **+1.01 points**, robust SE 0.185, **95% CI 0.65 to 1.38**, p < 0.001. This is a regression-adjusted estimate (Lin-type interacted regression of `z` on `x`, baseline `y` centred at the treated-group mean, and their interaction, HC2 standard errors). Equivalent imputation estimate (predict each treated unit's `z` without Q from the control-group relation of `z` on `y`): 1.014, bootstrap 95% CI 0.65 to 1.37.

## Why this design supports a causal answer

The study description states that Q was assigned by simple random draw (600 of 2000, equal probability, no unit information used), with full compliance, no switching, no interference, identical and blinded measurement, and no missing data. Under these conditions the control group (n = 1400) is a valid counterfactual for the treated units, so the ATT is identified. Because assignment was a simple random draw, the ATT and the average effect in the whole sample are the same quantity in expectation; the estimates here differ only trivially (ATT 1.014 vs ATE 1.036).

## Data checks

2000 rows, three columns, no missing values; `x` takes only 0/1 with 600 treated. Baseline `y` ranges 45–75; implied follow-up (`y + z`) ranges 45–97, so there are no floor or ceiling effects. Baseline balance: treated units had a slightly lower mean baseline by chance (−0.75 points, Welch p = 0.08; KS p = 0.13), consistent with randomisation.

## Supporting and sensitivity results

The unadjusted difference in mean `z` (treated − control) is +0.85 (SE 0.21, 95% CI 0.43 to 1.27, p < 0.001). This is also an unbiased estimator under randomisation, but it is less precise. Because `z` rises with baseline `y` (slope ≈ 0.22 per point) and the treated group happened to start 0.75 points lower, the unadjusted contrast is pulled down by the chance imbalance; adjusting for the pre-treatment baseline corrects this and reduces the standard error. I adopt the adjusted estimate for that reason, and both lead to the same qualitative conclusion.

Other specifications agree closely: ANCOVA `z ~ x + y` gives 1.02 (95% CI 0.66 to 1.39); a cubic control-group model for imputation gives 1.016. A randomisation (permutation) test of the sharp null of no effect for any unit gave p < 1/5000 (no permuted statistic out of 5000 was as extreme as observed).

## Heterogeneity (descriptive, not part of the headline answer)

The effect appears somewhat larger for units with higher baseline: the treatment × baseline interaction is +0.041 per baseline point (p = 0.048), and quintile-specific differences rise from about +0.3 (lowest baseline quintile, not individually significant) to about +1.3–1.4 (top two quintiles). The variance of `z` is also larger among treated units (Levene p = 0.001). This evidence is modest and close to conventional thresholds; the headline ATT is an average over the treated units and does not depend on it.

## Limitations

The effect is the average for these 600 treated units in this study, measured at the single follow-up after Q had ended; nothing in the material says whether it persists or generalises. Because the baseline was measured before assignment, the effect on the change `z` equals the effect on the follow-up level.
