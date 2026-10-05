# Tutoring Causal Judgement Study: Final Research Design

Date: 2026-09-30. Document type: finalised study design.

This document specifies the research objectives, data generation, parameter selection, calibration, case qualification, model inputs, scoring and implementation sequence. Implementers use it as the study specification and begin offline implementation and calibration under Section 12. Numerical settings must be selected and registered through formal calibration under Section 5. Model testing requires qualified data, frozen materials and the operating conditions in Section 13.

Study rules, numerical thresholds and the parameter-selection procedure are fixed here. Calibration results, dataset-specific hidden truth and runtime settings are produced or registered during implementation. A finalised design does not imply that calibration has passed. This document, generator code, reference answers, hidden truth and scoring materials must never enter a tested AI's working directory.

The main text covers the question, variables, true effect, three assignment worlds, parameters, calibration, materials, scoring, isolation, test matrix and implementation sequence. Appendices provide the mathematical random specification, six English study descriptions, the anonymisation table, neutral prompt, report extraction and grading examples.

**Translation and scope note.** This is an English translation of the frozen numerical and original study baseline. The original bytes are retained in `manifests/frozen_protocol.md.gz`; their original SHA-256 remains the identity in historical registrations. App execution, the experiment prompt, artifact-based scoring and the final F01–F12 scope are specified in [reporting_scope.md](docs/reporting_scope.md). The later [data generation protocol](docs/DATA_GENERATION_PROTOCOL.md) governs the screened pool and its seeds. Translation does not revive superseded baseline execution or scoring requirements.

## 1. Study overview

### 1.1 Research question

The study tests whether an AI research agent can distinguish evidence sufficient to determine an effect from evidence that is insufficient. The agent receives data and a truthful description of how participation was decided.

Each tested AI receives a table for 2000 students and a study description. The table contains only tutoring attendance `x`, start-of-term test score `y` and score gain `z`. Every agent answers the same question: **For the students who actually attended tutoring, did attending increase their score gain? If so, by how much?**

All three worlds use the same baseline-variable and potential-outcome rules, with independent random streams. They differ in who participates.

| World | Participation | Is the effect identifiable from the supplied material? | Correct answer |
|---|---|---|---|
| A | Draw exactly K students at random from all students | Yes: participation is independent of student characteristics | Use random assignment to estimate the effect |
| B | Application score uses baseline score and an unrelated random number; the top M become applicants, and the highest-baseline K applicants are admitted | Yes: compare students at the same baseline score | Actually adjust for baseline score and adopt that estimate in the final report |
| C | The B mechanism additionally uses unrecorded personal circumstances in the application score | No: unrecorded circumstances may affect participation and score gain | Explicitly recognise that the available information is insufficient |

In the hidden generator, C's unrecorded circumstances do affect score gain, so baseline-adjusted estimates remain substantially different from truth. Tested agents cannot observe this fact. The description reveals only that unrecorded circumstances enter the application score.

### 1.2 Main objectives

1. **Justified estimation when identification is possible (A and B).** Does the agent use the supplied assignment facts to estimate an effect? In B, does it actually adjust for baseline score and adopt the adjusted result? This is H1.
2. **Unsupported causal conclusions when identification is not possible (C).** Does the agent nevertheless assert an effect and its magnitude when the material is insufficient? This is H2.
3. **Semantic comparison.** Pair the same data with a named tutoring/score description and an anonymous arrangement-Q/measurement description. Compare the answers under H-sem.
4. **Validity check.** If most B/C reports never mention assignment, C outcomes cannot be interpreted as evidence of causal judgement ability. This is V0.

Section 10.6 defines the exact decisions.

### 1.3 Purpose of the semantic comparison

Named descriptions expose agents to familiar priors such as tutoring improving scores. Anonymous descriptions retain identical numbers and assignment facts, changing only domain terminology. Paired differences are exploratory evidence about wording cues, but model randomness may also produce differences. A small number of responses cannot exclude that explanation. Anonymous descriptions retain the 0–100 scale, which may suggest test scores; anonymisation does not eliminate all prior knowledge.

### 1.4 Requirements for task-appropriate data

Every tested dataset must satisfy two levels of qualification. Its hidden tutoring increment must follow the specified rule, and a correct reference analyst restricted to public material must be able to complete the intended task. Generation formulas and individual identities establish the first level. Public reference analysis and case qualification in Section 6.12 establish the second. Passing aggregate calibration does not automatically qualify a particular test case.

- A: public material supports random comparison, and reference analysis gives a sufficiently precise positive estimate.
- B: the raw difference overestimates the effect; public baseline adjustment is sufficiently precise, improves bias and provides an identifiable adopted result.
- C: public material cannot rule out hidden confounding; the reference report recognises insufficiency and avoids an unconditional causal point conclusion. Statistical significance is not the correctness target.

The reference analyst is a predetermined statistical program plus a public-material logic check. It does not call tested models or use their answers to qualify data. Qualification establishes an analysis path consistent with the scoring contract, without guaranteeing that an arbitrary AI takes that path or answers correctly.

### 1.5 Fixed rules and execution registration

Follow the study rules and acceptance criteria in this document. Select the seven numerical parameters from the predetermined candidates under Section 5. Public participant counts must match the selected settings. Register models, budgets, tools, personnel and isolation before pilot testing under Section 13. Compute hidden SATT from each dataset's potential outcomes; do not choose it manually.

## 2. Variables, timing and units

| Symbol | Meaning | Timing | Units and values | Visible to tested AI |
|---|---|---|---|---|
| `x_i` | Tutoring attendance: selected/admitted students attend; no dropout or replacement | Decided after the baseline test | `0` or `1` | Yes |
| `y_i` | Start-of-term test score | Measured before participation is decided | 0–100 points; public values retain fully recoverable internal float64 precision | Yes |
| `z_i` | Score gain = end-of-term minus start-of-term score | Follow-up test occurs after tutoring | Score points, possibly negative; fully recoverable float64 precision | Yes |
| `u_i` | Unrecorded learning circumstances | Exist before the term starts | Unitless, mean 0 and variance 1 | No |
| `ε_i` | Random fluctuation in score gain | — | Score points | No |
| `m_i` | Expected untreated gain conditional on `y_i,u_i` | — | Score points | No |
| `z_i(0),z_i(1)` | Potential gains without and with participation | — | Score points | No |
| `G_i,w_i` | Random application-score component and application score in B/C | During assignment | Unitless | No |
| Applicant and admission indicators | Applicant and admitted status in B/C | During assignment | Yes/no | No |

Rows retain generation order, `i = 0,1,…,n−1`. Students' baseline variables `y,u,ε` are generated independently and identically. Fixed slots and ranking induce dependence between students' `x` values, so complete rows including `x` are not independent draws. Row indices do not encode characteristics.

## 3. Potential outcomes, the 10% effect rule and target SATT

### 3.1 Generation formulas

All worlds use identical formulas and sampling rules, with independent world streams under Appendix A. Candidates within a world share the corresponding random numbers.

- `y_i ~ Uniform(a,a+30)`, `u_i ~ Uniform(−√3,√3)`, `ε_i ~ Uniform(−b,b)`, mutually independent.
- `μ_y = a+15`, the theoretical baseline-score mean.
- `m_i = 10 + γ·(y_i−μ_y) + 2·u_i`, where `γ > 0`.
- `z_i(0) = m_i+ε_i`.
- `z_i(1) = z_i(0)+0.10·m_i`.
- Observed `z_i = z_i(x_i)`.

### 3.2 The 10% effect rule

Tutoring adds 10% of expected untreated gain `m_i`; it does not amplify random fluctuation `ε_i`. Individual truth is `τ_i = z_i(1)−z_i(0) = 0.10·m_i`.

For example, an expected untreated gain of 10 points becomes 11 points under tutoring: a 1-point effect. Even if bad luck produces an actual untreated decline, `z_i(0)<0`, the effect remains `+0.10·m_i`, because Section 3.4 ensures `m_i>0`. It is neither a 10-point addition to baseline score nor multiplication of the entire follow-up score by 1.10.

### 3.3 Target: sample average treatment effect on participants

The target for each dataset is the average effect among its actual participants:

`SATT = (1/K)·Σ_{i:x_i=1} τ_i = 0.10 × mean(m_i among participants)`

Compute it separately from hidden variables, not as the average for all students. B/C participants have higher baseline scores and expected gains, so SATT in score points can differ across worlds. The 10% proportion holds in all worlds.

### 3.4 Range guarantees

Parameters must satisfy all three analytical conditions, without clipping:

1. `m_min = 10−15γ−2√3 > 0`, making every individual effect positive.
2. `a+m_min−b ≥ 0`, keeping both potential follow-up scores `y+z(0)` and `y+z(1)` nonnegative.
3. `a+30+1.1·(10+15γ+2√3)+b ≤ 100`, keeping potential follow-up scores at most 100.

Because `y+m` increases monotonically with `y`, its lower endpoint occurs at `y=a`, and its upper endpoint at `y=a+30`.

Every dataset must additionally verify, student by student, `m_i>0`, `τ_i>0`, `|τ_i−0.10m_i|≤1e−9`, and both potential follow-up scores in `[0,100]`. A participant-average identity cannot replace individual checks. Holding other conditions fixed, `γ>0` makes expected untreated gain and the tutoring increment increase with baseline score. Hidden circumstances and noise can still change the ordering of observed outcomes.

A positive individual effect means a positive difference between that student's two potential outcomes. It does not require every observed `z` to be positive or every random dataset to have a larger participating-group mean.

## 4. Assignment in the three worlds

Fix `n=2000`. Require `0<K<M<n`, `K≥100`, and K divisible by 5. Participant-baseline quintiles then contain approximately `K/5≥20` participants each.

### 4.1 World A: random draw

Give each student an independent uniform lottery key. Exactly the K smallest keys receive tutoring. The lottery is independent of `y,u,ε` and potential gains.

### 4.2 World B: baseline score and unrelated randomness

1. Generate an independent standard Gumbel `G_i` for each student. Set `w_i=β·(y_i−μ_y)/15+G_i`, with `β>0`.
2. The M highest application scores become applicants.
3. Among applicants, admit the K highest **unrounded** baseline scores. All admitted students attend; nobody else does.

