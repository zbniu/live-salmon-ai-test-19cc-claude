"""Create the standalone report from actual saved analysis outputs; no reanalysis."""
import json
import pathlib

root=pathlib.Path.cwd()
sub=root/'submission'
r=json.loads((sub/'results/att_estimate.json').read_text())
d=json.loads((sub/'results/data_checks.json').read_text())
lower,upper=r['bootstrap_95_percentile_interval']
report=f'''# Effect of arrangement Q on change among its recipients

The data support a positive average causal effect of arrangement Q for the 600 units that received it. **The adopted answer to the research question is an estimated increase of {r['att_points']:.2f} points in change `z`, with an approximate 95% confidence interval of {lower:.2f} to {upper:.2f} points.** This is an average effect for recipients, not a claim that every recipient benefited.

Only the attached study description and complete data file were used. All 2,000 units were analyzed: 600 received Q and 1,400 did not. There were no missing values or excluded rows.

## Why baseline adjustment is needed

Recipients' mean baseline was 67.07, compared with 56.86 for nonrecipients. Their mean changes were 13.02 and 9.39 points, respectively. The unadjusted difference of 3.63 points is not the adopted causal estimate: assignment favored higher baselines, and untreated changes also increase with baseline in these data. Comparing change scores alone does not remove that imbalance.

The supplied assignment mechanism uses baseline and unit-specific random numbers unrelated to unit characteristics. The subsequent candidate ranking also uses only baseline. This supports comparing treated and untreated outcomes conditional on baseline, rather than assuming the groups are comparable without adjustment. The documented consistency, absence of switching, and absence of interference support the potential-outcome interpretation. The hidden candidate list does not supply an additional unit characteristic that must be adjusted for.

## Estimation and comparison support

The target was the average treatment effect on the treated: the average difference between each recipient's change with Q and the change that recipient would have had without Q.

I fitted untreated change as a function of baseline using a natural cubic regression spline with seven basis functions and equally spaced knots across the observed baseline range (45.01–74.99). I then predicted untreated mean change at every one of the 600 recipients' baselines and averaged observed minus predicted change. All 1,400 nonrecipients contributed to the untreated regression. This approach permits nonlinear baseline relationships and does not impose a constant treatment effect.

Treated baselines ranged from 58.21 to 74.97, entirely within the untreated range of 45.01 to 74.99. Every one-point baseline bin containing recipients also contained nonrecipients. The greatest distance from a recipient's baseline to the nearest untreated baseline was {d['nearest_control_baseline_distance_quantiles']['max']:.3f} points. Thus the recipient target has good empirical comparison support; the absence of recipients at low baselines does not prevent estimating their effect.

| Quantity | Change in points |
|---|---:|
| Observed mean change among recipients | {r['mean_observed_treated_change']:.4f} |
| Estimated mean change those recipients would have had without Q | {r['estimated_mean_untreated_change_for_treated']:.4f} |
| **Adopted average effect of Q among recipients** | **{r['att_points']:.4f}** |

The confidence interval used 3,000 stratified bootstrap resamples, preserving the 600/1,400 group sizes, with seed 20261004; the bootstrap standard error was {r['bootstrap_standard_error']:.3f} points. Natural splines with four, five, or nine basis functions, control regressions with linear through cubic baseline terms, and one-point baseline stratification weighted to recipients all yielded positive estimates, spanning {r['sensitivity_min']:.2f}–{r['sensitivity_max']:.2f} points.

## Limits of the answer

The result is a statistical estimate, not an exact reconstruction of unobserved counterfactual changes. It relies on the supplied baseline-only assignment mechanism and estimation of a smooth untreated mean response; finite data cannot establish that response without any modeling assumption. Agreement across the alternative adjustments supports the estimate. The bootstrap interval is an approximate measure of sampling/model uncertainty, not an exact randomization interval for the study's fixed-quota selection scheme: selection values and assignment probabilities were not supplied. The evidence supports an average increase for Q recipients but does not establish individual effects or an effect for all 2,000 units.
'''
(sub/'final_report.md').write_text(report,encoding='utf-8')
(sub/'README.md').write_text('''# Execution package

`final_report.md` contains the answer. `results/att_estimate.json` contains the adopted numerical estimate and uncertainty; other results contain data checks, sensitivity estimates, all bootstrap replicates, all unit predictions, and figures.

The original analysis scripts are in `code/`. They were executed from the parent of `submission/`, with the attached CSV and description in `upload/` under their original names: `data(20261004-180826).csv` and `STUDY_DESCRIPTION(20261004-180826).md`. Supply those two original attachments in that layout to rerun the scripts. The required dependencies are Python, numpy, pandas, scipy, and matplotlib; versions and input SHA-256 values are in `results/data_checks.json`.

Execution order was `run.py 01_describe.py` (failed import), `run.py 01_describe.py` (successful after removing unused statsmodels), `run.py 02_estimate.py`, then `run.py 03_report.py`. Each invocation used the supplied bundled Python interpreter. See `run_log.txt` for actual command paths, timestamps, exit codes, and retained stdout/stderr. No analytical calculations occurred in the failed import attempt. The current descriptive script is the successful version; the original failed version is preserved in `code/history/`. No analysis was repeated to replace results. The bootstrap and sensitivity fits are parts of the planned analysis, not replacement records.

`04_package.py` verifies the report and packages the directory. Its archive-validation output records an actual inspection before the archive is refreshed to include that record and the completed log, followed by final inspection in the session. The packaging refresh does not rerun any analysis.

Pre-analysis input inspection used shell `cat`, `ls`, and `head`; their output was displayed in the session, not captured as analysis-result files. No Internet data sources were accessed.
''',encoding='utf-8')
history=sub/'code/history'
history.mkdir(exist_ok=True)
current=(sub/'code/01_describe.py').read_text()
original=current.replace('import scipy\n','import scipy\nimport statsmodels\n').replace("'scipy':scipy.__version__, 'matplotlib'", "'scipy':scipy.__version__, 'statsmodels':statsmodels.__version__, 'matplotlib'")
(history/'01_describe_attempt1.py').write_text(original,encoding='utf-8')
runner=(sub/'code/run.py').read_text()
original_runner=runner.replace("attempt = 1 + len(list(out.glob(f'{script.stem}*_stdout.txt')))\ntag = script.stem if attempt == 1 else f'{script.stem}_attempt{attempt}'\n",'').replace("f'{tag}_stdout.txt'","f'{script.stem}_stdout.txt'").replace("f'{tag}_stderr.txt'","f'{script.stem}_stderr.txt'")
(history/'run_attempt1.py').write_text(original_runner,encoding='utf-8')
with (sub/'run_log.txt').open('a',encoding='utf-8') as f:
    f.write('\nRecord clarification: the first 01_describe.py attempt failed at import statsmodels before loading or analyzing data. Its actual stderr and empty stdout are retained. The unused import and corresponding unused version field were removed; the runner was updated to preserve attempt-specific output filenames. Exact earlier source versions were restored from the recorded edits in code/history/; these are code snapshots, not reconstructed execution outputs. No analysis outputs are missing. Pre-analysis shell inspection outputs are available only in the session.\n')
print('Created final_report.md and README.md from saved numerical outputs, and retained earlier source versions in code/history/. No analytical calculations rerun.')
