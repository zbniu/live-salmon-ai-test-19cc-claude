# Tutoring and score gains

**Answer to the research question:** The supplied study and complete dataset do not establish whether tutoring increased score gains for the students who attended, or by how much. No causal point estimate is adopted. The positive comparisons below measure associations, not the effect asked about.

## Data and analyses

I used all 2,000 students: 600 attended and 1,400 did not. The dataset has the three specified columns, no missing or nonfinite values, and the stated attendance count. I calculated group summaries, examined starting-score support, and fitted ordinary least-squares regressions of gain on attendance, with no starting-score adjustment and with linear, quadratic, and cubic adjustment. No external information was used.

| Observed quantity | Attended | Did not attend |
|---|---:|---:|
| Students | 600 | 1,400 |
| Mean starting score `y` | 66.068 | 57.350 |
| Mean score gain `z` | 14.104 | 8.641 |
| Mean end score `y + z` | 80.173 | 65.990 |

The unadjusted difference in mean gains is **5.464 points**. Attendance coefficients after linear, quadratic, and cubic adjustment for starting score are **3.787, 3.808, and 3.821 points**, respectively. These are descriptive regression associations; none answers the causal research question. Model-based HC3 standard errors and approximate intervals are retained in the results, but cannot account for unidentified confounding.

Starting-score ranges overlap from 56.995 to 74.918; six attendees are above the highest nonattendee starting score. There are 793 nonattendees below the lowest attendee starting score. Even within the overlapping range, students were not randomly assigned to attendance.

## Why the causal question remains unresolved

For the actual attendees, the target is the average of `z(1) - z(0)`, where `z(1)` is gain with tutoring and `z(0)` is gain without it. Their `z(1)` values are observed; their `z(0)` values are not. Nonattendees' gains cannot automatically substitute for those missing outcomes.

Application depended on starting scores, unrecorded circumstances, and an independent random component. Admission then ranked applicants by starting score. The supplied material does not establish that the unrecorded circumstances are unrelated to potential score gains, even after conditioning on starting score. The random component makes application probabilistic; it does not make attendance random. Its realized values and the applicant list are unavailable, so it cannot be used as an observed instrument. Adjusting for `y` therefore does not establish an unbiased treatment effect.

The common class, perfect compliance, lack of interference, complete follow-up, and blinded outcome recording remove several other concerns, but do not supply the missing counterfactual comparison. Nor does a common class imply a common effect on every student. A cutoff analysis would additionally require assumptions about potential-outcome continuity and applicant composition near the cutoff; those are not supplied, and a local effect would not automatically be the average effect for all 600 attendees.

## What the numerical information permits

If the 0–100 test scale bounds both observed and counterfactual end scores, an attendee's untreated gain must lie between `-y` and `100 - y`. Thus the average causal effect among attendees is bounded by

`mean(y + z | x = 1) - 100` to `mean(y + z | x = 1)`,

or **−19.827 to +80.173 points**. This is a scale-only logical bound, not a confidence interval or a point estimate. It includes harmful, zero, and beneficial effects. If the scale is not a hard bound on counterfactual scores, this numerical bound need not apply; the lack of causal identification still does.

For example, assigning each attendee an untreated end score equal to their observed end score gives zero effect while preserving every observed value. Assigning untreated end scores of 0 gives a +80.173-point average effect; assigning 100 gives a −19.827-point average effect. These illustrative counterfactual completions leave the attendance mechanism and observed dataset unchanged. The description places no outcome-generation restriction that rules them out.

**Conclusion:** Attendees had higher observed gains, but the supplied material supports no definite answer about whether attending caused higher gains. Neither 5.464 points nor the adjusted coefficients should be reported as the causal increase for attendees.

## Reproducibility

The submission includes both supplied inputs, the executed Python analysis and execution wrapper in `code/`, actual numerical outputs and captured stdout/stderr in `results/`, and an execution log. The analysis used Python 3.12.14 and NumPy 2.3.5. The data SHA-256 is `f0f8b9dbd2b7b80890467cf755a72278b3cfa12fb6149ab007a5af5666a911fd`.
