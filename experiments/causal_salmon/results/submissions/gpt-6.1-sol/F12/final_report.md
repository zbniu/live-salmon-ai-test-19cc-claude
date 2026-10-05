# Effect of arrangement Q on change among its recipients

The data support a positive average causal effect of arrangement Q for the 600 units that received it. **The adopted answer to the research question is an estimated increase of 1.25 points in change `z`, with an approximate 95% confidence interval of 0.81 to 1.65 points.** This is an average effect for recipients, not a claim that every recipient benefited.

Only the attached study description and complete data file were used. All 2,000 units were analyzed: 600 received Q and 1,400 did not. There were no missing values or excluded rows.

## Why baseline adjustment is needed

Recipients' mean baseline was 67.07, compared with 56.86 for nonrecipients. Their mean changes were 13.02 and 9.39 points, respectively. The unadjusted difference of 3.63 points is not the adopted causal estimate: assignment favored higher baselines, and untreated changes also increase with baseline in these data. Comparing change scores alone does not remove that imbalance.

The supplied assignment mechanism uses baseline and unit-specific random numbers unrelated to unit characteristics. The subsequent candidate ranking also uses only baseline. This supports comparing treated and untreated outcomes conditional on baseline, rather than assuming the groups are comparable without adjustment. The documented consistency, absence of switching, and absence of interference support the potential-outcome interpretation. The hidden candidate list does not supply an additional unit characteristic that must be adjusted for.

## Estimation and comparison support

The target was the average treatment effect on the treated: the average difference between each recipient's change with Q and the change that recipient would have had without Q.

I fitted untreated change as a function of baseline using a natural cubic regression spline with seven basis functions and equally spaced knots across the observed baseline range (45.01–74.99). I then predicted untreated mean change at every one of the 600 recipients' baselines and averaged observed minus predicted change. All 1,400 nonrecipients contributed to the untreated regression. This approach permits nonlinear baseline relationships and does not impose a constant treatment effect.

Treated baselines ranged from 58.21 to 74.97, entirely within the untreated range of 45.01 to 74.99. Every one-point baseline bin containing recipients also contained nonrecipients. The greatest distance from a recipient's baseline to the nearest untreated baseline was 0.090 points. Thus the recipient target has good empirical comparison support; the absence of recipients at low baselines does not prevent estimating their effect.

| Quantity | Change in points |
|---|---:|
| Observed mean change among recipients | 13.0189 |
| Estimated mean change those recipients would have had without Q | 11.7642 |
| **Adopted average effect of Q among recipients** | **1.2547** |

The confidence interval used 3,000 stratified bootstrap resamples, preserving the 600/1,400 group sizes, with seed 20261004; the bootstrap standard error was 0.216 points. Natural splines with four, five, or nine basis functions, control regressions with linear through cubic baseline terms, and one-point baseline stratification weighted to recipients all yielded positive estimates, spanning 1.20–1.25 points.

## Limits of the answer

The result is a statistical estimate, not an exact reconstruction of unobserved counterfactual changes. It relies on the supplied baseline-only assignment mechanism and estimation of a smooth untreated mean response; finite data cannot establish that response without any modeling assumption. Agreement across the alternative adjustments supports the estimate. The bootstrap interval is an approximate measure of sampling/model uncertainty, not an exact randomization interval for the study's fixed-quota selection scheme: selection values and assignment probabilities were not supplied. The evidence supports an average increase for Q recipients but does not establish individual effects or an effect for all 2,000 units.