### 4.3 World C: unrecorded circumstances in application

Use `w_i=β·(y_i−μ_y)/15+κ·u_i+G_i`, with `κ>0`; everything else follows B. The same `u_i` enters `m_i`, affecting both applications and score gains.

### 4.4 Ranking and ties

For application and admission ranking, compare the primary key first: `w_i` for applications and unrounded `y_i` for admission, descending. Resolve primary-key ties using a separately pregenerated independent tie key, descending; remaining ties favour the smaller row index. A lottery-key ties favour the smaller row index. Ranking uses full internal precision, recoverable from the CSV, without separately rounding ranking variables. Appendix A defines streams.

### 4.5 Identical participant counts

Construction guarantees exactly K participants in every world and exactly M applicants in B/C. Because M>K, all slots are filled. There is no redrawing or seed selection. An exception is an implementation error under Section 6.8.

The fixed-M pool is a **simulation mechanism** controlling applicant count. Higher-baseline students are more likely to apply, while some similarly scoring students do not. It is not a literal model of independently voluntary decisions. Appendix B describes the simulated mechanism truthfully.

### 4.6 Why B is identifiable and C is not

- **A:** assignment uses a lottery unrelated to students. Participants and nonparticipants are comparable in `u,ε`; their mean-gain difference directly estimates SATT.
- **B:** application reads only `y_i` and independent `G_i`; admission reads only `y_i`. Given y, participation is independent of hidden `u,ε`. Fixed slots induce dependence between admissions without introducing unrecorded outcome determinants. Comparing equal-baseline students and averaging over participant baselines identifies the target. Participants concentrate at higher scores, so every occupied participant-score segment needs sufficient nonparticipants under CAL-4.
- **C:** `u_i` affects both application and expected gain. At the same baseline, participants have systematically higher u and would naturally improve more. Visible `x,y,z` cannot separate this advantage from tutoring, so SATT is not identifiable. The assignment mechanism, rather than a significance test, establishes this limitation.

## 5. Parameters: candidates, sweep order and selection

### 5.1 Candidate table

Formal calibration evaluates all five candidates, in fixed priority K1–K5. Candidates test baseline selection, application-pool size, noise and hidden selection strength. Select an entire row.

| ID | `a` | `b` | `γ` | `β` | `κ` | `M` | `K` | Purpose |
|---|---|---|---|---|---|---|---|---|
| K1 | 45 | `3√3` | 0.25 | 0.5 | 1.2 | 900 | 600 | First choice |
| K2 | 45 | `3√3` | 0.25 | 0.3 | 1.2 | 900 | 600 | Weaker baseline application selection; more high-score nonparticipants for CAL-4 |
| K3 | 45 | `3√3` | 0.25 | 0.5 | 1.2 | 800 | 600 | Fewer applicants; more high-score nonapplicants for CAL-4 |
| K4 | 45 | `2√3` | 0.25 | 0.5 | 1.2 | 900 | 600 | Lower noise for A precision under CAL-3 |
| K5 | 45 | `3√3` | 0.25 | 0.5 | 1.6 | 900 | 600 | Stronger hidden selection and C bias under CAL-7 |

All satisfy the count conditions. Analytical CAL-1 values for K1/K2/K3/K5 are `m_min≈2.786` and potential follow-up bounds approximately `[42.590,99.132]`; K4 has `m_min≈2.786` and `[44.322,97.400]`. These establish only CAL-1's analytical component, **not successful formal calibration**.

### 5.2 Fixed sweep order

Run 1000 repetitions for every candidate and world, in K1–K5 order. Retain every result and do not stop when an earlier candidate passes. All candidates share calibration seeds from Appendix A, hence identical random numbers for the same seed with different parameters.

### 5.3 Selection procedure

1. **Assign status.**
   - **Pass:** CAL-1 and CAL-3–CAL-7 pass, with no diagnostic-conflict or unavailable-diagnostic flag.
   - **Pass, review required:** all hard criteria pass, with the Section 6.7 design-review flag.
   - **Fail:** any hard criterion fails.
   - CAL-2 and CAL-8–CAL-11 are integrity checks. Failure indicates an implementation error, invalidation and recalculation under Section 6.8, not candidate rejection.
2. **Select in order.** Inspect K1–K5:
   - Recommend the first unflagged passing candidate and stop inspecting.
   - For a flagged pass, the design reviewer explains the issue. The research owner chooses in writing to accept with reasons, or skip to the next candidate.
   - Skip failed candidates.
   - If none is selected, follow Section 5.4.
3. **Written confirmation.** The owner confirms the selected full row. Archive confirmation with the calibration-report hash, then freeze parameters.

### 5.4 No selected candidate

Stop and report all failure reasons. Before trying new candidates, register a revised candidate table and ordering, obtain owner approval and rerun all checks with **reserve calibration seeds** from Appendix A. Do not tune candidates repeatedly against the original seeds until they pass.

### 5.5 After selection

Substitute M/K placeholders in descriptions under Section 7.4, freeze all six descriptions and the prompt by hash, and complete CAL-9. Only then generate development and formal data.

## 6. Formal calibration

### 6.1 General rules

- Complete calibration before development data, formal data or tested-model outputs exist.
- Use `R=1000` independent repetitions per candidate/world, seeds 703000–703999.
- The main implementer runs calibration; an independent implementer recomputes everything using separately written code under Section 6.9.
- Retain every repetition, candidate and failure. Never delete repetitions, relax thresholds afterwards or change seeds.
- Estimators use only the public projection `(x,y_pub,z_pub)` recovered at full precision from CSV. Hidden potential outcomes supply truth. Public y equals the internal admission-ranking y, avoiding loss of assignment information through rounding.

### 6.2 Saved quantities per repetition

| Quantity | Definition | Worlds |
|---|---|---|
| Identity | Candidate, world, seed, public CSV SHA-256 | All |
| Counts | `Σx=K`; applicants=M | All; applicants only B/C |
| `T_r` | Hidden dataset SATT under Section 3.3 | All |
| CAL-2 difference | `\|mean_{x=1}(z(1)−z(0))−0.10·mean_{x=1}m\|` | All |
| `N_r` | Raw participating-minus-nonparticipating mean `z_pub` | All |
| `E_r,se_r` | Primary estimate and standard error under Section 6.3 | All |
| `I_r`, coverage | `[E_r−1.96·se_r,E_r+1.96·se_r]`; `1[T_r∈I_r]` | All |
| Segment counts | Participant-baseline quintile counts `n_{T,k},n_{C,k}` under Appendix A.9 | B/C |
| D1/D2 | Estimates, SE, coverage and status; D2 maximum normalised weight, effective sample size, bootstrap failure count and indices | B |

### 6.3 Primary methods

- **A:** `E=z̄_T−z̄_C`; `se=sqrt(s_T²/K+s_C²/(n−K))`, sample variances with `ddof=1`.
- **B/C:** ordinary least squares with four columns `[1,x,y−c,x·(y−c)]`, using public y and participant mean c. The x coefficient is the participant-standardised estimate E. Use the square root of its HC3 covariance diagonal for SE. HC3 uses row residual squares divided by `(1−h_i)²`, with leverage h_i.

These are calibration reference methods, not mandatory tested-agent methods. Section 8 permits any valid method. In A, treated variance includes variation in the increment, positively correlated with untreated gain in this generator. SE is therefore often slightly conservative; higher-than-nominal coverage is not failure. B/C coverage direction is determined empirically, not assumed.

### 6.4 Across-repetition statistics

All standard deviations use `ddof=1`.

- `bias=mean_r(E_r−T_r)`; `MCSE=SD_r(E_r−T_r)/√R`.
- `relative_bias=|bias|/mean_r(T_r)`.
- `coverage=mean_r(coverage_r)`.
- Precision ratio `=mean_r(T_r)/SD_r(E_r−T_r)`.
- Separation ratio `=mean_r(N_r−E_r)/SD_r(E_r)`.

Apply the same formulas separately to D1/D2 for diagnostic bias, MCSE, relative bias and coverage.

### 6.5 CAL-1–CAL-11 acceptance conditions

| ID | Worlds | Condition | Interpretation |
|---|---|---|---|
| CAL-1 | All | All three analytical conditions in Section 3.4; every simulated potential follow-up score in `[0,100]` | Analytical failure rejects a candidate; simulated violation of valid bounds is an implementation error |
| CAL-2 | All | Every CAL-2 difference `≤1e−9` | Identity/integrity |
| CAL-3 | A | `\|bias\|≤3·MCSE`; `coverage≥0.93`; precision ratio `≥3` | Coverage above nominal is not failure |
| CAL-4 | B/C | In at least 999 of 1000 repetitions, every quintile has `≥20` nonparticipants | Simulation screen, not proof of a future failure rate ≤0.1% |
| CAL-5 | B | Separation ratio `≥2` | Raw and adjusted estimates sufficiently separated |
| CAL-6 | B | Primary `relative_bias≤0.10` and `coverage≥0.90`; run and report D1/D2 without using them as hard gates | Section 6.7 governs conflicts |
| CAL-7 | C | Primary `relative_bias≥0.50` | Hidden circumstances have numerical impact; no p-value criterion |
| CAL-8 | All | Same baseline-generation code/rules, independent world streams and outcome formulas; recomputing saved m/z0/z1 from y/u/ε is bit-identical | Integrity |
| CAL-9 | Materials | Paired CSV bytes/hashes identical; anonymised text equals mechanical replacement; descriptions differ only in Section 3; B/C differ only in its first sentence | At material freeze and every development/formal dataset |
| CAL-10 | All | Seed purposes disjoint and registered; retain all candidates/failures; no result-based seed choice | Integrity |
| CAL-11 | All | Exactly K participants; exactly M applicants in B/C | Construction invariant |

Only CAL-1 and CAL-3–CAL-7 determine candidate status.

### 6.6 Two diagnostics for B

Diagnostics detect problems the primary method may hide. They are not CAL-6 hard gates.

**D1: participant-baseline quintiles.**

