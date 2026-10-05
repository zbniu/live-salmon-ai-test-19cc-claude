# Effect of arrangement Q on change

**Answer.** Arrangement Q increased change `z` for the units who received it, on average, according to the randomized comparison. The primary estimate is **1.11 points** of additional change: mean change was 11.10 points among the 600 recipients and 9.99 points among the 1,400 nonrecipients. The approximate 95% confidence interval for the difference in group means is **0.69 to 1.54 points** (two-sided Welch test, *p* = 3.6 × 10⁻⁷).

Assignment was a draw with equal selection chances, all selected units received Q, all 2,000 units were observed, and one unit's treatment could not affect another unit's outcome. This makes the difference in mean changes a causal estimate under the study design. Adjusting for the measured baseline `y` in a linear model gives a similar estimate of **1.22 points** (HC2 robust 95% interval 0.86 to 1.58), a sensitivity check rather than the adopted answer.

The exact average effect *on these particular 600 recipients* cannot be observed: their changes without Q are missing counterfactuals. The 1.11 point figure estimates that average effect using the randomly assigned nonrecipients, rather than measuring each recipient's causal effect directly. The reported intervals describe sampling uncertainty in the respective group comparison/model; they do not reveal the unobserved counterfactual changes exactly.

Source: the supplied study description and complete `data.csv`. No external data were used.
