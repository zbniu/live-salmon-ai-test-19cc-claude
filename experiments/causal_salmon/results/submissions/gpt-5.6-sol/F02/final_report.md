# Arrangement Q and change: final research report

**Answer to the research question:** The supplied study description and data do not establish whether receiving arrangement Q increased change for the units who received it, or by how much. The causal effect among recipients is not identified. I adopt **no causal point estimate**. This is an absence of a definite causal answer, not evidence that Q had no effect.

The question concerns the average effect for the 600 recipients: the average difference between their change with Q and the change those same units would have had without Q. Writing these potential changes as z(1) and z(0), the target is the finite-study mean of z(1) − z(0) among recipients. Their observed change supplies z(1), but their z(0) is unobserved.

## Data and executed analysis

I used only the supplied STUDY_DESCRIPTION.md and data.csv (attached under names ending in “(3)”). All 2,000 rows were analyzed. There were exactly 600 recipients and 1,400 nonrecipients, three columns (x, y, z), and no missing or nonfinite values. No rows were excluded. I computed group summaries, baseline overlap, ordinary least-squares regressions adjusting for baseline, logical effect bounds, and explicit alternative counterfactual scenarios. Follow-up was calculated as y + z.

| Observed quantity | Received Q | Did not receive Q |
| --- | ---: | ---: |
| Number of units | 600 | 1,400 |
| Mean baseline y | 65.708 | 56.888 |
| Mean change z | 14.124 | 8.719 |
| Standard deviation of change | 3.729 | 3.903 |
| Mean follow-up y + z | 79.832 | 65.607 |

Recipients' mean observed change exceeded nonrecipients' by **5.405 points**. This is an observed association, **not the numerical answer to the causal research question**. Recipients also started 8.820 points higher on average. A positive change within recipients does not itself show a positive effect of Q, since their change without Q might also have been positive.

For descriptive baseline adjustment, I fitted z on an intercept, x, and y, obtaining an x coefficient of **3.713 points**. Replacing the linear baseline term with a cubic polynomial gave **3.725 points**. Both models used all 2,000 rows and common baseline slopes across groups. These are model-dependent adjusted associations. Their similarity does not establish that adjustment removed confounding. I do not interpret either coefficient as the effect among recipients, and do not attach a causal confidence interval or significance claim to them.

## Why the causal question remains unresolved

Selection into the candidate group depended on baseline and on unrecorded circumstances, together with an independent random number. Having an independent random component and a nonzero chance of candidacy does not make Q assignment independent of those circumstances. The supplied material does not establish whether those circumstances predict change without Q. We therefore cannot justify the assumption that recipients and nonrecipients with the same baseline would have had the same average change without Q.

Acceptance then favored candidates with higher baseline. Treated baseline values ranged from 55.593 to 74.955; untreated values ranged from 45.014 to 74.988. All recipients were within the observed untreated baseline range, and 642 nonrecipients had baseline at or above the lowest recipient baseline. This observed range overlap permits descriptive comparisons, but does not resolve selection on unrecorded circumstances.

Neither candidacy nor the random selection numbers are observed, so these data cannot exploit the random component directly. A baseline cutoff alone also does not establish a valid regression-discontinuity analysis: candidacy is hidden and the required continuity assumptions are not supplied. Even a valid local cutoff effect would require additional assumptions to answer the average-effect question for all recipients. Identical treatment, no switching, no interference, consistent measurement, blinded recording, and complete data are valuable protections, but do not establish comparability of counterfactual changes. The same arrangement for every recipient also does not establish the same treatment effect for every recipient.

## What can be said about the causal quantity

If the stated 0–100 scale is a hard bound for follow-up under either arrangement, each recipient's no-Q change can lie between −y and 100 − y. Consequently the average effect among recipients is logically bounded by

**-20.168 to 79.832 points.**

These are assumption-light bounds on the causal quantity, not a point estimate or confidence interval. They follow from the observed recipients' mean follow-up (79.832) minus an unknown no-Q mean follow-up between 0 and 100. They include negative, zero, and positive effects. If “0–100 scale” is not intended as a hard bound on potential follow-up, these numerical bounds should not be adopted; the nonidentification conclusion still holds.

The code also checked three concrete alternatives for recipients' unobserved no-Q changes: setting z(0) equal to observed z, observed z − 1, or observed z + 1 gives average effects of **0, +1, or −1 point**, respectively. In each case the resulting no-Q follow-up values remain within 0–100. Each alternative leaves every observed value unchanged and is not ruled out by the supplied design statements. These are illustrative counterfactual scenarios, not fitted or estimated effects.

**Conclusion:** The observed association favors Q, but the supplied material does not determine the sign or magnitude of Q's causal effect among the 600 recipients. Establishing a definite answer would require additional causal assumptions or information about the selection process and untreated potential changes.
