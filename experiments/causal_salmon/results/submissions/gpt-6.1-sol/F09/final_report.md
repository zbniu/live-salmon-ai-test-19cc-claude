# Final report: Did arrangement Q increase change among its recipients?

**Answer: The supplied material does not support a definite answer. Neither the sign nor the average size of Q's causal effect on its 600 recipients is identified. No numerical causal-effect estimate is adopted.**

The question asks what happened to recipients because they received Q, compared with what would have happened to those same units without Q. Its target is the average of `z(1) − z(0)` over the 600 recipients, where `z(1)` and `z(0)` are a unit's changes with and without Q. For recipients, only `z(1)` is observed. A positive observed change is not, by itself, a positive causal effect.

## Data and executed analyses

I used only the attached study description and the complete attached CSV. All 2,000 rows and all three columns (`x`, `y`, `z`) were read. Validation found 600 recipients, 1,400 nonrecipients, no missing or nonfinite values, and baseline values within 0–100. No rows were dropped. The analyses computed group summaries, baseline overlap and bins, and descriptive ordinary least squares regressions using all rows. Regression models included an intercept, receipt indicator, and baseline terms of degree one, two, or three; HC3 standard errors were saved as working-model diagnostics, not causal uncertainty measures.

| Observed quantity | Recipients | Nonrecipients |
|---|---:|---:|
| Number of units | 600 | 1,400 |
| Mean baseline `y` | 66.068 | 57.350 |
| Mean change `z` | 14.104 | 8.641 |
| Baseline range | 56.995–74.988 | 45.024–74.918 |

The **unadjusted observed difference in mean change is +5.464 points** (recipient mean minus nonrecipient mean). This is a descriptive comparison, **not the answer to the causal research question**. Recipients also had a mean baseline 8.719 points higher.

The receipt coefficients after adjusting for baseline were +3.787 points with a linear baseline term, +3.808 with quadratic terms, and +3.821 with cubic terms. These are model-dependent associations. Their similarity does not establish that unrecorded selection factors have been removed.

## Why the causal question remains unresolved

The 900 candidates were selected using baseline, unrecorded circumstances, and an independent random component. Q was then assigned to the 600 candidates with the highest baselines. The independent component makes candidate selection partly random; it does not make actual receipt random or establish that recipients and nonrecipients have comparable untreated outcomes, even at the same baseline. The unrecorded circumstances could affect both selection and change, and the description supplies no assumption excluding this possibility. Neither the random component nor candidate status is available for analysis.

Baseline overlap alone cannot solve this problem. There were 607 nonrecipients at or above the lowest recipient baseline (56.995), and 793 below it. Similar baseline values do not establish comparability on unrecorded circumstances. Having some chance of candidate status is also different from having comparable chances of actual receipt after the capacity rule.

The baseline ranking rule does not, on the supplied assumptions, identify the average effect for all recipients through a cutoff analysis. Such an analysis would need additional assumptions about outcome continuity and candidate selection near a cutoff; a local effect would additionally need assumptions to represent all 600 recipients. Those assumptions are not supplied or established here. Uniform Q, no switching, no interference, consistent measurement, blinded follow-up recording, and complete inclusion are useful safeguards, but do not supply recipients' missing untreated outcomes.

## Direct check of the ambiguity

I constructed three hypothetical completions of the missing potential outcomes. For an assumed constant effect `d`, define `z(0) = z − d*x` and `z(1) = z + d*(1 − x)`. Each completion reproduces every observed change exactly. Choosing `d = +1`, `0`, or `−1` yields, respectively, a one-point benefit, no effect, or a one-point harm for every recipient. Code verified that all potential follow-up measurements in all three examples also remain within 0–100. These are logical examples, not estimates of how the simulation actually generated outcomes. The supplied restrictions on outcomes do not distinguish them; none requires changing the observed assignment or selection rule.

Thus the positive observed comparisons are compatible with causal benefit, no benefit, or harm. **The numerical difference +5.464 points describes the observed groups; it is not an identified effect of Q. Whether Q increased recipients' change, and by how much, remains undetermined.**

## Execution record

`code/analyze.py` performed the analyses once, launched by `code/run_analysis.py`. `results/` contains the numerical tables, JSON summary, actual captured standard output and standard error, and delivery verification. `code/finalize.py` generated and checked this report and archive. `run_log.txt` records execution order and distinguishes early terminal inspections from captured analysis records. No internet or external data were used.
