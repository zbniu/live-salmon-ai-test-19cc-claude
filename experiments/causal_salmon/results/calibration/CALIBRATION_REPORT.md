# Causal Salmon: Complete Offline Calibration Report

Status: calibration complete; K1 confirmed; final synthetic datasets qualified; tested-model experiments not started.

## Protocol, completeness and independent verification

Frozen protocol SHA-256: `f85fedf447c734d9d5e7a2cb630284fe18c7091c5cf653610adbc43ec8e7144c`. Research tag: `20260929`. Calibration seeds: `703000–703999`. Each independently authored implementation must retain five candidates × three worlds × 1,000 repetitions.

Independent comparison: **passed**; 15000/15,000 repetitions and 1000000/1,000,000 bootstrap estimates checked. Both regenerate data. Public CSV hashes and treatment vectors are exact; common numerical outputs use the registered 1e-8 relative/absolute tolerance; all statuses and decisions must agree.

Both implementations retain public CSVs, recoverable hidden student tables, truth/random-flow registration, all 200 bootstrap attempts per B repetition, reference reports/access audits, and completion manifests. Main and independent code, initial selftests, environment and dependency identities are archived in the initial registration files and each run identity.

CAL-9 final-exam checks are separate from calibration. Final descriptions have been frozen and their mechanical pairing verified for the selected batch.

## Candidate and primary-method results

| Candidate | World | Mean SATT | Signed bias | MCSE | Relative bias | Coverage | Precision ratio | Distinction ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| K1 | A | 1.0004106 | 0.0043426867 | 0.0064130007 | 0.0043409043 | 0.959 | 4.9330668 | 0 |
| K1 | B | 1.1713078 | 0.005172647 | 0.00676404 | 0.0044161294 | 0.944 | 5.4760182 | 11.289053 |
| K1 | C | 1.2830855 | 2.3972007 | 0.0061443635 | 1.8683094 | 0 | 6.6035684 | 8.39578 |
| K2 | A | 1.0004106 | 0.0043426867 | 0.0064130007 | 0.0043409043 | 0.959 | 4.9330668 | 0 |
| K2 | B | 1.1538737 | 0.0041817616 | 0.0064508662 | 0.0036241067 | 0.948 | 5.6564018 | 10.62881 |
| K2 | C | 1.2750217 | 2.3754674 | 0.005939473 | 1.86308 | 0 | 6.788435 | 8.1985448 |
| K3 | A | 1.0004106 | 0.0043426867 | 0.0064130007 | 0.0043409043 | 0.959 | 4.9330668 | 0 |
| K3 | B | 1.1443447 | 0.0033718905 | 0.0062950462 | 0.0029465688 | 0.946 | 5.7485453 | 10.206709 |
| K3 | C | 1.2676743 | 2.3818185 | 0.0058020951 | 1.8788884 | 0 | 6.9091216 | 7.7904992 |
| K4 | A | 1.0004106 | 0.0052869534 | 0.0054057072 | 0.0052847834 | 0.964 | 5.852289 | 0 |
| K4 | B | 1.1713078 | 0.0046399021 | 0.0053094827 | 0.0039613003 | 0.955 | 6.9761986 | 14.249286 |
| K4 | C | 1.2830855 | 2.3956844 | 0.0046291216 | 1.8671277 | 0 | 8.7651024 | 11.035986 |
| K5 | A | 1.0004106 | 0.0043426867 | 0.0064130007 | 0.0043409043 | 0.959 | 4.9330668 | 0 |
| K5 | B | 1.1713078 | 0.005172647 | 0.00676404 | 0.0044161294 | 0.944 | 5.4760182 | 11.289053 |
| K5 | C | 1.2964986 | 2.705251 | 0.0059345426 | 2.0865822 | 0 | 6.9085167 | 8.0940974 |

