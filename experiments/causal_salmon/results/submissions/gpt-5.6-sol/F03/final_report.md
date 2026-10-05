# Tutoring and score gain

## Answer to the research question

The data provide strong evidence that attending tutoring increased **average score gain for the students who attended**. The estimate adopted for this question is **1.110 points (about 1.11 points)** on the test's 0–100 scale. An approximate 95% randomization-based interval targeting the average effect for the 600 attendees is **0.705 to 1.516 points**.

This is an estimate of an average causal benefit, not a claim that every attendee benefited. The exact effect for these particular 600 students cannot be observed: their gains without tutoring are missing counterfactual outcomes. The supplied material supports statistical evidence of a positive average effect, rather than certainty about that exact effect or its value.

## Data and causal justification

Only the supplied study description and complete CSV were used. All 2,000 rows were analyzed; there were exactly 600 attendees and 1,400 nonattendees, three expected numeric columns, and no missing or nonfinite values. No observations were excluded or transformed in the primary analysis. Baseline scores and reconstructed end-of-term scores were within the stated 0–100 scale.

The study description states that exactly 600 students were chosen by a random draw with equal selection chances, without using student information. All selected students attended, no other students attended, and no student's attendance affected another student's gain. Outcome collection was consistent across groups, with blinded end-score recording. These stated features justify using the nonattendees as a randomized comparison group. Attendance is not confounded by self-selection under this design.

The target is the average of z_i(1) − z_i(0) over the realized set of attendees, where z_i(1) and z_i(0) are that student's gains with and without tutoring. A positive gain among attendees alone would not establish a tutoring effect; nonattendees also gained substantially.

## Primary calculation and uncertainty

| Group | Students | Mean gain, points | Gain standard deviation, points |
|---|---:|---:|---:|
| Tutoring attendees | 600 | 11.104341 | 4.524213 |
| Nonattendees | 1,400 | 9.994118 | 4.239446 |

The primary estimate is the observed difference in mean gains: 11.104341 − 9.994118 = **1.110223 points**. It is selected because it follows directly from the stated random assignment and does not require choosing an outcome regression model.

For clarity about the attendee target, let T be the randomly selected attendee set and C its complement. The estimation error of this mean difference for the actual attendee average effect is mean_T[z(0)] − mean_C[z(0)]. Under the stated complete randomization, that error has expectation zero and variance S_0²(1/600 + 1/1400), where S_0² is the finite-cohort variance of untreated potential gains. The observed control gain variance is an unbiased estimate of S_0². This gives an estimated standard error of **0.206864 points**, and the normal-approximation interval reported above. The coverage is across repetitions of the original random draw, with the attendee target changing with that draw; it is not an exact finite-sample interval or an interval for individual effects. No constant treatment-effect assumption is required for this error identity.

A conventional unequal-variance comparison gives the same point estimate, a standard error of 0.216684, a 95% Welch interval of 0.685–1.535 points, and a two-sided p-value of 3.55e-07. This is a supplementary trial-average comparison; its interval is not the attendee-targeted interval adopted above. Both comparisons support a positive average benefit.

## Starting-score sensitivity analysis

Attendees' mean starting score was 59.853373, versus 60.275083 for nonattendees, a difference of −0.421710 points (standardized difference −0.049). Starting-score ranges overlapped almost completely. Randomization supplies the causal justification regardless of this small observed imbalance.

As a secondary analysis, separate linear regressions of gain on starting score were fitted in each group and standardized to the observed attendees' starting scores. This estimates their conditional-mean average effect as **1.214 points**, with an HC3 robust, conditional-mean 95% interval of 0.853–1.575. Separate cubic polynomial and cubic B-spline regressions with increasing flexibility gave attendee-standardized estimates ranging from 1.211 to 1.235 points across all fitted adjustments, including the linear model. These are exploratory sensitivity analyses, not pre-specified models or independent confirmations. Their agreement suggests the positive finding is not driven by the small starting-score imbalance or a particular regression shape. Their intervals concern modeled conditional means and should not be interpreted as exact intervals for the realized finite set's missing outcomes.

## Scope and execution record

The result applies to average score gain in this simulated cohort and does not establish effectiveness in a different population, the undisclosed gain-generating mechanism, or any particular student's benefit. Randomization permits estimation but does not reveal both potential outcomes for any student. There is no supplied basis for an exact numerical causal effect.

The first analysis attempt stopped at an import because `statsmodels` was unavailable; no statistical calculations ran in that attempt. Its code and traceback were retained. The successful analysis used the available Python, NumPy, pandas and SciPy libraries, including explicit least-squares and HC3 covariance calculations. The archive contains executed code, numerical CSV/JSON results, actual captured execution outputs, and the chronological run log. Earlier outputs were retained, and statistical analyses were not rerun to replace execution records.