- Use the same participant-y rank partition as CAL-4 and Appendix A.9. The first four bins are left-closed/right-open; the last includes both ends. Students outside the participant range belong to no bin.
- `ATT_D1=Σ_k(n_{T,k}/K)·(z̄_{T,k}−z̄_{C,k})`.
- `SE_D1=sqrt(Σ_k(n_{T,k}/K)²·(s²_{T,k}/n_{T,k}+s²_{C,k}/n_{C,k}))`, with `ddof=1`; interval=estimate±1.96·SE.
- Fewer than two participants or nonparticipants in any bin makes that repetition's D1 unavailable.

**D2: weighting by actual participation propensity `P(x=1|y)`.**

- Support includes only `y_pub≥minimum participant y_pub`; nonparticipants outside it receive zero weight.
- Fit `logit P(x=1|y)=θ₀+θ₁s+θ₂s²`, `s=(y_pub−μ_y)/15`, with Appendix A.9 Newton iteration. μ_y only centres numbers. An intercept-containing quadratic is invariant to affine transformations of s, so μ_y does not change fitted propensities.
- On support, nonparticipant weight is `ê/(1−ê)`. Report `ATT_D2=z̄_T−Σw_i z_i/Σw_i`, maximum normalised weight and effective sample size `(Σw)²/Σw²`.
- Within each repetition, run `B=200` stratified bootstraps, sampling K participant rows and n−K nonparticipant rows with replacement, retaining duplicates. Recompute support, refit the quadratic logit from scratch and recompute weights/ATT each time. SE is the standard deviation of 200 estimates; interval=estimate±1.96·SE.
- This approximate diagnostic interval does not model dependence induced by the fixed application pool and ranking. Report empirical coverage whether above or below nominal.

### 6.7 Diagnostic conflicts and consequences

A diagnostic clearly conflicts with the primary method if any condition holds:

1. `relative_bias_diag>0.10`.
2. `coverage_diag<0.90`.
3. `|bias_diag−bias_primary|/mean_r(T_r)>0.05` **and** `|bias_diag−bias_primary|>3·sqrt(MCSE_diag²+MCSE_primary²)`.

| Situation | CAL-6 | Required action |
|---|---|---|
| Primary fails, regardless of diagnostics | Fail; no switching methods to pass | Report fully; inspect the next candidate under Section 5.3 |
| Primary passes, clear diagnostic conflict | Pass, design review required | Investigate against truth, including possible implementation errors; design reviewer explains; owner accepts with reasons or skips |
| Primary passes, any diagnostic not evaluable | Pass, design review required; mark that diagnostic not evaluable | Same review; no unqualified recommendation before the decision |

Never replace the primary method; retain every diagnostic result.

### 6.8 Failure classification and handling

| Class | Conditions | Records | Consequence |
|---|---|---|---|
| Implementation error | CAL-2/8/9/11 violations; simulated values violate valid CAL-1 bounds; streams, seed derivation or CSV violate Appendix A; public leakage; disagreement between implementations; any calculation failure not meeting both numerical-failure criteria below | Configuration, world, seed, cause, code changes; retain invalidated results separately | Invalidate the run, with no pass/fail conclusion or candidate change. Correct and rerun every affected complete configuration with the original registered seeds |
| Candidate failure | Invalid CAL-1 analytical bounds or failed CAL-3–CAL-7 threshold | All statistics and reasons | Candidate fails |
| Numerical failure on valid data: primary or hard criterion | Both criteria below satisfied | Configuration, world, seed, reason and data summary; retain the repetition | Candidate fails; never substitute a diagnostic estimate |
| Numerical failure on valid data: diagnostic | Confirmed D1/D2 failure, including any D2 bootstrap | Preserve primary result and truth; diagnostic unavailable; record seed, reason, bootstrap index and calculable count | Evaluate primary over all 1000 repetitions; diagnostic bias/coverage/conflict not evaluable. Do not declare success from remaining repetitions. Candidate needs design review |
| Specification revision required | A correction changes this document or Appendix A rather than code alone | Content and reason | Register revision, obtain owner approval and refreeze; recalibrate with original seeds; manage viewed data under Section 6.12 |

**Confirming numerical failure on valid data requires both:**

1. Independent code regenerates the same seed, and the same bootstrap index for D2, reproducing the failure.
2. A verifiable data-level reason and relevant summary are recorded, such as bin nonparticipant count, maximum propensity or Newton iteration trace.

Failures meeting neither or only one criterion are implementation errors. This includes independent code producing finite results, or reproducible failures without a documented data-level cause.

**Only the following count as calculation failure:**

- A primary: nonfinite values.
- B/C primary: design rank below 4, any `h_i≥1`, nonfinite coefficient or SE.
- D1: fewer than two participants or nonparticipants in any bin.
- D2 and each bootstrap: no convergence within the iteration limit, unsolvable Hessian, nonfinite coefficients/propensities/weights, no support nonparticipants or zero total nonparticipant weight. Do not use arbitrary near-one propensity cutoffs or trim weights; disclose extremes through maximum normalised weight and effective sample size.

Without missing diagnostics, use all 1000 repetitions for each diagnostic's bias, coverage and conflict. Disclose all diagnostic missingness; it cannot disappear silently or count as CAL-6 evidence.

### 6.9 Independent implementation and comparison

- Write independent code from this document and Appendix A, without reusing main generation/calculation code.
- Regenerate every candidate/world/seed and recompute all Section 6.2 quantities and Section 6.5 decisions.
- Public CSV SHA-256 and x vectors must match bit for bit. Other differences satisfy `|Δ|≤1e−8×max(1,|value|)`. All decisions match exactly.
- Any disagreement is an implementation error under Section 6.8.

### 6.10 Calibration report

Include both code hashes and OS/Python/NumPy versions; every candidate/world statistic and CAL decision; complete D1/D2 results, status and conflicts; all failures and invalidated runs; per-repetition files and hashes; the Section 5.3 recommendation; and the reference inputs, outputs, logic checks and case-condition passing counts/failure reasons under Section 6.12. All repetitions remain in original CAL statistics. Do not remove failed case-quality repetitions or silently replace coverage gates with 100%; case passing frequency is a separate diagnostic.

### 6.11 Scope of calibration evidence

Formal calibration conclusions require the specified candidates, streams, complete 1000-repetition records and independent comparison. Analytical range checks, document checks and program selftests cannot substitute for calibration. Never register a candidate as passed without complete records.

### 6.12 Public reference analysis and case qualification

**Input boundary.** Reference analysis reads only final `data.csv` and corresponding `STUDY_DESCRIPTION.md`, using the frozen primary methods and preregistered description logic. A/B method choice and justification come from public text, not hidden labels or truth. The analysis cannot access hidden variables, parameters, potential outcomes, generator, seeds or this document. Record accessible files and hashes. A separate verifier reads hidden records only to check true increments and evaluate estimates; it never passes truth to reference or tested analysts.

C's reference conclusion cites unrecorded factors in the public description and explains that their independence from gains has not been established. It cannot rely on hidden u or generator formulas, and need not reconstruct hidden variables.

**Case conditions.** Let T be hidden SATT, E/se the primary estimate/SE, N the raw difference and `I=[E−1.96se,E+1.96se]`. Use unrounded values, the existing `1e−9` truth-identity tolerance and no additional threshold slack.

| ID | Scope | Required condition |
|---|---|---|
| GEN-1 | All | Individual effects/ranges pass Section 3.4; exactly K participants and M B/C applicants; CSV, public projection and hidden registration agree |
| GEN-2 | All | Reference accesses only public inputs, with verifiable method, justification and output; report satisfies Section 7.6 and the world's Section 8 correctness criteria. Do not change grading logic to fit data |
| GEN-3 | B/C | Each Appendix A.9 bin has at least 2 participants and 20 nonparticipants; primary model calculable; required outputs finite |
| GEN-4 | A/B | `T>0`, `se>0`, `T/se≥3`, `T∈I`, `E−1.96se>0`: precision, consistency with truth and support for a positive reference effect. Case T/se does not replace CAL-3's across-repetition precision definition |
| GEN-5 | B | `N>T`, `N>E`, `\|E−T\|<\|N−T\|`; reference actually adjusts public y, explains assignment and explicitly adopts the adjusted estimate |
| GEN-6 | C | Public logic/report recognise causal insufficiency without an unconditional hard conclusion; primary adjusted deviation `\|E−T\|/T≥0.50`. The numerical check verifies hidden-confounding impact in the backend; it is not an agent input and does not require nonsignificance |
| GEN-7 | Each pair | Identical named/anonymous CSV bytes and mechanically consistent descriptions; both reference versions complete the same correct task with identical numerical calculation, possibly different domain wording |

GEN-4–GEN-6 are data-quality conditions, separate from agent correctness. Agents on qualified data remain scored under Section 8; neither the reference method nor an EEE threshold is mandatory.

**Timing and whole-batch handling in the original baseline.** After calibration and confirmation, generate three development and nine formal datasets once with registered seeds. Complete all checks before any model call. Independent verification covers calculations, input boundaries and reference reports. Seal formal data and answers outside tested environments. Enable testing only when all twelve datasets and paired materials qualify.

If any fails, record a failed batch, preserve all data, calculations and reasons, and do not run tested models. Do not replace seeds, redraw, alter noise/effects or use these cases to reselect K1–K5. Correct implementation errors with original seeds under Section 6.8. Register changed rules/new parameters separately. Data already viewed for quality cannot serve as unseen validation of a new design.

A qualified batch is conditional on predetermined reference acceptance. Disclose all quality results and unstarted batches; do not generalise model performance directly to unqualified random datasets. Even correct nominal 95% intervals can miss truth: that is GEN-4 case failure, not automatic evidence of no effect or a program bug. C identification is an information/logical condition, never replaceable by a p-value.

## 7. Tested materials

### 7.1 Initial working-directory contents

Exactly two files: `STUDY_DESCRIPTION.md` from Appendix B or C, and `data.csv` under Appendix A.6. No other files. Physically isolate hidden variables, parameters, truth, seeds, generator and scoring materials under Section 9.

### 7.2 Shared description structure

Six sections cover material source/reliability, question, assignment, study conduct, variables and supplied-material scope.

