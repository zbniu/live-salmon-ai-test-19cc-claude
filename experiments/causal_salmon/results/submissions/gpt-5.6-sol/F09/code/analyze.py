"""Analyze all supplied rows; descriptive regressions are not causal estimates."""
import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='upload/data(10).csv')
    parser.add_argument('--description', default='upload/STUDY_DESCRIPTION(10).md')
    parser.add_argument('--out', default='submission/results')
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(args.data)
    assert list(df.columns) == ['x', 'y', 'z']
    assert len(df) == 2000 and not df.isna().any().any()
    assert np.isfinite(df.to_numpy()).all()
    assert set(df.x.unique()) == {0, 1}
    assert int(df.x.sum()) == 600
    assert df.y.between(0, 100).all()
    df['followup'] = df.y + df.z
    summary = df.groupby('x').agg(
        n=('x', 'size'), baseline_mean=('y', 'mean'), baseline_sd=('y', 'std'),
        baseline_min=('y', 'min'), baseline_max=('y', 'max'),
        change_mean=('z', 'mean'), change_sd=('z', 'std'),
        change_min=('z', 'min'), change_max=('z', 'max'),
        followup_mean=('followup', 'mean'), followup_min=('followup', 'min'),
        followup_max=('followup', 'max'))
    summary.to_csv(out / 'group_summary.csv')
    t = df[df.x == 1]
    c = df[df.x == 0]
    lo = max(t.y.min(), c.y.min())
    hi = min(t.y.max(), c.y.max())
    overlap = {
        'range_intersection_min': float(lo), 'range_intersection_max': float(hi),
        'treated_in_control_baseline_range': int(t.y.between(c.y.min(), c.y.max()).sum()),
        'control_below_minimum_treated_baseline': int((c.y < t.y.min()).sum()),
        'control_at_or_above_minimum_treated_baseline': int((c.y >= t.y.min()).sum()),
        'treated_above_maximum_control_baseline': int((t.y > c.y.max()).sum()),
        'baseline_ties': int(df.y.duplicated().sum())}
    # Every observation contributes to these descriptive least-squares fits.
    # A cubic fit checks sensitivity to curvature without asserting a true model.
    scaled_y = (df.y.to_numpy() - df.y.mean()) / df.y.std(ddof=0)
    models = []
    coefficients = []
    for degree in (0, 1, 3):
        design = np.column_stack([np.ones(len(df)), df.x.to_numpy()] +
                                 [scaled_y ** j for j in range(1, degree + 1)])
        beta, _, rank, _ = np.linalg.lstsq(design, df.z.to_numpy(), rcond=None)
        resid = df.z.to_numpy() - design @ beta
        models.append({'baseline_polynomial_degree': degree, 'n': len(df),
                       'x_coefficient': float(beta[1]), 'design_rank': int(rank),
                       'residual_rmse': float(np.sqrt(np.mean(resid ** 2))),
                       'interpretation': 'descriptive association, not a causal effect'})
        names = ['intercept', 'x'] + [f'standardized_y_power_{j}' for j in range(1, degree + 1)]
        coefficients.extend({'degree': degree, 'term': name, 'coefficient': float(b)}
                            for name, b in zip(names, beta))
    pd.DataFrame(models).to_csv(out / 'descriptive_models.csv', index=False)
    pd.DataFrame(coefficients).to_csv(out / 'model_coefficients.csv', index=False)
    df['baseline_bin'] = pd.cut(df.y, bins=np.arange(0, 101, 10), include_lowest=True)
    bins = df.groupby(['baseline_bin', 'x'], observed=False).agg(
        n=('x', 'size'), mean_y=('y', 'mean'), mean_z=('z', 'mean')).reset_index()
    bins.to_csv(out / 'baseline_bins.csv', index=False)
    # Illustrative completions of missing potential outcomes, NOT observed data
    # or effect estimates. They leave every observed value unchanged.
    examples = []
    for effect in (-1.0, 0.0, 1.0):
        untreated_followup_for_treated = t.followup - effect
        examples.append({'hypothetical_ATT': effect,
                         'hypothetical_mean_z0_among_treated': float((t.z - effect).mean()),
                         'counterfactual_followup_min': float(untreated_followup_for_treated.min()),
                         'counterfactual_followup_max': float(untreated_followup_for_treated.max()),
                         'all_counterfactual_followups_within_0_100': bool(untreated_followup_for_treated.between(0, 100).all()),
                         'status': 'hypothetical completion, not an estimate'})
    pd.DataFrame(examples).to_csv(out / 'nonidentification_examples.csv', index=False)
    result = {
        'n_rows': len(df), 'n_treated': len(t), 'n_control': len(c),
        'missing_values': int(df[['x', 'y', 'z']].isna().sum().sum()),
        'duplicate_full_rows': int(df[['x', 'y', 'z']].duplicated().sum()),
        'naive_difference_in_mean_change': float(t.z.mean() - c.z.mean()),
        'baseline_mean_difference': float(t.y.mean() - c.y.mean()),
        'overlap': overlap, 'descriptive_models': models,
        'hypothetical_examples': examples,
        'causal_conclusion': 'ATT sign and magnitude are not identified by the supplied material',
        'versions': {'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__},
        'source_sha256': {name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
                          for name, path in [('data.csv', args.data), ('STUDY_DESCRIPTION.md', args.description)]}}
    (out / 'analysis.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(summary.to_string())
    print('\nDescriptive models:\n' + pd.DataFrame(models).to_string(index=False))
    print('\nAnalysis details:\n' + json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
