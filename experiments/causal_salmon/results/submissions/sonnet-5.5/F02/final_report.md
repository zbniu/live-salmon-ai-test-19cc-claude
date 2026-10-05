# Did arrangement Q increase the change `z`?

## Answer
**The supplied material does not support a definite answer that Q increased `z`.** The credible causal estimate is close to zero and too imprecise to distinguish "no effect" from an effect of about ±2.5 points. My adopted estimate is **0.18 points (95% CI about −2.3 to +2.6; bootstrap CI −2.6 to +2.4)** (fuzzy regression-discontinuity, local linear, bandwidth 5 baseline points, triangular kernel, n = 698). This is the effect of Q on the units that were candidates and whose baseline is near the acceptance threshold (≈55.6). Estimates range from −1.8 to +0.9 across bandwidths 3–10 and linear/quadratic fits, all with CIs containing 0. The naive gap (treated 14.12 vs untreated 8.72 = 5.4 points) is **not** an effect estimate: it is mostly baseline-driven.

## Why the naive comparison is invalid
Per the study description, Q went to the 600 highest-baseline (`y`) candidates, and candidacy depended on `y`, on unrecorded circumstances, and on random noise. Consequently:
- Treated units have much higher `y` (65.7 vs 56.9), and `z` rises steadily with `y` (about 6.4 in the lowest `y` bin to 14.3 in the highest, with no treatment in the lowest bins). A treated/untreated difference, or even a difference among units above the threshold (4.0), is confounded by `y` and by the unrecorded circumstances that also drive candidacy.
- No covariates are available to adjust for the unrecorded circumstances, so ordinary regression adjustment cannot identify the effect.

## Identification used
Because candidates were accepted in descending `y` until 600 slots were full, there is an exact cutoff c in `y`: the lowest treated `y` is 55.593, and **no** unit below it was treated (0 of 758), while above it 600 of 1242 were treated (642 untreated = non-candidates). So the probability of treatment jumps from 0 to about 0.46 at c (first-stage jump 0.47, SE 0.056 at h=5), while everything else (baseline, unrecorded circumstances, noise) varies smoothly through c. The unit count is balanced around c (e.g., 212 vs 212 within 3 points; 357 vs 341 within 5), and z-means by `y` bin follow a smooth trend. The estimate is the jump in `z` at c divided by the jump in treatment probability (fuzzy RD / 2SLS). It targets units at the threshold who were candidates (the units Q reached there), and relies on the usual RD continuity assumption, which I could not fully test, only partially (density balance and placebo cutoffs).

## Results (fuzzy RD, effect of Q on z, points)
| order | bandwidth | effect | SE |
|---|---|---|---|
| linear | 3 | −0.73 | 1.68 |
| linear | 4 | −0.02 | 1.41 |
| **linear** | **5 (adopted)** | **0.18** | **1.24** |
| linear | 7 | 0.78 | 1.06 |
| linear | 10 | 0.89 | 0.92 |
| quadratic | 5 | −0.90 | 2.00 |
| quadratic | 10 | 0.36 | 1.29 |

Reduced-form jump in `z` at c (h=5, linear): 0.09 (SE 0.59). Placebo jumps at untreated cutoffs 48, 50, 52 were 1.2, 0.3, 1.5 (SE ≈ 0.7–0.8), so some noise of about this size exists in the local fits — a reminder of the limited precision.

## Conclusion
There is no evidence in these data that Q raised `z`; the best estimate is near zero (≈0.2 points), with plausible values from about −2.5 to +2.5 on the 0–100 scale. A moderate positive effect (e.g., ≥3 points) is not supported, but small effects cannot be excluded. The estimate applies to candidate units near baseline ≈55.6, not necessarily to units far above it. Effects measured here are post-arrangement (follow-up taken after Q ended), i.e., persistence of any effect.
