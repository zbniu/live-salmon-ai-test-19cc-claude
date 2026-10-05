"""Generate the report from recorded results, without rerunning analyses."""
import hashlib
import json
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
workspace = root.parent
a = json.loads((root/'results'/'02_descriptive.json').read_text())
u = a['unadjusted']
att = json.loads((root/'results'/'04_att_inference.json').read_text())
models = json.loads((root/'results'/'03_adjusted.json').read_text())
linear, quadratic = models[1], models[2]
ci = att['approximate_randomization_ci95']
report = f'''# Tutoring and score gain

The research question is whether attending the tutoring class increased score gain `z` for the students who attended, and by how much.

**The randomized study provides statistical evidence of a positive average causal effect. The adopted estimate is an increase of {u['difference']:.2f} score points ({u['difference']:.6f} before rounding) for attendees, with an approximate 95% randomization interval of {ci[0]:.2f} to {ci[1]:.2f} points.** This is the numerical result that answers the research question. It estimates the average additional gain caused by tutoring, rather than the total gain during the term. The exact realized causal effect and each student's individual benefit cannot be determined from these files.

I used only the supplied study description and the complete CSV. All 2,000 rows were analyzed: 600 attendees and 1,400 nonattendees, with no missing or nonfinite values and no exclusions, imputation, or outcome transformations. The observed baseline scores and reconstructed end scores were within the stated 0–100 scale.

| Group | Students | Mean score gain | SD of score gain |
|---|---:|---:|---:|
| Attended tutoring | 600 | {u['treated_mean']:.6f} | 4.501767 |
| Did not attend | 1,400 | {u['control_mean']:.6f} | 4.114024 |

The primary estimate is the attendee mean minus the nonattendee mean: {u['treated_mean']:.6f} − {u['control_mean']:.6f} = {u['difference']:.6f} points. The attendees' total mean gain of {u['treated_mean']:.2f} points is not the estimated tutoring effect, since students also gained points without tutoring.

The study states that exactly 600 students were selected by a random draw using no student information, everyone complied, and students' attendance did not affect other students' outcomes. These facts support a causal interpretation of the randomized comparison. The comparison does not require the relationship between baseline score and gain to be linear or the treatment effect to be identical for all students.

To match the question's focus on the actual attendees, define their average causal effect as the mean of `Z(1) − Z(0)` over the 600 selected students. Only `Z(1)` is observed for them. The error in the primary estimator relative to this target is the difference between attendees' and nonattendees' mean untreated potential gains `Z(0)`. Under the stated complete random draw, this error has mean zero and variance `S0² × (1/600 + 1/1400)`, where `S0²` is the finite-population variance of untreated gains. Using the observed controls' sample variance ({att['control_sample_variance']:.6f}) to estimate `S0²` gives a standard error of {att['randomization_error_se']:.6f} points. The reported interval uses the large-sample normal approximation, estimate ± 1.96 standard errors. Its coverage is approximate over repeated random draws, targeting the attendees selected in each draw; it is not an exact guarantee about these 600 students.

As a conventional randomized-group comparison, the Welch standard error is {u['se']:.6f}, its 95% interval is {u['ci95'][0]:.2f} to {u['ci95'][1]:.2f}, and its two-sided p-value is {u['p_two_sided']:.6g}. This alternative also supports a positive average effect. Its uncertainty calculation differs from the attendee-targeted calculation above.

Attendees started {abs(a['baseline_difference']):.2f} points lower on average, and baseline score predicted gain in both groups. Sensitivity analyses therefore adjusted for this pre-treatment score. Separate linear regressions for the two groups, standardized to the attendees' baseline-score distribution, estimated an effect of {linear['effect']:.2f} points (HC3 robust, approximate 95% interval {linear['ci95'][0]:.2f} to {linear['ci95'][1]:.2f}). Separate quadratic regressions gave {quadratic['effect']:.2f} points ({quadratic['ci95'][0]:.2f} to {quadratic['ci95'][1]:.2f}); a common-slope linear ANCOVA gave {models[0]['effect']:.2f} points ({models[0]['ci95'][0]:.2f} to {models[0]['ci95'][1]:.2f}). These are model-assisted checks, not replacements for the primary randomized comparison, and their intervals use regression-based uncertainty.

A Monte Carlo randomization test, drawing 99,999 assignments of exactly 600 attendees with seed 20261004, produced 4 absolute mean differences at least as large as the observed one. The plus-one two-sided p-value was {att['sharp_null_test']['p_two_sided_plus_one']:.6g} (Monte Carlo standard error about {att['sharp_null_test']['monte_carlo_se_approx']:.2g}). This test concerns the sharp null of no effect for any student, not the hypothesis that the actual attendees' average effect is exactly zero.

The positive average-effect estimate and agreement of the checks support the conclusion that tutoring increased attendees' score gain on average, by roughly one point. They do not establish that every attendee benefited, disclose the score-generating mechanism, or establish an effect for students outside this simulated study. If “definite answer” means an exact, assumption-free value of the realized causal effect, the supplied material does not support one: the attendees' untreated counterfactual gains are unobserved.

The accompanying code and results preserve the actual execution record, including an initial failed import of an unavailable optional package before any statistical calculation. The repaired analysis used NumPy, pandas, and SciPy without installing packages or accessing internet sources.
'''
(root/'final_report.md').write_text(report, encoding='utf-8')
inputs = root/'inputs'
inputs.mkdir(exist_ok=True)
for source, name in [('data(7).csv','data.csv'),('STUDY_DESCRIPTION(7).md','STUDY_DESCRIPTION.md')]:
    shutil.copyfile(workspace/'upload'/source, inputs/name)
manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs.iterdir())}
(root/'results'/'05_input_hashes.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(root/'README.md').write_text('''# Execution bundle

`final_report.md` is the self-contained report. The unchanged inputs are in `inputs/`.
`code/` contains all executed analysis, reporting, and packaging scripts.
`results/` contains generated numerical results and captured stdout/stderr.
`run_log.txt` records execution order, exit status, and output paths.

The first descriptive attempt failed at an unused `statsmodels` import, before producing statistics. Its original source is preserved as `code/01_describe_failed.py`; the original command in the log used the then-current name `01_describe.py`. Step 02a generated the repaired source, and step 02b executed it. This was error recovery, not replacement of an earlier successful analysis. No numerical analysis outputs are missing. Empty stdout/stderr files indicate that the respective stream was empty.

Successful statistical scripts can be run with Python and the recorded NumPy/pandas/SciPy versions:

    python code/02_describe.py inputs/data.csv
    python code/03_adjusted.py inputs/data.csv
    python code/04_att_inference.py inputs/data.csv

These commands reproduce the analyses but would overwrite their output files; use a separate copy to preserve the delivered execution record. `run_step.py` captures a script's output and appends its run to the log. The report reads saved result files; it does not rerun the analyses.
''',encoding='utf-8')
print(f'Created final_report.md: {len(report.encode("utf-8"))} UTF-8 bytes; copied both unchanged inputs; wrote README.md and input hashes.')
