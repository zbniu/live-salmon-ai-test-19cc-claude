# Did tutoring increase score gains for the students who attended?

**The supplied material does not support a definite answer. Neither the sign nor the average size of the causal effect for attendees is identified. I do not adopt a numerical point estimate of that effect.** The positive differences below describe associations, not the answer to the causal research question.

## Question and data

The target is the average effect among the 600 students who attended: the mean of each attendee's gain with tutoring minus that same student's gain without tutoring. In potential-outcome notation, the finite-study target is ATT = (1/600) × sum over attendees of [z(1) − z(0)]. Their z(1) is observed; their z(0) is not. Because baseline score y precedes attendance, the effect on gain is also the effect on end-of-term score.

Only the supplied `STUDY_DESCRIPTION.md` and `data.csv` were used. Code analyzed all 2,000 rows, with exactly the stated three columns, 600 attendees and 1,400 nonattendees. There were no missing or nonfinite values, exclusions, or imputations. All observed end-of-term scores, calculated as y + z, lie within 0–100.

## Observed results

| Group | Students | Mean initial score y | Mean gain z | Mean end score y + z |
| --- | ---: | ---: | ---: | ---: |
| Attended | 600 | 65.708 | 14.124 | 79.832 |
| Did not attend | 1400 | 56.888 | 8.719 | 65.607 |

The unadjusted difference in mean gain is **5.405 points**. Attendees also started **8.820 points** higher on average. Neither the attendees' own mean gain nor the between-group gain difference establishes how much tutoring caused them to improve.

As descriptive checks, ordinary least squares on all 2,000 students gives an attendance coefficient of **3.713 points** when controlling linearly for initial score, and **3.725 points** when controlling with a cubic polynomial in initial score. These are adjusted associations under the specified regression models. HC3 standard errors and model-based intervals are recorded in the results files, but they do not resolve causal identification and are not confidence intervals for the target causal effect.

## Why the causal answer is undetermined

The description says the top 900 application scores determined applicants, and the 600 applicants with the highest initial scores attended. Application scores depended on initial score, unrecorded circumstances, and an independent random component. An independent random component in this selection rule does not make attendance random: admission still depends on the other score components and on initial score. The random component itself is unavailable and cannot be used as an observed instrument.

The unrecorded circumstances could also predict gains without tutoring. Nothing supplied states or establishes that attendees and nonattendees have the same untreated potential gains after conditioning on initial score. Regression or matching on y therefore requires an additional, unsupported causal assumption. The same tutoring class for all attendees does not imply an equal treatment effect for every student. Complete follow-up, consistent measurement, blinding, and lack of spillovers address other problems but do not remove selection bias.

Attendance begins at an observed initial score of 55.593, yet 642 nonattendees have scores at or above that value. The score threshold applies to applicants, whose identities are unavailable. A regression-discontinuity interpretation would need additional continuity and related identification assumptions not supplied here. Even a valid discontinuity estimate would concern students near the admission threshold, rather than automatically answering the average-effect question for all 600 attendees.

The missing counterfactuals illustrate the ambiguity directly. Write S1 = y + z for an attendee's observed end score and S0 for their unobserved end score without tutoring. Leaving every observed row and the assignment process unchanged, S0 = S1 gives zero effect. S0 = 0.99 × S1 gives a positive average effect of 0.798 points. S0 = 0.99 × S1 + 1 gives a negative average effect of -0.202 points. All these hypothetical untreated scores remain within 0–100. The supplied material places no outcome restriction that selects one of these alternatives. These are identification examples, not estimates or reconstructed observations.

If both potential end scores are constrained to 0–100, the purely scale-based bound on the average effect is **[-20.168, 79.832] points**, obtained by allowing each attendee's untreated end score to range from 100 to 0. This is a conditional identification bound, not a confidence interval. It includes harm, no effect, and benefit. If the scale description does not constrain counterfactual scores, even this bound is unavailable.

**Answer to the research question:** attendees had higher observed gains, but these two files do not determine whether tutoring increased their gains, or by how much. A causal point estimate would require additional identification assumptions or information about assignment and untreated outcomes.

## Execution records

`code/analyze.py` performed the analysis once, invoked by `code/run_analysis.py`. `results/analysis.json`, the CSV summaries, and the preserved stdout/stderr contain the actual execution outputs. `code/finalize.py` assembled this report from those outputs and checked the delivery files without rerunning the analysis. The supplied inputs and their SHA-256 hashes are included for reproducibility. `run_log.txt` records execution order and output status.
