# Effect of tutoring on score gain

**The data provide evidence that tutoring increased score gain on average for students who attended. I adopt an estimated increase of 0.85 score points (unadjusted randomized comparison; approximate 95% confidence interval 0.43 to 1.27 points).** This estimates an average benefit, not a benefit for every attendee or an exactly known causal effect for the particular 600 attendees.

## Data and causal interpretation

This analysis uses only the supplied study description and the complete supplied CSV. All 2,000 records were analyzed: 600 attendees and 1,400 nonattendees. The three columns were as described, with no missing or nonfinite values. Baseline scores and calculated end-of-term scores were within 0–100.

According to the study description, the 600 attendees were selected by a random draw giving every student the same chance, all selected students attended, nobody else attended, and there was no interference between students. Outcomes were recorded consistently and without knowledge of attendance. These facts support a causal interpretation of the randomized group comparison. Baseline score `y` was measured before assignment; gain `z` is the end-of-term score minus baseline score.

## Primary result answering the question

| Group | Students | Mean gain, points | Gain standard deviation |
|---|---:|---:|---:|
| Attended tutoring | 600 | 10.7589 | 4.5018 |
| Did not attend tutoring | 1,400 | 9.9112 | 4.1140 |

The primary estimate is the difference in mean gains: **10.7589 − 9.9112 = 0.8477 points**. Its standard error is 0.2142 points. A two-sided Welch comparison gives an approximate 95% interval of **[0.4275, 1.2680]** and p = 0.0000805. The standard error is calculated as the square root of the sum of each group's sample variance divided by its size; the interval uses the Welch–Satterthwaite degrees of freedom (1,047.10).

The 10.7589-point gain among attendees is not itself the tutoring effect: nonattendees also improved. The 0.8477-point difference is the numerical result adopted to answer the research question.

## Baseline-adjusted check

Attendees' baseline mean was 59.1577, versus 59.9100 among nonattendees. I also fitted separate outcome regressions for the two groups, allowing baseline score to have different slopes by attendance, and averaged their predicted differences over the attendees' observed baseline scores. This directly targets the attendees' baseline distribution. HC3 heteroskedasticity-robust standard errors were used; these model-based intervals condition on the observed baseline scores.

| Baseline regression | Estimated average effect for attendees, points | Approximate 95% interval |
|---|---:|---:|
| Linear | 1.0139 | 0.6499 to 1.3778 |
| Quadratic | 1.0150 | 0.6508 to 1.3792 |
| Cubic | 1.0155 | 0.6510 to 1.3800 |

These checks support the same positive conclusion and suggest a benefit of about one point after adjustment. They are supplementary because the forms of the outcome regressions are not guaranteed by the supplied description; the primary estimate relies on the random assignment rather than a specified baseline response curve.

## Limits and conclusion

Randomization supports estimation of an average causal effect and makes attendees a randomly selected subset of the study students. Nevertheless, each student's score gain without their assigned treatment is unobserved. Thus the exact average causal effect for these particular 600 attendees, and each individual's effect, cannot be determined from these files. The confidence interval above is conventional large-sample uncertainty for the randomized average-effect comparison, not an exact identification interval for the realized attendees' counterfactual outcomes. The supplied material also does not establish generalizability beyond these study students.

**The supported conclusion is a positive average tutoring effect: approximately 0.85 points by the adopted randomized comparison, with baseline-adjusted estimates around 1.01 points.** The exact effect is not known.

## Execution record

The first analysis attempt stopped at import because `statsmodels` was unavailable; it produced no statistical results. Its source and traceback are preserved. The successful attempt used NumPy, pandas and SciPy, with direct least-squares and HC3 calculations. The archive contains executed analysis code, machine-readable results, console records, both supplied inputs, and `run_log.txt`. No internet or external study data were used.
