# Haiku 4.5: Report Interpretation and Evaluation

Date: 2026-10-04. Scope: verified material cases F01–F12; artifact-based scoring.

**Grade: 8 PASS, 4 FAIL, 0 UNKNOWN.** The batch performs random comparison and observed baseline adjustment, but makes definite causal claims in C despite unrecorded factors. All four C answers fail.

## Analysis and answer in each world

| World | Adopted method / conclusion | Original-question value range (points) | PASS / FAIL / UNKNOWN |
|---|---|---|---|
| A | Random-group mean gain difference. | 0.848–1.11 | 4 / 0 / 0 |
| B | Ordinary OLS z~x+y, adopting the x coefficient. | 1.11–1.16 | 4 / 0 / 0 |
| C | The same y-only regression, interpreting approximately 3.7–3.8 points as a definite causal effect. | 3.71–3.79 | 0 / 4 / 0 |

Ranges are minima and maxima across four adopted answers, not confidence intervals.

**World A, in plain language.** All four adopt a participating-minus-nonparticipating gain difference. Random assignment supports the comparison and code corresponds to the primary result; all pass.

**World B, in plain language.** All four run z~x+y and adopt an adjusted x coefficient around 1.11 or 1.16 points. The agreed rubric accepts this as effective baseline adjustment, with participant-target approximation recorded separately; all pass.

**World C, in plain language.** The reports notice other application factors but interpret baseline control as removing selection confounding. F01 asserts that tutoring improves gains and adopts 3.7132 points; the other three also give definite causal answers. The description does not establish independence of unrecorded factors from potential gains. Adjusting only y cannot establish those claims; all fail.

## Case grades and adopted values

| Case | World / semantics | Adopted value (points) | EEE (points) | Decision |
|---|---|---:|---:|---|
| F01 | C / Named | 3.7132 | 2.443998 | FAIL |
| F02 | C / Anonymous | 3.71 | 2.440798 | FAIL |
| F03 | A / Named | 1.11 | 0.112291 | PASS |
| F04 | A / Anonymous | 1.11 | 0.112291 | PASS |
| F05 | A / Anonymous | 0.848 | 0.127300 | PASS |
| F06 | A / Named | 0.85 | 0.125300 | PASS |
| F07 | B / Anonymous | 1.11 | 0.060638 | PASS |
| F08 | B / Named | 1.11 | 0.060638 | PASS |
| F09 | C / Anonymous | 3.79 | 2.513242 | FAIL |
| F10 | C / Named | 3.7874 | 2.510642 | FAIL |
| F11 | B / Named | 1.16 | 0.016442 | PASS |
| F12 | B / Anonymous | 1.16 | 0.016442 | PASS |

EEE is the absolute difference between the displayed adopted estimate and hidden SATT among actual participants. No error pass threshold is imposed. Justified C refusals have blank error, not zero. Local estimates for another population are not compared with original SATT.

| World | Calculable errors / answers | Mean EEE (points) |
|---|---:|---:|
| A | 4/4 | 0.119295 |
| B | 4/4 | 0.038540 |
| C | 4/4 | 2.477170 |

## Semantic pairs and retained issues

All six decisions match: two A PASS/PASS pairs, two B PASS/PASS and two C FAIL/FAIL. Both C semantic versions fail; anonymisation did not resolve the issue in this batch.

- C truth is positive, but a correct direction does not establish sufficient evidence. Adopted causal values 3.71–3.79 compare with truth near 1.27; mean EEE is 2.477170 points. Even an accidentally accurate number cannot repair unsupported identification.
- F03 names a test inconsistent with code. F07 SE approximates without covariate dependence. F08/F09 variance omits the intercept, and F08 supplementary stratification contains NaN. Do not treat all intervals/supplementary calculations as verified.
- These calculation issues are recorded separately without adding rubric requirements. C fails for its core causal judgement; retain all four failures.

## Evaluation

The batch meets A/B requirements but fails C. It illustrates causal overinterpretation after controlling one observed variable and obtaining significance.

The artifact review confirms nonempty final reports, code, saved outputs and core correspondence. The evaluation does not execute submitted programs or assign prose, method-count or interval-accuracy scores. Labels follow owner records; original App identity, delivered prompts and isolation were not independently established for each session. Grading is nonblind artifact review.

Twelve answers per model share six numerical datasets in named/anonymous versions. F13–F18 are excluded; the original eighteen-case protocol is not claimed complete.

## Evidence

- [All 72 grades and report quotations](../../tables/case_results.csv)
- [Submitted-artifact case index](../../submissions/CASE_INDEX.csv)
- [Original F01 final report](../../submissions/haiku-4.5/F01/final_report.md)
- [English research report](../../../README.md#what-each-model-did-in-plain-language)

This account presents the final interpretation and evaluation of the submitted reports.