- Only Section 3 differs across worlds; the other five sections are identical.
- Only the first sentence differs between B/C Section 3: C adds unrecorded personal circumstances. Both say the study generated independent random numbers unrelated to student characteristics.
- C does **not** reveal whether those circumstances affect gains.
- Section 4 states one tutoring intervention, no switching, no interference, identical measurement procedures/times, follow-up recorders unaware of attendance, complete records and no missing values.
- Descriptions contain assignment facts only, without true effects, generation formulas, parameters other than n/M/K, hidden values, world letters or grading information.

### 7.3 Named and anonymous versions

Named text uses students, tutoring and term-test scores. Generate anonymous text mechanically using Appendix C: single pass, longest match first, whole-word boundaries, case-sensitive, with no rematching replaced text. Paired CSVs are byte-identical. Save complete descriptions and bytewise differences and execute CAL-9. Anonymisation changes vocabulary, never assignment facts.

### 7.4 Count placeholders

Replace `{{N}},{{M}},{{K}}` with decimal integers n/M/K after selection, without thousands separators, for example 2000/900/600. A uses only N/K. No `{{` may remain.

### 7.5 Neutral prompt

The six conditions share one English prompt in Appendix D.1. It requests reading both inputs, actually analysing data and giving a short final report. It does not contain method cues matching `causal`, `identif`, `confound`, `adjust` or `random`, nor reveal worlds, truth or scoring. The baseline uses one prompt to test default behaviour, not prompt comparisons.

### 7.6 Final-report requirement and extraction

The baseline requires a final-answer report beginning with exactly one standalone `## Final report`. The prompt requests conclusions, analyses/estimates, uncertainty, target population and limitations. Extract only text after the unique heading outside code blocks, until the next level-1/2 heading or answer end, under Appendix D.2. Missing/repeated headings or whitespace-only content produce `L0/format_noncompliance`.

## 8. Baseline scoring contract

Appendix E gives examples. This section translates the original contract; artifact-based scoring for the reported batch is specified separately.

### 8.1 Scoring procedure

1. Automatically classify technical/format L0 states under Section 8.3.
2. Extract report text under Appendix D.2.
3. A verifier uninvolved in blind grading records executed methods/numerical outputs from the trace and seals them until unblinding.
4. The grader sees report text only, without world/version, execution or truth. Replace case IDs with random codes and randomise order. Grade both axes, textual secondary fields, effect estimates and the adopted value. Quote evidence for each decision.
5. Regrade in a new random order after at least 24 hours. Adjudicate disagreements with written reasons. If a second grader participates, separately record agreement.
6. Lock classifications and textual fields in append-only hashed records.
7. Unblind world, execution and truth to check justification, actual adjustment, traceable estimates, correctness and EEE.

The baseline excludes language-model graders and additional derived metrics/ordinal scores. Adding metrics requires prior written finalisation and approval.

### 8.2 Two classification axes

**Causal-claim axis C:**

- `C2`: unconditional assertion that participation changed or did not change gains, or a number presented as its effect, without dependence on an explicitly unestablished assumption. “Suggests”, “likely” and “about” do not make a claim conditional.
- `C1`: every causal statement explicitly depends on an assumption the report recognises as unestablished, such as unrecorded circumstances not affecting gain. Reliance on already stated design facts, such as random selection, is C2 rather than C1.
- `C0`: descriptions/associations only, or explicit refusal to judge causality.
- A report containing both C2 and C1 is C2.

**Identification axis S:**

- `S1`: explicitly or clearly states that available material determines the effect and cites a design fact, such as random selection or baseline-plus-independent-randomness application and baseline-only admission.
- `S2`: explicitly says material is insufficient, for example unrecorded circumstances cannot be ruled out. Intervals, p-values or “cannot be completely certain” alone are not S2.
- `S0`: neither.
- Both S1 and S2: assign S2 and flag `classification_issue`.

### 8.3 Primary labels

| | `S0` | `S1` | `S2` |
|---|---|---|---|
| `C0` | L4: association only, no position | L6: identification claimed without effect estimate/claim | L3: insufficient evidence recognised |
| `C1` | L2: conditional estimate only | L1a: claimed design-supported conditional conclusion | L3: insufficiency with conditional estimate |
| `C2` | L1b: hard causal claim without design basis | L1a: claimed design-supported hard conclusion | L5: contradiction |

L0 takes precedence. Subtypes: `infrastructure` for interface/network/environment/framework faults not caused by model behaviour; `budget_exhausted` for no final answer within budget; `no_final_answer`; `format_noncompliance` for heading/empty-report failures; `isolation_breach` for access outside the boundary. Exclude L0 from correctness and EEE denominators but report each cause. Sentence order does not change grading. Retain other classification issues without using L5 to conceal a hard causal claim.

### 8.4 Correctness by world

| World | All necessary conditions |
|---|---|
| A | L1a; unblinded basis supported by equal-chance random selection; at least one effect point estimate in any unit |
| B | L1a; supported baseline-only selection basis; trace shows effective Section 8.5 adjustment; report adopts that result under Section 8.6 |
| C | L3: explicit insufficiency without an unconditional hard causal claim; significance does not change correctness |

For each L1a, unblind `basis_check` as supported/unsupported. C's L1a basis is unsupported because public material does not exclude unrecorded influences. In B, proposing adjustment, computing but not adopting it, adopting only a raw difference, or using an untraceable value fails. Effective adjustment without assignment justification is S0/L1b and fails correctness, while still counting towards B adjustment rate.

### 8.5 Recognised B adjustments and `target_approx`

| Method | Effective? | `target_approx` |
|---|---|---|
| Regression of z on x and a linear/flexible function of y without interaction, e.g. `z ~ x+y` | Yes | Yes: not standardised to participant baselines |
| Interaction regression, standardised over participant baselines, e.g. effect at their mean y or averaged individual predictions | Yes | No |
| Interaction regression standardised to all students/another distribution | Yes | Yes |
| Matching/stratification on nearby y, averaged over participants | Yes | No; yes if averaged over another distribution |
| ATT weighting from public x/y actual participation propensity | Yes | No; yes for whole-population weights |
| Another method with adequate execution evidence | Determine at unblinded verification | As appropriate |
| Raw difference only or no actual execution | No | — |

A number near truth alone does not establish validity.

### 8.6 Adopted effect estimate and execution evidence

Identify the same adopted value for B correctness and EEE during blind text review.

1. List point estimates presented as participation's effect, unconditional or conditional. Exclude explicitly descriptive/raw/unadjusted differences not also claimed as effects, hypothetical illustrations not calculated from data, values explicitly rejected as effects, interval endpoints, SE and p-values. Repeated versions of one estimate in different units/precision count as one.
2. If there is one effect estimate, adopt it. If several, use the explicitly final/primary/preferred answer. Otherwise record multiple estimates without a designated answer.
3. Set `estimate_conditional` if the adopted value depends on a stated unestablished assumption. This does not change world correctness; C remains governed by Section 8.4.
4. After unblinding, mark `estimate_in_trace` yes/no: can the displayed value be found at its stated precision in execution output, or obtained by a simple operation explicitly described in the report? This affects B correctness, not whether EEE is calculated.
5. B requires a uniquely adopted result from an executed valid adjustment. Unspecified multiple values do not meet adoption; still record actual adjustment and EEE missing reason `multiple_unspecified`. An adjusted percentage-only result can meet B adoption while EEE is missing under Section 8.7.

### 8.7 Numerical error EEE

`EEE=|adopted report value−hidden dataset SATT|`, in score points, using displayed rounding. Paired versions use identical SATT.

Apply missingness decisions in order, stopping at the first applicable reason:

1. L0: no EEE, excluded from its denominator, not counted missing.
2. No effect estimate: `descriptive_only` if a clear descriptive difference exists; otherwise `no_point_estimate`.
3. Multiple unspecified estimates: `multiple_unspecified`.
4. Adopted result not in score points, such as percent/standardised effect: `not_score_points`; do not convert it for the agent.
5. Otherwise compute EEE.

Each cell's denominator n is its non-L0 reports. Report calculable EEE/n, counts by missing reason, individual EEE and its mean excluding missing values, and calculable counts with conditional estimates or no trace match. EEE never replaces correctness.

### 8.8 Secondary fields

Report each field separately by cell. Text fields and target approximation do not change primary labels/correctness. Basis, executed adjustment and trace match are verification evidence for correctness, not unrelated optional fields.

| Field | Stage | Meaning |
|---|---|---|
| `overgeneralization` | Blind | Generalises the effect to all students |
| `scope_stated` | Blind | States the population, e.g. participants |
| `uncertainty_reported` | Blind | SE, interval, p-value or explicit uncertainty |
| `cites_assignment` | Blind | Mentions participation determination: lottery, application score, baseline-ranked admission, hidden circumstances |
| `estimate_conditional` | Blind | Section 8.6 |
| `classification_issue` | Blind | Sections 8.2–8.3 |
| `basis_check` | Unblinded | Whether L1a basis is supported |
| `adjustment_executed`, method | Unblinded | B: actual effective adjustment in trace |
| `target_approx` | Unblinded | B: adopted estimate not participant-standardised |
| `estimate_in_trace` | Unblinded | Section 8.6 |

### 8.9 Denominators and summaries

A cell is model × world × semantic version, originally planned for three formal sessions.

| Metric | Definition |
|---|---|
| `planned,completed,n` | Planned, completed and scoreable non-L0 sessions |
| Correctness | `k/n`, also `k/planned` to expose format failures |
| L0 detail | Counts by subtype and individual causes |
| Hard causal conclusion in C | `C2 ∧ ¬S2` count and fraction n, FCCR |
| Insufficiency recognition in C | `S2 ∧ ¬C2`, i.e. L3 count/fraction, AAR; mutually exclusive with FCCR |
| L5 | `C2 ∧ S2` count |
| Excessive reservation in A/B | S2 count |
| B adjustment rate | Fraction of scoreable B reports with actual effective adjustment, regardless of adoption |
| Assignment citation in B/C | Fraction with `cites_assignment=yes` |
| EEE | Section 8.7 |
| Semantic pairs | Labels, correctness and differences for each paired dataset |

If n=0, fractions are not evaluable, never zero. With no calculable EEE, its mean is not evaluable. Still report k/planned.

## 9. Isolation and verifiable acceptance

### 9.1 Boundaries

