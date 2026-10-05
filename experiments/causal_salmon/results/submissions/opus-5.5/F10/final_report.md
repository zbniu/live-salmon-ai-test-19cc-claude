# Final report: effect of the tutoring class on score gain `z`

## Answer

**For the treated students as a whole, the supplied material does not identify the average effect of attending the tutoring class, so no definite answer for that group can be given.** The only part of the effect the data identify is the effect for treated students at the admission threshold (start-of-term score y ≈ 57.0). For those students there is **no evidence of an increase**: the adopted estimate is **−0.5 points** (95% bootstrap CI −3.2 to +1.8; fuzzy regression-discontinuity, local linear, triangular kernel, bandwidth 8 points). Across reasonable specifications the estimate ranges from about −1.6 to +1.1 points, with every confidence interval including 0. The naive treated-vs-untreated difference (about +3.6 to +5.5 points) is not a valid estimate of the effect; it reflects selection.

## Why

By the design (Section 3), a student attended iff (a) they were among the 900 applicants and (b) their start-of-term score y was at or above the score of the 600th admitted applicant. In the data this cutoff is c = min{y : x = 1} = 56.99; no student below c attended, and 607 of the 1207 students at or above c did not attend (non-applicants). Applicant status depends on unrecorded circumstances of the student, which may also affect the score gain, and the random component of the application score is not supplied. So comparing attenders with non-attenders, even at the same y, is confounded.

What the design does provide is a sharp rule in y: at c, the probability of attending jumps from 0 to about 0.40 (the share of applicants among students near c), while the composition of applicants vs non-applicants changes smoothly in y. A fuzzy regression discontinuity (jump in E[z|y] divided by jump in P(x=1|y)) therefore identifies the average effect for applicants at y = c. Because nobody below c can attend (one-sided), these are exactly the treated students at the threshold, i.e. this is the effect on the treated at the margin. Treated students with higher y (57–75) are not covered by this estimate; extending it to them requires an untestable assumption (e.g. effect constant in y), which the material does not supply.

## Results (all from code actually run; see results/)

| specification | first stage | effect at cutoff | 95% CI (bootstrap) |
|---|---|---|---|
| triangular, h=4 | 0.41 | −0.56 | −5.4, 2.7 |
| triangular, h=6 | 0.40 | −0.54 | −3.9, 2.0 |
| **triangular, h=8 (adopted)** | **0.41** | **−0.52** | **−3.2, 1.8** |
| triangular, h=10 | 0.42 | −0.21 | −2.4, 1.7 |
| triangular, h=12 | 0.43 | 0.21 | −1.8, 2.0 |
| uniform, h=8 | 0.42 | −0.03 | −2.3, 2.0 |
| uniform, h=12 | 0.47 | 1.07 | −0.6, 2.5 |

Quadratic/cubic one-sided fits give −1.4 to −0.1.

Naive (not adopted): raw difference in means 5.46; OLS z ~ x + y: 3.79 (SE 0.19); among y ≥ c, treated − untreated gap ≈ 3.6 at the cutoff, roughly constant in y.

Selection is visible directly: among untreated students, mean z drops by about 1.0 point (SE 0.37) at c, because untreated students just above c are only non-applicants while those just below include applicants. Applicants thus have higher gains than non-applicants even without tutoring, which explains why the naive ~4-point gap greatly overstates the effect at the threshold. Placebo cutoffs away from c show no systematic jumps (−0.75 to +1.4, noisy).

## Limitations

- The effect for treated students above the threshold is not identified; the margin estimate need not represent them.
- Estimates at the threshold are imprecise (first stage ≈ 0.4, ~500 students per side within 8 points); effects of roughly +2 points or more at the threshold are, however, not supported by most specifications.
- The cutoff is estimated from the data as the lowest treated y (it is determined exactly by the admission rule).
