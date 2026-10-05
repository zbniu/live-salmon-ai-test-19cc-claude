from pathlib import Path
import json, shutil

root = Path(__file__).resolve().parents[2]
s = root/'submission'
r = json.loads((s/'results/02_effect_summary.json').read_text())
low, high = r['bootstrap']['percentile_95_ci']
report = f'''# Effect of arrangement Q on recipients’ change

The supplied study and data provide evidence that **arrangement Q increased change `z` on average among the 600 units that received it**. My adopted estimate of the average treatment effect on recipients is **{r['att']:.2f} points**, with an **approximate 95% confidence interval of {low:.2f} to {high:.2f} points**. This is the numerical result answering the research question. It does not mean that every recipient benefited or that the exact realized effect is known.

The target is the average difference between each recipient’s change with Q and the change that same recipient would have had without Q. Because baseline precedes treatment, an effect on change is also an effect on follow-up measurement, in the same point units.

## Data and causal comparison

I used the complete CSV: 2,000 units, comprising 600 recipients and 1,400 nonrecipients. The three expected columns were present, with no missing values or duplicate rows. Only the supplied CSV and study description were used; no external data or internet sources were accessed.

Recipients had a higher mean baseline (66.84 versus 57.23). Their mean observed change was 12.83 points, compared with 9.38 for nonrecipients. The unadjusted difference of 3.45 points mixes the effect of Q with baseline differences and is **not** the adopted causal estimate.

The documented assignment mechanism uses baseline and independently generated random selection noise, with no other unit characteristic entering assignment. This supports comparing recipients with nonrecipients after conditioning on baseline. The subsequent acceptance of the highest-baseline candidates makes baseline adjustment necessary even though the candidate-selection step includes randomness. The stated consistency and absence of interference support the treatment comparison.

The data support the needed comparisons for the recipient population: recipients’ baselines range from 57.356 to 74.976, entirely inside the nonrecipients’ range of 45.005 to 74.996. There are 577 nonrecipients at or above the minimum recipient baseline. Every recipient has a nonrecipient within 0.117 baseline points. No recipient was excluded from the estimate. The lack of recipients at lower baselines does not prevent estimating an effect for recipients, but this analysis does not estimate the effect for all 2,000 units.

## Estimation and checks

I fitted the mean change without Q as a flexible function of baseline using all 1,400 nonrecipients: a cubic B-spline with five equally spaced interior knots across the observed baseline range. I then predicted change without Q for every recipient and averaged the observed-minus-predicted differences. This allows the treatment effect to vary across recipients and does not impose a common treatment coefficient.

The recipients’ observed mean change was {r['observed_treated_mean']:.3f} points. Their estimated mean change without Q was {r['estimated_untreated_mean_for_treated']:.3f} points. Their difference was **{r['att']:.3f} points**.

The adopted interval comes from 2,000 bootstrap resamples, sampling recipients and nonrecipients separately and refitting the untreated-outcome model each time (seed 20261004). The bootstrap standard error was {r['bootstrap']['standard_error']:.3f} points. A heteroskedasticity-robust sandwich calculation gave a standard error of {r['sandwich_se']:.3f} and a similar 95% interval, 0.786 to 1.611.

Results were stable under changes in the baseline model. Linear, quadratic, cubic, and cubic-spline models with 3, 5, 7, or 9 interior knots estimated increases from 1.17 to 1.23 points. Baseline nearest-neighbor matching with replacement, using 1, 5, 10, or 20 nonrecipients per recipient, gave increases from 1.08 to 1.17 points. These are sensitivity checks, not additional independent experiments.

## Interpretation and limits

The positive adjusted estimate and the interval excluding zero support an average increase of about **1.2 points attributable to Q for its recipients**. The causal interpretation relies on the supplied assignment account and on adequately estimating the untreated mean as a function of baseline. The smooth regression model is an analysis assumption, not a disclosed feature of the simulation; alternative smooth models and close matching support its conclusion.

The interval is approximate model/resampling uncertainty. It is not an exact randomization interval for the fixed-slot assignment: selection values, candidate membership, and the complete probability law of assignment were not supplied. The data do not reveal recipients’ unobserved outcomes without Q, so they cannot establish the exact finite-study average effect or every individual effect. Nevertheless, they support the reported positive average-effect estimate under the stated design and statistical modeling assumptions.
'''
(s/'final_report.md').write_text(report,encoding='utf-8')
inputs = s/'inputs'; inputs.mkdir(exist_ok=True)
for name in ['data(20261004-180745).csv','STUDY_DESCRIPTION(20261004-180745).md']:
    shutil.copy2(root/'upload'/name, inputs/name)
(s/'README.md').write_text('''# Execution bundle

`final_report.md` gives the answer. `results/` contains actual analysis outputs, including captured stdout and stderr; `run_log.txt` records execution order. `inputs/` contains unchanged copies of the two supplied files.

The executed analysis scripts are `code/01_diagnostics.py` and `code/02_effect_analysis.py`. `code/run_step.py` captured their stdout, stderr, timestamps, and exit status. `code/03_write_report.py` generated the report from the saved outputs and copied inputs; `code/04_verify_delivery.py` checked and packaged delivery.

To reproduce analysis in a fresh directory, put `submission/` in that directory, create a sibling `upload/` directory, and copy the two files from `submission/inputs/` into `upload/` keeping their names. Run the first two scripts with Python providing numpy, pandas, scipy, and matplotlib. Their paths resolve relative to the scripts. A new run will overwrite analysis outputs, so preserve this original bundle first. No installation or internet access was used in the recorded run.
''',encoding='utf-8')
with (s/'run_log.txt').open('a') as f:
    f.write('\nSubstantive output linkage (recorded after successful steps, not reconstructed analysis):\n')
    f.write('01_diagnostics.py -> results/01_diagnostics.json, results/01_baseline_bins.csv, plus captured stdout/stderr.\n')
    f.write('02_effect_analysis.py -> results/02_effect_summary.json, results/02_model_sensitivity.csv, results/02_matching_sensitivity.csv, results/02_bootstrap_draws.csv, results/02_recipient_predictions.csv, results/02_diagnostics.png, plus captured stdout/stderr.\n')
    f.write('03_write_report.py -> final_report.md, README.md, inputs/ (unchanged copies), plus captured stdout/stderr.\n')
    f.write('The diagnostic PNG was viewed during this session. No analysis execution errors occurred, and neither analysis was rerun. Preliminary shell output was not saved as a raw file, as noted above.\n')
print(report)
print('Report written; input copies and reproduction notes saved.')
