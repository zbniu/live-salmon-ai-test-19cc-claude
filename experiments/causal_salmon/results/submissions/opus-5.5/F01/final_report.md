# Final report: effect of the tutoring class on score gain `z` for students who attended

## Answer in brief

**The supplied material does not support a definite answer for all 600 attending students.** What the data do identify is the effect for attending students at the admission cutoff (start-of-term score y ≈ 55.6, the lowest-scoring admitted students). There, the estimated effect of attending is **+0.8 points of score gain (fuzzy regression-discontinuity, local linear, triangular kernel, bandwidth 8 points; robust SE 1.0; 95% CI about −1.2 to +2.8; bootstrap 95% CI −1.5 to +2.7)**. Across reasonable specifications the estimate ranges from about −0.8 to +1.5 points, never statistically distinguishable from zero. So there is no evidence that attending increased score gains at the cutoff; effects of roughly 3 points or more are unlikely there. This cutoff estimate is the result I adopt; it answers the research question only for the attending students at the cutoff, not for the attending population as a whole.

The simple comparisons — attended minus not attended, 5.4 points; the same comparison within levels of y, 3.8 points — **are not valid answers**: the data show that students who attended were selected on unrecorded circumstances associated with higher gains (details below).

## Why the design allows only this

From the study description, the treated students are exactly the applicants with y at or above the 600th-highest applicant y. In the data this cutoff is c = 55.593 (minimum y among attendees). Consequences:

- Below c, nobody attended. At and above c, attendees = applicants and non-attendees = non-applicants.
- Applicant status depended on unrecorded circumstances, which may also affect gains. So above c, attendees vs non-attendees at the same y is confounded.
- At c, attendance switches on for applicants only (one-sided non-compliance). The fuzzy-RD ratio — jump in E[z | y] over jump in P(attend | y) — therefore identifies the average effect for attendees at y = c, provided applicant status and potential gains vary smoothly with y. The study design makes this plausible: y was measured before assignment and the cutoff is set by a count.

## Results (all from `data.csv`, n = 2000, 600 attended)

**First stage.** P(attend) jumps from 0 to about 0.46 at c (SE ≈ 0.045). This is the applicant share there.

**Fuzzy RD, effect at c** (`results/02_rd_estimates.csv`):

| specification | estimate | SE |
|---|---|---|
| linear, triangular, h = 8 (adopted) | 0.81 | 1.01 |
| linear, triangular, h = 4 / 6 / 10 | −0.02 / 0.56 / 0.89 | 1.42 / 1.14 / 0.92 |
| quadratic, triangular, h = 8 / 10 | 0.12 / 0.36 | 1.42 / 1.29 |
| linear, full sample | 1.52 | 0.79 |

Very narrow bandwidths (h ≤ 3) give negative but very imprecise values.

**Direct evidence of selection on unrecorded circumstances** (`results/03_selection_decomposition.csv`, h = 8, bootstrap CIs):

- At c, non-attending students just above the cutoff (non-applicants) have gains about 1.4 points lower than the pooled students just below it (95% CI −2.5 to −0.3).
- The implied untreated gain of applicants at c is about 3.1 points higher than that of non-applicants (CI 0.7 to 5.8).
- That selection gap accounts for nearly all of the 3.9-point raw contrast at the cutoff.

**Comparison quantities that do not answer the question:**

- Naive difference in means: 5.40.
- Within-y contrast above c, averaged over attendees: 3.82 (SE 0.20). It is roughly constant across y bands (3.6–4.1).
- Both contain the selection gap.

**Assumption-dependent extrapolation (not adopted).** Suppose both the effect and the selection gap were constant across y. Then the ATT for all attendees would be 3.82 − 3.07 ≈ 0.75, consistent with the cutoff estimate. Nothing in the data can verify those constancy assumptions above c. The applicant share rises with y (0.39 to 0.56), so the composition of applicants, and hence the selection gap, may change.

## Checks and caveats

- Placebo cutoffs above c show no jumps in P(attend), nor in z within attendees or within non-attendees (all |t| < 1.4).
- Below c, two of three placebo cutoffs (y = 51, 53) show jumps of about −1.5 (t ≈ −2.1) in narrow windows. This suggests local fits are noisier, or E[z|y] less smooth, than the nominal SEs imply. It is a further reason to read the cutoff estimate as "small, not distinguishable from zero" rather than as a precise number.
- The RD estimate is local to the lowest-y admitted students and has wide uncertainty.
- The effect for higher-y attendees is not identified by the supplied material.
