# Final report: effect of the tutoring class on score gain among attendees (ATT)

## Answer
Yes. For the students who attended the tutoring class, attending increased their score gain `z` by an estimated **1.21 points** (0–100 scale), **95% bootstrap CI ≈ 0.81 to 1.59** (regression-adjustment estimator, adopted as the main result). This is the average effect on the treated (ATT) for the 600 attendees.

## Why this is identified
Per the study description, attendance depended only on the start-of-term score `y` and a study-generated random number unrelated to any student characteristic (applicant selection), plus admission among applicants in descending `y`. Hence, conditional on `y`, attendance is independent of potential score gains (no unmeasured confounding), with no interference, no switching, blinded measurement and no missing data. So comparing attendees with non-attendees of the same `y` identifies the effect.

Overlap: because admission among applicants was by descending `y`, all attendees have `y ≥ 57.36` (min attendee score); no student below that can serve as a comparison for attendees, but none is needed. Within `y ≥ 57.36` there are 600 attendees and 577 non-attendees (non-applicants, who were excluded only through the random component), spread over the whole attendee range (e.g., 95 non-attendees in the top quintile, y 71.4–75). The analysis is restricted to that common-support region.

Adjustment is essential: `z` rises with `y` among non-attendees (~0.19 points per point of `y`), and attendees have higher `y` (mean 66.8 vs 57.2), so the naive difference (3.45 points) is heavily confounded and is not the answer.

## Results (region y ≥ 57.36; 500 stratified bootstrap replicates)
| estimator | ATT | boot SE | 95% CI |
|---|---|---|---|
| **Regression adjustment, linear in y (main)** | **1.213** | 0.210 | 0.81 – 1.59 |
| Regression adjustment, quadratic | 1.209 | 0.206 | 0.82 – 1.60 |
| Regression adjustment, cubic | 1.205 | 0.215 | 0.80 – 1.64 |
| Regression adjustment, cubic spline | 1.218 | 0.217 | 0.82 – 1.65 |
| 5-nearest-neighbour matching on y | 1.083 | 0.247 | 0.57 – 1.51 |
| IPW (ATT odds weights) | 1.209 | 0.225 | 0.74 – 1.64 |
| Doubly robust | 1.211 | 0.207 | 0.80 – 1.60 |
| OLS z ~ x + y | 1.158 | 0.218 | 0.77 – 1.62 |

All estimators agree (≈1.1–1.2 points) and all CIs exclude zero. The linear control model is preferred by AIC; quadratic using all non-attendees gives 1.205. There is some evidence the effect grows with `y` (x·y interaction 0.088 per point, p = 0.03); the ATT of ~1.2 is the average over attendees' `y` distribution.

## Caveats
Identification rests on the stated design (assignment depends only on `y` and independent randomness). The bootstrap treats students as i.i.d. and ignores the rank-based dependence of admission; this is expected to have minor impact. Results apply to attendees, not to all students.
