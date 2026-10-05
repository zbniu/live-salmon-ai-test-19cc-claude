# Effect of arrangement Q on recipients' change

## Answer to the research question

**The supplied material does not establish whether receiving arrangement Q increased change `z` for the 600 units that received it, or by how much. No causal point estimate is adopted.** The positive observed differences below are associations, not answers to the causal question. This conclusion does not mean that Q had no effect.

The target is the average effect for the actual recipients:

`ATT = mean[z_i(Q) − z_i(no Q) | received Q]`.

Each recipient's change under Q is observed, but their change without Q is not. Their positive observed change alone does not show how they would have changed without Q.

## Data and executed analyses

Only the supplied study description and complete CSV were used. All 2,000 rows were analyzed, with 600 recipients and 1,400 nonrecipients. No values were missing and no rows were excluded. The code checked column names, treatment counts, finite values, measurement ranges, baseline overlap, group summaries, and baseline-bin summaries, and fitted one descriptive linear regression.

| Observed quantity | Received Q | Did not receive Q |
|---|---:|---:|
| Number of units | 600 | 1400 |
| Mean baseline `y` | 65.708 | 56.888 |
| Mean change `z` | 14.124 | 8.719 |
| Standard deviation of change | 3.729 | 3.903 |
| Mean follow-up `y + z` | 79.832 | 65.607 |

The **unadjusted observed difference in mean change is 5.405 points** (recipients minus nonrecipients). Recipients' mean baseline was 8.820 points higher. An ordinary least-squares model of `z` on an intercept, receipt indicator `x`, and centered baseline `y`, using all 2,000 rows, gave an `x` coefficient of **3.713 points**. This is a baseline-adjusted descriptive association; its linear specification and adjustment do not identify the causal effect.

Recipients' baseline measurements ranged from 55.593 to 74.955; 639 nonrecipients had baselines within that range. Baseline overlap supplies potential comparisons but does not establish that their untreated changes would be comparable.

## Why the causal answer is undetermined

Candidate selection depended on baseline, unrecorded circumstances, and an independent random number. The document does not state that the unrecorded circumstances were unrelated to changes that would occur without Q. Receipt could therefore be associated with untreated potential changes even at the same baseline. Adjusting for baseline cannot establish or remove that possible confounding.

An independent random component in a selection score does not make final receipt randomly assigned. Neither the random values, selection scores, nor candidate list are available, and assignment probabilities cannot be recovered from the supplied protocol. There is no observed randomized instrument to use. The subsequent baseline ranking among candidates also does not by itself identify an effect for all recipients: a discontinuity analysis would require additional continuity assumptions and would at most address an effect near a cutoff, rather than this overall recipient effect. Those assumptions and any transport from a local effect are not established here.

The study's consistent treatment, absence of switching and interference, complete follow-up, and blinded measurement support interpretation of the observed records. They do not supply the missing counterfactual comparison or establish that assignment was independent of untreated changes.

## Numerical restriction on the causal answer

Using the stated 0–100 measurement scale as the allowable range of counterfactual follow-up measurements, the data give only the following logical bounds for the recipients' average causal effect:

**-20.168 to +79.832 points.**

These bounds concern the research question directly, but they are not a point estimate or a confidence interval. The recipients' observed mean follow-up is 79.832. If their average follow-up without Q could be anywhere from 0 to 100, their average effect could be anywhere from `79.832 − 100` to `79.832 − 0`. Baseline cancels when comparing the two potential changes for the same unit.

For illustration, assigning each recipient an unobserved follow-up without Q equal to their observed follow-up produces exactly zero effect. Assigning each a counterfactual follow-up of 100 produces the negative endpoint; assigning each 0 produces the positive endpoint. These are hypothetical completions, not observations or estimates. Each leaves the supplied observations and actual selection unchanged; the supplied material imposes no further restriction that rules them out. Thus positive, zero, and negative average effects remain compatible with the information supplied.

The uncertainty is one of causal identification, not merely sampling precision. A small regression standard error or a test of the observed group difference would not resolve it.

## Reproducibility

The accompanying submission contains the exact input copies, executed Python code, actual numerical outputs and captured stdout/stderr, and an execution log. `results/analysis_summary.json` contains the full-precision descriptive differences and logical bounds. The hypothetical completions are explicitly labeled in `results/hypothetical_counterfactual_completions.csv`. No internet resources or external datasets were used.
