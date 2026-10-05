# Did the tutoring class raise score gain `z` for the students who attended it?

## Answer
**Yes. For attendees, attending raised the score gain by about 1.2 points (0–100 scale).**
Adopted estimate (effect on the treated, ATT): **+1.21 points, bootstrap 95% CI ≈ 0.78 to 1.64** (SE ≈ 0.22).
The naive difference in mean `z` (attendees minus all non-attendees) is 3.45, but it is **not** the answer; it mostly reflects that attendees had higher start scores `y`, and higher `y` goes with higher `z`.

## Why the naive comparison fails, and what is valid
- Admission was decided by `y` only (applicants admitted in descending `y` among the 900 applicants). The lowest `y` among attendees is 57.356; every student with `y` below that did not attend (823 students). They cannot be compared with attendees at all (no overlap), so they were excluded from the effect estimation. In the control group `z` rises with `y`, so using them would bias the result.
- Among students with `y` >= 57.356 (n = 1177: 600 attendees, 577 non-attendees), attendance depends on `y` plus a random number unrelated to anything about the student (applicant status was set by the application score; the non-attendees here are non-applicants). Hence, given `y`, who attended is as good as random, and comparing attendees with non-attendees *at the same `y`* identifies the effect on attendees. The key assumption is that `y` is the only confounder, which the study description states by construction; this cannot be tested with the data.
- Overlap is reasonable (share attending is about 0.4–0.6 across y 57.4–75), and attendees' mean `y` is 66.8 vs 65.6 for non-attendees in this region.

## Results (region y >= cutoff; bootstrap 1000 resamples)
| method | ATT estimate | SE | 95% CI |
|---|---|---|---|
| OLS z ~ x + y | 1.16 | 0.21 | 0.74, 1.58 |
| OLS with quadratic in y | 1.15 | 0.21 | 0.74, 1.58 |
| OLS with x*y interaction, effect at treated mean y | 1.21 | 0.21 | 0.79, 1.64 |
| OLS with x*(y, y²), averaged over attendees | 1.21 | 0.22 | 0.78, 1.64 |
| Inverse-propensity weighting (ATT, logistic in y, y²) | 1.21 | 0.22 | 0.78, 1.65 |
| 1-nearest-neighbour matching on y | 1.09 | 0.30 | 0.47, 1.66 |

All estimators agree at roughly 1.1–1.2; I adopt 1.21 (IPW / interaction-adjusted, which averages over the attendees' own distribution of `y`).

## Caveats
- There is evidence that the effect grows with `y` (interaction 0.09 per point, p = 0.034). The 1.2 is an average over the actual attendees; it is not a constant effect. Restricting to narrower windows near the cutoff gives smaller, less precise estimates (y<=70: 0.88; y<=65: 0.69; y<=62.5: 0.46 with SE 0.40), consistent with that heterogeneity. The effect for marginal students near the cutoff is therefore less well determined and possibly smaller.
- The estimate relies on a smooth relation between `z` and `y` and on no other confounders given `y`. No dedicated check is possible for unmeasured confounders; the design (random component only) supports it.
- The effect for students who did not attend (or those below the cutoff) is not identified from these data and is not claimed.
