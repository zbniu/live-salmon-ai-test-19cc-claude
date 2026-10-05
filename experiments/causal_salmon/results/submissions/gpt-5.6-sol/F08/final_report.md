# Did tutoring increase gains for the students who attended?

**The evidence supports a positive average effect. My adopted estimate is that attending tutoring increased score gain by 1.20 points on average for the 600 attendees, with an approximate 95% confidence interval of 0.79 to 1.61 points.** This adjusted average effect answers the research question. It is an estimate, not an exact determination of the attendees' unobserved counterfactual gains or of each student's individual effect.

The analysis uses only the supplied study description and the complete data.csv. All 2,000 students were read and validated: 600 attended and 1,400 did not; all three variables were present, with no missing values or duplicate rows. No external data or internet research was used.

## What the comparison shows

| Quantity | Attendees | Nonattendees |
|---|---:|---:|
| Number of students | 600 | 1,400 |
| Mean starting score | 66.84 | 57.23 |
| Mean observed score gain | 12.83 | 9.38 |

The unadjusted gain difference is 3.45 points. **This is not the causal-effect estimate adopted for the question:** attendees started with substantially higher scores, and starting score also predicts gain among nonattendees. Subtracting the two overall group means mixes tutoring's effect with differences in starting score.

## Why adjustment is justified, and how the effect was estimated

The supplied assignment mechanism selects applicants using only starting score and a student-specific random number unrelated to student characteristics, then admits applicants in order of starting score. Thus, conditional on baseline scores in this cohort, the remaining attendance selection comes from those random numbers rather than another student characteristic. The stated absence of switching and interference supports interpreting a baseline-adjusted comparison as an attendance effect. Attendance was not randomized without regard to starting score.

The target is the average treatment effect on the treated: the average of each attendee's gain with tutoring minus that same attendee's gain without tutoring. The latter is unobserved and must be estimated from comparable nonattendees. For this target, comparison support is needed at attendees' starting scores; it is not necessary to estimate an effect for low-scoring students who never attended.

Attendees' starting scores range from 57.36 to 74.98. Nonattendees span 45.01 to 75.00, with 577 nonattendees at or above the lowest attendee score. Every attendee falls within the observed nonattendee score range, and every half-point stratum containing attendees has comparison students. This supplies practical support across the target range. The unreported application scores and applicant list are not required to perform this outcome adjustment.

I fitted untreated gain as a smooth function of starting score using all 1,400 nonattendees: an ordinary least-squares cubic B-spline with interior knots at 50, 55, 60, 65 and 70, and score-scale boundaries at 0 and 100. I predicted each attendee's gain without tutoring at their own starting score, then averaged observed minus predicted gains over all 600 attendees. This allows the average effect to reflect the attendees' score distribution and does not require a constant tutoring effect across starting scores.

The estimated mean gain without tutoring for these attendees is **11.63 points**, compared with their observed **12.83 points**. Their difference is the adopted **1.20-point average effect**. The estimated standard error is 0.210 points. The confidence interval combines HC3 robust covariance for the untreated regression with the sampling variance of attendees' adjusted gains. It is a conventional approximate interval under the regression and independent-error approximation; it is not an exact randomization interval for the fixed-capacity assignment and does not include outcome-model misspecification.

## Checks and limits

Sensitivity analyses used untreated linear through fourth-degree polynomial models; additional models using only controls in the attendee score range; attendee-weighted comparisons in 0.5-, 1-, 2-, 2.5- and 5-point strata; and nearest-control matching with replacement using 1, 5, 10 or 20 neighbors. Their adjusted point estimates range from 1.08 to 1.21 points. The one-point stratified estimate is 1.13 points, with an approximate 95% interval of 0.71 to 1.56. These checks support the direction and approximate magnitude of the primary result. Matching estimates are reported as point-estimate checks only; no naive matching confidence intervals were calculated.

Continuous starting scores preclude exact same-score comparisons, so estimation still relies on reasonable smoothness or sufficiently close comparisons. No finite dataset proves the untreated outcome model correct. The supplied design and consistent adjusted estimates support a positive average effect of about **1.2 points for attendees**, while not establishing a precise effect for every student or an average effect for all 2,000 students.

## Reproducibility

The accompanying submission includes the executed Python code, original input copies, numerical outputs, student-level untreated predictions, and an execution log. The log retains the initial directory-redirection failure and the missing-package failure; the failed Python source and traceback are preserved. These errors occurred before statistical calculations. The successful inspection and analysis each ran once; report generation reads those saved outputs.
