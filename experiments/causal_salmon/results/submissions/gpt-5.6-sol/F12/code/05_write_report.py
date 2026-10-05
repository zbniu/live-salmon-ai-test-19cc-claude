"""Write the final report from the retained, corrected execution outputs."""
from pathlib import Path
import json, shutil
import pandas as pd

root=Path(__file__).resolve().parents[2]
sub=root/'submission';out=sub/'results'
r=pd.read_csv(out/'04_att_models.csv')
p=r[r.method=='Natural cubic spline 6 knots (primary)'].iloc[0]
checks=json.loads((out/'04_checks.json').read_text())
inspect=json.loads((out/'01_data_checks.json').read_text())
m=pd.read_csv(out/'04_matching_sensitivity.csv')
table='\n'.join(f'| {v.method} | {v.att:.3f} | {v.ci95_low:.3f} to {v.ci95_high:.3f} |' for v in r.itertuples())
report=f'''# Effect of arrangement Q on change among its recipients

## Answer

The data support an increase in change `z` among the 600 units that received Q. **The adopted estimate of their average causal effect is +{p.att:.2f} points**, with an approximate 95% confidence interval of **{p.ci95_low:.2f} to {p.ci95_high:.2f} points**. This answers the research question for the recipients, rather than for all 2,000 units. It is an estimated average effect, not a claim that Q helped every recipient or that the exact effect is known.

Recipients' observed mean change was {checks['treated_mean_change']:.3f} points. After adjusting for baseline, their estimated mean change had they not received Q was {p.estimated_control_change_for_treated:.3f} points. The difference, {p.att:.3f} points, is the numerical result adopted to answer the question.

## Data and causal comparison

Only the supplied study description and complete CSV were used. All 2,000 rows were analyzed: 600 recipients and 1,400 untreated units. There were no missing values and no duplicated full rows. No rows were removed or values altered.

The target is the mean of each recipient's change under Q minus that same recipient's change without Q. The latter is unobserved. The described assignment mechanism uses baseline `y` and random selection unrelated to unit characteristics. Baseline is therefore the relevant measured selection variable to adjust for. The subsequent baseline ranking makes treatment especially concentrated at higher baselines. Candidate status is unavailable, but the stipulated random selection does not introduce an additional characteristic of the unit that must be adjusted for. The description also supplies consistent treatment and no effects of one unit's treatment on another unit's change.

Recipients' mean baseline was 67.073, versus 56.864 in untreated units. Their unadjusted mean changes were 13.019 and 9.393, a difference of {checks['raw_difference']:.3f} points. **That unadjusted difference is not the adopted causal effect** because the groups differ substantially in baseline and untreated change varies with baseline.

Baseline comparison is feasible in this dataset: recipients' baselines range from 58.213 to 74.972, and untreated baselines range from 45.007 to 74.991. No recipient lies outside the untreated range. Every recipient has an untreated unit within 0.090 baseline points. Both treatment groups occur in every one-point baseline band containing recipients. This supports estimating the counterfactual for recipients without extrapolating beyond untreated baseline support. No effect for low-baseline nonrecipients is inferred.

## Estimation and sensitivity

The primary analysis fits untreated change as a smooth function of baseline using a natural cubic spline with six knots at the pooled baseline quantiles 0%, 20%, 40%, 60%, 80%, and 100%. The six knot values are 45.007, 50.885, 57.356, 62.783, 69.079, and 74.991. The spline has six parameters including its constant component. Averaging its predictions over the actual 600 recipient baselines estimates their untreated mean change. Subtracting this average from their observed mean change estimates the average treatment effect on the treated. All untreated rows inform the control curve and all recipient rows enter the target average.

Results were similar with alternative baseline adjustments:

| Baseline model | Estimated effect (points) | Approximate 95% interval |
| --- | ---: | --- |
{table}

Nearest-baseline matching with replacement, using 1, 5, 10, or 20 untreated neighbors per recipient, gave estimates of {m.att.iloc[0]:.3f}, {m.att.iloc[1]:.3f}, {m.att.iloc[2]:.3f}, and {m.att.iloc[3]:.3f} points. These are sensitivity checks, not additional adopted answers. Matching intervals were not calculated because control reuse would invalidate a simple paired-test interval.

## Uncertainty and limits

The primary standard error is {p.se_HC3:.3f} points. The interval uses heteroskedasticity-robust HC3 covariance from separate treated and untreated outcome regressions, evaluated at the mean recipient spline basis, and a normal approximation. The treated regression supplies uncertainty in recipients' observed mean; it does not impose a constant treatment effect. The recipient baselines are held fixed for this calculation.

The causal estimate relies on the stated assignment mechanism and on estimating the untreated conditional mean smoothly from nearby observed units. Continuous baselines prevent exact, assumption-free recovery of every recipient's untreated outcome. The interval additionally uses an independent conditional-outcome-error working model. The undisclosed selection values, candidate list, and selection distribution prevent an exact design-based randomization interval; the reported interval is approximate and model based. Sensitivity across reasonable baseline models and local matching supports the positive average effect, but cannot prove an exact causal magnitude without modeling assumptions. The supplied material supports the estimated increase of about 1.24 points, not a logically certain individual or exact finite-sample effect.

## Execution provenance

The primary results come from `code/04_estimate_corrected.py` and `results/04_att_models.csv`. `code/01_inspect.py` checked the complete input. An initial attempt, `code/02_estimate.py`, stopped at an unavailable `statsmodels` import and produced no model estimates. `code/03_estimate.py` produced exploratory outputs, but a fitted-mean check exposed a rank-deficient treated spline design handled with an unstable matrix inverse. The corrected analysis uses an SVD pseudoinverse and passes the fitted-mean check. Its point estimate agrees with the earlier run; its corrected uncertainty is adopted here. Earlier code, outputs, and errors remain in the archive and are not replaced. `run_log.txt` records the actual execution order. Input copies are included for reproduction, and no internet or external analytical sources were used.
'''
(sub/'final_report.md').write_text(report,encoding='utf-8')
inputs=sub/'inputs';inputs.mkdir(exist_ok=True)
shutil.copyfile(root/'upload'/'data(20261004-013818).csv',inputs/'data.csv')
shutil.copyfile(root/'upload'/'STUDY_DESCRIPTION(20261004-013818).md',inputs/'STUDY_DESCRIPTION.md')
readback=(sub/'final_report.md').read_text(encoding='utf-8')
assert readback==report and len(readback)>0 and '+1.24 points' in readback
assert inspect['rows']==2000
verification=dict(report_nonempty=True,report_characters=len(readback),adopted_att=float(p.att),
                  adopted_ci=[float(p.ci95_low),float(p.ci95_high)],inputs_copied=True,
                  corrected_fitted_mean_check=checks['primary_treated_fitted_mean_check'])
(out/'05_report_checks.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
with (sub/'run_log.txt').open('a',encoding='utf-8') as log:
    log.write('Notes: Initial source-description read and file listing occurred via the execution tool before the saved runner; their terminal outputs were not saved as result files. No earlier statistical execution is omitted.\n')
    log.write('02 failed before analysis at import; no 02 model outputs exist. 03 exploratory outputs are retained but its treated-model covariance is superseded by 04 because of a rank-deficient inverse. 04 is the adopted estimation run, with its mean-reproduction checks passing.\n')
print(json.dumps(verification,indent=2))
print('Created final_report.md from actual 04 outputs; earlier execution records retained.')
