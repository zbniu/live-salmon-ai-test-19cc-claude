# Effect of arrangement Q on recipients' change

**Answer.** Receiving arrangement Q increased the change `z` for the 600 units that received it by an estimated **1.25 points** on the measurement scale, on average. A 95% bootstrap interval for this effect is **0.81 to 1.64 points**. This is the result that answers the research question; it is an average effect for recipients, not a claim that every recipient benefited by that amount.

The treated units' observed average change was 13.02 points. A cubic regression spline fitted to all 1,400 untreated units' changes as a function of baseline `y` predicts an average untreated change of 11.77 points at the 600 recipients' baselines. Their difference is 1.246 points. The interval comes from 2,000 stratified bootstrap resamples of units within the treated and untreated groups, refitting that model each time.

The assignment procedure makes receipt depend on baseline and an unrelated random component. Comparing outcomes conditional on baseline therefore supports a causal interpretation under the described procedure, consistency and no interference. All treated baselines (58.21–74.97) lie within the control baseline range (45.01–74.99); every recipient had at least 15 controls within 0.5 baseline points. The raw treated-minus-control change difference, 3.63 points, is confounded by the much higher treated baseline (67.07 versus 56.86) and is not the answer.

As checks on the functional form, linear control regression gives 1.20 points; cubic polynomial and alternative spline specifications give 1.24–1.26; averaging differences from controls within 0.5 baseline points gives 1.24. These close estimates support the adopted estimate. The exact causal effect cannot be observed for an individual because the same unit cannot both receive and forgo Q. The interval reflects sampling/model estimation under this adjustment and bootstrap procedure, rather than uncertainty about any unreported study feature.

Only the supplied study description and the complete 2,000-row CSV were used. Executed analysis code, outputs, and execution record accompany this report.