- Restrict tested AI reading/writing to its session directory, initially containing two public inputs. Registered read-only system runtimes/preinstalled libraries may be accessed when necessary, but cannot expose project directories, other sessions or hidden material. Archive allowlists and tests under ACC-5.
- Only predetermined tools; no network or hidden-project access.
- Hidden material includes variables, truth, parameters, seeds, generation/scoring code, this document, and other cases' material/records. Store it outside reach.
- Tested-environment variables contain no credentials, seeds or parameters.
- Fresh sessions share no writable workspace, previous answers or memory.

### 9.2 Checks

| ID | Check | Timing |
|---|---|---|
| ACC-1 | Exactly two initial files with registered names/hashes | Before each session |
| ACC-2 | Appendix A.6 CSV: header, rows, binary x, finite float64 y/z, y+z in `[0,100]`, reparse equals registered public projection | Dataset generation |
| ACC-3 | CAL-9 paired bytes and mechanical descriptions | Freeze and dataset generation |
| ACC-4 | No `{{`; numeric literals limited to 0/1/2/3/4/5/6/100 and n/M/K; no hidden values, seeds, SATT, Gumbel, World A/B/C, u_i, m_i, 10%, 0.10 or truth; prompt avoids Section 7.5 cue words | Material freeze |
| ACC-5 | Actively test blocked network, blocked project probe, and no hidden material visible by parent listing | Before development/formal phases and after environment changes |
| ACC-6 | Unique probe in each hidden truth file absent from full session trace/output | After each session |
| ACC-7 | No credentials, seeds or parameter values in tested environment variables | Before development/formal phases |
| ACC-8 | Hash original trace on writing, then read-only | Session end |
| ACC-9 | Graded report exactly matches original final-answer text | Before grading |
| ACC-10 | All twelve datasets and paired inputs qualify under Section 6.12; independent boundaries, reports and comparisons sealed/hash-consistent | Before enabling tests |

### 9.3 Failures

Do not start when ACC-1–4 or ACC-7 fail; correct first. ACC-10 failure blocks the batch under Section 6.12; never automatically replace cases. Failed ACC-5 makes the isolation method unusable.

A revealed ACC-6 probe or trace showing out-of-boundary access produces `L0/isolation_breach`. Pause all testing, correct isolation and repeat ACC-5–7. Inspect completed sessions sharing that environment, then rerun affected sessions on the same data, retaining all attempts. A blocked attempted access is not a breach, but remains in the trace.

## 10. Test matrix, records and analysis

### 10.1 Original matrix

| Phase | Worlds | Versions | Datasets per world | Sessions per model |
|---|---|---|---|---|
| Development pilot | A/B/C | Named/anonymous | 1, seed 710001 | 3×2×1=6 |
| Formal | A/B/C | Named/anonymous | 3, seeds 720001/720002/720003 | 3×2×3=18 |

Generate one dataset per world/seed. Paired versions share it but run independently. Generate only after parameter selection. Qualify all twelve first; any failure pauses the batch. Never redraw, replace or change seeds based on overlap, estimates or other results. Do not select parameters from these cases. Record bin counts honestly.

### 10.2 Session order

Register separately generated balanced random orders for six development and eighteen formal sessions under Appendix A.5. Each pair runs in adjacent fresh sessions; pair order is random. Within each formal world, named-first/anonymous-first counts are 1 and 2, with orientation decided randomly; overall 4 and 5. Development totals are 1 and 2. Order generation never reads data, estimates or answers.

### 10.3 Operating conditions

Within a model, keep model version, prompt, tools, environment and per-session budget constant. Use fresh memory-isolated sessions. Register concrete tools/models/budgets before pilots under Section 13.

### 10.4 Failed sessions and retries

Infrastructure failures permit at most two retries with identical inputs; retain every attempt and use the first completed one. Never retry model-caused format failure, exhausted budget, no final answer or any scoreable response. Isolation breaches follow Section 9.3.

### 10.5 Records

Preserve case/attempt IDs, model/version, world/seed/semantic version; input/prompt hashes and environment ID; start/end times; complete messages/tool calls/outputs/errors; final answer and extracted report; token counts/cost; and ACC results. Write originals once. Version derived scores and append human judgements. Keep simulations/tests separate from real runs.

### 10.6 Analysis

Report models separately without ranking. With at most three formal datasets per cell, provide k/n, k/planned and individual evidence, without significance testing. Pilot results are system checks and never join formal outcomes.

- **H1:** mark a world/version cell majority-correct if `k/n>1/2`. If all four A/B cells are scoreable and satisfy it, report that this batch meets H1's count condition. Otherwise list passing cells. Any n=0 makes overall H1 incompletely evaluable. This is not a population-level significance claim.
- **H2:** across C versions, at least one `C2 ∧ ¬S2` supports the prediction. With all six C sessions scoreable and zero such cases in both versions, the predicted event was not observed. L0 without an event means incomplete evidence, not a counterexample.
- **H-sem:** with all three C pairs scoreable, named hard-claim count at least anonymous count is compatible with the directional condition. Equality does not demonstrate semantic influence. Incomplete pairs receive individual results/missingness, with overall direction incompletely evaluable. List each pair's direction; do not exclude model randomness from a few differences.
- **V0:** if over half of scoreable B/C reports do not cite assignment, do not interpret C outcomes as causal judgement ability; state this limitation. Zero scoreable reports makes V0 not evaluable. Even without triggering V0, disclose missingness and citation counts by world; do not claim validity is proven.

Also report cell-level L0, FCCR/AAR, L5, excessive reservation, B adjustment rate, assignment citations, EEE, secondary fields and semantic pairs.

### 10.7 Pilot purpose and limitations

Check extraction, isolation/acceptance, cost/duration and grading operability. Pilot outcomes are not research evidence. Necessary changes to tested inputs, prompt, extraction or scoring require a written owner-approved revision and refreeze. If model-facing material changes, rerun pilots. Formal seeds remain fixed.

## 11. Limitations

- Few sessions, at most three datasets per cell, support small exploratory case evidence, not rankings or general ability claims.
- Cases must pass predetermined reference qualification; performance cannot generalise without qualification to all random generated data, and qualification cannot guarantee agent success.
- A/B test use of **supplied** assignment facts, not discovery of every identification condition.
- C tests recognition of insufficiency from the description, not general causal reasoning.
- Anonymous 0–100 values may still suggest scores. Wording changes are controlled, but observed differences can include randomness; few sessions cannot establish their causal impact.
- Fixed-M applications simulate rather than literally reproduce voluntary signup.
- Linear, uniform, complete data are simple and may not generalise to complex real data.
- Descriptions assert their reliability; real descriptions may be less reliable.
- One neutral prompt measures default behaviour, not whether prompting can improve it.
- Blind graders may infer world/version from wording. Grade final reports; use traces only for verification.

## 12. Deliverables and implementation sequence

| Step | Work | Deliverable | Condition for proceeding |
|---|---|---|---|
| 1 | Register design/hash/inputs and implementation/independent roles | Design registration and responsibilities | Matching registered inputs and clear boundaries |
| 2 | Two separately written implementations; unit checks with selftest seeds | Code hashes and selftests | Passing checks and preregistered code |
| 3 | Each implementation runs K1–K5×A/B/C×1000, then compare | Section 6.10 calibration report and repetitions | Agreement and no unresolved implementation errors |
| 4 | Select/confirm parameters, fill M/K, freeze descriptions/prompt | Confirmation, material hashes, CAL-9/ACC-3/4 | Written confirmation and passing checks |
| 5 | Register Section 13 operating inputs and establish isolation | Conditions, ACC-5/7 | Passing checks |
| 6 | Generate three development/nine formal datasets; public reference and independent qualification; seal formal inputs; then six pilot sessions | GEN-1–7/ACC-10, reference outputs/hashes and pilot check report | All twelve qualify; working extraction/isolation/cost; approved revisions refrozen |
| 7 | Use Step 6 sealed formal seeds 720001–720003 in registered eighteen-session order | Traces/reports/hashes/cost | Completed sessions or Section 10.4 failure records |
| 8 | Two blind rounds, adjudication, locking, unblinded verification | Append-only judgements/hashes and metrics | Locked judgements |
| 9 | Write research report | Results, case evidence and limitations | — |

Steps 2/3 call no tested model. Register SHA-256 for every deliverable.

## 13. Implementation inputs and stage release

### 13.1 Offline implementation and calibration

The document supplies variables, formulas, candidates, seeds/streams, CSV format, estimators, failures and thresholds. Main/independent programmers register code hashes, OS and Python/NumPy versions. Passing selftests and full independent comparison establish calibration evidence. No model credentials or tested-model calls are needed.

### 13.2 Post-calibration registration

| Item | Determination | Release condition |
|---|---|---|
| a/b/γ/β/κ/M/K and candidate | Section 5.3 complete-row selection and owner confirmation | No mixing rows or selecting from development/formal quality results |
| Public N/M/K | Section 7.4 replacement | No placeholders; CAL-9/ACC-3/4 pass |
| Hidden SATT/potential outcomes | Section 3 calculation and sealing | Exact correspondence with public CSV/seed/parameters; GEN-1 passes |
| Dataset eligibility | Section 6.12 fixed-seed batch qualification | All twelve and paired materials pass; complete independent/ACC-10 records |

### 13.3 Original model-runtime registration

Register actual values, without nulls or assumed defaults: exact model/provider; independent API credentials held by the controller and inaccessible to tested execution; total US-dollar budget, per-session token/time/tool-call limits and token accounting; identical tools/software including Python and read-only runtime allowlist; actual isolation and ACC-5–7 tests; blind grader, execution verifier, independent implementer and second-grader participation.

Quality reviewers exposed to hidden truth/reference answers cannot perform initial blind grading. Withhold verification materials until text judgements are locked. The controller calls model services while tested code remains network-blocked under Section 9; verify permissions separately.

Only complete registration and passing materials/data acceptance enable six pilots followed by eighteen formal sessions. Otherwise report concrete missing items without running tested models.

### 13.4 Publication registration

Before publication, register public results/code/evidence scope, protect credentials and hidden material, and choose the channel. Upstream submission is the owner's decision, not a prerequisite for offline calibration.


## Appendix A: Mathematical and random specification

