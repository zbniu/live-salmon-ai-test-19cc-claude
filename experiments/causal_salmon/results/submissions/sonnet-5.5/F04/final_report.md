# Did arrangement Q increase the change `z`?

## Answer
**Yes. Receiving arrangement Q increased `z` by about 1.2 points (0.0–100 scale) on average.**
Adopted estimate (ANCOVA, adjusting for baseline `y`, HC3 robust SE): **+1.22 points, 95% CI 0.86 to 1.58, p < 0.001.**
The unadjusted difference in means agrees: **+1.11 points, 95% CI 0.69 to 1.53** (Welch t = 5.12, p ≈ 4e-7).
Mean `z`: 11.10 in the Q group (n = 600) vs. 9.99 in the non-Q group (n = 1400).

## Why this is a causal estimate
- 600 of 2000 units were selected by a simple random draw using no unit information, so assignment is independent of potential outcomes; no unit switched, no interference, no missing data, blinded outcome recording (study description §3–4).
- Consistent with this, baseline `y` is balanced between arms (59.85 vs 60.28; Welch p = 0.31; KS p = 0.13).
- Because assignment was randomized, the treated-minus-control difference estimates the effect on the treated (which here equals the average effect over all units). Baseline `y` is measured before assignment, so adjusting for it is legitimate and only improves precision (R² ≈ 0.27; the SE falls from 0.217 to 0.184). The point estimates before and after adjustment (1.11 vs 1.22) differ by less than one SE.

## Robustness
- Mann-Whitney (one-sided) p ≈ 8e-7; permutation test (20,000 re-randomizations): no draw as extreme as observed (p < 5e-5).
- Allowing a treatment × baseline interaction gives an effect of 1.23 at mean baseline (CI 0.86–1.59); the interaction is small and not clearly different from zero (0.038 per baseline point, p = 0.076).
- A flexible cubic-in-baseline model gives 1.01 (CI 0.47–1.54) at mean baseline; the effect is positive throughout.
- Quantile regression (adjusted) gives positive shifts of about 1.0–1.4 at the 10th, 25th, 50th, 75th and 90th percentiles, so the effect is not driven by outliers or one tail.
- Residuals are approximately symmetric (skew ≈ 0) with similar spread in both arms (SD 3.82 vs 3.66).

## Caveats
- Effect is on the change score as defined: follow-up (measured after Q had ended) minus baseline. The result therefore refers to a difference in change that is present after Q ended, not during it.
- Heterogeneity by baseline level: quartile-wise differences (0.79, 1.39, 0.72, 1.94; SE ≈ 0.37 each) are not monotone and the evidence for heterogeneity is weak; I do not claim any baseline-dependent pattern. The single number to use is the average effect, ≈ 1.2 points (plausible range about 0.9–1.6; unadjusted analysis gives 0.7–1.5).
- Nothing in the data can speak to mechanisms, the effect of Q on other outcomes, or units outside this study.

## Files
code/01_explore.py, code/02_estimate.py; outputs in results/; execution record in run_log.txt.
