"""Analyze the complete attached CSV; no network or external data.

Usage: python analyze.py DATA_CSV RESULTS_DIRECTORY
Regressions are descriptive associations, not identified causal effects.
"""
import csv
import hashlib
import json
from pathlib import Path
import platform
import sys
import numpy as np


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    source = Path(sys.argv[1])
    out = Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    with source.open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == ['x', 'y', 'z'], reader.fieldnames
        rows = list(reader)
    a = np.array([[float(r[k]) for k in ['x', 'y', 'z']] for r in rows])
    assert a.shape == (2000, 3), a.shape
    assert np.isfinite(a).all(), 'Nonfinite or missing data'
    x, y, z = a.T
    assert set(np.unique(x)) == {0, 1}
    assert np.sum(x) == 600
    assert ((y >= 0) & (y <= 100)).all()
    followup = y + z
    group_rows = []
    for label in [0, 1]:
        mask = x == label
        group_rows.append(dict(x=label, n=int(mask.sum()),
            baseline_mean=float(y[mask].mean()), baseline_sd=float(y[mask].std(ddof=1)),
            baseline_min=float(y[mask].min()), baseline_max=float(y[mask].max()),
            change_mean=float(z[mask].mean()), change_sd=float(z[mask].std(ddof=1)),
            change_min=float(z[mask].min()), change_max=float(z[mask].max()),
            followup_mean=float(followup[mask].mean()),
            followup_min=float(followup[mask].min()), followup_max=float(followup[mask].max())))
    write_csv(out / 'group_summary.csv', group_rows)

    bin_rows = []
    for low in range(0, 100, 10):
        high = low + 10
        for label in [0, 1]:
            mask = (x == label) & (y >= low) & ((y < high) if high < 100 else (y <= high))
            bin_rows.append(dict(baseline_low=low, baseline_high=high, x=label,
                n=int(mask.sum()), mean_change=float(z[mask].mean()) if mask.any() else None))
    write_csv(out / 'baseline_bins.csv', bin_rows)

    # Polynomial terms centered/scaled for numerical stability; additive treatment term.
    # HC3 SEs describe fitted association uncertainty under working regression assumptions.
    regression_rows = []
    yc = (y - y.mean()) / 10
    for degree in [0, 1, 2, 3]:
        design = np.column_stack([np.ones(len(x)), x] + [yc ** j for j in range(1, degree + 1)])
        beta = np.linalg.lstsq(design, z, rcond=None)[0]
        resid = z - design @ beta
        bread = np.linalg.inv(design.T @ design)
        hat = np.sum((design @ bread) * design, axis=1)
        adj = resid / (1 - hat)
        cov = bread @ ((design.T * (adj ** 2)) @ design) @ bread
        se = float(np.sqrt(cov[1, 1]))
        regression_rows.append(dict(baseline_polynomial_degree=degree,
            treatment_association=float(beta[1]), hc3_standard_error=se,
            r_squared=float(1 - np.sum(resid**2) / np.sum((z-z.mean())**2)), n=len(x)))
    write_csv(out / 'descriptive_regressions.csv', regression_rows)

    # Explicit completions of missing potential outcomes. These are hypothetical
    # examples compatible with observed outcomes, not estimates or simulated data.
    # x marks which potential outcome was observed, so z = (1-x)*z0 + x*z1.
    scenarios = []
    for delta in [-1.0, 0.0, 1.0]:
        z0 = z - delta * x
        z1 = z + delta * (1 - x)
        assert np.allclose((1-x)*z0 + x*z1, z, rtol=0, atol=1e-12)
        scenarios.append(dict(assumed_constant_effect=delta,
            recipient_average_effect=float((z1-z0)[x == 1].mean()),
            max_observed_reconstruction_error=float(np.max(np.abs((1-x)*z0+x*z1-z))),
            all_potential_followups_within_0_100=bool(((y+z0 >= 0) & (y+z0 <= 100) & (y+z1 >= 0) & (y+z1 <= 100)).all())))
    write_csv(out / 'hypothetical_counterfactual_examples.csv', scenarios)

    treated_min = float(y[x == 1].min())
    control_min, control_max = float(y[x == 0].min()), float(y[x == 0].max())
    summary = dict(input_file=source.name, sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        n_rows=len(x), n_columns=3, missing_or_nonfinite_values=0,
        python_version=platform.python_version(), numpy_version=np.__version__,
        groups=group_rows,
        unadjusted_change_difference=float(z[x == 1].mean() - z[x == 0].mean()),
        unadjusted_baseline_difference=float(y[x == 1].mean() - y[x == 0].mean()),
        overlap=dict(minimum_recipient_baseline=treated_min,
            controls_below_minimum_recipient_baseline=int(((x == 0) & (y < treated_min)).sum()),
            controls_at_or_above_minimum_recipient_baseline=int(((x == 0) & (y >= treated_min)).sum()),
            recipients_within_observed_control_baseline_range=int(((x == 1) & (y >= control_min) & (y <= control_max)).sum())),
        observed_followups_within_0_100=bool(((followup >= 0) & (followup <= 100)).all()),
        descriptive_regressions=regression_rows, hypothetical_counterfactual_examples=scenarios,
        causal_conclusion='Recipient average causal effect is not identified by supplied assumptions and data.')
    (out / 'analysis_summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