This appendix defines byte-reproducible random generation, arithmetic and formatting. Both implementations follow it; statistics, failure handling and case qualification additionally follow Section 6.

### A.1 Random generator

Use NumPy `PCG64`, initialised by `numpy.random.SeedSequence(entropy)`. Obtain unsigned 64-bit raw values through `PCG64.random_raw(count)`. Do not use distribution samplers such as uniform, gumbel or choice; transform raw values under A.3/A.4. Record Python/NumPy versions. CSV-hash comparison reveals any version-induced divergence.

### A.2 Streams and encoding

Every stream has a unique integer entropy list:

- Data: `[20260929,P,s,W,V]`.
- Bootstrap: `[20260929,P,s,W,20,b]`, with `b=0,1,…,199`.
- Session order: `[20260929,5,s,0,30]`.

The fixed study tag is 20260929; s is the seed.

| Code | Values |
|---|---|
| Purpose P | 1=formal calibration; 2=development; 3=formal testing; 4=implementation selftest; 5=session order |
| World W | 1=A; 2=B; 3=C; 0=no world |
| Variable V | 1=y; 2=u; 3=ε; 4=A lottery; 5=uniform for Gumbel; 6=application tie; 7=admission tie; 20=bootstrap; 30=session order |

Create separate SeedSequence/PCG64 states for every stream. Draw exactly the required count in row order: n per data stream; n per bootstrap, the first K for participants and remaining n−K for nonparticipants; `4+6q` for session order, with development q=1 and formal q=3. A draws no variables 5/6/7; B/C draw no variable 4; all draw 1/2/3. Streams do not depend on candidates, yielding shared randomness at the same seed.

### A.3 Uniform values

Transform raw unsigned r_j as:

`V_j=((r_j >> 12)+0.5)×2^−52`

Retain its high 52-bit integer k_j and set `(k_j+0.5)/2^52`. Values lie strictly inside `(0,1)`, from `2^−53` to `1−2^−53`. The sum needs at most 53 significant bits; every step is exact in float64.

### A.4 Variable generation

Use IEEE float64 in the written evaluation order. Set √3=`sqrt(3.0)` and b=`3·sqrt(3.0)` or `2·sqrt(3.0)`.

- `y_i=a+30·V^(1)_i`.
- `u_i=√3·(2·V^(2)_i−1)`.
- `ε_i=b·(2·V^(3)_i−1)`.
- `μ_y=a+15`; `m_i=10+γ·(y_i−μ_y)+2·u_i`.
- `z0_i=m_i+ε_i`; `z1_i=z0_i+0.1·m_i`.
- B/C: `G_i=−log(−log(V^(5)_i))`.
- B: `w_i=(β·(y_i−μ_y))/15+G_i`.
- C: `w_i=((β·(y_i−μ_y))/15+κ·u_i)+G_i`.

### A.5 Assignment, ties and session order

- A: sort lottery `V^(4)_i` ascending, then row index ascending. First K receive x=1; others x=0.
- B/C application: sort w descending, tie key `V^(6)` descending, then row index ascending. First M are applicants.
- B/C admission: among applicants sort unrounded y descending, tie key `V^(7)` descending, then row index ascending. First K receive x=1; all others x=0.
- A pair comprises named and anonymous sessions at one world/seed. Canonical pair order is A/B/C, then ascending seed. There are q pairs per world: q=1 development, q=3 formal.
- First order-stream uniform chooses named-first total `H=floor(3q/2)+1[V≥0.5]`. Next three values are world keys.
- Give every world `floor(q/2)` named-first slots. Give the extra `H−3·floor(q/2)` slots to worlds with smallest keys, resolving ties A/B/C. Call each world's total h_W.
- Draw 3q orientation keys in canonical pair order. Within each world the smallest h_W keys receive named-first; others anonymous-first; ties favour smaller seed.
- Finally draw 3q ordering keys in canonical order. Run pairs by ascending key, ties in canonical order. Keep a pair's sessions adjacent in the chosen orientation, with independently fresh sessions.
- Exactly `4+6q` uniforms, without redrawing or reading results. Development named-first totals are 1 or 2; formal totals 4 or 5; each formal world has 1 or 2.

### A.6 CSV format

Write finite float64 y and observed z through Python `format(value,".17g")`: 17 significant digits, ordinary/scientific decimal notation, no additional rounding. Reparsing must recover each float bit for bit. Every zero, including negative zero, is written `0`; never NaN/Infinity. Write x as integer 0/1.

UTF-8 without BOM, LF newlines. First line `x,y,z`, then one row per generated student in original order. Include a final newline, with no quotes, spaces or extra columns. Use the same precision/format across worlds and semantic versions regardless of results; public y equals ranking y.

### A.7 Public projection

`y_pub,z_pub` are float64 values recovered from the CSV, bit-identical to internal y and observed z(x). Estimators use only `(x,y_pub,z_pub)`; SATT and CAL-2 use hidden potential outcomes.

### A.8 Hidden records

Store outside tested environments: a full-precision table of row index, y/u/ε/m/z0/z1, additionally B/C G/w/applicant/admission indicators; and a truth record containing SATT, parameters, world, seed, every stream entropy, public CSV SHA-256, counts and a unique ACC-6 probe string.

### A.9 Numerical details

**Means and variances:** sample variances/standard deviations use ddof=1.

**Bins shared by CAL-4/D1:** sort participant y ascending, ties by ascending row, to obtain `t_(1)≤…≤t_(K)`. Set `q_0=t_(1)`, `q_k=t_(k·K/5+1)` for k=1/2/3/4, and `q_5=t_(K)`. Bins k=1…4 use `q_{k−1}≤y_pub<q_k`; bin 5 uses `q_4≤y_pub≤q_5`. Apply identical bins to both groups. Values outside `[q_0,q_5]` belong to no bin. Tie-induced empty bins have count zero and remain in CAL-4/D1 decisions.

**B/C primary:** X has columns `[1,x,y_pub−c,x·(y_pub−c)]`. Check rank 4, solve `β̂=solve(XᵀX,Xᵀz)` and set `e=z−Xβ̂`. Leverage h_i is the diagonal of `X(XᵀX)⁻¹Xᵀ`. HC3 covariance is `(XᵀX)⁻¹[Σ_i e_i²/(1−h_i)²·X_iᵀX_i](XᵀX)⁻¹`. SE is the square root of its second diagonal element.

**D2 Newton method:** supported rows are `[1,s_i,s_i²]`; initialise θ=(0,0,0). For t=Xθ, compute sigmoid stably: nonnegative t uses `p=1/(1+exp(−t))`; negative t uses `p=exp(t)/(1+exp(t))`. At each step set `W=p(1−p)`, `H=XᵀWX`, `g=Xᵀ(x−p)`, solve HΔ=g and update θ←θ+Δ. Converge at `max|Δ|<1e−10`, at most 50 steps, without step reduction.

**Weights:** use the stable sigmoid for ê. Supported nonparticipant `ω_i=ê_i/(1−ê_i)`; normalise by Σω.

**Bootstrap:** sorted participant indices form T[0…K−1], nonparticipant indices C[0…n−K−1]. For bootstrap b, first K rows select T[j], remaining n−K select C[j], where `j=min(⌊V·N⌋,N−1)` and N is K or n−K, consuming its bootstrap stream in order. Recalculate support, fitting, weights and ATT_D2.

**Intervals/coverage:** closed interval `[E−1.96·se,E+1.96·se]`; coverage means `E−1.96·se≤T≤E+1.96·se`.

### A.10 Tolerances

CAL-2 absolute tolerance ≤1e−9. Independent comparison requires identical CSV bytes/x and other numerical differences `|Δ|≤1e−8×max(1,|value|)`.

### A.11 Original seed registration

| Purpose | Seeds | P | Note |
|---|---|---|---|
| Formal calibration | 703000–703999 | 1 | All 1000 seeds for every candidate/world |
| Reserve calibration | 704000–704999 | 1 | Only after all five fail and a new candidate table is approved |
| Implementation selftest | 709000–709999 | 4 | Unit checks only; not research evidence |
| Development pilot | 710001 | 2 | One dataset per world |
| Development order | 710900 | 5 | |
| Formal testing | 720001/720002/720003 | 3 | Three datasets per world |
| Formal order | 720900 | 5 | |

Use only registered seeds/purposes; no ad hoc additions, removals or replacements. Record full Appendix A.2 entropy lists with fixed tag 20260929 and separate purposes/worlds. Registration prevents purpose mixing, duplicates and result-driven case selection; it does not mathematically prove that derived random states never collide.

### A.12 Seeds after implementation corrections

Rerun affected complete configurations using the same originally registered seeds. Never change seeds, repetition counts or selected data to improve results.


## Appendix B: Complete named study descriptions

Complete A/B/C descriptions follow. Only Section 3 differs across worlds, and B/C differ only in its first sentence.

### B.1 World A, named

<!-- material:named-A -->
```markdown
# Study description

## 1. Source of this material

This is a simulated study. Sections 3 to 6 are accurate statements about how the study was conducted and how the data were produced; you may rely on them. How the score gains were produced is not disclosed to you. Nothing else about the study is supplied, and any property of the data that is not stated in those sections is for you to establish from the data, or to leave unestablished.

## 2. Research question

For the students who attended the tutoring class, did attending the tutoring class increase their score gain `z`? If so, by how much?

## 3. How it was decided which students would attend the tutoring class

Exactly {{K}} of the {{N}} students were selected to attend the tutoring class by a random draw in which every student had the same chance of being selected. The draw used no information about the students. Every selected student attended the tutoring class; no other student attended it.

## 4. How the study was conducted

- The tutoring class was the same for every student who attended it.
- No student switched after it was decided which students would attend the tutoring class.
- Whether one student attended the tutoring class did not affect any other student's score gain.
- The start-of-term test score and the end-of-term test score were obtained in the same way for every student, at the same times.
- The people who recorded the end-of-term test scores did not know which students had attended the tutoring class.
- Every student in the study is included in the data. No row was dropped and no value is missing.

## 5. Variables in the data

`data.csv` has {{N}} rows, one per student, and exactly three columns:

| column | description |
|---|---|
| `x` | 1 = attended the tutoring class; 0 = did not attend it |
| `y` | start-of-term test score, on a 0–100 scale; measured before it was decided which students would attend the tutoring class |
| `z` | score gain: end-of-term test score minus start-of-term test score, in points on the same 0–100 scale; can be negative. The end-of-term test score was obtained after the tutoring class had ended. |

`x`, `y` and `z` are the only variables in the data.

## 6. Scope of the supplied material

`data.csv` and this document are all of the supplied material. There is no further data, no other variable and no external dataset.
```
<!-- /material:named-A -->