Bias is mean(E−T), not mean absolute error. MCSE and all SDs use ddof=1. Cross-repeat precision is mean(T)/SD(E−T); distinction is mean(N−E)/SD(E). Nominal intervals are closed E ±1.96 SE. These are calibration results, not tested-AI results.

| Candidate | State | CAL-1 | CAL-2 | CAL-3 | CAL-4 | CAL-5 | CAL-6 | CAL-7 | CAL-8 | CAL-9 | CAL-10 | CAL-11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| K1 | passed | pass | pass | pass | pass | pass | pass | pass | pass | deferred | pass | pass |
| K2 | passed | pass | pass | pass | pass | pass | pass | pass | pass | deferred | pass | pass |
| K3 | passed | pass | pass | pass | pass | pass | pass | pass | pass | deferred | pass | pass |
| K4 | passed | pass | pass | pass | pass | pass | pass | pass | pass | deferred | pass | pass |
| K5 | passed | pass | pass | pass | pass | pass | pass | pass | pass | deferred | pass | pass |

CAL-4 requires at least 999/1,000 repetitions with ≥20 controls in every prescribed participant-score segment, separately in B and C. Candidate science status follows CAL-1 and CAL-3–7. Integrity failures invalidate implementation evidence and cannot justify changing candidates.

## Mandatory diagnostics and support

| Candidate | Diagnostic | Status | Available / 1000 | Bias | MCSE | Relative bias | Coverage | Conflict |
|---|---|---|---:|---:|---:|---:|---:|---|
| K1 | D1 | ok | 1000 | 0.013303153 | 0.0069771604 | 0.011357521 | 0.954 | False |
| K1 | D2 | ok | 1000 | 0.0041187082 | 0.0069447903 | 0.0035163328 | 0.95 | False |
| K2 | D1 | ok | 1000 | 0.0069338482 | 0.0066461137 | 0.0060091914 | 0.952 | False |
| K2 | D2 | ok | 1000 | 0.0023907736 | 0.0066131342 | 0.0020719543 | 0.948 | False |
| K3 | D1 | ok | 1000 | 0.012698369 | 0.0064349994 | 0.011096629 | 0.947 | False |
| K3 | D2 | ok | 1000 | 0.00040623636 | 0.0063960885 | 0.00035499474 | 0.945 | False |
| K4 | D1 | ok | 1000 | 0.013109697 | 0.0054726365 | 0.011192358 | 0.95 | False |
| K4 | D2 | ok | 1000 | 0.0038985032 | 0.0054374553 | 0.0033283335 | 0.95 | False |
| K5 | D1 | ok | 1000 | 0.013303153 | 0.0069771604 | 0.011357521 | 0.954 | False |
| K5 | D2 | ok | 1000 | 0.0041187082 | 0.0069447903 | 0.0035163328 | 0.95 | False |

D1 uses the exact rank-defined five segments. D2 uses support y≥minimum participant y, quadratic logit with zero initialization, ≤50 Newton steps and max|delta|<1e-10; no penalty, step reduction or weight trimming. Every bootstrap refits support and model. A single confirmed diagnostic failure makes its entire candidate aggregate not evaluable; remaining repeats are not used to claim diagnostic performance.

- K1: B segment support passes 1000/1000; C 1000/1000. D2 maximum normalized control weight range 0.0018869829–0.0045267239; ESS range 451.1572–603.83321; failed bootstrap attempts 0.
- K2: B segment support passes 1000/1000; C 1000/1000. D2 maximum normalized control weight range 0.0015678566–0.0036192254; ESS range 539.05371–706.4905; failed bootstrap attempts 0.
- K3: B segment support passes 1000/1000; C 1000/1000. D2 maximum normalized control weight range 0.0014908695–0.0034797418; ESS range 598.3446–788.34949; failed bootstrap attempts 0.
- K4: B segment support passes 1000/1000; C 1000/1000. D2 maximum normalized control weight range 0.0018869829–0.0045267239; ESS range 451.1572–603.83321; failed bootstrap attempts 0.
- K5: B segment support passes 1000/1000; C 1000/1000. D2 maximum normalized control weight range 0.0018869829–0.0045267239; ESS range 451.1572–603.83321; failed bootstrap attempts 0.

