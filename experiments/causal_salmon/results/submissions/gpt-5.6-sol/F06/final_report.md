# Tutoring and score gain

The research question is whether attending the tutoring class increased score gain `z` for the students who attended, and by how much.

**The randomized study provides statistical evidence of a positive average causal effect. The adopted estimate is an increase of 0.85 score points (0.847747 before rounding) for attendees, with an approximate 95% randomization interval of 0.45 to 1.24 points.** This is the numerical result that answers the research question. It estimates the average additional gain caused by tutoring, rather than the total gain during the term. The exact realized causal effect and each student's individual benefit cannot be determined from these files.

I used only the supplied study description and the complete CSV. All 2,000 rows were analyzed: 600 attendees and 1,400 nonattendees, with no missing or nonfinite values and no exclusions, imputation, or outcome transformations. The observed baseline scores and reconstructed end scores were within the stated 0–100 scale.

| Group | Students | Mean score gain | SD of score gain |
|---|---:|---:|---:|
| Attended tutoring | 600 | 10.758905 | 4.501767 |
| Did not attend | 1,400 | 9.911158 | 4.114024 |

The primary estimate is the attendee mean minus the nonattendee mean: 10.758905 − 9.911158 = 0.847747 points. The attendees' total mean gain of 10.76 points is not the estimated tutoring effect, since students also gained points without tutoring.

The study states that exactly 600 students were selected by a random draw using no student information, everyone complied, and students' attendance did not affect other students' outcomes. These facts support a causal interpretation of the randomized comparison. The comparison does not require the relationship between baseline score and gain to be linear or the treatment effect to be identical for all students.

To match the question's focus on the actual attendees, define their average causal effect as the mean of `Z(1) − Z(0)` over the 600 selected students. Only `Z(1)` is observed for them. The error in the primary estimator relative to this target is the difference between attendees' and nonattendees' mean untreated potential gains `Z(0)`. Under the stated complete random draw, this error has mean zero and variance `S0² × (1/600 + 1/1400)`, where `S0²` is the finite-population variance of untreated gains. Using the observed controls' sample variance (16.925194) to estimate `S0²` gives a standard error of 0.200744 points. The reported interval uses the large-sample normal approximation, estimate ± 1.96 standard errors. Its coverage is approximate over repeated random draws, targeting the attendees selected in each draw; it is not an exact guarantee about these 600 students.

As a conventional randomized-group comparison, the Welch standard error is 0.214163, its 95% interval is 0.43 to 1.27, and its two-sided p-value is 8.05421e-05. This alternative also supports a positive average effect. Its uncertainty calculation differs from the attendee-targeted calculation above.

Attendees started 0.75 points lower on average, and baseline score predicted gain in both groups. Sensitivity analyses therefore adjusted for this pre-treatment score. Separate linear regressions for the two groups, standardized to the attendees' baseline-score distribution, estimated an effect of 1.01 points (HC3 robust, approximate 95% interval 0.65 to 1.38). Separate quadratic regressions gave 1.02 points (0.65 to 1.38); a common-slope linear ANCOVA gave 1.02 points (0.66 to 1.39). These are model-assisted checks, not replacements for the primary randomized comparison, and their intervals use regression-based uncertainty.

A Monte Carlo randomization test, drawing 99,999 assignments of exactly 600 attendees with seed 20261004, produced 4 absolute mean differences at least as large as the observed one. The plus-one two-sided p-value was 5e-05 (Monte Carlo standard error about 2.2e-05). This test concerns the sharp null of no effect for any student, not the hypothesis that the actual attendees' average effect is exactly zero.

The positive average-effect estimate and agreement of the checks support the conclusion that tutoring increased attendees' score gain on average, by roughly one point. They do not establish that every attendee benefited, disclose the score-generating mechanism, or establish an effect for students outside this simulated study. If “definite answer” means an exact, assumption-free value of the realized causal effect, the supplied material does not support one: the attendees' untreated counterfactual gains are unobserved.

The accompanying code and results preserve the actual execution record, including an initial failed import of an unavailable optional package before any statistical calculation. The repaired analysis used NumPy, pandas, and SciPy without installing packages or accessing internet sources.