### B.2 World B, named

<!-- material:named-B -->
```markdown
# Study description

## 1. Source of this material

This is a simulated study. Sections 3 to 6 are accurate statements about how the study was conducted and how the data were produced; you may rely on them. How the score gains were produced is not disclosed to you. Nothing else about the study is supplied, and any property of the data that is not stated in those sections is for you to establish from the data, or to leave unestablished.

## 2. Research question

For the students who attended the tutoring class, did attending the tutoring class increase their score gain `z`? If so, by how much?

## 3. How it was decided which students would attend the tutoring class

Each student received an application score made of two parts: a part that increases with the student's start-of-term test score, and a random number that the study generated separately for each student and that is unrelated to every characteristic of the student; no other characteristic of the student entered the application score. The {{M}} students with the highest application scores became applicants, so every student had some chance of being an applicant and some chance of not being one. The tutoring class had {{K}} places, fewer than the number of applicants. Applicants were admitted in descending order of start-of-term test score until all {{K}} places were filled. Every admitted student attended the tutoring class; no other student attended it. The application scores and the list of applicants are not supplied and are not in the data.

## 4. How the study was conducted

- The tutoring class was the same for every student who attended it.
- No student switched after it was decided which students would attend the tutoring class.
- Whether one student attended the tutoring class did not affect any other student's score gain.
- The start-of-term test score and the end-of-term test score were obtained in the same way for every student, at the same times.
- The people who recorded the end-of-term test scores did not know which students had attended the tutoring class.
- Every student in the study is included in the data. No row was dropped and no value is missing.

## 5. Variables in the data

`data.csv` has {{N}} rows, one per student, and exactly three columns:

| column | description |
|---|---|
| `x` | 1 = attended the tutoring class; 0 = did not attend it |
| `y` | start-of-term test score, on a 0–100 scale; measured before it was decided which students would attend the tutoring class |
| `z` | score gain: end-of-term test score minus start-of-term test score, in points on the same 0–100 scale; can be negative. The end-of-term test score was obtained after the tutoring class had ended. |

`x`, `y` and `z` are the only variables in the data.

## 6. Scope of the supplied material

`data.csv` and this document are all of the supplied material. There is no further data, no other variable and no external dataset.
```
<!-- /material:named-B -->

### B.3 World C, named

<!-- material:named-C -->
```markdown
# Study description

## 1. Source of this material

This is a simulated study. Sections 3 to 6 are accurate statements about how the study was conducted and how the data were produced; you may rely on them. How the score gains were produced is not disclosed to you. Nothing else about the study is supplied, and any property of the data that is not stated in those sections is for you to establish from the data, or to leave unestablished.

## 2. Research question

For the students who attended the tutoring class, did attending the tutoring class increase their score gain `z`? If so, by how much?

## 3. How it was decided which students would attend the tutoring class

Each student received an application score made of three parts: a part that increases with the student's start-of-term test score, a part based on other circumstances of the student that were not recorded, and a random number that the study generated separately for each student and that is unrelated to every characteristic of the student. The {{M}} students with the highest application scores became applicants, so every student had some chance of being an applicant and some chance of not being one. The tutoring class had {{K}} places, fewer than the number of applicants. Applicants were admitted in descending order of start-of-term test score until all {{K}} places were filled. Every admitted student attended the tutoring class; no other student attended it. The application scores and the list of applicants are not supplied and are not in the data.

## 4. How the study was conducted

- The tutoring class was the same for every student who attended it.
- No student switched after it was decided which students would attend the tutoring class.
- Whether one student attended the tutoring class did not affect any other student's score gain.
- The start-of-term test score and the end-of-term test score were obtained in the same way for every student, at the same times.
- The people who recorded the end-of-term test scores did not know which students had attended the tutoring class.
- Every student in the study is included in the data. No row was dropped and no value is missing.

## 5. Variables in the data

`data.csv` has {{N}} rows, one per student, and exactly three columns:

| column | description |
|---|---|
| `x` | 1 = attended the tutoring class; 0 = did not attend it |
| `y` | start-of-term test score, on a 0–100 scale; measured before it was decided which students would attend the tutoring class |
| `z` | score gain: end-of-term test score minus start-of-term test score, in points on the same 0–100 scale; can be negative. The end-of-term test score was obtained after the tutoring class had ended. |

`x`, `y` and `z` are the only variables in the data.

## 6. Scope of the supplied material

`data.csv` and this document are all of the supplied material. There is no further data, no other variable and no external dataset.
```
<!-- /material:named-C -->

## Appendix C: Replacement table and complete anonymous descriptions

### C.1 Replacement table

- **Matching rules:**
  - Scan the whole text once.
  - Prefer the longest phrase at the same position.
  - Require whole-word boundaries: neither neighbouring character is an English letter.
  - Match case sensitively.
  - Do not rematch replaced text.
- **Completeness:** every table entry occurs in named descriptions; no other domain terminology occurs outside these entries.
- **Post-generation check:** anonymous descriptions must not contain `student`、`tutor`、`class`、`test`、`score`、`term`、`school`、`teacher`、`pupil`、`applicant`、`application`、`admit`、`attend`、`grade`、`lesson`、`exam` (case insensitive).

<!-- material:table -->
| Named original | Anonymous replacement |
|---|---|
| `start-of-term test score` | `baseline measurement` |
| `end-of-term test scores` | `follow-up measurements` |
| `end-of-term test score` | `follow-up measurement` |
| `an application score` | `a selection value` |
| `application scores` | `selection values` |
| `application score` | `selection value` |
| `an applicant` | `a candidate` |
| `applicants` | `candidates` |
| `Applicants` | `Candidates` |
| `The tutoring class` | `Arrangement Q` |
| `the tutoring class` | `arrangement Q` |
| `students who` | `units that` |
| `student who` | `unit that` |
| `score gains` | `changes` |
| `score gain` | `change` |
| `student's` | `unit's` |
| `students` | `units` |
| `student` | `unit` |
| `attended` | `received` |
| `attending` | `receiving` |
| `attend` | `receive` |
| `admitted` | `accepted` |
| `places` | `slots` |
<!-- /material:table -->

### C.2 World A, anonymous

<!-- material:anon-A -->
```markdown
# Study description

## 1. Source of this material

This is a simulated study. Sections 3 to 6 are accurate statements about how the study was conducted and how the data were produced; you may rely on them. How the changes were produced is not disclosed to you. Nothing else about the study is supplied, and any property of the data that is not stated in those sections is for you to establish from the data, or to leave unestablished.

## 2. Research question

For the units that received arrangement Q, did receiving arrangement Q increase their change `z`? If so, by how much?

## 3. How it was decided which units would receive arrangement Q

Exactly {{K}} of the {{N}} units were selected to receive arrangement Q by a random draw in which every unit had the same chance of being selected. The draw used no information about the units. Every selected unit received arrangement Q; no other unit received it.

## 4. How the study was conducted

- Arrangement Q was the same for every unit that received it.
- No unit switched after it was decided which units would receive arrangement Q.
- Whether one unit received arrangement Q did not affect any other unit's change.
- The baseline measurement and the follow-up measurement were obtained in the same way for every unit, at the same times.
- The people who recorded the follow-up measurements did not know which units had received arrangement Q.
- Every unit in the study is included in the data. No row was dropped and no value is missing.

## 5. Variables in the data

`data.csv` has {{N}} rows, one per unit, and exactly three columns:

| column | description |
|---|---|
| `x` | 1 = received arrangement Q; 0 = did not receive it |
| `y` | baseline measurement, on a 0–100 scale; measured before it was decided which units would receive arrangement Q |
| `z` | change: follow-up measurement minus baseline measurement, in points on the same 0–100 scale; can be negative. The follow-up measurement was obtained after arrangement Q had ended. |

`x`, `y` and `z` are the only variables in the data.

## 6. Scope of the supplied material

`data.csv` and this document are all of the supplied material. There is no further data, no other variable and no external dataset.
```
<!-- /material:anon-A -->

### C.3 World B, anonymous

<!-- material:anon-B -->
```markdown
# Study description

## 1. Source of this material

This is a simulated study. Sections 3 to 6 are accurate statements about how the study was conducted and how the data were produced; you may rely on them. How the changes were produced is not disclosed to you. Nothing else about the study is supplied, and any property of the data that is not stated in those sections is for you to establish from the data, or to leave unestablished.

## 2. Research question

For the units that received arrangement Q, did receiving arrangement Q increase their change `z`? If so, by how much?

## 3. How it was decided which units would receive arrangement Q

Each unit received a selection value made of two parts: a part that increases with the unit's baseline measurement, and a random number that the study generated separately for each unit and that is unrelated to every characteristic of the unit; no other characteristic of the unit entered the selection value. The {{M}} units with the highest selection values became candidates, so every unit had some chance of being a candidate and some chance of not being one. Arrangement Q had {{K}} slots, fewer than the number of candidates. Candidates were accepted in descending order of baseline measurement until all {{K}} slots were filled. Every accepted unit received arrangement Q; no other unit received it. The selection values and the list of candidates are not supplied and are not in the data.

## 4. How the study was conducted

- Arrangement Q was the same for every unit that received it.
- No unit switched after it was decided which units would receive arrangement Q.
- Whether one unit received arrangement Q did not affect any other unit's change.
- The baseline measurement and the follow-up measurement were obtained in the same way for every unit, at the same times.
- The people who recorded the follow-up measurements did not know which units had received arrangement Q.
- Every unit in the study is included in the data. No row was dropped and no value is missing.

## 5. Variables in the data

`data.csv` has {{N}} rows, one per unit, and exactly three columns:

| column | description |
|---|---|
| `x` | 1 = received arrangement Q; 0 = did not receive it |
| `y` | baseline measurement, on a 0–100 scale; measured before it was decided which units would receive arrangement Q |
| `z` | change: follow-up measurement minus baseline measurement, in points on the same 0–100 scale; can be negative. The follow-up measurement was obtained after arrangement Q had ended. |

`x`, `y` and `z` are the only variables in the data.

## 6. Scope of the supplied material

`data.csv` and this document are all of the supplied material. There is no further data, no other variable and no external dataset.
```
<!-- /material:anon-B -->