## Reference analysis and GEN diagnostics

Public reference analysis receives only two fixed-name files in an opaque staged directory and a standalone pre-registered numerical executable. Method selection uses the public allocation paragraph. The operating-system sandbox denies project/parent listing and network access; runtime libraries are explicitly whitelisted. Backend truth is joined only by the hidden-side checker. Access policies, probes, input hashes, outputs and traces are retained for each named/anonymous pair. Reference templates are checked against the report contract; they are not a general automated replacement for later human scoring.

| Candidate | World | GEN condition | Passed / applicable | Failure reasons |
|---|---|---|---:|---|
| K1 | A | GEN-1 | 1000/1000 | none |
| K1 | A | GEN-2 | 1000/1000 | none |
| K1 | A | GEN-4 | 959/1000 | interval_misses_truth: 41; lower_interval_not_positive: 4 |
| K1 | A | GEN-7 | 1000/1000 | none |
| K1 | B | GEN-1 | 1000/1000 | none |
| K1 | B | GEN-2 | 1000/1000 | none |
| K1 | B | GEN-3 | 1000/1000 | none |
| K1 | B | GEN-4 | 944/1000 | interval_misses_truth: 56 |
| K1 | B | GEN-5 | 1000/1000 | none |
| K1 | B | GEN-7 | 1000/1000 | none |
| K1 | C | GEN-1 | 1000/1000 | none |
| K1 | C | GEN-2 | 1000/1000 | none |
| K1 | C | GEN-3 | 1000/1000 | none |
| K1 | C | GEN-6 | 1000/1000 | none |
| K1 | C | GEN-7 | 1000/1000 | none |
| K2 | A | GEN-1 | 1000/1000 | none |
| K2 | A | GEN-2 | 1000/1000 | none |
| K2 | A | GEN-4 | 959/1000 | interval_misses_truth: 41; lower_interval_not_positive: 4 |
| K2 | A | GEN-7 | 1000/1000 | none |
| K2 | B | GEN-1 | 1000/1000 | none |
| K2 | B | GEN-2 | 1000/1000 | none |
| K2 | B | GEN-3 | 1000/1000 | none |
| K2 | B | GEN-4 | 948/1000 | interval_misses_truth: 52 |
| K2 | B | GEN-5 | 1000/1000 | none |
| K2 | B | GEN-7 | 1000/1000 | none |
| K2 | C | GEN-1 | 1000/1000 | none |
| K2 | C | GEN-2 | 1000/1000 | none |
| K2 | C | GEN-3 | 1000/1000 | none |
| K2 | C | GEN-6 | 1000/1000 | none |
| K2 | C | GEN-7 | 1000/1000 | none |
| K3 | A | GEN-1 | 1000/1000 | none |
| K3 | A | GEN-2 | 1000/1000 | none |
| K3 | A | GEN-4 | 959/1000 | interval_misses_truth: 41; lower_interval_not_positive: 4 |
| K3 | A | GEN-7 | 1000/1000 | none |
| K3 | B | GEN-1 | 1000/1000 | none |
| K3 | B | GEN-2 | 1000/1000 | none |
| K3 | B | GEN-3 | 1000/1000 | none |
| K3 | B | GEN-4 | 946/1000 | interval_misses_truth: 54 |
| K3 | B | GEN-5 | 1000/1000 | none |
| K3 | B | GEN-7 | 1000/1000 | none |
| K3 | C | GEN-1 | 1000/1000 | none |
| K3 | C | GEN-2 | 1000/1000 | none |
| K3 | C | GEN-3 | 1000/1000 | none |
| K3 | C | GEN-6 | 1000/1000 | none |
| K3 | C | GEN-7 | 1000/1000 | none |
| K4 | A | GEN-1 | 1000/1000 | none |
| K4 | A | GEN-2 | 1000/1000 | none |
| K4 | A | GEN-4 | 964/1000 | interval_misses_truth: 36; lower_interval_not_positive: 1 |
| K4 | A | GEN-7 | 1000/1000 | none |
| K4 | B | GEN-1 | 1000/1000 | none |
| K4 | B | GEN-2 | 1000/1000 | none |
| K4 | B | GEN-3 | 1000/1000 | none |
| K4 | B | GEN-4 | 955/1000 | interval_misses_truth: 45 |
| K4 | B | GEN-5 | 1000/1000 | none |
| K4 | B | GEN-7 | 1000/1000 | none |
| K4 | C | GEN-1 | 1000/1000 | none |
| K4 | C | GEN-2 | 1000/1000 | none |
| K4 | C | GEN-3 | 1000/1000 | none |
| K4 | C | GEN-6 | 1000/1000 | none |
| K4 | C | GEN-7 | 1000/1000 | none |
| K5 | A | GEN-1 | 1000/1000 | none |
| K5 | A | GEN-2 | 1000/1000 | none |
| K5 | A | GEN-4 | 959/1000 | interval_misses_truth: 41; lower_interval_not_positive: 4 |
| K5 | A | GEN-7 | 1000/1000 | none |
| K5 | B | GEN-1 | 1000/1000 | none |
| K5 | B | GEN-2 | 1000/1000 | none |
| K5 | B | GEN-3 | 1000/1000 | none |
| K5 | B | GEN-4 | 944/1000 | interval_misses_truth: 56 |
| K5 | B | GEN-5 | 1000/1000 | none |
| K5 | B | GEN-7 | 1000/1000 | none |
| K5 | C | GEN-1 | 1000/1000 | none |
| K5 | C | GEN-2 | 1000/1000 | none |
| K5 | C | GEN-3 | 1000/1000 | none |
| K5 | C | GEN-6 | 1000/1000 | none |
| K5 | C | GEN-7 | 1000/1000 | none |

