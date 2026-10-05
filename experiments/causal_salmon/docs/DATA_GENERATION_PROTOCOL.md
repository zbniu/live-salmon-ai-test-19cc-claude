# Data generation protocol

This is a screened synthetic benchmark. This document controls the candidate seeds and final batch selection; [planning.md](../planning.md) supplies the outcome, numerical, statistical and evaluation definitions. Performance on the selected questions is conditional on GEN qualification and cannot be generalized to unscreened random datasets.

## Frozen settings

Use the confirmed K1 complete row in [selected_parameters.json](../configs/selected_parameters.json): 2,000 students; 600 participants; 900 applicants in B/C; baseline scores Uniform(45,75); gain intercept 10; gamma 0.25; beta 0.5; kappa 1.2; noise multiplier 3; treatment increment 0.10 times expected untreated improvement. Retain the original 0–100 scale.

The study tag is 20260929. Random streams use PCG64 raw integers, the specified high-52-bit uniform transform, independent purpose/world/variable streams and the prescribed float64 operation order. CSVs use `.17g` precision. Named and anonymous sessions share identical CSV bytes and mechanically paired descriptions.

## Finite candidate pool

| Phase | Worlds | Seeds per world | Purpose | Selected per world |
|---|---|---|---:|---:|
| Development | A, B, C | 730001–730010 | 2 | 1 |
| Formal | A, B, C | 740001–740010 | 3 | 3 |

Generate all 60 candidates, ordered by development then formal, A/B/C and ascending seed. Do not stop when a quota is reached. Each candidate must pass every applicable GEN-1–7 check and independent comparison. Within each phase/world select the lowest-seed qualifying candidates up to its quota. Do not extend the pool, change parameters, edit student values or rank candidates by appearance. An unmet quota stops the batch. Numerical failures require investigation and retention of the original evidence.

## Independent verification

Both programs generate the entire pool separately and use their own statistical implementations. Complete purpose-4 selftests with seeds 709000–709009 in every world and register source/environment identities before candidate execution. Neither program imports the other's generation or statistical code.

Each B candidate requires all 200 ordered stratified bootstrap attempts, recomputing support and refitting from scratch. Compare CSV bytes, treatment assignments, common hidden values, stream inputs, statistics, intervals, bootstrap results, reference decisions and GEN outcomes. Preserve every failed candidate in the complete pool ledger; do not remove failures from calibration denominators.

Public references receive only `data.csv` and `STUDY_DESCRIPTION.md` in a sandbox with blocked repository and network access. A uses the prescribed mean difference; B/C use interaction OLS, participant standardization and HC3 uncertainty. C reports insufficient evidence and treats its estimate as descriptive. Hidden-truth checks run separately.

## Delivery and interpretation

Store the selected 3 development and 9 formal CSVs in `datasets/public/`, with controlled truth in `datasets/ground_truth/`. Store the full pool, qualification tables, independent comparisons and reports in `results/quality_checks/data/`. Deliver all 60 outcomes and exclusion reasons, including unselected candidates.

Only a complete independently qualified 12-case batch receives ACC-10 acceptance. Screening guarantees acceptance for selected questions; it does not improve the estimator's nominal coverage. Calibration describes the underlying unfiltered generator.

Model, budget, scoring-personnel and tested-model runtime registrations must be completed before model experiments. Data qualification authorizes no tested-model calls or publication.
