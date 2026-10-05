"""Write a standalone report from the saved analysis outputs; preserve inputs."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[2]
SUB = ROOT/'submission'
a = json.loads((SUB/'results'/'analysis.json').read_text(encoding='utf-8'))
p = a['primary']
s = a['sensitivity_estimates'][0]
report = f'''# Effect of arrangement Q on its recipients

**Answer.** The supplied randomized study provides statistical evidence that Q increased the **average change `z` among the 600 units that received it**. The result adopted to answer the research question is **+{p['effect_points']:.3f} points**, with an **approximate 95% randomization confidence interval of +{p['approx_95ci_low']:.3f} to +{p['approx_95ci_high']:.3f} points**. This is an estimated average causal effect, not the recipients' total observed improvement. The exact effect is unobserved, and the study does not establish that every recipient benefited.

## Data and comparison

I used every row of `data.csv` and only the supplied study description as study information. The file has the stated three columns, 2,000 rows, 600 recipients and 1,400 controls, with no missing or nonfinite values. Baseline and reconstructed follow-up measurements are within the stated 0–100 scale. No observations were excluded, and no external sources were used.

| Group | Units | Mean baseline `y` | Mean change `z` |
|---|---:|---:|---:|
| Received Q | 600 | {p['treated_mean_baseline']:.3f} | {p['treated_mean_change']:.3f} |
| Did not receive Q | 1,400 | {p['control_mean_baseline']:.3f} | {p['control_mean_change']:.3f} |

The main estimate is the difference in mean changes: {p['treated_mean_change']:.6f} − {p['control_mean_change']:.6f} = {p['effect_points']:.6f} points. The mean change of {p['treated_mean_change']:.3f} points in recipients is **not** the estimated effect of Q; controls also improved.

## Why this comparison answers a causal question

Exactly 600 units were selected by an equal-probability random draw using no unit information. Assignment was followed perfectly, all units were measured, and the description rules out effects of one unit's assignment on another unit's change. These facts justify using controls to estimate what recipients would have experienced without Q. Baseline differences are chance imbalances, not evidence of assignment based on baseline.

The target is the average of `z(1) − z(0)` for the **actual 600 recipients**, where `z(1)` and `z(0)` denote their changes with and without Q. It is not a claim about an external population, nor an assumption that effects are identical across units.

For this particular target, the difference-in-means estimation error is the difference between recipients' and controls' means of the untreated potential change `z(0)`. Complete random assignment therefore gives error variance `(1/600 + 1/1400) × S₀²`, where `S₀²` is the finite-population variance of untreated potential changes. I estimated that variance using the control sample variance. The resulting standard error is {p['se_points']:.6f} points; the reported interval is the estimate plus or minus 1.96 standard errors. This is a large-sample randomization approximation for the recipients' average effect, rather than a conventional two-group interval targeting the overall study-population average effect. It does not require constant treatment effects or a model for how changes were generated.

## Baseline adjustment and limitations

Recipients had a baseline mean 0.752 points lower than controls, and higher baseline values predict larger changes in controls. As a sensitivity check, I fitted a linear regression of change on baseline using controls, predicted each recipient's untreated change, and averaged the observed-minus-predicted changes. This gives **+{s['effect']:.3f} points** (first-order approximate 95% interval {s['ci_low']:.3f} to {s['ci_high']:.3f}). Quadratic and cubic control regressions and comparisons within baseline deciles weighted to the recipients' baseline distribution give estimates between +1.005 and +1.015 points. These checks use all rows and support the same positive-average-effect conclusion. Their residual-based intervals are approximate and do not include higher-order uncertainty from estimating the adjustment functions.

I retain the unadjusted randomized estimate as the main numerical answer because it follows directly from the supplied assignment design without selecting a response model after inspecting outcomes. Sampling uncertainty remains, and no recipient's untreated outcome is observed. Consequently the supplied material supports an estimated positive **average** effect, not a definite reconstruction of its exact size, individual effects, or the undisclosed process generating changes.

## Execution materials

The accompanying package contains the two unchanged input files, the Python code actually executed, saved numerical outputs and console records, and a chronological run log. `results/analysis.json` and `results/effect_estimates.csv` contain the primary and sensitivity results. The log distinguishes initial file-inspection output available only in the session transcript from saved analysis records. No statistical analysis was rerun to replace an execution record.
'''
(SUB/'final_report.md').write_text(report,encoding='utf-8')
inp = SUB/'inputs'
inp.mkdir(exist_ok=True)
mapping = {'data(20261004-180728).csv':'data.csv',
    'STUDY_DESCRIPTION(20261004-180729).md':'STUDY_DESCRIPTION.md'}
hashes = {}
for src,dest in mapping.items():
    source = ROOT/'upload'/src
    target = inp/dest
    shutil.copyfile(source,target)
    assert source.read_bytes()==target.read_bytes()
    hashes[dest] = hashlib.sha256(target.read_bytes()).hexdigest()
(SUB/'results'/'input_hashes.json').write_text(json.dumps(hashes,indent=2),encoding='utf-8')
print(f'Created final_report.md ({len(report.encode("utf-8"))} UTF-8 bytes).')
print('Preserved unchanged inputs/data.csv and inputs/STUDY_DESCRIPTION.md.')
print('Output: results/input_hashes.json.')
