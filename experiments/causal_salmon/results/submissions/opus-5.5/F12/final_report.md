# Effect of arrangement Q on change `z` among the units that received it (ATT)

## Answer
Yes. For the 600 units that received arrangement Q, receiving it increased their change `z` by an estimated **1.23 points** on the 0–100 scale (95% bootstrap CI **0.82 to 1.65**; bootstrap SE 0.21). This is the average effect on the treated (ATT) and is the result adopted to answer the research question.

## Why this comparison is valid
Per the study description, a unit received Q exactly when it was a candidate *and* its baseline `y` was at or above the 600th-highest baseline among candidates. In the data that cutoff is c = 58.21 (the lowest `y` among treated units). Candidacy depended only on `y` and on study-generated random noise unrelated to any unit characteristic, so **conditional on `y`, receiving Q is unrelated to units' potential changes**. Below c no unit was treated; at or above c, 600 treated and 536 untreated units (the non-candidates) coexist at every part of the range (treated share 27–64% across `y` bins; the highest-`y` control is above the highest-`y` treated unit). Every treated unit therefore has untreated comparators at the same baseline, and the ATT is identified by comparing treated units with untreated units of the same `y` within y ≥ c, with no extrapolation.

Adjusting for `y` matters: `z` rises strongly with baseline among untreated units (≈0.2–0.26 points per baseline point), and treated units have higher baselines. The naive difference in means (3.63 overall; 1.53 within y ≥ c) is confounded by baseline and is not the answer.

## Estimates (region y ≥ c; n = 1136; 1000 bootstrap resamples)
| method | ATT | 95% CI |
|---|---|---|
| **Outcome regression, linear in y (adopted)** | **1.232** | **0.819 – 1.651** |
| Outcome regression, quadratic | 1.230 | 0.825 – 1.641 |
| Outcome regression, cubic | 1.233 | 0.809 – 1.642 |
| Propensity (odds) weighting | 1.230 | 0.798 – 1.692 |
| 5-nearest-neighbour matching on y | 1.102 | 0.708 – 1.615 |
| Stratification, 10 bins | 1.204 | 0.809 – 1.636 |

All methods agree (1.10–1.23), and all intervals exclude zero.

## Checks
- Among untreated units, `z` vs `y` shows no jump at c (jump 0.14, 95% CI −0.56 to 0.84) and no significant slope change, consistent with the non-candidates above c being comparable to the untreated population generally, as the design implies.
- The effect appears to grow with baseline: ≈0.85 (lowest third of treated `y`), 1.25 (middle), 1.60 (highest third), each SE ≈0.25. The 1.23 figure is the average over the treated units.

## Caveats
Estimates assume the stated design (Sections 3–6 of the study description) and smoothness of the untreated `z`–`y` relationship, which the robustness of the different estimators supports. The result is the average effect for the treated units only; it does not describe what Q would do for units with baseline below 58.2, none of whom received it.
