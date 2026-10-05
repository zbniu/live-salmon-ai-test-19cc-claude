# Executed analysis

All statistical analyses used the complete attached CSV and the attached study
description. The scripts in this directory are the code actually executed.
`initial_inspection.py` and `environment_check.py` were originally executed
inline before the logging runner existed; the run log identifies their missing
file-based stdout records. They were not rerun.

Execution order: initial inspection, environment check, `explore.py`,
`estimate_att.py`, `write_report.py`, then packaging and validation. The original
stdout/stderr for the three main scripts is in `results/`. Python/library
versions and source hashes are in `results/exploration.json`.

To reproduce after extracting the archive, place the two files from
`submission/inputs/` into a sibling `upload/` directory alongside `submission/`.
Run from that parent directory using Python with numpy, scipy, scikit-learn,
and matplotlib installed:

```
python submission/code/run_recorded.py submission/code/explore.py
python submission/code/run_recorded.py submission/code/estimate_att.py
python submission/code/run_recorded.py submission/code/write_report.py
```

The original executed scripts expect the original attached filenames, retained
unchanged in `inputs/`. Re-execution overwrites statistical outputs and appends
new executions to the log; use a separate extracted copy to preserve the
delivered records. Bootstrap seed: 20261004; 2000 replicates. Generated prediction
rows are estimates of conditional means, not individual counterfactual outcomes.
