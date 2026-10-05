# Final data generation plan

**Status:** The complete 60-candidate pool has been generated and independently verified. All 12 selected datasets pass qualification. Model experiments have not started.

The [generation protocol](DATA_GENERATION_PROTOCOL.md) defines the final pool and selection rules. The [complete specification](../planning.md) defines numerical calculations and experiment evaluation.

## Parameters and outcomes

Use the confirmed K1 row: `n=2000`, `a=45`, `b_multiplier=3`, `gamma=0.25`, `beta=0.5`, `kappa=1.2`, `M=900`, `K=600`, `m_intercept=10`, `effect_fraction=0.1`.

```text
m    = 10 + 0.25 * (y - 60) + 2 * u
z(0) = m + epsilon
z(1) = z(0) + 0.10 * m
```

`y` is Uniform(45,75), `u` is Uniform(-sqrt(3),sqrt(3)), and `epsilon` is Uniform(-3sqrt(3),3sqrt(3)). Public data contain `x,y,z`; the participant SATT is computed from hidden potential outcomes. Scores remain on the 0–100 scale.

## Candidate pool and selection

| Phase | Seeds per world | Purpose | Candidates | Selected |
|---|---|---:|---:|---:|
| Development | 730001–730010 | 2 | 30 | 3 |
| Formal | 740001–740010 | 3 | 30 | 9 |

Both implementations generate every candidate. Select the first qualifying seed in each development world and the first three in each formal world. Keep all failed candidates and reasons. Do not extend the pool or edit values.

| Phase | World | Selected seeds |
|---|---|---|
| Development | A, B, C | 730001 in each world |
| Formal | A | 740001, 740002, 740004 |
| Formal | B | 740001, 740002, 740003 |
| Formal | C | 740001, 740002, 740003 |

## Execution and acceptance

1. Freeze the specification, K1 settings, candidate pool, six descriptions, substitution table and shared prompt; register file hashes.
2. Register both source trees and environments. Each completes 30 selftest cases, 60 public references and 2000 B bootstrap attempts using purpose 4; compare their results before candidate execution.
3. Generate all 60 candidates with two processes and single-thread numerical libraries. Retain all 200 B bootstrap attempts per candidate, including failures.
4. Run public-only references and separate hidden qualification. A uses a mean difference; B/C use interaction OLS, participant standardization and HC3. C recognizes insufficient causal evidence.
5. Compare all 60 pairs, including CSV bytes, assignments, hidden values, streams, intervals, GEN outcomes and 4000 B bootstrap results.
6. Apply the fixed seed-order rule. Copy the 12 jointly accepted cases into permanent dataset directories. Check paired descriptions and all applicable GEN conditions; accept the batch only when every selected case passes.
7. Verify recovery, deterministic report rebuilding and complete file hashes. Deliver selected and pool indices, all GEN outcomes, failures and independent comparison records.

The complete pool contains 56 qualifying candidates and four GEN-4 coverage failures. Both programs agree on every comparison and select the same 12 cases. Each generated 120 public references and 4000 B bootstrap attempts. This is a benchmark conditional on disclosed GEN screening; its results cannot establish performance on an unfiltered question population.

## Storage and experiment boundary

Final CSVs are in `datasets/public/{development,formal}/`; controlled truth is in `datasets/ground_truth/`. Qualification evidence is in `results/quality_checks/data/`, with settings in `configs/data_generation.json` and submission checksums in `manifests/delivery.json`.

The Git package includes public CSVs, candidate CSVs, code, settings and compact reports. Hidden records and complete controller execution evidence are excluded. See [repository structure](REPOSITORY_STRUCTURE.md) and [reproduction commands](reproduction.md).

Model, budget, scoring-personnel and tested-model isolation registration remain required before any model experiment. No tested models have run and no repository has been published.
