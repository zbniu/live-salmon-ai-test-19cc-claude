# Effect of the tutoring class on score gain among attendees (ATT)

## Answer
Yes. For the students who attended the tutoring class, attending increased their score gain `z`
by an estimated **1.23 points** on the 0–100 scale (95% bootstrap CI **0.80 to 1.66**; SE 0.22).
This is the adopted answer to the research question (average treatment effect on the treated).
The raw difference in mean gain between attendees and non-attendees (3.63 points) is **not** the answer:
it is inflated because attendees had much higher start-of-term scores, and gain rises with `y`
among non-attendees too.

## Why this is identified
Per the study description, attendance depended only on the start-of-term score `y` and on a
study-generated random number unrelated to any student characteristic. Hence, given `y`, attendance
is independent of the untreated gain `z(0)`: comparing attendees with non-attendees at the same `y`
removes confounding. Admission among applicants went by descending `y`, so every attendee has
`y >= 58.21` (the lowest attendee's `y`) and nobody below that value attended. Above 58.21,
attendance = being an applicant, and non-applicants exist at every `y`: the share attending is about
0.4–0.65 throughout, with 536 non-attendees spanning the attendees' full `y` range (estimated
propensity ranges 0.40–0.64 in both groups). So the analysis uses the 1,136 students with `y >= 58.21`
(600 attendees, 536 non-attendees); the 864 lower-`y` non-attendees carry no information about
comparable attendees.

## Methods and results (region y >= 58.21; 2,000 stratified bootstrap draws)
| estimator | ATT | 95% CI |
|---|---|---|
| Regression adjustment, linear control model in `y` (**adopted**, lowest CV error) | 1.23 | 0.81–1.66 |
| Regression adjustment, quadratic / cubic | 1.23 / 1.23 | ≈0.80–1.66 |
| IPW (ATT odds weights, logit propensity quadratic in `y`) | 1.23 | 0.80–1.66 |
| Doubly robust AIPW | 1.23 | 0.80–1.65 |
| Cubic B-spline control model (df = 5) | 1.46 | 1.02–1.90 |
| 5-nearest-neighbour matching on `y` | 1.10 | 0.70–1.63 |

The IPW weights balance mean `y` exactly (67.07 vs 67.07). Sensitivity: more flexible spline
models (df 4–10) give 1.40–1.53 but have higher cross-validated prediction error than the
linear model; matching with 1–40 neighbours gives 1.10–1.26; full-sample polynomial regressions
give 1.20–1.24. All estimates lie between about 1.1 and 1.5 points and every 95% interval excludes 0.
Descriptively, the estimated effect is somewhat larger for attendees with higher `y`
(≈1.0, 1.7, 1.7 points by tercile of `y`; interaction slope 0.07 per point of `y`, SE 0.04,
not clearly different from zero); the reported 1.23 is the average over all 600 attendees.

## Caveats
The bootstrap treats the admission cutoff (58.21) as fixed; it is determined by `y` and the random
numbers only, not by outcomes. Inference relies on the stated assignment mechanism (Section 3 of
the study description) and on correct modelling of how `z` varies with `y`; the results are stable
across the specifications tried. The effect is on score *gain*, which, since `y` is pre-treatment,
equals the effect on the end-of-term score.

## Files
Code: `code/01_explore.py`, `code/02_att.py`, `code/03_sensitivity.py`; outputs in `results/`;
execution record in `run_log.txt`.
