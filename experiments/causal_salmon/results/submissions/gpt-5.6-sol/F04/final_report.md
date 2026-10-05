# Effect of arrangement Q on change

The supplied randomized study provides strong evidence that receiving arrangement Q **increased change `z` on average among its recipients**. The adopted estimate is **1.11 points**, with an approximate **95% randomization confidence interval of 0.70 to 1.52 points**. This average causal effect, rather than the recipients' total observed change, answers the research question. The data do not reveal the exact counterfactual effect for these particular recipients or establish that every recipient benefited.

## Data and causal comparison

Only the supplied `STUDY_DESCRIPTION(5).md` and the complete `data(5).csv` were used. All 2,000 rows were analyzed; no observations were excluded and there were no missing values. Exactly 600 units received Q and 1,400 did not.

| Group | Units | Mean baseline `y` | Mean change `z` | SD of change |
|---|---:|---:|---:|---:|
| Received Q | 600 | 59.853 | 11.104 | 4.524 |
| Did not receive Q | 1,400 | 60.275 | 9.994 | 4.239 |

The primary estimate is the difference in mean changes: 11.104341 minus 9.994118 = 1.110223 points. The 11.10-point increase observed within the Q group is not itself Q's effect, because controls also improved substantially.

The study description states that the 600 recipients were selected by an equal-chance random draw using no unit information. It also establishes full adherence, no effects on other units, consistent measurement, blinded follow-up recording, and complete observation. These facts support treating the control group as a randomized comparison for recipients' changes without Q. No assumption that all units have the same treatment effect is needed for the primary point estimate.

## Uncertainty and target

The target is the average of `z(1) - z(0)` over the 600 actual recipients, where `z(1)` and `z(0)` denote change with and without Q. Each recipient's `z(0)` is unobserved. Under the stated random assignment, the difference in observed means is unbiased, over repeated draws, for this recipient-average effect: its estimation error is the treated-minus-control difference in `z(0)`.

For this target, the randomization variance of that error is `(1/600 + 1/1400) × S0²`, where `S0²` is the finite-study variance of untreated potential changes. The observed control sample variance, 17.972903, estimates `S0²`. This yields a standard error of 0.206864 points. A large-sample normal interval gives the adopted 95% interval above. Its coverage is approximate over repeated random assignments, for the recipients selected in each draw; it is not an exact reconstruction of these recipients' missing outcomes.

As a conventional two-group check, a Welch analysis gives the same 1.11-point estimate, a 95% interval of 0.69 to 1.54, and a two-sided p-value of 3.55e-07. Its standard error uses both arms' observed variances; the primary interval instead uses the randomization error appropriate to the recipient-average target. Both intervals lie above zero.

## Baseline adjustment and limits

Recipients' mean baseline was slightly lower. Exploratory baseline-adjusted regressions allowed separate baseline trends in each arm and averaged the fitted contrasts over the actual recipients' baseline values. Linear, quadratic, and cubic trends gave estimates of 1.214, 1.214, and 1.213 points, respectively. The linear model's HC3 robust interval was 0.85 to 1.58 points. These model-based sensitivity results support the positive conclusion; they do not replace the adopted design-based estimate or identify individual effects. No model was selected by its p-value.

The supported conclusion is an average causal increase of about **1.11 points** for Q recipients in this study, with the uncertainty stated above. The supplied material does not establish exact individual effects, a common effect across units, persistence beyond the measured follow-up, or effects in an external population.
