"""Write the report from saved estimates; no analysis is rerun."""
from pathlib import Path
import json

root=Path(__file__).resolve().parents[1]
s=json.loads((root/'results/main_estimate.json').read_text())
report=f'''# Tutoring and score gain: final report

## Answer to the research question

The supplied data support a positive average causal effect of attending tutoring for the students who attended. **The adopted estimate is an increase of {s['att']:.2f} score-gain points for the 600 attendees**, with an approximate 95% bootstrap confidence interval of **{s['bootstrap_percentile_95_ci'][0]:.2f} to {s['bootstrap_percentile_95_ci'][1]:.2f} points**. This is an estimate of the average treatment effect on the treated (ATT), not a claim that every attendee benefited or that the exact individual effects are known.

Attendees' observed average gain was {s['mean_gain_attended']:.2f} points. Their estimated average gain if they had not attended was {s['estimated_attendee_gain_without_tutoring']:.2f} points. The difference between these two quantities, {s['att']:.2f} points, is the numerical result that answers the research question.

## Data and causal comparison

Only the attached study description and complete CSV were used; no internet or external data were accessed. All 2,000 students were included: 600 attendees and 1,400 nonattendees. The data have the stated three columns, no missing values, and no duplicate rows.

Attendees had a higher mean starting score (67.07 versus 56.86). Their unadjusted mean-gain advantage was {s['unadjusted_gain_difference']:.2f} points (13.02 versus 9.39). That comparison mixes the tutoring effect with selection by starting score and is not the adopted causal estimate.

According to the study description, selection used starting score and student-independent random application noise; no other student characteristic entered selection. Thus starting score is the stated source of confounding to adjust for. The supplied consistency and no-interference conditions allow comparison with the same tutoring intervention. The applicant list is unnecessary for this adjustment because, at a given starting score, the stated selection mechanism does not use another characteristic of that student. This interpretation relies on the stated independence of the application randomization.

There is good empirical overlap for the attendees: their starting scores range from 58.21 to 74.97, within the nonattendees' range of 45.01 to 74.99. There are 536 nonattendees at or above the lowest attendee score. Every attendee has a nonattendee within 0.090 starting-score points. No attendee was excluded or required extrapolation beyond the observed control-score range. The estimate targets the attendees; it does not require estimating treatment effects for the lower-score students who never attended in this realization.

## Estimation and uncertainty

I estimated the untreated mean gain as a flexible function of starting score, using all 1,400 nonattendees. The main model is ordinary least-squares regression with a restricted cubic spline, five nonconstant degrees of freedom, and six knots at control-score quantiles from 5% through 95%. Knot scores were 46.07, 49.70, 53.58, 57.63, 63.36, and 72.12. I predicted untreated gain at each of the 600 attendees' starting scores and averaged those predictions. Subtracting this counterfactual mean from the attendees' actual mean gain gives the ATT estimate. This procedure does not impose a common tutoring effect across starting scores.

The confidence interval uses 2,000 bootstrap samples, resampling students separately within attendance groups and refitting the control model with the original knots held fixed; random seed 20261004. The bootstrap standard error is {s['bootstrap_se']:.3f} points. This is approximate statistical inference under ordinary student-level resampling and the smooth outcome-regression model. It is not an exact randomization interval for the quota-based admission process; the undisclosed application scores and noise distribution do not permit reconstructing that process.

The result was stable across alternative adjustments:

| Adjustment, standardized to attendees | Estimated effect, points |
| --- | ---: |
| Main restricted cubic spline | 1.252 |
| Other restricted cubic splines (3, 4, 6, 7, or 9 nonconstant degrees of freedom) | 1.236–1.249 |
| Separate control polynomials, degrees 1–3 | 1.201–1.244 |
| Local linear control regressions, bandwidths 0.75, 1.5, or 3 starting-score points | 1.228–1.239 |
| Starting-score strata, widths 1, 2, or 4 points | 1.220–1.246 |
| One nearest-score control per attendee, with replacement | 1.136 |

These are sensitivity estimates of the same attendee-targeted effect, not additional independent studies. The earlier exploratory regressions that imposed an additive treatment coefficient are also retained in the execution outputs, but are not the adopted ATT estimator.

## Limits and conclusion

The exact counterfactual gains and exact realized average causal effect cannot be recovered from this dataset: each student supplies only one observed outcome. Estimating the untreated mean at the attendees' scores requires a smoothness/modeling approximation because scores are continuous. Agreement across spline, local, stratified, and matching estimates supports the stability of the conclusion, but does not prove that any outcome model is exactly correct. The confidence interval does not include every possible model error or dependence among students.

Within the stated assignment mechanism and these estimation assumptions, the evidence supports tutoring increasing attendees' average score gain by **about 1.25 points**, rather than interpreting the raw 3.63-point difference as the effect. There is no basis here to assert benefit for each individual student or an effect on students outside the attendee population.

## Reproducibility

The accompanying submission contains the executed code, actual numerical and graphical outputs, original inputs, and an execution log. The first exploratory script failed because `statsmodels` was unavailable; its code and actual error output are preserved. A subsequent, separately saved script performed the exploratory calculations using the available numerical libraries. The main estimates were executed once and saved; report generation reads those saved results and does not rerun the analyses.
'''
(root/'final_report.md').write_text(report,encoding='utf-8')
assert len(report.strip())>0
print('Wrote final_report.md from results/main_estimate.json; no statistical analysis rerun.')
print('Adopted estimate:',s['att'],'95% bootstrap CI:',s['bootstrap_percentile_95_ci'])
