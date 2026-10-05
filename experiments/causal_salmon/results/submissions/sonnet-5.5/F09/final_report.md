# Did arrangement Q increase the change `z`? — Final report

## Answer
**The supplied material does not support a definite answer.** The only credible estimate of the effect of Q on the units that received it comes from a fuzzy regression-discontinuity analysis at the point where acceptance into Q cut off along the baseline measurement `y`. It is statistically indistinguishable from zero and very imprecise.

**Adopted result (preferred specification: local-linear fuzzy RD, triangular kernel, bandwidth ±10 baseline points around the cutoff y = 56.99, n = 1,348):**
effect of Q on `z` = **−0.2 points, 95% CI about −2.3 to +1.9** (SE 1.06).
Across the other reasonable bandwidths/specifications the point estimates range from about −1.3 to +1.2 points, and every 95% CI includes 0 (widest from about −5.0 to +2.7). There is no evidence that Q increased `z`, but a modest positive effect (up to ~2 points) cannot be ruled out, and neither can a small negative one.

The "obvious" estimates of about +3.8 to +4.0 points (regression of `z` on `x` and `y`) and +5.5 (raw difference in means) should **not** be taken as the answer: they rest on an assumption that is contradicted by the study design (see below).

## Why the simple comparisons are not trustworthy
- Treated units are not a random subset. Assignment depended on the baseline `y`, and also on "other circumstances of the unit that were not recorded" (the selection value included an unobserved part). Those circumstances may also influence `z`, so adjusting for `y` alone cannot remove the bias. Raw difference in means: 5.46 (treated have higher `y`, and `z` rises with `y` even among controls). OLS adjusting for `y`: 3.79 (SE 0.19); restricted to y ≥ cutoff: 4.01 (SE 0.20). Their small standard errors reflect sampling noise only, not this selection problem.
- No other covariates exist, so the unobserved part cannot be controlled for.

## Identification strategy used
From the design: the 900 highest selection values were candidates; the 600 candidates with the highest `y` were accepted. Hence there is a cutoff in `y`:
- No treated unit has y below **56.995** (the lowest treated `y`; 0 of 600 treated units are below it, and all 793 untreated units below it are non-treated).
- Above the cutoff only a fraction of units are treated (the candidates; the rest are non-candidates, who have lower selection values through the unobserved part/random number). The treated share jumps from 0 to roughly 0.4–0.5 at the cutoff (first stage 0.41 at ±10), so this is a *fuzzy* design with one-sided non-compliance.
- Fuzzy RD (2SLS with instrument 1{y ≥ cutoff}, separate linear slopes on each side) estimates the effect of Q on candidates at the cutoff, i.e. on treated units near y ≈ 57, provided potential outcomes (and the mix of unobserved circumstances) vary smoothly in `y` around the cutoff. This is an assumption I cannot test with no further variables; the only check available is the density of `y`, which is smooth across the cutoff (e.g. 670 units within 10 points below vs 678 within 10 points above), as expected because the random component and unobserved part mean candidacy did not alter who was in the study.

## Results (all in `results/`)
| bandwidth h | poly. order | n | first stage | ITT jump in z | Fuzzy RD effect | SE | 95% CI |
|---|---|---|---|---|---|---|---|
| 4 | 1 | 555 | 0.41 | −0.23 | −0.56 | 1.75 | −4.0, 2.9 |
| 6 | 1 | 812 | 0.40 | −0.22 | −0.54 | 1.43 | −3.4, 2.3 |
| 8 | 1 | 1084 | 0.41 | −0.21 | −0.52 | 1.23 | −2.9, 1.9 |
| **10** | **1** | **1348** | **0.42** | **−0.09** | **−0.21** | **1.06** | **−2.3, 1.9** |
| 12 | 1 | 1602 | 0.43 | 0.09 | 0.21 | 0.93 | −1.6, 2.0 |
| 15 | 1 | 1816 | 0.45 | 0.32 | 0.70 | 0.82 | −0.9, 2.3 |
| 20 | 1 | 2000 | 0.46 | 0.49 | 1.07 | 0.75 | −0.4, 2.5 |
| 30 | 1 | 2000 | 0.46 | 0.57 | 1.23 | 0.73 | −0.2, 2.7 |
| 20 | 2 | 2000 | 0.43 | −0.21 | −0.49 | 1.21 | −2.9, 1.9 |
| 30 | 3 | 2000 | 0.37 | −0.48 | −1.32 | 1.88 | −5.0, 2.4 |

(Robust-to-heteroskedasticity standard errors; the full table is in `results/fuzzy_rd.csv`.) The choice of ±10 as "preferred" was made on judgment, not by a data-driven selector; the estimates are sensitive to bandwidth/polynomial order in sign, which is itself a sign of how little information the data hold about the effect.

## Caveats
- The estimate applies only to units near the cutoff (baseline ≈ 57, the lower end of treated units); effects for units with higher baseline cannot be inferred from this design.
- Validity relies on continuity of potential outcomes at the cutoff, including the unobserved circumstances; this cannot be verified here. The cutoff was taken as the lowest treated `y` (the true cutoff lies at or marginally below it, a negligible difference).
- The simple adjusted estimates (~+4) differ from the RD estimates, consistent with (but not proof of) positive selection on unobserved circumstances; the data alone cannot establish the true causal effect more precisely than the intervals above.

**Bottom line:** no definite answer; the best-identified estimate is about 0 points (95% CI roughly −2 to +2), so there is no evidence that Q increased `z` and the data cannot confirm a benefit of any specific size.
