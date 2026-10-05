# Did arrangement Q increase the change `z`?

## Answer
**Yes.** Receiving arrangement Q increased `z` by about **1.0 point** on the 0–100 scale
(baseline-adjusted estimate **1.02, 95% CI 0.66 to 1.39, p < 0.001**). This is the number adopted as the answer.
Because assignment was random, this estimate applies to the treated units and to the study population alike.

## Why this is a causal estimate
Exactly 600 of 2000 units were chosen by a simple random draw using no unit information (Sec. 3). No switching, no interference,
identical measurement, blinded outcome assessors, and no missing rows were stated (Sec. 4). Group differences in `z` can therefore be read as the effect of Q.
Baseline `y` was measured before assignment, so adjusting for it is legitimate and does not introduce post-treatment bias.

## Results (code: `code/analysis.py`, output: `results/analysis_output.txt`)
- n = 600 treated, 1400 control; no missing values.
- Unadjusted difference in mean `z`: 10.76 − 9.91 = **0.85** (Welch SE 0.21, 95% CI 0.43 to 1.27, p = 8e-5). Mann–Whitney p = 1e-4. Permutation p < 1e-4.
- Baseline `y` is slightly lower in the treated group by chance (59.16 vs 59.91, p = 0.08; KS p = 0.13). That is consistent with random assignment, but baseline `y` is strongly related to `z` (slope ≈ 0.23, r = 0.48), so the unadjusted estimate is slightly biased downward in this particular draw.
- **Adjusted for `y` (OLS, robust HC3 errors): Q effect = 1.02 (SE 0.19, 95% CI 0.66 to 1.39).** Adding `y²` gives 1.03; the quadratic term is not significant. Adjusting reduces the standard error (0.21 → 0.19) and corrects the chance imbalance, so I prefer it over the raw difference.
- The two estimates (0.85 raw, 1.02 adjusted) agree in direction and are statistically compatible; both support a positive effect of roughly 1 point.

## Caveats
- Possible effect heterogeneity by baseline: the Q×`y` interaction is 0.04 per point (p = 0.049, borderline and not corrected for multiple looks). By baseline quartile the differences were 0.49, 1.08, 1.05 and 1.28, hinting at a slightly larger effect at higher baseline, but this is weak evidence; the average effect is the robustly supported result.
- `z` was measured after Q ended, so the effect is on the change persisting after the arrangement, not during it.
- The effect is modest relative to the SD of `z` (≈4.25), about 0.24 SD.
- The mechanism by which Q acts is not known from the supplied material.
