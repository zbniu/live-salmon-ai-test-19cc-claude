# Did arrangement Q increase the change `z` for units that received it?

## Answer
**Yes, modestly.** For the 600 units that received arrangement Q, it increased `z` by about **+1.2 points** on the 0–100 scale (average effect on the treated).
**Adopted estimate: 1.21 points, 95% bootstrap CI about 0.79 to 1.61** (imputation estimator, quadratic in baseline `y`, controls with `y` ≥ 57.36). The estimate was stable (1.08–1.21) across estimators, see below.

The raw difference in mean `z` (treated minus untreated) is 3.45 points. It is **not** the answer: it mostly reflects that treated units have higher baseline `y` (mean 66.8 vs 57.2) and `z` rises strongly with `y` (corr 0.55).

## Reasoning
- By the design (section 3), receipt of Q depends only on baseline `y` plus an independent random number (which decides who is among the 900 candidates). Given `y`, who received Q is therefore unrelated to anything else affecting `z`, so comparing treated and untreated units *at the same `y`* is valid. No other covariates exist or are needed.
- Overlap: all treated units have `y` ≥ 57.356; below that, nobody is treated, so no comparison is possible there. Above it, there are 577 untreated units (non-candidates) vs 600 treated, spread across the whole range 57.4–75. So the effect is identified for the treated units (the estimand asked about) by comparing them with untreated units of the same `y`. The effect for units with `y` < 57.4 is not identifiable from these data (and is not asked about).
- Setup assumptions (no interference, uniform Q, blinded outcome assessment, no missing data) are stated in section 4 and were relied upon, not tested.

## Results (effect on treated, points of `z`)
| Method | Estimate | 95% CI / SE |
|---|---|---|
| Naive difference, all units | 3.45 | not adjusted, biased |
| Imputation (control outcome model in `y`), linear, controls with y≥57.36 | 1.21 | 0.78–1.64 |
| **Imputation, quadratic, controls with y≥57.36 (adopted)** | **1.21** | **0.79–1.61** |
| Imputation, cubic | 1.21 | 0.80–1.62 |
| Imputation, quadratic, all 1400 controls | 1.21 | 0.81–1.65 |
| IPW (ATT weights, logistic in `y`, `y`²) | 1.21 | 0.80–1.60 |
| Nearest-neighbour matching on `y`, 1 / 5 neighbours | 1.09 / 1.08 | 0.43–1.63 / 0.60–1.54 |
| OLS `z~x+y(+y²/y³)`, overlap sample (regression-weighted average, HC3 SE 0.21) | 1.14–1.16 | ±0.41 |

## Caveats
- Heterogeneity: the interaction of Q with `y` is small and only marginal (0.09 per point of `y`, p≈0.03, not corrected for multiplicity); the effect at `y`=65 is about 1.05. I treat this as unestablished and report only the average.
- Control outcomes are roughly linear in `y` in the overlap region, so results do not depend on the functional form.
- Unmeasured confounding beyond `y` is excluded only by the design description, not verified from the data.
- Because `z` was measured after Q ended, the effect is on change at follow-up, not necessarily during Q.
- Bootstrap CIs are percentile intervals (1000 resamples; 500 for IPW).
