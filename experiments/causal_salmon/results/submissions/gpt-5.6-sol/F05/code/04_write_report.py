"""Write the final report from recorded results; do not rerun analyses."""
import json
from pathlib import Path
import shutil

r = json.loads(Path('submission/results/03_primary_results.json').read_text())
lo,hi=r['recipient_target_approx_95_interval']
wlo,whi=r['conventional_welch_95_interval']
report=f'''# Effect of arrangement Q on change

## Answer to the research question

The randomized study provides strong statistical evidence that arrangement Q **increased change `z` on average among its recipients**. The primary estimate adopted in this report is **{r['primary_difference_points']:.3f} points**, with an **approximate 95% randomization-based interval of {lo:.3f} to {hi:.3f} points**. This is the estimated additional change attributable to Q, rather than the recipients' total observed change.

This is an estimate, not a definite determination of the exact effect in these particular 600 recipients. The data do not reveal what each recipient's change would have been without Q, and they cannot establish that Q increased change for every recipient. If the question requires an exact causal amount or a benefit for every recipient, the supplied material does not support that conclusion.

## Data and causal interpretation

Only the supplied study description and complete CSV were used. All 2,000 rows and all three variables were read; 600 units received Q and 1,400 did not. There were no missing or nonfinite values, and no rows were excluded.

The description states that exactly 600 units were chosen by an equal-chance random draw using no unit information, with complete adherence, no effects between units, uniform measurement, blinded follow-up recording, and complete observation. These facts support a causal comparison using the untreated units to estimate what would have happened without Q. Baseline `y` was measured before assignment. Since `z` is follow-up minus baseline, an effect on `z` equals an effect on follow-up when baseline is held fixed.

The target is the **average causal effect for the 600 actual recipients**: the average of each recipient's change with Q minus that same recipient's change without Q. It is not the average effect for an external population, an individual effect, or simply whether recipients improved from baseline.

## Primary analysis

| Group | Units | Mean observed change, points |
|---|---:|---:|
| Received Q | 600 | {r['mean_z_treated']:.6f} |
| Did not receive Q | 1,400 | {r['mean_z_control']:.6f} |
| Difference, Q minus control | | **{r['primary_difference_points']:.6f}** |

The unadjusted difference in means is the primary estimate. It uses random assignment without requiring a linear outcome model, equal variances, or identical treatment effects across units. The recipients' observed improvement of {r['mean_z_treated']:.3f} points is not all attributable to Q: controls also improved by {r['mean_z_control']:.3f} points.

For uncertainty about the recipient-specific average effect, let `z_i(0)` denote unit i's change without Q and let `tau_T` denote the actual recipients' average causal effect. The estimation error is exactly:

`difference - tau_T = mean_T[z(0)] - mean_C[z(0)]`.

Under the described complete randomization, its repeated-assignment variance is `(1/600 + 1/1400) * S0^2`, where `S0^2` is the finite-population variance of untreated potential changes over all 2,000 units. The control sample variance unbiasedly estimates that variance. This gives a standard error of **{r['recipient_target_randomization_se']:.6f} points**. The reported interval uses the estimate plus or minus 1.96 standard errors; it is a large-sample approximation, not an exact finite-sample guarantee. Its interpretation is repeated-randomization coverage of the average effect in whichever units are assigned Q, with that target varying across assignments.

As a conventional comparison, Welch's two-sample analysis gives a 95% interval of **{wlo:.3f} to {whi:.3f} points** and a two-sided p-value of **{r['conventional_welch_two_sided_p']:.6g}**. That is a separate group-comparison calculation, not the interval adopted for the recipient-specific target. Both intervals exclude zero.

## Baseline sensitivity

Mean baseline was {r['mean_baseline_treated']:.3f} in recipients and {r['mean_baseline_control']:.3f} in controls, a chance difference of {r['baseline_difference']:.3f} points. Untreated change increased with baseline in the observed control data. A control-only linear regression of change on baseline, used to predict untreated change at every recipient's baseline, gives an adjusted average effect estimate of **{r['secondary_linear_adjusted_recipient_effect']:.3f} points**. Quadratic, cubic, and cubic spline control regressions give estimates between **1.015 and 1.019 points**. These secondary, model-assisted checks support the primary conclusion; they do not replace the primary estimate or establish the unobserved counterfactual relationship exactly. No outcomes or subsets were selected to maximize an effect.

## Limits and conclusion

Randomization makes the comparison credible, but does not observe the recipients' untreated outcomes. Therefore the exact realized average effect remains unknown, and heterogeneous individual effects are possible. The intervals describe assignment uncertainty within this experiment; no claim about other populations or an undisclosed outcome-generating mechanism is made.

The supported answer is: **Q likely increased recipients' average change by about 0.85 points; the primary approximate 95% interval is 0.45 to 1.24 points.** The evidence supports a positive average causal effect, not a guaranteed benefit for each recipient.

## Execution and reproducibility

The archive includes the two input files, the code actually executed, the produced tables and JSON results, directly captured stdout/stderr, and an ordered execution log. The first inspection script failed at an import because `statsmodels` was unavailable; that script and its actual error are retained. A separate inspection script and the analysis then completed using NumPy, pandas, and SciPy. The report was written from the recorded results without repeating the analyses. Initial shell inspection output was available in the session tool transcript but was not separately captured to a file; this limitation is recorded in the log.
'''
Path('submission/final_report.md').write_text(report,encoding='utf-8')
Path('submission/inputs').mkdir(exist_ok=True)
shutil.copyfile('upload/data(6).csv','submission/inputs/data.csv')
shutil.copyfile('upload/STUDY_DESCRIPTION(6).md','submission/inputs/STUDY_DESCRIPTION.md')
Path('submission/results/04_report_summary.json').write_text(json.dumps({
    'primary_estimate_points':r['primary_difference_points'],
    'primary_approximate_95_interval':r['recipient_target_approx_95_interval'],
    'report':'submission/final_report.md',
    'analysis_source':'submission/results/03_primary_results.json'
},indent=2)+'\n',encoding='utf-8')
with Path('submission/run_log.txt').open('a',encoding='utf-8') as f:
    f.write('\nArtifact linkage (verified from the files produced, not reconstructed execution streams):\n')
    f.write('01_inspect.py: failed at statsmodels import; no analysis output tables or JSON were produced. Actual error is in 01_inspect.stderr.txt.\n')
    f.write('02_inspect.py: produced 02_group_summary.csv, 02_baseline_bands.csv, 02_integrity.json.\n')
    f.write('03_analyze.py: produced 03_baseline_sensitivity.csv, 03_unit_predictions.csv, 03_baseline_subgroups.csv, 03_primary_results.json.\n')
    f.write('04_write_report.py: produced final_report.md, results/04_report_summary.json, and byte-for-byte copies of both input files in inputs/. No analyses rerun.\n')
print('Created submission/final_report.md from recorded 03_primary_results.json.')
print('Created submission/results/04_report_summary.json and copied both inputs.')
print(f'Report is {len(report.encode("utf-8"))} UTF-8 bytes.')
