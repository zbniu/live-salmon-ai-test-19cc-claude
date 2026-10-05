# Final report: effect of the tutoring class on score gain z

## Answer
**The supplied material does not support a definite answer.** The only credible comparison available (a regression-discontinuity design at the admission cutoff) gives an estimated effect of about **-0.5 points (95% CI -4.0 to +3.0; robust CI -4.7 to +3.7)** on score gain for attendees near the cutoff. This is statistically indistinguishable from zero, and the interval is too wide to rule out either no effect or an effect of a few points in either direction. The naive difference in means (+5.46 points) is **not** a valid answer to the question.

## Why the naive comparison is invalid
Attendees (x=1) average z = 5.46 points higher than non-attendees, but admission depends on start-of-term score y, and z rises steeply with y (roughly 0.5 points per point of y: mean z about 6.6 in the lowest y bin and about 14 in the highest). Attendees have much higher y, so the raw gap mostly reflects y. Application also depended on unrecorded student circumstances, so ordinary regression adjustment for y cannot remove confounding either.

## Design used
Among applicants, places were filled in descending order of y, so there is a sharp y-cutoff c = 56.9946 (lowest y among attendees; highest y of any non-attendee below it is 56.9933). Findings from the data:
- No one below c attended (0 of 793). Above c, 600 of 1207 attended (607 did not, i.e. non-applicants). Attendance probability jumps from 0 to about 0.40 at the cutoff (first stage 0.404, SE 0.062).
- Because only applicants are admitted, this is a fuzzy RD with one-sided non-compliance. The ratio of the jump in z to the jump in attendance estimates the effect for **applicants at y near 57, i.e. attendees at the cutoff**. This matches the question's target population but only locally; it says nothing about attendees with much higher y without extra assumptions.
- Identification relies on continuity at c of the mean no-tutoring gain and of the applicant share in y. This is plausible given the random component of the application score but cannot be fully tested (no applicant list, no other covariates). Counts of students just below/above c are similar (e.g. 208 vs 216 within 3 points), with no sign of sorting; a formal density test was not obtained (see run log).

## Results (fuzzy RD, effect of attending on z, points)
| Specification | Estimate | 95% CI |
|---|---|---|
| rdrobust, linear, MSE bandwidth 3.8, triangular (conventional) | **-0.53** | -4.02 to 2.96 |
| rdrobust robust bias-corrected | - | -4.71 to 3.70 |
| Local linear, h=5 / 8 / 10 (triangular) | -0.25 / -0.52 / -0.21 | all include 0 (e.g. h=8: -2.9 to 1.9) |
| Local quadratic, h=6 to 18 (triangular) | -0.06 to -1.12 | all include 0 |
| Local linear, wide h=15-18 (uniform) | +1.4 | about 0.0 to 2.8 (borderline) |

Across 36 bandwidth/kernel/order combinations (results/02b_fuzzy_rd_grid.csv), point estimates range from about -1.6 to +1.4 and nearly all CIs contain 0. The only intervals that barely exclude 0 come from wide-bandwidth linear fits, where bias from curvature in z over y is most likely; quadratic fits with the same windows give negative estimates. So there is no robust evidence of a positive or a negative effect.

## Conclusion
The data are consistent with no effect and with moderate effects of either sign; the best (local, cutoff-specific) point estimate is about -0.5 points with a roughly ±3.5 point confidence interval. Whether tutoring increased the gain, and by how much, is not established. The +5.46 raw difference should not be read as the effect.
