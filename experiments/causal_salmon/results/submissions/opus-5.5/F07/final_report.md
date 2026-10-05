# Final report: effect of arrangement Q on change `z` among units that received it

## Answer
Yes. For the 600 units that received arrangement Q, receiving it increased their change `z` by an estimated **1.21 points** on the 0–100 scale (average effect on the treated, ATT; bootstrap SE 0.22; 95% percentile CI **0.80 to 1.65**). This is the adopted result. The raw treated–untreated difference (3.45 points) is not the answer: it is mostly confounded by baseline, because treated units have higher baselines and `z` rises with baseline among untreated units.

## Why the effect is identified
Per the study description, treatment = being a candidate AND having baseline `y` at least as high as `c`, the baseline of the 600th accepted candidate (c = min `y` among treated = 57.36). Candidacy depended only on `y` plus a random number unrelated to every unit characteristic. Hence, among units with `y ≥ c`, whether a unit was treated depends only on `y` and that independent random number, so treatment is unconfounded given `y`; and since every unit had some chance of not being a candidate, untreated units exist at every `y ≥ c` (577 untreated vs 600 treated in that region; share treated by 5-point bin 21%–57%). Below `c` nobody was treated. Other conditions needed (no interference, consistent treatment, no switching, blinded and identical measurement, no missing data) are stated in the description. The ATT is therefore estimated by comparing treated units with untreated units of the same baseline, within `y ≥ c`.

## Methods and results (data.csv, all 2000 rows; 1000 bootstrap resamples of the full data, re-deriving `c` each time)

| Estimator | ATT | SE | 95% CI |
|---|---|---|---|
| Naive difference in means (not adjusted, biased) | 3.45 | 0.20 | 3.07–3.83 |
| OLS z ~ x + y, region y ≥ c | 1.16 | 0.21 | 0.76–1.59 |
| **Imputation: linear control model in y ≥ c, averaged over treated (adopted)** | **1.21** | **0.22** | **0.80–1.65** |
| Imputation: cubic control model | 1.21 | 0.22 | 0.79–1.63 |
| Imputation: B-spline fit on all controls | 1.22 | 0.22 | 0.81–1.65 |
| 1-NN matching on y | 1.09 | 0.31 | 0.46–1.63 |
| 5-NN matching on y | 1.08 | 0.25 | 0.59–1.56 |
| ATT odds weighting (cubic logit propensity) | 1.20 | 0.22 | 0.79–1.63 |
| Doubly robust (weighted regression) | 1.20 | 0.22 | 0.79–1.63 |

All adjusted estimators agree at roughly 1.1–1.2 points with confidence intervals excluding zero. The adopted estimator allows the effect to vary with baseline (equivalent to the x×y interaction model, whose x coefficient at the treated mean baseline is 1.21, HC2 SE 0.21). There is modest evidence that the effect grows with baseline (interaction 0.088 per baseline point, p ≈ 0.03), but the averaged effect over the treated units is the quantity asked for.

## Caveats
The estimate relies on the stated assignment mechanism (no confounding given baseline) and on a correctly specified relationship between `z` and `y` among untreated units in the y ≥ c range; linear, cubic, spline, matching and weighting approaches give nearly identical answers, so functional-form sensitivity appears small. Uncertainty is sampling uncertainty only.
