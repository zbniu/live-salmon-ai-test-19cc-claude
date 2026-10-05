# Did tutoring increase score gains for the students who attended?

**The supplied material does not establish whether tutoring increased their gains, or by how much. The average causal effect among the 600 attendees is not identified. No causal point estimate is adopted.** Attendees had higher observed gains, but the admission process permits differences in their gains without tutoring that cannot be measured with the supplied variables.

## Question and analysis

The target is the average treatment effect among the actual attendees: the mean of each attendee's gain with tutoring minus the gain that same student would have had without tutoring. Denote this quantity by ATT. Only the first of those two outcomes is observed for attendees.

I used only `STUDY_DESCRIPTION.md` and the complete `data.csv`; no internet or external dataset was used. The data contain 2,000 students, with 600 attendees and 1,400 nonattendees, exactly the three described columns, and no missing values. All observed starting and reconstructed ending scores (`y + z`) lie between 0 and 100. Every row was included in the descriptive summaries and regression models.

## What the data show

| Group | Students | Mean starting score | Mean gain |
| --- | ---: | ---: | ---: |
| Attendees | 600 | 65.708 | 14.124 |
| Nonattendees | 1,400 | 56.888 | 8.719 |

The observed difference in mean gains is **5.405 points**. This is a descriptive comparison, **not the answer to the causal research question**.

As additional descriptive analyses, I fitted ordinary least-squares models for gain with attendance and starting score. The attendance coefficient was 3.713 points with a linear starting-score adjustment (HC3 95% interval: 3.334 to 4.093), and 3.725 points with a cubic starting-score adjustment (3.343 to 4.107). These intervals quantify uncertainty within the specified associational models; they do not account for selection through unrecorded circumstances or establish causality.

The lowest observed starting score among attendees was 55.593. There were 758 nonattendees below that value and 642 at or above it. Above the lowest admitted applicant's score, the stated admission rule implies that nonattendees were nonapplicants: applicants there would have been admitted. Comparing attendees with these students therefore also compares selected applicants with nonapplicants.

## Why the causal question remains unresolved

Application scores depended on starting score, unrecorded student circumstances, and an independent random component. That random component did not make attendance a randomized treatment: selection also depended on the other components and subsequent admission by starting score. Neither the random component nor applicant status is supplied. The unrecorded circumstances could also influence gains without tutoring. Nothing in the study establishes that adjusting for starting score removes that source of selection.

Consequently, neither the raw difference nor the adjusted attendance coefficients identify the mean counterfactual gain for attendees. Having some chance of applying does not establish comparability of selected applicants and nonapplicants.

Admission by starting score might motivate a local regression-discontinuity analysis under additional assumptions. However, continuity of the relevant potential outcomes and selection near a cutoff is not established by the supplied material. Even a valid local effect near a cutoff would not determine the average effect for all 600 attendees without further assumptions about effect variation. Giving everyone the same tutoring class does not imply that every student benefits equally.

Complete follow-up, no switching, no interference, consistent measurement, and blinded recording remove several other concerns, but they do not provide the missing untreated outcomes or establish exchangeability.

## Numerical implication for the requested effect

Taking the stated 0–100 test-score scale as the support for potential ending scores gives a limited, assumption-transparent bound. Attendees' mean observed ending score is 79.831651. Their mean ending score without tutoring could lie anywhere from 0 to 100 under that support restriction alone. Since starting scores cancel when comparing the same student's gains,

`ATT = mean(observed ending score among attendees) − mean(their ending score without tutoring)`.

Thus the **logical bounds for the requested average causal effect are −20.168 to +79.832 points**. These are outcome-support bounds, not a confidence interval and not a point estimate; they do not assert that effects near the endpoints are plausible. They permit negative, zero, and positive effects. For example, assigning every attendee an untreated ending score equal to their observed ending score produces zero effect, while assigning an untreated ending score five points lower produces a +5-point effect; both completions respect the score scale and leave all observed data unchanged. The supplied material cannot select between those counterfactual explanations.

**Answer:** There is a positive observed association, but a tutoring-caused increase for the attendees is not established, and its magnitude cannot be determined from these two files.

## Execution record

The first analysis attempt failed at import because `statsmodels` was unavailable, before producing numerical results. Its source, empty stdout, and error output are preserved. The corrected attempt used installed NumPy, pandas, and SciPy, including explicit least-squares and HC3 calculations, and completed successfully. `results/` contains the actual summaries, model outputs, support diagnostics, counterfactual examples, and captured streams; `run_log.txt` records execution order. No successful analysis was rerun to replace earlier records. One illustrative −5-point constant-effect completion in the output violates the upper score bound and is marked invalid; it is not used as evidence in this report.