GEN frequencies are separate diagnostics. Every repetition, including GEN failures, remains in the original CAL denominators. GEN-4 uses per-case T/SE and includes coverage and a positive lower limit; it does not replace CAL-3. C requires information insufficiency and ≥50% adjusted error, not a nonsignificant result.

## Failures and diagnosis

No unavailable primary/diagnostic fits or failed bootstrap attempts were found in the complete independent comparison. All GEN failures remain in the original CAL denominators.

## Confirmed parameters

K1 is the first eligible row in the registered K1–K5 order and was confirmed by the study owner. The complete row is `n=2000`, `a=45`, `b_multiplier=3`, `gamma=0.25`, `beta=0.5`, `kappa=1.2`, `M=900`, `K=600`, `m_intercept=10`, `effect_fraction=0.1`. Final questions use the separately registered finite-pool policy.

## Evidence identities and reproduction

| Artifact | SHA-256 |
|---|---|
| Main summary | `00bbade04686ba005c69cd71854afbe722c67425d20fb996175fbc49e6faac39` |
| Independent summary | `b536ba967e0a4420205bf2d3c9960694327127e0b0c02e5845cd443c6437b810` |
| Full comparison | `c42ec794d1888a69733500c8a22fbe01a04bd4800a18772e7dabc6356275fb68` |
| Dependency lock | `01e13f7ff7e532a4eb267c6827fee0fb431b794560856ec755e5ee6963bae21f` |

All per-repetition files are fingerprinted in their evidence.sha256.json; COMPLETE contains that manifest hash. Public reference evidence has its own manifest and is additionally pinned by the main external-evidence manifest. Input protocol/configuration/environment identities are in run.json; raw evidence is never overwritten.

Source, settings and final file identities are registered in manifests/. Reproduction commands are provided in docs/reproduction.md. Calibration uses all registered repetitions; final-question screening does not change these calibration results.
