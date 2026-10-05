# Screened Synthetic Data Batch Qualification

**Status:** All 12 selected datasets qualify under the registered screening protocol. No tested models have run.

The owner authorized a finite candidate pool and transparent GEN screening before candidate generation. Both programs generated all 60 registered candidates using unchanged K1 parameters, assignment, random streams, numerical algorithms and public materials. Selection takes the lowest-seed qualifying candidates within each phase/world. No candidate seeds were appended and no student values were manually edited.

## Complete pool and selection

| Phase/world | Generated | Qualified | Selected |
|---|---:|---:|---:|
| development/A | 10 | 8 | 1 |
| development/B | 10 | 9 | 1 |
| development/C | 10 | 10 | 1 |
| formal/A | 10 | 9 | 3 |
| formal/B | 10 | 10 | 3 |
| formal/C | 10 | 10 | 3 |

All 4 candidate quality failures are retained in FAILURES.json and POOL_INDEX.csv. GEN_TABLE.csv reports all 420 candidate checks, including unselected candidates. Both programs retained 120 public-only reference analyses and 4000 B bootstrap attempts each; every candidate and bootstrap pair agreed.

## Selected datasets

| Phase | World | Seed | SATT | Reference estimate | SE | 95% interval |
|---|---|---:|---:|---:|---:|---|
| development | A | 730001 | 0.99963539 | 0.89367143 | 0.21185902 | [0.47842775120951764, 1.3089151095433227] |
| development | B | 730001 | 1.1763322 | 1.244004 | 0.21390777 | [0.8247447881985126, 1.6632632333076538] |
| development | C | 730001 | 1.2910136 | 3.7390342 | 0.19282927 | [3.36108881854532, 4.116979542431461] |
| formal | A | 740001 | 0.97529986 | 0.84774664 | 0.21416335 | [0.42798647731858935, 1.2675068073209856] |
| formal | A | 740002 | 1.0010757 | 1.0109184 | 0.20837581 | [0.6025018609877817, 1.4193350194438645] |
| formal | A | 740004 | 0.99770939 | 1.1102228 | 0.21668401 | [0.6855221929523394, 1.5349235023653536] |
| formal | B | 740001 | 1.176442 | 1.2005672 | 0.21079637 | [0.7874063657147827, 1.6137281236454482] |
| formal | B | 740002 | 1.1706383 | 1.1686534 | 0.20651398 | [0.7638859938767368, 1.5734208056221315] |
| formal | B | 740003 | 1.1793402 | 1.3146435 | 0.21469596 | [0.8938394215918624, 1.735447573579722] |
| formal | C | 740001 | 1.2767578 | 3.8872387 | 0.19601836 | [3.503042695757214, 4.271434670180666] |
| formal | C | 740002 | 1.2725385 | 3.3984957 | 0.19600079 | [3.0143341451983887, 3.782657243671054] |
| formal | C | 740003 | 1.2692017 | 3.7089503 | 0.19667033 | [3.323476425584613, 4.094424117233155] |

All 12 selected cases and named/anonymous pairs pass every applicable GEN check. Hidden truth is checked separately from public reference analyses. C estimates remain descriptive and its reports recognize insufficient information. ACC-10 is true for this screened batch.

## Interpretation and execution boundary

This is an explicitly screened synthetic benchmark, conditional on GEN qualification. It is not an unscreened random sample. Its guaranteed acceptance coverage is a selection property, not a claim that nominal confidence intervals cover every future draw. The original calibration describes the unchanged unfiltered generator. All pool exclusions must accompany any publication, and model-performance conclusions apply to the selected benchmark.

Model, budget and scoring-personnel registration and tested-model runtime isolation remain required before experiments. Offline reference sandbox checks do not certify the future model environment. No model calls or publication are authorized by data qualification.