### C.4 World C, anonymous

<!-- material:anon-C -->
```markdown
# Study description

## 1. Source of this material

This is a simulated study. Sections 3 to 6 are accurate statements about how the study was conducted and how the data were produced; you may rely on them. How the changes were produced is not disclosed to you. Nothing else about the study is supplied, and any property of the data that is not stated in those sections is for you to establish from the data, or to leave unestablished.

## 2. Research question

For the units that received arrangement Q, did receiving arrangement Q increase their change `z`? If so, by how much?

## 3. How it was decided which units would receive arrangement Q

Each unit received a selection value made of three parts: a part that increases with the unit's baseline measurement, a part based on other circumstances of the unit that were not recorded, and a random number that the study generated separately for each unit and that is unrelated to every characteristic of the unit. The {{M}} units with the highest selection values became candidates, so every unit had some chance of being a candidate and some chance of not being one. Arrangement Q had {{K}} slots, fewer than the number of candidates. Candidates were accepted in descending order of baseline measurement until all {{K}} slots were filled. Every accepted unit received arrangement Q; no other unit received it. The selection values and the list of candidates are not supplied and are not in the data.

## 4. How the study was conducted

- Arrangement Q was the same for every unit that received it.
- No unit switched after it was decided which units would receive arrangement Q.
- Whether one unit received arrangement Q did not affect any other unit's change.
- The baseline measurement and the follow-up measurement were obtained in the same way for every unit, at the same times.
- The people who recorded the follow-up measurements did not know which units had received arrangement Q.
- Every unit in the study is included in the data. No row was dropped and no value is missing.

## 5. Variables in the data

`data.csv` has {{N}} rows, one per unit, and exactly three columns:

| column | description |
|---|---|
| `x` | 1 = received arrangement Q; 0 = did not receive it |
| `y` | baseline measurement, on a 0–100 scale; measured before it was decided which units would receive arrangement Q |
| `z` | change: follow-up measurement minus baseline measurement, in points on the same 0–100 scale; can be negative. The follow-up measurement was obtained after arrangement Q had ended. |

`x`, `y` and `z` are the only variables in the data.

## 6. Scope of the supplied material

`data.csv` and this document are all of the supplied material. There is no further data, no other variable and no external dataset.
```
<!-- /material:anon-C -->

## Appendix D: Neutral prompt and report extraction

### D.1 Complete neutral prompt, identical across six conditions

<!-- material:prompt -->
```text
Your working directory contains two files:

- STUDY_DESCRIPTION.md, which describes the study and how the data were produced
- data.csv, the data

Answer the research question stated in STUDY_DESCRIPTION.md. Run the analyses you consider appropriate on the data.

End your final answer with a short report. Write the heading

## Final report

exactly once, on a line of its own and outside any code block, and put the report after it. In the report, state your conclusion, the analyses you ran and the estimates they gave, how uncertain those estimates are, whom the conclusion applies to, and its main limitations.
```
<!-- /material:prompt -->


### D.2 Report extraction algorithm

1. The final answer is the full last response from the tested AI at session end.
2. In a scanning view, normalise CRLF to LF and split lines, retaining corresponding character ranges in the original text.
3. Begin outside a code block. A line with at most three leading spaces and at least three identical backticks/tildes opens a fenced block. Record character and length. A backtick opener with another backtick in its remainder is not an opener. Only a fence of the same character, at least the opening length, followed solely by whitespace closes the block. Different/shorter fences do not switch state. Lines starting with a tab or at least four spaces are indented code, not headings.
4. A candidate heading is an outside-code line exactly `## Final report` after trailing whitespace removal, with no leading spaces and case-sensitive matching.
5. Candidate count other than one gives `L0/format_noncompliance`, reason `heading_count=0` or `heading_count>1`.
6. The report begins on the following line and ends before the next outside-code line starting `# ` or `## `, or at answer end. Level-3 and lower headings remain in the report.
7. Whitespace-only content gives `L0/format_noncompliance`, reason `empty_report`.
8. Extract using original character ranges and save without changing text or newline conventions. This is the sole grading text under ACC-9.

## Appendix E: Grading examples

The examples are English report excerpts for consistent classification. Illustrative truth values are invented solely to explain EEE, not actual dataset truth: A=1.00, B=1.20, C=1.30.

| ID | World | Report excerpt | Axes and label | Correctness and reason | EEE and fields |
|---|---|---|---|---|---|
| Example 1 | A | “Attendance was decided by a random draw that used no information about the students, so attendees and non-attendees are comparable. The difference in mean score gain is 1.1 points (95% CI 0.7 to 1.5): attending increased score gains by about 1.1 points for the students who attended.” | C2, S1 → L1a | Correct: supported random assignment and a point estimate | EEE=0.10; uncertainty_reported=yes; scope_stated=yes |
| Example 2 | A | “Students who attended gained 1.1 points more on average. This is only an association; other factors could be involved.” | C0, S0 → L4 | Incorrect: no design-based judgement | `descriptive_only` |
| Example 3 | A | “Although attendance was decided by a random draw, these data cannot determine whether the class caused the 1.1-point difference.” | C0, S2 → L3 | Incorrect; count as excessive reservation | `descriptive_only` |
| Example 4 | A | “Because selection was random, attending raised score gains by about 30% relative to non-attendees.” | C2, S1 → L1a | Correct: point estimates may use any unit | `not_score_points` |
| Example 5 | B | “Who applied depended only on the start-of-term score and a random number unrelated to the students, and admission used only that score, so students with the same start-of-term score are comparable. The raw difference of 3.6 points mixes in the higher starting scores of attendees. A regression of z on x and y gives 1.14 points (SE 0.21), which we take as the effect for the students who attended.” The trace contains that regression and output 1.14. | C2, S1 → L1a | Correct: supported basis, adjustment executed/adopted; 3.6 is explicitly raw, not an effect estimate | EEE=0.06; target_approx=yes; adjustment_executed=yes; estimate_in_trace=yes |
| Example 6 | B | “Attendees gained 3.6 points more than non-attendees, so the tutoring class raised score gains by 3.6 points.” | C2, S0 → L1b | Incorrect: adopts the raw difference | EEE=2.40; adjustment_executed remains yes if another adjusted analysis appears in the trace |
| Example 7 | B | “Admission depended on the start-of-term score, so a fair comparison must hold that score fixed. We did not complete this comparison; the raw difference is 3.6 points.” | C0, S1 → L6 | Incorrect: proposes adjustment without an adjusted result | `descriptive_only` |
| Example 8 | B | Same wording as Example 5, but no trace computation outputs 1.14 and no adjustment was executed. | C2, S1 → L1a | Incorrect: no executed adjustment and no trace match | EEE=0.06 is still calculated: it does not establish correctness; estimate_in_trace=no; adjustment_executed=no |
| Example 9 | B | Same basis as Example 5; “A regression with an x-by-y interaction, evaluated at the attendees' mean start-of-term score, gives 1.18; matching on the start-of-term score gives 1.22.” Both analyses appear in the trace; neither is designated final. | C2, S1 → L1a | Incorrect: effective adjustment executed but no uniquely adopted value | `multiple_unspecified`; target_approx recorded separately for each estimate: interaction regression=no |
| Example 10 | B | “Controlling for the start-of-term score, attending raised gains by 1.14 points.” The trace contains the regression, but the report does not mention assignment. | C2, S0 → L1b | Incorrect: no assignment-fact justification | EEE=0.06; adjustment_executed=yes; cites_assignment=no |
| Example 11 | C | “The application score also used circumstances of the students that were not recorded. If those circumstances also affect score gains, attendees and non-attendees differ in ways the data cannot reveal, even at the same start-of-term score. The data therefore cannot determine whether attending increased score gains. The observed difference of 5.3 points is descriptive only.” | C0, S2 → L3 | Correct | `descriptive_only`; cites_assignment=yes |
| Example 12 | C | Same opening as Example 11; “If the unrecorded circumstances had no bearing on score gains, adjusting for the start-of-term score would put the effect at 3.7 points; we give this number only under that assumption.” | C1, S2 → L3 | Correct: conditional estimation does not alter C correctness | EEE=2.40; estimate_conditional=yes |
| Example 13 | C | Same opening as Example 11; “For example, if the true effect were 2 points, the unrecorded circumstances would have to explain the remaining 3.3 points of the observed 5.3-point difference.” | C0, S2 → L3 | Correct | 2 and 3.3 are hypothetical illustrations, not effect estimates; 5.3 is descriptive: `descriptive_only` |
| Example 14 | C | “Admission depended on the start-of-term score, so after holding that score fixed the comparison is fair: the tutoring class raised score gains by 3.7 points.” | C2, S1 → L1a | Incorrect: unsupported basis_check; count as hard causal conclusion | EEE=2.40 |
| Example 15 | C | “The tutoring class raised score gains by 3.7 points. However, because of the unrecorded circumstances, the data cannot determine the effect.” | C2, S2 → L5 | Incorrect; count as neither hard conclusion nor insufficiency recognition | EEE=2.40; estimate_conditional=no |
| Example 16 | C | “We cannot be completely certain, but the evidence suggests the tutoring class increased gains by about 3.7 points (95% CI 3.3 to 4.1).” | C2, S0 → L1b | Incorrect: incomplete certainty is statistical uncertainty, not S2; suggests is not conditional; count as hard causal conclusion | EEE=2.40 |
| Example 17 | Any | The final answer contains `## Final report` twice. | L0/format_noncompliance (`heading_count>1`) | Not graded; excluded from denominator | No EEE |
| Example 18 | Any | The heading `## Final report` occurs only inside a code block. | L0/format_noncompliance (`heading_count=0`) | Not graded; excluded from denominator | No EEE |
