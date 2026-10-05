# Did arrangement Q increase the change `z` for the units that received it?

## Answer
**Yes, modestly.** For the 600 units that received arrangement Q, it raised the change `z` by about **+1.2 points** (0–100 scale) relative to what they would have had without it.

**Adopted estimate (effect on the treated, ATT): 1.23 points, 95% bootstrap CI about 0.8 to 1.65** (stratification on baseline `y`: 1.24, CI 0.81–1.68; control-regression imputation, linear/quadratic/cubic in `y`: 1.23, CI 0.78–1.65). The change `z` averaged 13.0 in the treated group, so the arrangement accounts for roughly 1.2 of those points.

The naive comparison (treated mean z 13.02 minus untreated mean z 9.39 = **3.63**) is **not** the answer: it is inflated roughly threefold by selection on baseline `y`.

## Why the naive difference is wrong and how the estimate was obtained
- Treatment depended on baseline `y` (accepted in descending order of `y` among candidates), and `z` itself rises with `y` (~0.2–0.3 points per baseline point in the untreated). Treated units have a much higher mean `y` (67.1 vs 56.9), so the raw gap mixes the arrangement effect with the `y`–`z` relationship.
- By the selection design, the only thing linking treatment to `y` is a random component unrelated to any unit characteristic, so given `y` treatment is as good as random (no other characteristic entered selection). The other part of the mechanism is a pure function of `y`.
- Overlap: all 600 treated have `y` ≥ 58.21. All candidates that were rejected have `y` below that value, so untreated units with `y` ≥ 58.21 (n = 536) are non-candidates selected by chance alone. Untreated units below 58.21 (n = 864) have no treated counterpart and cannot be compared directly.
- The effect on the treated therefore needs only `E[z | y, untreated]` for `y` ≥ 58.21, which is observed directly from the 536 comparable untreated units (no extrapolation). I compared treated and untreated units at equal `y` on this common-support sample (n = 1136).

## Results (common support, y ≥ 58.21)
| Method | Estimate | 95% CI |
|---|---|---|
| Unadjusted, support-restricted | 1.53 | – |
| Imputation, linear in y | 1.23 | 0.78–1.65 |
| Imputation, quadratic | 1.23 | 0.82–1.65 |
| Imputation, cubic | 1.23 | 0.81–1.65 |
| Stratification on y (10 strata, ATT weights) | 1.24 | 0.81–1.68 |
| Matching (5 nearest on y) | 1.10 | 0.69–1.63 |
| IPW (logit on y) | 1.22 | – |
| OLS z ~ x + y (HC3; equal-weight over support) | 1.18 (SE 0.21) | – |
| OLS z ~ x + y, full sample (HC3) | 1.16 (SE 0.21) | – |

All adjusted estimators agree on 1.1–1.25. Nonlinearity in `y` is negligible (quadratic terms p = 0.47 control, 0.72 treated), and the effect shows no clear dependence on `y` (x:y interaction p = 0.12). Treated exceed untreated at every baseline stratum (differences ≈ 0.6–2.0).

## Caveats
- The estimate applies to units like those treated (baseline `y` between 58 and 75); nothing is established for lower-`y` units, which were never treated.
- Identification rests on the described selection mechanism (random component independent of everything else) and on the conditions stated in the study description (no interference, no switching, blinded follow-up, no missing data). I cannot verify these from the data; the data only show overlap and good fit.
- `z` was measured after Q ended, so the +1.2 is the effect still present at follow-up, not necessarily the effect during Q.
- Bootstrap intervals are conditional on the common-support sample (cutoff taken from the data). The "full sample" OLS rows use the extra untreated units only through the model.
