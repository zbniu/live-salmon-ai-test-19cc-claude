# Does tutoring increase score gains for its attendees?

**Answer: the supplied material does not establish whether tutoring increased the attendees' gains, or by how much.** The average causal effect for the 600 attendees is not identified. No numerical point estimate is adopted as the answer to the causal research question.

## What the complete data show

All 2,000 students were analyzed: 600 attended and 1,400 did not. The three supplied variables had no missing values, and no rows were excluded. Starting scores and reconstructed observed end scores (`y + z`) were within 0–100.

| Observed group | Students | Mean starting score | Mean score gain |
| --- | ---: | ---: | ---: |
| Attended | 600 | 66.068 | 14.104 |
| Did not attend | 1,400 | 57.350 | 8.641 |

The observed mean gain difference is **5.464 points** (attendees minus nonattendees). This is an association between attendance and gain, **not the causal effect asked for**. As descriptive checks, ordinary least squares using all rows gives an attendance coefficient of 3.787 points after linear adjustment for starting score, and 3.821 points with a common cubic starting-score curve. These coefficients depend on the adjustment model and do not remove possible selection on unrecorded circumstances. No causal significance test or causal confidence interval is justified by those fits.

## Why the causal answer is undetermined

Let `z(1)` and `z(0)` denote a student's gain with and without tutoring. The question's target is the average of `z(1) - z(0)` over the 600 actual attendees. Their `z(1)` values are observed; their `z(0)` values are not.

The application score combined starting score, unrecorded circumstances, and an independent random number. The top 900 application scores determined applicants; starting-score ranking among applicants then determined the 600 attendees. The independent random component does not make attendance a randomized treatment: applicants were selected using other characteristics, and the application scores, applicant indicators, and random numbers are unavailable. The study does not establish that those unrecorded circumstances are unrelated to untreated gains, or that attendance is independent of potential gains after conditioning on starting score. Every student's having some chance of applying does not establish that independence. Adjustment for `y` therefore does not identify the effect.

There are 607 nonattendees at or above the smallest observed attendee starting score (56.995); attendance is not simply a deterministic threshold in starting score for all students. A possible discontinuity analysis would require further assumptions about continuity of potential outcomes and applicant selection at a cutoff. Those assumptions are not supplied or established by these data. Even if justified, a local cutoff effect would not by itself identify the average effect over all 600 attendees. The uniform class, no switching, no interference, complete records, and blinded outcome recording are useful design features, but do not supply the missing counterfactual comparison.

The ambiguity can be made concrete without changing any observed row or the described attendance process. For attendees, set each unobserved end score without tutoring equal to their observed end score: the average effect is zero. Alternatively set it 0.925 points lower or 0.925 points higher: the average effects are respectively +0.925 and −0.925 points. All these counterfactual end scores stay within 0–100. The unobserved treated outcomes of nonattendees can also be completed within the scale, with the same treatment rule and no interference. These are logically compatible possibilities, not estimates of the hidden data-generating process.

## Numerical information about the causal target

The stated 0–100 end-score scale gives only broad logical bounds. For an attendee, an untreated end score can range from 0 to 100, so their effect can range from `observed_end_score - 100` to `observed_end_score`. The mean observed end score among attendees is 80.173. Thus the finite-study average causal effect can range from **-19.827 to 80.173 points** using the supplied scale restrictions alone. These bounds concern the research question's target; they are neither a confidence interval nor evidence of a positive effect. Both endpoints can be attained by assigning all attendees' untreated end scores to 100 or 0, respectively, without altering the observations. Harm, no effect, and benefit remain compatible with the supplied information.

## Reproducibility

Only the two supplied files were used as study evidence; no internet or external dataset was accessed. `code/analyze.py` generated the group summaries, descriptive regressions, score-bin summaries, logical bounds, and explicitly hypothetical counterfactual examples. Machine-readable outputs are in `results/`; input copies and their hashes are included, and `run_log.txt` records execution. The report's causal conclusion is non-identification, not the raw or adjusted association.
