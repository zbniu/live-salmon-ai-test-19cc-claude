# Did the tutoring class raise the score gain z for attendees?

## Answer
**The supplied material does not support a definite answer.** The only identification strategy the design allows (a fuzzy regression discontinuity at the admission cutoff) gives an effect estimate for attendees that is statistically indistinguishable from zero and is too imprecise to say how large the effect is, or even whether it is positive. Plausible values (95% CIs across reasonable specifications) run from about -3 to +3 points. I do **not** endorse the large "naive" differences (+5.4 raw, about +3.9 after adjusting for start-of-term score), because they are not valid under this design (see below).

Adopted numerical result (the one that answers the research question): **fuzzy-RD estimate of the effect of attendance on z for students at the admission cutoff (y ≈ 55.6): about +0.9 points (local linear, triangular kernel, bandwidth 10; 95% CI -0.9 to +2.7).** The data-driven optimal-bandwidth version (rdrobust, bandwidth ≈ 2.8) gives -0.8 (95% CI -4.4 to 2.8). These are consistent with each other and with zero, and I regard the number as inconclusive rather than as a finding.

## Design logic
- Admission rule: applicants (top 900 on an application score that depends on y, unrecorded circumstances, and noise) were admitted in descending order of y until 600 places were filled. So there is a cutoff c on y: everyone admitted has y ≥ c, and no one below c attends. In the data c = min y among attendees = 55.593 (no attendee below it; 642 non-attendees above it, i.e. non-applicants).
- Above c, attendance is *not* determined by y: attendees are applicants, non-attendees are non-applicants, and applicant status depends on unrecorded circumstances. Hence comparing attendees with non-attendees, even at equal y, is potentially confounded by those unrecorded circumstances. Comparing only on y is not enough.
- What *is* valid: the jump in P(attend) at c is from 0 to about 0.46 (first stage, strong: z-stat ≈ 9.7 for the jump in attendance), caused only by the cutoff rule applied to y measured before assignment. Dividing the jump in mean z at c by the jump in attendance (fuzzy RD) identifies the effect for the applicants at y = c. This needs only that mean no-treatment outcomes and the applicant share are smooth in y at c, which is plausible here (y measured before assignment; no switching; blind outcome recording).
- Scope: this effect is **local to attendees with y near 55.6**. Attendees have y from 55.6 to 75; the effect for those higher-y attendees is not identified without extrapolation.

## Results (all from code in `code/`, outputs in `results/`)
| Approach | Estimate of effect on z | Comment |
|---|---|---|
| Raw mean difference attendees − others | +5.41 | Invalid: attendees have much higher y (65.7 vs 56.9) and z rises with y |
| Attendees vs non-attendees with y ≥ c, adjusted for y (OLS / local) | ≈ +3.8 to +4.0 (SE ≈ 0.2–0.8) | Invalid unless unrecorded circumstances don't affect z; data suggest they do (next row) |
| Selection check: jump at c in mean z among *non-attendees* | -0.9 to -1.7 (SE 0.4–0.6, h = 5–20) | Non-applicants just above c score lower than the untreated mix just below c, i.e. selection on unrecorded factors that matter for z. This is the reason the 3.9 is not trusted |
| **Fuzzy RD, local linear, triangular, h = 10** | **+0.89 (SE 0.92; CI -0.91, 2.68)** | Adopted, inconclusive |
| Fuzzy RD, local linear, h = 3–20, triangular/uniform | -0.7 to +1.8 | h ≥ 12 uniform: CI just excludes 0 (lower end 0.16–0.20) |
| Fuzzy RD, local quadratic, h = 3–20 | -1.8 to +1.0 (SE 1.1–2.7) | CIs include 0 throughout |
| rdrobust (MSE-optimal bandwidth), p = 1 / p = 2 | -0.83 (CI -4.4, 2.8) / -1.57 (CI -6.4, 3.3) | Robust bias-corrected CIs even wider |
| Global polynomial fuzzy RD, order 1/2/3/4 | +1.63 / +0.57 / +0.38 / -1.09 | Sensitive to functional form |

The reduced-form jump in mean z at c is small (about -0.4 to +0.7, SE 0.4–0.8) while a true effect of ~3.9 on 46% of units would imply a jump near +1.8; the data cannot discriminate between an effect of about 0 and one of about 3. Placebo jumps at fake cutoffs below c (where nobody is treated) range from about -1.4 to +0.9 (SE ≈ 0.6–0.8), a reminder that sampling noise/curvature of this size is normal here.

## Conclusion
Attendance in the tutoring class is *associated* with a gain 4–5 points larger than for non-attendees, but this association mostly (possibly entirely) reflects who applies and who has higher start-of-term scores. The one design-based estimate available (fuzzy RD at the cutoff) is about +1 point with a confidence interval of roughly -1 to +3 (wider at other bandwidths), so we cannot conclude that the class increased attendees' gains, nor quantify the effect; and it only speaks to attendees at the cutoff. A definite answer for all attendees is not supported by the supplied material.

## Limitations / honesty notes
- The cutoff c is estimated as the minimum attendee y; it is exact if the design was followed as described.
- Results depend on bandwidth and polynomial order; I report the range rather than choosing the most favourable one.
- Fuzzy-RD standard errors are heteroskedasticity-robust (HC1-type); rdrobust uses its own nearest-neighbour variance.
