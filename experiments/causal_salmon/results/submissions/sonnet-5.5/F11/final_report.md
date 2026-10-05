# Final report: effect of the tutoring class on score gain z, for attendees

## Answer
Yes. Attending the tutoring class increased the score gain of the students who attended it by about **1.2 points** (adopted estimate: 1.23, regression-adjusted ATT; 95% CI roughly 0.8 to 1.7 points on the 0–100 scale). The naive attendee vs non-attendee difference (3.63 points) is **not** the answer: it is mostly selection on start-of-term score.

## Reasoning
- Admission rule: students became applicants through a score = increasing function of y + independent random noise (top 900). The 600 applicants with the highest y were admitted. So attendance (x=1) is determined by y and by a random, characteristic-unrelated component (applicant status). Given y, x is as-good-as-random in the region where both groups exist; no other characteristic influences it. Hence adjusting for y alone is sufficient (no unmeasured confounding, by design).
- z rises strongly with y (slope ~0.27 per point), and attendees have much higher y (mean 67.1 vs 56.9), so the raw difference (13.02 − 9.39 = 3.63) is confounded.
- Overlap: all attendees have y ≥ 58.21. Among students with y ≥ 58.21, 536 did not attend (non-applicants) and 600 attended, so attendees have valid comparison students at the same y. The 864 non-attendees below 58.21 have no attended counterparts and were excluded from the main analysis (they only provide extrapolation, not comparison). The estimand is therefore the effect on attendees (ATT), which is what the question asks.
- Assumptions taken from the study description: no interference, same class for all, no switching, blinded outcome recording, no missing data. Data features (not stated) I checked: the range and overlap of y, linearity of z in y.

## Estimates (all on region y ≥ 58.21 unless stated)
| method | effect of attending | SE |
|---|---|---|
| OLS z ~ x + y | 1.18 | 0.21 |
| + y² | 1.18 | 0.21 |
| + y² + y³ | 1.18 | 0.21 |
| x × (y−67) interaction, coefficient at y=67 | 1.23 | 0.22 |
| **ATT from x×(y+y²) model, averaged over attendees (adopted)** | **1.23** | 0.22 (bootstrap), CI 0.83–1.69 |
| 5-nearest-neighbour matching on y (ATT) | 1.10 | ~0.16 (approx., ignores matching uncertainty) |
| full sample, cubic in y | 1.19 | 0.21 |
| narrow window y in [58.2, 61.2), n=238 | 0.90 | 0.46 |
| window [58.2, 63.2), n=370 | 0.85 | 0.37 |

Estimates agree at about 1.1–1.2 across specifications; the narrow-window estimates are smaller but noisier and statistically compatible with them. Effect heterogeneity in y is mild (interaction model vs additive differ by ~0.05).

## Caveats
- The result is for attendees only; it says nothing about students with y < 58.2, who could not attend.
- Validity rests on the stated design (conditional on y, attendance is driven only by an independent random number) and on correct modeling of z vs y; results were robust to polynomial order and matching.
- Exact point estimate depends on the method (about 0.9–1.2); I report ~1.2 with uncertainty of roughly ±0.4.
