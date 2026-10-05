# Tutoring and score gain: final report

## Answer to the research question

The supplied study supports a positive average effect of tutoring for the students who attended. **The adopted estimate is an increase of 1.24 score points in their average gain, with an approximate 95% confidence interval of 0.81 to 1.65 points.** This adjusted average effect for the 600 attendees is the numerical result that answers the research question. It is an estimate, not an exact reconstruction of their unobserved outcomes without tutoring; it does not establish that every attendee benefited.

## Data and causal comparison

Only the attached study description and complete data.csv were used. All 2,000 students were analyzed: 600 attended and 1,400 did not. The file has exactly the specified three columns, no missing or nonfinite values, and 2,000 distinct starting scores.

The relevant quantity is the average, among attendees, of their gain with tutoring minus the gain those same students would have had without tutoring (the average treatment effect on the treated, or ATT).

Attendees' mean starting score was 67.073, compared with 56.864 for nonattendees. Their observed mean gains were 13.019 and 9.393, respectively. Thus, the unadjusted gain difference is 3.626 points. **That unadjusted difference is not the adopted causal answer**, because higher starting scores influence attendance and are associated with larger gains.

The described assignment mechanism depends on starting score and independently generated randomness, with no other student characteristic entering selection. This provides a basis for comparing attendees with nonattendees at the same starting score, accounting for the score-based admissions ranking. The missing applicant list does not introduce an additional student characteristic that needs adjustment. The stated absence of switching and interference supports interpreting attendance as the treatment.

Observed overlap is adequate for the attendee target: attendee starting scores range from 58.213 to 74.972, within the nonattendee range of 45.007 to 74.991. All 600 attendees have an observed nonattendee within 0.090 starting-score points. No inference about a tutoring effect for the lowest-scoring students is needed to answer this question.

## Method and numerical results

I fitted the mean score gain without tutoring as a smooth function of starting score using all 1,400 nonattendees. The primary model was a restricted cubic spline with five knots fixed at the 5th, 27.5th, 50th, 72.5th, and 95th percentiles of the complete starting-score distribution. Knots were determined from starting scores, not from gains. I predicted the no-tutoring gain for each attendee and averaged their observed gain minus that prediction. This directly targets attendees and does not require a common treatment effect for all starting scores.

| Quantity for the 600 attendees | Score-gain points |
| --- | ---: |
| Observed mean gain with tutoring | 13.019 |
| Estimated mean gain without tutoring, at attendees' starting scores | 11.777 |
| **Adopted average effect of tutoring** | **+1.242** |
| Approximate 95% confidence interval for that effect | 0.809 to 1.650 |

The interval uses 3,000 stratified bootstrap resamples, preserving the 600-attendee and 1,400-nonattendee group sizes, refitting the control regression in each resample, and taking the 2.5th and 97.5th percentiles. Its bootstrap standard error is 0.215 points; the random seed was 20261004.

Checks with linear, quadratic, and cubic control regressions, splines with four and seven knots, starting-score strata of widths 0.5, 1, and 2 points, and matching to 1, 5, 10, or 20 nearest nonattendees all retained the full 600-attendee target. Their estimates ranged from 1.11 to 1.26 points and were all positive. Outcome-model prediction checks showed similar errors across the regression forms. These checks support the stability of the primary estimate; they do not independently prove its assumptions.

## Limits of the answer

Causal interpretation relies on the supplied selection description: after accounting for starting score, the selection randomness must be unrelated to students' potential gains. Estimation also uses a smooth conditional mean for nonattendees; with distinct continuous scores, the data cannot reveal exact counterfactual gains without some statistical estimation. The observed overlap and agreement across methods make the fitted comparison credible.

The confidence interval is an approximate model/sampling interval. The bootstrap does not reproduce the fixed-capacity applicant/admission lottery, whose application scores and full probability law are unavailable, so it is not an exact finite-population randomization interval. The exact average causal gain for these particular 600 students is unobserved, and individual treatment effects are not identified. Subject to these limits, the evidence favors an average increase of about **1.24 points** for attendees, rather than the unadjusted 3.63-point difference. The conclusion concerns this simulated study and its attendees.
