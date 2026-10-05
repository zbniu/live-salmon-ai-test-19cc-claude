from pathlib import Path
import json
import pandas as pd
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[2]
out=root/'submission/results'
a=json.loads((out/'att_result.json').read_text())
b=json.loads((out/'analysis.json').read_text())
s=pd.read_csv(out/'group_summary.csv',index_col='x')
report=f'''# Tutoring class: effect on attendees’ score gains

The data provide strong evidence that attending the tutoring class increased the attendees’ **average** score gain. **The adopted estimate answering the research question is an increase of {a['adopted_estimate_points']:.2f} points**, with an approximate 95% randomization confidence interval of **{a['approximate_95_percent_randomization_interval'][0]:.2f} to {a['approximate_95_percent_randomization_interval'][1]:.2f} points**. This is an estimated average causal benefit, not a claim that every attendee benefited or that the exact effect is known.

## Data and comparison

Only the supplied study description and complete CSV were used; no internet or external data were accessed. All 2,000 rows were analyzed. The data contained the stated three columns, no missing or nonfinite values, exactly 600 attendees and 1,400 nonattendees, and starting and implied ending scores within 0–100. No students were excluded.

| Group | Students | Mean starting score | Mean score gain | SD of score gain |
|---|---:|---:|---:|---:|
| Attended | 600 | {s.loc[1,'y_mean']:.3f} | {s.loc[1,'z_mean']:.3f} | {s.loc[1,'z_sd']:.3f} |
| Did not attend | 1,400 | {s.loc[0,'y_mean']:.3f} | {s.loc[0,'z_mean']:.3f} | {s.loc[0,'z_sd']:.3f} |

The estimate is the attendees’ mean gain minus the nonattendees’ mean gain: {s.loc[1,'z_mean']:.6f} − {s.loc[0,'z_mean']:.6f} = {a['adopted_estimate_points']:.6f} points. The attendees’ observed 11.10-point gain itself is not the tutoring effect; students also gained points without tutoring.

## Why this estimates a causal effect for attendees

The description establishes that 600 students were selected by a uniform random draw using no student information, everyone complied, there was no interference between students, and every outcome was retained. The nonattendees therefore provide a randomized comparison for what attendees would have gained without tutoring. No assumption that starting score captures all relevant student characteristics is necessary.

The specific target is the average of each actual attendee’s gain with tutoring minus that same student’s gain without tutoring (the sample average treatment effect on the treated, SATT). Write D for the observed difference in group means. Then D minus SATT equals the difference between the two groups’ mean gains **under no tutoring**. Under the stated complete random draw, that estimation error has mean zero and variance (1/600 + 1/1400) times the finite-population variance of untreated gains. The observed nonattendee variance estimates the latter. This gives a standard error of {a['standard_error_points']:.6f} points and the adopted interval D ± 1.96 × SE.

The interval uses a large-sample normal approximation, with coverage interpreted over repeated random draws of 600 attendees, where the attendee set and its average effect change with the draw. It is not an exact finite-sample or conditional-on-this-specific-set guarantee. This uncertainty calculation does not require identical tutoring effects for all students.

## Sensitivity checks

A conventional unadjusted Welch comparison gave the same 1.11-point estimate, a standard error of {b['primary']['se']:.3f}, and a 95% interval of {b['primary']['ci95'][0]:.2f} to {b['primary']['ci95'][1]:.2f} points (two-sided p = {b['primary']['p_two_sided']:.2g}). That is a conventional randomized-group comparison; the attendee-specific interval above is the adopted uncertainty result.

As a supplementary check, regressions allowed separate relationships between starting score and gain in the two groups. Linear and quadratic starting-score models, standardized to the actual attendees’ starting-score distribution, estimated benefits of {b['sensitivity'][0]['contrasts']['attendees']['estimate']:.2f} and {b['sensitivity'][1]['contrasts']['attendees']['estimate']:.2f} points, respectively. Their approximate HC2 robust intervals were both 0.85 to 1.57 points. These model-dependent checks support the same conclusion; they do not replace the randomized, unadjusted estimate.

## Limits and conclusion

Each student has only one observed outcome, so the exact counterfactual gain and exact causal effect for the realized 600 attendees cannot be recovered. The material also does not establish that every attendee benefited, that effects are constant, or that the result generalizes beyond these students and this class. Nevertheless, the randomized design and the positive uncertainty interval support an average causal increase: **about 1.11 points for the attendees**.

## Execution record

The submission contains the executed analysis code, numerical outputs, and run log. The first analysis attempt stopped at an unavailable package import before any analysis ran; that code and its error are retained. The successful analysis implemented least squares and HC2 covariance directly with installed NumPy, pandas, and SciPy. A subsequent calculation addressed uncertainty for SATT specifically. The run log identifies preliminary inspection outputs that were visible in the tool session but were not separately saved. No numerical outputs were reconstructed to replace missing records.
'''
(root/'submission/final_report.md').write_text(report,encoding='utf-8')
with (root/'submission/run_log.txt').open('a',encoding='utf-8') as f:
 f.write('\n'+datetime.now(timezone.utc).isoformat()+' code/write_report.py: read recorded results; generated final_report.md (UTF-8), no analyses repeated; exit=0.\n')
print('Report written:',len(report.encode('utf-8')),'bytes')
