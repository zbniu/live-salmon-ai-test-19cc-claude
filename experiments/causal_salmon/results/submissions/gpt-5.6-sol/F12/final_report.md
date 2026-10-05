# Effect of arrangement Q on change among its recipients

## Answer

The data support an increase in change `z` among the 600 units that received Q. **The adopted estimate of their average causal effect is +1.24 points**, with an approximate 95% confidence interval of **0.81 to 1.66 points**. This answers the research question for the recipients, rather than for all 2,000 units. It is an estimated average effect, not a claim that Q helped every recipient or that the exact effect is known.

Recipients' observed mean change was 13.019 points. After adjusting for baseline, their estimated mean change had they not received Q was 11.782 points. The difference, 1.237 points, is the numerical result adopted to answer the question.

## Data and causal comparison

Only the supplied study description and complete CSV were used. All 2,000 rows were analyzed: 600 recipients and 1,400 untreated units. There were no missing values and no duplicated full rows. No rows were removed or values altered.

The target is the mean of each recipient's change under Q minus that same recipient's change without Q. The latter is unobserved. The described assignment mechanism uses baseline `y` and random selection unrelated to unit characteristics. Baseline is therefore the relevant measured selection variable to adjust for. The subsequent baseline ranking makes treatment especially concentrated at higher baselines. Candidate status is unavailable, but the stipulated random selection does not introduce an additional characteristic of the unit that must be adjusted for. The description also supplies consistent treatment and no effects of one unit's treatment on another unit's change.

Recipients' mean baseline was 67.073, versus 56.864 in untreated units. Their unadjusted mean changes were 13.019 and 9.393, a difference of 3.626 points. **That unadjusted difference is not the adopted causal effect** because the groups differ substantially in baseline and untreated change varies with baseline.

Baseline comparison is feasible in this dataset: recipients' baselines range from 58.213 to 74.972, and untreated baselines range from 45.007 to 74.991. No recipient lies outside the untreated range. Every recipient has an untreated unit within 0.090 baseline points. Both treatment groups occur in every one-point baseline band containing recipients. This supports estimating the counterfactual for recipients without extrapolating beyond untreated baseline support. No effect for low-baseline nonrecipients is inferred.

## Estimation and sensitivity

The primary analysis fits untreated change as a smooth function of baseline using a natural cubic spline with six knots at the pooled baseline quantiles 0%, 20%, 40%, 60%, 80%, and 100%. The six knot values are 45.007, 50.885, 57.356, 62.783, 69.079, and 74.991. The spline has six parameters including its constant component. Averaging its predictions over the actual 600 recipient baselines estimates their untreated mean change. Subtracting this average from their observed mean change estimates the average treatment effect on the treated. All untreated rows inform the control curve and all recipient rows enter the target average.

Results were similar with alternative baseline adjustments:

| Baseline model | Estimated effect (points) | Approximate 95% interval |
| --- | ---: | --- |
| Linear | 1.201 | 0.787 to 1.614 |
| Quadratic | 1.238 | 0.818 to 1.657 |
| Natural cubic spline 4 knots | 1.246 | 0.824 to 1.668 |
| Natural cubic spline 6 knots (primary) | 1.237 | 0.813 to 1.661 |
| Natural cubic spline 8 knots | 1.245 | 0.821 to 1.670 |

Nearest-baseline matching with replacement, using 1, 5, 10, or 20 untreated neighbors per recipient, gave estimates of 1.136, 1.108, 1.264, and 1.218 points. These are sensitivity checks, not additional adopted answers. Matching intervals were not calculated because control reuse would invalidate a simple paired-test interval.

## Uncertainty and limits

The primary standard error is 0.216 points. The interval uses heteroskedasticity-robust HC3 covariance from separate treated and untreated outcome regressions, evaluated at the mean recipient spline basis, and a normal approximation. The treated regression supplies uncertainty in recipients' observed mean; it does not impose a constant treatment effect. The recipient baselines are held fixed for this calculation.

The causal estimate relies on the stated assignment mechanism and on estimating the untreated conditional mean smoothly from nearby observed units. Continuous baselines prevent exact, assumption-free recovery of every recipient's untreated outcome. The interval additionally uses an independent conditional-outcome-error working model. The undisclosed selection values, candidate list, and selection distribution prevent an exact design-based randomization interval; the reported interval is approximate and model based. Sensitivity across reasonable baseline models and local matching supports the positive average effect, but cannot prove an exact causal magnitude without modeling assumptions. The supplied material supports the estimated increase of about 1.24 points, not a logically certain individual or exact finite-sample effect.

## Execution provenance

The primary results come from `code/04_estimate_corrected.py` and `results/04_att_models.csv`. `code/01_inspect.py` checked the complete input. An initial attempt, `code/02_estimate.py`, stopped at an unavailable `statsmodels` import and produced no model estimates. `code/03_estimate.py` produced exploratory outputs, but a fitted-mean check exposed a rank-deficient treated spline design handled with an unstable matrix inverse. The corrected analysis uses an SVD pseudoinverse and passes the fitted-mean check. Its point estimate agrees with the earlier run; its corrected uncertainty is adopted here. Earlier code, outputs, and errors remain in the archive and are not replaced. `run_log.txt` records the actual execution order. Input copies are included for reproduction, and no internet or external analytical sources were used.
