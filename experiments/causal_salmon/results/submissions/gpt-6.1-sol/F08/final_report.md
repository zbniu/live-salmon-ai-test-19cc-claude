# Effect of tutoring on score gains among attendees

**Answer:** The supplied study supports a positive average effect of attending tutoring on the score gain of the students who attended. My adopted estimate is **1.22 additional score points per attendee**, with an approximate **95% confidence interval of 0.81 to 1.63 points**. This is an estimate of the **average treatment effect among attendees (ATT)** and is the numerical result that answers the research question. It does not establish that every attendee benefited or identify the exact effect for each student.

## Data and causal comparison

I used all 2,000 rows of `data.csv`: 600 attendees and 1,400 nonattendees. The file has the three specified columns, no missing or nonfinite values, and the stated attendance counts. Only the two supplied files were used; no internet sources were accessed.

The attendees started with higher scores: their mean starting score was 66.84, compared with 57.23 for nonattendees. Their observed mean gains were 12.83 and 9.38, respectively. The resulting **raw difference of 3.45 points is descriptive, not the adopted causal effect**.

According to the study description, application and admission depended on the pretreatment score `y` and random numbers unrelated to student characteristics. Thus, starting score is the relevant adjustment variable: unmeasured student characteristics did not separately determine attendance. The unseen applicant list does not itself require an additional adjustment. Conditional comparisons by starting score use nonattendees to estimate what attendees would have gained without tutoring. The stated absence of switching and interference supports interpreting this as the effect of attendance.

There is useful observed comparison coverage. Attendees' starting scores range from 57.36 to 74.98; nonattendees' scores range from 45.01 to 75.00. All attendees lie within the nonattendee range, and 577 nonattendees have starting scores at or above the lowest attendee score. Both groups occur in every one-point starting-score stratum containing attendees. This supports estimating an effect for attendees without extrapolating beyond the observed control range. It does not justify extrapolating the result to all students or other classes.

## Estimation and adopted result

I fitted the mean untreated gain as a smooth function of starting score using all 1,400 nonattendees: a cubic B-spline with five knot locations at the control-score minimum, quartiles, and maximum (seven basis functions). I then predicted the untreated mean gain at each of the 600 attendees' starting scores. The estimate is the attendee average of observed gain minus that predicted untreated mean:

`ATT estimate = mean over attendees [observed z - estimated mean untreated gain at y]`.

This averages over the actual attendees' score distribution and does not impose the same treatment effect at every starting score.

| Quantity | Score points |
|---|---:|
| Observed mean gain among attendees | 12.826 |
| Estimated mean gain for those attendees without tutoring | 11.607 |
| **Adopted ATT estimate: additional gain due to attendance** | **1.218** |
| Approximate standard error | 0.210 |
| Approximate 95% confidence interval | 0.807 to 1.630 |

The standard error combines variability of attendees' observed-minus-predicted gains with HC3 heteroskedasticity-robust uncertainty in the fitted control mean. A separate 2,000-replicate bootstrap, resampling students within attendance groups and refitting the spline, gives a percentile interval of 0.81 to 1.64 points.

## Sensitivity and limits

The conclusion is stable across alternative adjustments. Linear, quadratic, and cubic models fitted to controls yield ATT estimates of 1.17, 1.21, and 1.19 points. Cubic splines with 4, 6, 8, 10, or 15 knot locations yield 1.20–1.22 points. Direct comparisons within starting-score strata, weighted by the attendees' distribution, yield 1.16 points with one-point strata, 1.21 with two-point strata, and 1.31 with five-point strata. Wider strata can leave more differences in starting scores within strata. Every reported adjusted interval remains above zero.

The causal interpretation relies on the supplied assignment mechanism and on estimating the untreated mean adequately from students with similar starting scores. The spline is an estimated outcome relationship, not a disclosed data-generating formula; the alternative adjustments check sensitivity to its form. Confidence intervals are approximate and assume independent student outcome/sampling variation and adequate estimation of that mean. Neither the bootstrap nor the standard error recreates the fixed-seat admissions process, so these are not exact randomization intervals. Since every student in this study is observed, the intervals represent inferential uncertainty about counterfactual outcomes, not missing observed records. The individual counterfactual gains are unobserved, so the exact realized average effect for these 600 students cannot be read directly from the file.

Within these limits, the evidence supports **an average increase of about 1.2 points in score gain among attendees**, rather than the unadjusted 3.45-point group difference.
