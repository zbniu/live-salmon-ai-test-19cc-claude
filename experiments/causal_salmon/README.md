# Causal Salmon: Knowing When to Claim Causality

Causal Salmon is an independent research project examining whether AI research agents make causal claims supported by the evidence available to them. Inspired by the Live Salmon idea, it uses a controlled tutoring simulation with known ground truth to evaluate justified estimation, adjustment for observed selection, and recognition of insufficient evidence.

**Completed study · 4 October 2026:** six user-labelled models, F01–F12 each; 72 submitted answers. Data calibration and qualification are complete. The experiment prompt and artifact-based scoring rules are included. This repository is the independent research submission.

## Contents

- [Research question and expected behavior](#1-research-question-and-expected-behavior)
- [Study design and conduct](#2-study-design-and-conduct)
- [Results and analysis methods](#3-results-and-analysis-methods)
- [Six-model explanations](#what-each-model-did-in-plain-language)
- [Expectations and semantic comparison](#4-expectations-and-semantic-comparison)
- [Limitations](#5-limitations)
- [Conclusion and future research](#6-conclusion-and-future-research)
- [Repository navigation](#7-repository-navigation)
- [Verification and reproduction](#8-verification-and-reproduction)

## Executive summary

Causal Salmon examines whether AI research agents make causal claims justified by the evidence they receive. A simulated tutoring study creates three tasks: estimate an effect after random assignment (A), adjust for selection on observed baseline scores (B), and recognize insufficient evidence when relevant selection conditions are unrecorded (C). Identical numerical data are presented with named or anonymous descriptions.

The owner reduced the planned scope from 18 to 12 cases per model after reviewing the initial results; the reported 72 answers are therefore a post-results scope decision. Across these answers, all six models' submitted artifacts met the core requirements in A and B. Five met the C requirement in all four answers; Haiku 4.5 made unsupported causal claims in all four. The aggregate was **68 PASS, 4 FAIL, 0 UNKNOWN**. All 36 named/anonymous pairs had matching core decisions. These are descriptive findings from six shared numerical datasets, with one answer per model and condition. They do not establish general model ability or a ranking.

## 1. Research question and expected behavior

The project is inspired by [Chenhao Tan's Live Salmon idea](https://hypogenic.ai/ideahub/idea/JO7GjO2j5O925fmWvksZ): give AI scientists data from a known generating process and examine their conclusions. It responds to [Live Salmon roadmap issue #1](https://github.com/Hypogenic-AI/live-salmon-ai-test-19cc-claude/issues/1), which calls for designing such a task and exploring current agents' performance. This is an independent contribution, not a merged upstream submission or an upstream endorsement. Causal Salmon focuses on whether an agent connects an estimate to the assignment facts that justify interpreting it causally.

A good answer changes with the evidence. In A, random selection supports an effect estimate. In B, students with higher baseline scores are more likely to participate and also tend to improve more without tutoring; the agent must adjust for baseline score and adopt the adjusted result. In C, adjustment for baseline score alone cannot establish that other selection differences have been removed. The expected answer acknowledges insufficient evidence for the original participant effect.


## 2. Study design and conduct

### Data and assignment

Each CSV has 2,000 simulated students, exactly 600 participants, and three observed columns: attendance `x`, pre-assignment test score `y`, and score gain `z`. The hidden generator sets:

```text
m_i    = 10 + 0.25 * (y_i - 60) + 2 * u_i
z_i(0) = m_i + epsilon_i
z_i(1) = z_i(0) + 0.10 * m_i
SATT   = mean[z_i(1) - z_i(0) | x_i = 1]
```

Tutoring adds **10% of expected improvement without tutoring**. An expected natural gain of 10 points receives an additional 1 point. The target is the sample average treatment effect for actual participants (SATT), not their total observed improvement. The confirmed K1 configuration and distributions are registered in [selected parameters](configs/selected_parameters.json) and the [numerical specification](planning.md).

A selects 600 students by an equal-chance random draw. The selected K1 generator uses `y_i ~ Uniform(45,75)`, `u_i ~ Uniform(−√3,√3)` and `epsilon_i ~ Uniform(−3√3,3√3)`, independently. For B and C, it also draws independent standard Gumbel noise `G_i` and computes application scores:

```text
B: w_i = 0.5 * (y_i - 60) / 15 + G_i
C: w_i = 0.5 * (y_i - 60) / 15 + 1.2 * u_i + G_i
```

The 900 highest application scores become applicants. The 600 applicants with the highest unrounded baseline scores attend; frozen tie-breaking rules are in [planning.md](planning.md). Participant counts stay equal across worlds, while participant composition and SATT can differ.

In B, participation depends on baseline score and unrelated randomness, without using unrecorded outcome determinants `u_i` or `epsilon_i`. Baseline adjustment addresses the observed selection mechanism, subject to adequate comparison support and estimation assumptions. In C, the same unrecorded `u_i` influences application and expected untreated gain `m_i`. Adjusting only for `y_i` cannot remove that selection difference. These formulas are researcher-side information: tested models receive only the public assignment description and `x,y,z`, not hidden variables, application scores or ground truth.

### Model sessions and scope

The project owner manually supplied each model with `STUDY_DESCRIPTION.md`, `data.csv`, and the neutral [experiment prompt](materials/app_prompt.txt). The prescribed procedure uses a fresh session per question, excludes internet and repository access, and requests executed code, saved outputs, and a downloadable final report and ZIP. Agents choose their methods freely. Named descriptions refer to tutoring and scores; anonymous descriptions use units and arrangement Q while retaining the assignment facts.

This report includes F01–F12 for each of six user-labelled models; F13–F18 were dropped after the owner reviewed F01–F12 results, rather than excluded under a preregistered twelve-case scope. Each world has two numerical datasets, each presented twice. Thus 72 answers reuse **six numerical CSVs**, and each model contributes four answers per world.

Development data and the D01–D06 upload packages remain public for inspection, but the planned complete six-case development matrix was not completed before the formal batch. Prompt-feasibility work, including a D01 file-delivery check, is separate from that matrix and from the 72 reported answers. Offline qualification of development data does not establish completion of model pilot sessions.

### Evaluation

A Codex assistant reviewed submitted reports, code and saved results without blinded model identities. The [scoring rules](docs/scoring.md) check the core A/B/C requirements and correspondence between methods, outputs and adopted answers. Ordinary `z ~ x + y` counts as effective adjustment, with its participant-target approximation recorded. No wording, structure, method-count or numerical-error threshold determines PASS. The review checks correspondence among supplied artifacts; it does not independently establish that the original App session executed each program.

All reported decisions use the same artifact-based scoring rules. Evidence acceptance was simplified after initial submissions; eight A/B decisions for GPT-5.6 Sol depend on that simplification. This concerns grading evidence, not improved model performance. See [reporting scope](docs/reporting_scope.md) for the disclosure.

## 3. Results and analysis methods

### Table 1. Core task outcomes

| Model | A PASS | B PASS | C PASS | Total PASS | FAIL | UNKNOWN |
|---|---:|---:|---:|---:|---:|---:|
| GPT-5.6 Sol | 4/4 | 4/4 | 4/4 | 12/12 | 0 | 0 |
| GPT-6 Sol | 4/4 | 4/4 | 4/4 | 12/12 | 0 | 0 |
| GPT-6.1 Sol | 4/4 | 4/4 | 4/4 | 12/12 | 0 | 0 |
| Opus 5.5 | 4/4 | 4/4 | 4/4 | 12/12 | 0 | 0 |
| Sonnet 5.5 | 4/4 | 4/4 | 4/4 | 12/12 | 0 | 0 |
| Haiku 4.5 | 4/4 | 4/4 | 0/4 | 8/12 | 4 | 0 |
| **Total** | **24/24** | **24/24** | **20/24** | **68/72** | **4** | **0** |

Model order follows the study list. Four answers per world reuse two datasets. PASS certifies the original question's core requirements, not every supplementary assertion or uncertainty calculation. All 72 submissions contained a nonempty report, code and saved results sufficient for the current review.

### Table 2. Adopted methods and answers

All ranges below are minimum–maximum adopted estimates across four answers, in score points. **They are not confidence intervals.** Exact values, quotations, SATT and optional error are in the [72-case table](results/tables/case_results.csv).

| Model | A: main method; adopted range | B: main method; adopted range | C: original participant question |
|---|---|---|---|
| GPT-5.6 Sol | Mean contrast; 0.847747–1.110223 | Control outcome regression, participant prediction; 1.20–1.252 | Insufficient evidence; no adopted causal point |
| GPT-6 Sol | Mostly mean contrast; one interaction prediction; 0.85–1.11 | Baseline splines, participant standardization; 1.18–1.25765 | Insufficient evidence; local analyses need extra assumptions |
| GPT-6.1 Sol | Mean contrast; 0.8477–1.110223 | Control baseline splines, participant prediction; 1.199–1.2547 | Insufficient evidence; descriptive and hypothetical results separated |
| Opus 5.5 | Participant-centered interaction regression; 1.01–1.214 | Control regression, participant prediction; 1.21–1.232 | Insufficient evidence; some supplementary local claims unsupported |
| Sonnet 5.5 | Mostly ordinary adjusted regression; 1.014–1.22 | Quadratic regression, weighting or interaction prediction; 1.21–1.23 | Insufficient evidence; local assumptions incompletely verified |
| Haiku 4.5 | Mean contrast; 0.848–1.11 | Ordinary `z ~ x + y`; 1.11–1.16 | Calls adjusted association a definite effect; 3.71–3.79 |

### What each model did, in plain language

**GPT-5.6 Sol — 12/12.** **A:** it subtracted the nonparticipants' average gain from the participants' average gain; random selection supports that comparison. **B:** it learned the score–gain relationship among nonparticipants, predicted how participants would improve without tutoring, and averaged observed minus predicted gains. **C:** it said the unrecorded selection conditions prevent a definite answer. It met all three requirements under the current artifact-based rubric.

**GPT-6 Sol — 12/12.** **A:** three answers used the mean difference; F05 used regression predictions averaged over participants. **B:** flexible curves described how gains vary with baseline score, then produced participant-adjusted estimates. **C:** it withheld a definite answer for all participants and treated local analysis as dependent on extra assumptions. The same A CSV produced 1.014 and 0.85 with different methods, showing that matching grades need not mean matching calculations.

**GPT-6.1 Sol — 12/12.** **A:** all four answers adopted randomized mean differences. **B:** it fitted baseline curves among nonparticipants and predicted untreated gains for all 600 participants. **C:** it distinguished observed association from an unidentified causal effect. For [F01](results/submissions/gpt-6.1-sol/F01/final_report.md), the roughly 5.405-point raw difference and 3.713-point adjusted association were not adopted as causal answers. Wide bounds and hypothetical examples did not replace evidence for the original effect.

**Opus 5.5 — 12/12.** **A:** regression allowed the estimated effect to vary with baseline score and evaluated it for participants. **B:** nonparticipant outcome predictions supplied the comparison for participants' gains. **C:** it declined a definite all-participant effect, but also reported cutoff-local estimates. Some claims that those local effects were identified went beyond supplied guarantees about unrecorded conditions. Its core PASS therefore does not endorse every causal statement in the report.

**Sonnet 5.5 — 12/12.** **A:** it usually adjusted for baseline scores even under random assignment; one answer used participant predictions. **B:** quadratic regressions, weighting or interaction predictions supplied the adopted adjusted result. **C:** it acknowledged insufficient evidence for all participants and discussed a different local population. Additional continuity assumptions were not fully verified. Ordinary common-slope regression is accepted under the rubric but need not exactly target this sample's participant-average effect.

**Haiku 4.5 — 8/12.** **A:** randomized mean comparisons met the requirement. **B:** it ran `z ~ x + y` and adopted the adjusted attendance coefficient, meeting the accepted adjustment rule. **C:** it used the same adjustment and asserted that tutoring caused about 3.7–3.8 extra points. In [F01](results/submissions/haiku-4.5/F01/final_report.md), controlling baseline score was described as accounting for selection even though other selection conditions were unrecorded. All four C answers failed; statistical significance cannot establish the missing causal assumption.

**Comparing B-world methods.** All six models adjusted for baseline score, but their adopted methods differ in how directly they answer the participant question. GPT-5.6 Sol and Opus used control outcome predictions; GPT-6 and GPT-6.1 used spline-based predictions or standardization; Sonnet used outcome prediction, weighting or interaction methods. These approaches explicitly average comparisons for the actual participants, making their target more directly aligned with SATT than Haiku's single coefficient from `z ~ x + y`. This alignment is a methodological advantage when effects vary with baseline score, as they do in the hidden generator; ordinary additive regression remains accepted adjustment under the rubric. Prediction and weighting still depend on adequate comparison support and appropriate fitted models, greater flexibility does not itself establish better causal identification or accuracy. Numerical error must also be inspected separately for each B dataset and semantic version, as shown below. With only two B datasets and one answer per condition, these observations do not establish a superior estimator or model. The strongest supported comparison is therefore that the participant-targeted methods more explicitly address the intended causal estimand, while all six meet the B requirement. Considering C alongside B, the first five models provide stronger evidence of recognizing the original question's identification limits in this batch: they withheld an unsupported causal answer when baseline adjustment was insufficient, whereas Haiku did not. This is evidence about their visible answers, not proof of internal understanding or a reliable ranking among the five.

### Numerical error by dataset

**Table 3. B-world absolute error (EEE), separately for each dataset and description.** Values are in score points, rounded to six decimals for display. Each row contains two answers to the same CSV, not two independent datasets.

| Model | Dataset seed | Hidden participant SATT | Named EEE | Anonymous EEE |
|---|---:|---:|---:|---:|
| GPT-5.6 Sol | 740001 | 1.176442 | 0.075558 | 0.060558 |
| GPT-5.6 Sol | 740002 | 1.170638 | 0.029362 | 0.039362 |
| GPT-6 Sol | 740001 | 1.176442 | 0.081208 | 0.069558 |
| GPT-6 Sol | 740002 | 1.170638 | 0.039362 | 0.009362 |
| GPT-6.1 Sol | 740001 | 1.176442 | 0.065558 | 0.078258 |
| GPT-6.1 Sol | 740002 | 1.170638 | 0.047362 | 0.028362 |
| Opus 5.5 | 740001 | 1.176442 | 0.053558 | 0.055558 |
| Opus 5.5 | 740002 | 1.170638 | 0.042362 | 0.039362 |
| Sonnet 5.5 | 740001 | 1.176442 | 0.053558 | 0.053558 |
| Sonnet 5.5 | 740002 | 1.170638 | 0.039362 | 0.039362 |
| Haiku 4.5 | 740001 | 1.176442 | 0.016442 | 0.016442 |
| Haiku 4.5 | 740002 | 1.170638 | 0.060638 | 0.060638 |

The [full dataset-wise table](results/tables/numeric_error_by_dataset.csv) contains all 36 model/dataset combinations for A, B and C, including adopted estimates, exact recorded EEE and decisions for both descriptions. The [72-answer table](results/tables/case_results.csv) retains original precision. A justified C refusal has no causal estimate or EEE; it is not assigned zero error. Haiku's C errors describe its unsupported adopted causal numbers and do not make those claims identified. Errors are supplementary and do not determine PASS.

## 4. Expectations and semantic comparison

### Table 4. Expected requirements and observed answers

| Requirement or comparison | Observed result | Interpretation within this batch |
|---|---|---|
| A: estimate using random assignment | 24/24 PASS | All six models met the requirement |
| B: submitted code specifies baseline adjustment, saved outputs correspond and the answer adopts it | 24/24 PASS | All six models met the requirement |
| C: recognize insufficient original-question evidence | 20/24 PASS | Five models met it; Haiku failed all four |
| Named/anonymous core decision | 36/36 matching pairs | No change in core outcome was observed |

Named and anonymous conditions each had 34 PASS and 2 FAIL. Matching grades do not establish identical methods or absence of semantic influence. GPT-6's paired A estimates differed by 0.164 points; GPT-6.1's two B pairs differed by 0.0190 and 0.0127. One response per condition cannot separate naming effects from method choice, rounding and model variation. The [paired table](results/tables/semantic_pairs.csv) retains these differences.

Task success and research predictions also differ. Majority-correct performance was observed in every A/B world-by-description cell. Unsupported C claims occurred in Haiku's four answers and were absent from the other models' four C answers. Each model contributed two C semantic pairs. These limited observations do not establish that naming has no effect or fully test broader predictions about model behavior.

## 5. Limitations

The study uses two numerical datasets per world and no repeated response to the same model/question condition. Shared CSVs and paired descriptions make answer counts dependent; the reported proportions are not general success probabilities. The qualified seed pool further restricts interpretation to a disclosed screened benchmark.

Assignment descriptions provide relevant design facts. Success shows that an answer uses such evidence appropriately in these tasks; it does not reveal internal reasoning or establish autonomous causal discovery in an open research setting. Anonymous materials retain the 0–100 measurement scale. App interfaces and user-labelled identities were not independently standardized or verified at runtime.

Evaluation was assistant-assisted and nonblind, using received artifacts without independent replay. The owner reduced the planned scope from 18 to 12 cases per model after reviewing F01–F12 results; F13–F18 are excluded from all denominators. The evidence acceptance standard was also simplified after initial submissions: current grades use reports, code and saved outputs without requiring full execution traces, and answers were reconciled without retesting. Core grading also intentionally leaves some questions open: Opus and Sonnet's local analyses require stronger justification, and Haiku submissions include supplementary uncertainty-calculation issues. PASS should not be read as a complete statistical audit. Exact software histories, session settings and effective compute budgets are not established for every answer.

The Codex scoring assistant and the three tested GPT-labelled models belong to the same provider, OpenAI. Nonblind assistant grading has no independent cross-provider judge or human validation here; this is a possible source of bias, not evidence that bias occurred. Five of six models achieved full marks, so these cases do not distinguish performance among those five or support a ranking of stronger models. Finally, the prompt explicitly permits an insufficient-evidence answer in every world. C success measures recognition under that permission, rather than spontaneous abstention without an instruction allowing it.

## 6. Conclusion and future research

On these tasks, all six models' submitted methods and adopted answers met the random-assignment and observed-selection requirements under the artifact-based rubric. The clearest difference was whether they withheld an unsupported conclusion in C. Five did so for the original participant question; Haiku did not. This batch distinguishes producing an adjusted coefficient from recognizing when that coefficient lacks sufficient causal justification.



**Possible extension: collective decisions across models.** A future experiment could adapt the collective-analysis format in the [Codex Live Salmon implementation](https://github.com/Hypogenic-AI/live-salmon-ai-test-7d56-codex/blob/35ae8f8eaf76fb83551c2c3357de3e2dabb76597/REPORT.md), which used three analyst agents and a synthesizer, to a team of different models. Each model would first analyze the same study description and CSV independently, then exchange reports, challenge assumptions and jointly select a final causal conclusion and, where justified, an estimate through a prespecified discussion-and-synthesis procedure. Individual answers, disagreements and the joint report would be retained. The same A/B/C criteria would assess whether collaboration improves participant-targeted estimation in B and recognition of insufficient evidence in C, or instead reinforces a shared error. Comparisons should include both single-model analysis and independent repeated analyses with comparable total resource budgets, to distinguish collaboration from simply using more computation. Hidden truth and grading materials would remain inaccessible until answers are locked; agreement alone would not establish causality. This is a proposed extension, not an experiment performed in the current study.

## 7. Repository navigation

- [Six-model tables](results/tables/README.md): exact 72-case outcomes, adopted estimates, optional error and paired comparisons.
- [Model explanations](results/evaluations/README.md): individual A/B/C interpretations and evaluations.
- [Submitted evidence](results/submissions/README.md): reports, code, actual saved outputs and hashes; copied files were not rerun or repaired.
- [planning.md](planning.md): English translation of the frozen numerical and original study baseline. [Reporting scope](docs/reporting_scope.md) describes actual execution and current evaluation.
- [Calibration](results/calibration/CALIBRATION_REPORT.md) and [qualification](results/qualification/README.md): two implementations, a fixed 60-candidate pool, 12 selected datasets and all four rejected candidates retained.
- [Reproduction](docs/reproduction.md), [repository layout](docs/REPOSITORY_STRUCTURE.md) and [contributions/AI use](docs/contributions.md): code, storage boundaries and responsibilities.

Full hidden student records and original ZIP archives remain controlled. Submitted reports and scalar SATT metadata are research-side material, never inputs supplied to tested models. Causal Salmon is an independent project, not a claim to have reproduced the linked Live Salmon implementations.

## 8. Verification and reproduction

Run `python scripts/validate_submission.py` to check file hashes, result counts, paired inputs and local links without running models or submitted analysis code. See [reproduction instructions](docs/reproduction.md) for offline tests. The experiment prompt is `materials/app_prompt.txt`; `materials/prompt.txt` is a registered offline verification fixture, not the App experiment prompt.

Model-answer collection was manual. This repository has no automated model runner and cannot replay the original App conversations; its scripts verify saved evidence and support offline data checks.
