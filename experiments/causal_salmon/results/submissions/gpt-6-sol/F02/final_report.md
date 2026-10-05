# Final report

**Answer:** The supplied study does not establish whether arrangement Q increased the change `z` for the 600 units that received it, or by how much. The average treatment effect on those units is not identified. No numerical causal effect is adopted.

Across all 2,000 units, the treated group's mean change was **14.1241 points** and the untreated group's was **8.7190 points**, a **5.4051-point observed difference**. This is a descriptive comparison, **not** the answer to the causal question: treated units also had a higher mean baseline (65.7076 versus 56.8876), and candidate selection depended partly on unrecorded circumstances that could be related to change.

The 600 recipients were the highest-baseline units among 900 unobserved candidates. The lowest treated baseline was 55.5929, with no treated units below it. A threshold analysis can compare outcomes locally around that value, but it cannot recover the average effect across all recipients from the supplied information. In two-sided local-linear calculations, the outcome jump divided by the treatment jump ranged from −0.15 points with a 3-point bandwidth to 1.48 with a 10-point bandwidth (0.42 with a 5-point bandwidth). These bandwidth-sensitive local comparisons are not the requested effect; identifying even a local causal effect requires continuity assumptions about untreated outcomes at the threshold that the study does not supply.

The 0–100 follow-up scale gives only broad **logical bounds** for the recipients' average effect: **−20.1683 to 79.8317 points**. These are not a confidence interval. Every treated unit's observed follow-up is between 58.69 and 96.97, so counterfactual follow-ups three points above or below the observed value are individually feasible. Thus zero, positive, and negative average effects are compatible with the recorded measurements and assignment description. The data cannot determine the sign or magnitude of the effect asked about.

The calculations use every row of the attached CSV. The code and its recorded outputs are included with this report.
