# Effect of arrangement Q on change

The data provide strong statistical evidence that arrangement Q increased **average change `z` among the 600 recipients**. The numerical answer adopted for the research question is an estimated increase of **1.110 points**, with an **approximate 95% confidence interval of 0.705 to 1.516 points**. This estimates the additional change caused by Q, beyond the change that would have occurred without Q. It does not establish that every recipient benefited.

## Data and causal comparison

Only the supplied study description and complete CSV were used. All 2,000 rows were analyzed: 600 units received Q and 1,400 did not. The columns and assignment counts matched the description, and all values were finite and nonmissing. No units were excluded.

| Observed quantity | Q recipients | Controls |
|---|---:|---:|
| Number of units | 600 | 1400 |
| Mean baseline `y` | 59.853 | 60.275 |
| Mean change `z` | 11.104 | 9.994 |
| Standard deviation of change | 4.524 | 4.239 |

The adopted estimate is the difference in mean change: 11.104341 − 9.994118 = 1.110223 points. The recipients' observed increase of 11.104 points is not itself Q's estimated effect: controls also increased by 9.994 points.

The study description establishes that exactly 600 units were selected by an equal-probability random draw using no unit information. All selected units received Q, there was no switching or interference, measurement was uniform, follow-up recorders were blinded, and all units were retained. These features justify using the control group to estimate what recipients' changes would have been without Q. Baseline adjustment is not needed to remove treatment-selection confounding in this design.

## Uncertainty for the recipients' average effect

Let `z_i(1)` and `z_i(0)` denote a unit's changes with and without Q. The target is the mean of `z_i(1) − z_i(0)` over the actual 600 recipients. For the unadjusted estimate, estimation error equals the recipients' mean `z_i(0)` minus the controls' mean `z_i(0)`. Under the complete random draw, that error has mean zero and variance `(1/600 + 1/1400) × S_0²`, where `S_0²` is the finite-study variance of changes without Q.

The control sample variance, 17.972903, estimates `S_0²`. It gives a recipient-effect standard error of 0.206864 points. The adopted interval uses the estimate ± 1.96 standard errors. This is a large-sample randomization approximation; it does not assume every unit has the same Q effect. Its coverage concerns repeated random assignments, rather than an exact conditional guarantee for this particular selected set.

For comparison, the conventional difference-in-means Welch analysis gives SE 0.216684, a 95% interval of 0.685 to 1.535, and a two-sided p-value of 3.55e-07. That interval concerns the usual all-unit average-effect comparison and is retained as a supporting result. The recipient-specific interval above is the interval adopted for the stated question.

## Baseline sensitivity checks

Recipients' mean baseline was 0.422 points lower than controls'. Because baseline predicts change, separate regressions were fitted within each assignment group and their predicted mean differences were averaged over the recipients' baseline values. This allows the groups to have different baseline relationships. All rows contributed to every fit.

| Baseline adjustment, standardized to recipients | Estimated additional change (points) |
|---|---:|
| Separate linear regressions | 1.214 |
| Separate quadratic regressions | 1.214 |
| Separate cubic regressions | 1.213 |
| Six five-point baseline bands, weighted by recipient counts | 1.217 |

These are sensitivity estimates, not replacements for the adopted randomized mean comparison. Their agreement suggests that the small observed baseline imbalance does not drive the conclusion. Polynomial adjustments assume an adequate regression approximation; the bands can leave residual differences within bands. The saved HC3 regression intervals describe model-based sensitivity uncertainty and are not the adopted recipient randomization interval.

## What remains unknown

The recipients' changes without Q were not observed. Their exact realized average effect and individual effects therefore cannot be recovered with certainty from these files. Randomization nevertheless supports the positive average-effect estimate and its statistical uncertainty. No claim is made that Q helped every recipient, that effects are constant, or that this estimate applies outside the 2,000 study units.

The executed code, numerical tables, validation results, and ordered execution log accompany this report. An initial exploration attempt failed because `statsmodels` was unavailable; that failure and the successful replacement using NumPy, pandas, and SciPy are retained. No analysis was rerun to erase that record.
