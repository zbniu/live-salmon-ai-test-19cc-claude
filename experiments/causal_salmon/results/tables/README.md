# Six-model result tables

Scope: six models × F01–F12 = 72 answers, 68 PASS, 4 FAIL, 0 UNKNOWN. A and B each have 24/24 PASS; C has 20/24. These are 72 answers to six numeric datasets, not 72 independent dataset draws. F13–F18 have been abandoned after results were reviewed.

| File | Contents |
|---|---|
| [model_summary.csv](model_summary.csv) | Six-model summary; original planned denominator columns are retained as historical metadata |
| [methods_and_results.csv](methods_and_results.csv) | Adopted method descriptions and estimate ranges, not confidence intervals |
| [case_results.csv](case_results.csv) | All 72 grades, report quotations, adopted values, optional EEE and evidence paths |
| [semantic_pairs.csv](semantic_pairs.csv) | All 36 named/anonymous pairs |
| [numeric_error_by_dataset.csv](numeric_error_by_dataset.csv) | Primary numerical-error view: 36 model/dataset combinations, with separate named/anonymous values and EEE |
| [numeric_error.csv](numeric_error.csv) | Supplementary descriptive means by model/world; not estimator rankings |

[Per-model explanations](../evaluations/README.md), [submitted evidence](../submissions/README.md) and [report](../../README.md#3-results-and-analysis-methods) supply interpretation and original files. The [original source registration](../../manifests/original_table_provenance.json) is preserved as historical provenance; current copied paths and hashes are in [the packaging provenance](../../manifests/packaging_provenance.json).

EEE does not determine PASS. Blank C estimates/EEE for justified refusals are not zero. Scalar SATT is research-side metadata; full student truth is excluded. Source labels, original prompt delivery and isolation were not independently authenticated. No submitted code was executed to produce this export. The rubric was simplified after initial submissions, as disclosed in [reporting scope](../../docs/reporting_scope.md).
