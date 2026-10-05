"""Deterministic English report reconstruction from full saved evidence."""
import argparse
import json
from pathlib import Path

import numpy as np

from src.calibration.storage import sha,write_json
from src.calibration.summary import read_records

ROOT=Path(__file__).resolve().parents[2]


def number(value):
    return 'not evaluable' if value is None else format(value,'.8g')


def render(run_id):
    directory=ROOT/'results/calibration'/run_id
    summary=json.loads((directory/'main/summary.json').read_text())
    comparison=json.loads((directory/'comparison.json').read_text())
    records=read_records(directory/'main')
    lines=['# Causal Salmon: Complete Offline Calibration Report','',
           'Status: offline calibration evidence; parameter confirmation pending; exam datasets not generated; tested-model experiments not started.','',
           '## Protocol, completeness and independent verification','',
           'Frozen protocol SHA-256: `f85fedf447c734d9d5e7a2cb630284fe18c7091c5cf653610adbc43ec8e7144c`. Research tag: `20260929`. Calibration seeds: `703000–703999`. Each independently authored implementation must retain five candidates × three worlds × 1,000 repetitions.','',
           f'Independent comparison: **{"passed" if comparison["passed"] else "implementation discrepancies remain"}**; {comparison["repetitions_checked"]}/15,000 repetitions and {comparison["bootstrap_estimates_checked"]}/1,000,000 bootstrap estimates checked. Both regenerate data. Public CSV hashes and treatment vectors are exact; common numerical outputs use the registered 1e-8 relative/absolute tolerance; all statuses and decisions must agree.','',
           'Both implementations retain public CSVs, recoverable hidden student tables, truth/random-flow registration, all 200 bootstrap attempts per B repetition, reference reports/access audits, and completion manifests. Main and independent code, initial selftests, environment and dependency identities are archived in the initial registration files and each run identity.','',
           'Original documentation checks remain historical starting evidence. They do not count as calibration or experiment checks. CAL-9 final-exam material freezing remains deferred until written parameter confirmation; current-candidate calibration descriptions have undergone mechanical pairing checks.','',
           '## Candidate and primary-method results','',
           '| Candidate | World | Mean SATT | Signed bias | MCSE | Relative bias | Coverage | Precision ratio | Distinction ratio |',
           '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for candidate,value in summary['candidates'].items():
        for world,w in value['worlds'].items():
            metrics=w['primary']
            meanT=float(np.mean([r['T'] for r in records if r['candidate']==candidate and r['world']==world]))
            lines.append('| '+' | '.join([candidate,world,number(meanT),*[number(metrics[field]) for field in ('bias','MCSE','relative_bias','coverage','precision_ratio','distinction_ratio')]])+' |')
    lines+=['','Bias is mean(E−T), not mean absolute error. MCSE and all SDs use ddof=1. Cross-repeat precision is mean(T)/SD(E−T); distinction is mean(N−E)/SD(E). Nominal intervals are closed E ±1.96 SE. These are calibration results, not tested-AI results.','',
            '| Candidate | State | CAL-1 | CAL-2 | CAL-3 | CAL-4 | CAL-5 | CAL-6 | CAL-7 | CAL-8 | CAL-9 | CAL-10 | CAL-11 |','|---|---|'+'---|'*11]
    for candidate,value in summary['candidates'].items():
        cells=[candidate,value['state']]+['deferred' if value['CAL'][f'CAL-{i}'] is None else 'pass' if value['CAL'][f'CAL-{i}'] else 'fail' for i in range(1,12)]
        lines.append('| '+' | '.join(cells)+' |')
    lines+=['','CAL-4 requires at least 999/1,000 repetitions with ≥20 controls in every prescribed participant-score segment, separately in B and C. Candidate science status follows CAL-1 and CAL-3–7. Integrity failures invalidate implementation evidence and cannot justify changing candidates.','',
            '## Mandatory diagnostics and support','',
            '| Candidate | Diagnostic | Status | Available / 1000 | Bias | MCSE | Relative bias | Coverage | Conflict |','|---|---|---|---:|---:|---:|---:|---:|---|']
    for candidate,value in summary['candidates'].items():
        for diag in ('D1','D2'):
            m=value['worlds']['B'][diag]
            c=value['diagnostic_conflicts'][diag]
            lines.append('| '+' | '.join([candidate,diag,m['status'],str(m['count']),*[number(m[k]) for k in ('bias','MCSE','relative_bias','coverage')],str(c['conflict']) if c['status']=='ok' else 'not evaluable'])+' |')
    lines+=['','D1 uses the exact rank-defined five segments. D2 uses support y≥minimum participant y, quadratic logit with zero initialization, ≤50 Newton steps and max|delta|<1e-10; no penalty, step reduction or weight trimming. Every bootstrap refits support and model. A single confirmed diagnostic failure makes its entire candidate aggregate not evaluable; remaining repeats are not used to claim diagnostic performance.','']
    for candidate,value in summary['candidates'].items():
        subset=[r for r in records if r['candidate']==candidate and r['world']=='B']
        weights=[r['D2']['max_weight'] for r in subset if r['D2'].get('max_weight') is not None]
        ess=[r['D2']['ess'] for r in subset if r['D2'].get('ess') is not None]
        failed=sum(len(r['D2'].get('bootstrap_failures',[])) for r in subset)
        lines.append(f'- {candidate}: B segment support passes {value["worlds"]["B"]["support_passes"]}/1000; C {value["worlds"]["C"]["support_passes"]}/1000. D2 maximum normalized control weight range {number(min(weights)) if weights else "unavailable"}–{number(max(weights)) if weights else "unavailable"}; ESS range {number(min(ess)) if ess else "unavailable"}–{number(max(ess)) if ess else "unavailable"}; failed bootstrap attempts {failed}.')
    lines+=['','## Reference analysis and GEN diagnostics','',
            'Public reference analysis receives only two fixed-name files in an opaque staged directory and a standalone pre-registered numerical executable. Method selection uses the public allocation paragraph. The operating-system sandbox denies project/parent listing and network access; runtime libraries are explicitly whitelisted. Backend truth is joined only by the hidden-side checker. Access policies, probes, input hashes, outputs and traces are retained for each named/anonymous pair. Reference templates are checked against the report contract; they are not a general automated replacement for later human scoring.','',
            '| Candidate | World | GEN condition | Passed / applicable | Failure reasons |','|---|---|---|---:|---|']
    for candidate,value in summary['candidates'].items():
        for world,checks in value['GEN'].items():
            for gen,c in checks.items():
                if c['applicable_count']:
                    reasons='; '.join(f'{name}: {count}' for name,count in sorted(c['reasons'].items())) or 'none'
                    lines.append(f'| {candidate} | {world} | {gen} | {c["passed_count"]}/{c["applicable_count"]} | {reasons} |')
    lines+=['','GEN frequencies are separate diagnostics. Every repetition, including GEN failures, remains in the original CAL denominators. GEN-4 uses per-case T/SE and includes coverage and a positive lower limit; it does not replace CAL-3. C requires information insufficiency and ≥50% adjusted error, not a nonsignificant result.','',
            '## Failures, invalidated attempts and diagnosis','']
    failures=comparison['failure_reproductions']
    if failures:
        lines.append(f'{len(failures)} method/bootstrap failures are retained in comparison.json with both implementations’ data-level summaries. Numerical-failure classification requires independently reproduced status and a verifiable data reason; any mismatch remains an implementation error. Diagnostic conflicts and unavailable aggregates require the owner’s explicit acceptance or skip decision.')
        for candidate,value in summary['candidates'].items():
            for diag,c in value['diagnostic_conflicts'].items():
                if c['status']!='ok' or c['conflict']:
                    lines.append(f'- {candidate}/{diag}: {c["status"]}; conflict criteria {c["criteria"]}. Inspect all preserved failure traces and diagnostic/primary bias and coverage; the primary estimator is unchanged.')
    else:
        lines.append('No unavailable primary/diagnostic fits or failed bootstrap attempts were found in the complete independent comparison.')
    for impl in ('main','independent'):
        invalid=list((directory/impl).glob('invalidated/**/reason.json'))
        lines.append(f'- {impl}: {len(invalid)} resumed/interrupted attempt records under invalidated/. Initial exploratory selftest attempts are retained separately; they are not formal calibration evidence.')
    if comparison['mismatches']:
        lines.append(f'Unresolved implementation discrepancies: {len(comparison["mismatches"])}. No scientific recommendation is released.')
    lines+=['','## Fixed-order recommendation and written confirmation','']
    recommendation=None
    if comparison['passed']:
        for candidate,value in summary['candidates'].items():
            if value['state']=='passed':
                recommendation={'candidate':candidate,'requires_review':False}
                break
            if value['state']=='passed_review_required':
                recommendation={'candidate':candidate,'requires_review':True}
                break
    if recommendation:
        candidate=recommendation['candidate']
        p=next(p for p in json.loads((ROOT/'configs/calibration_candidates.json').read_text())['candidates'] if p['id']==candidate)
        lines.append(f'First eligible candidate in the registered K1–K5 order: **{candidate}**'+(' (**review required; not an unconditional recommendation**).' if recommendation['requires_review'] else '.'))
        lines.append('')
        lines.append(f'Complete row: a={p["a"]}, b={p["b_multiplier"]}×sqrt(3), gamma={p["gamma"]}, beta={p["beta"]}, kappa={p["kappa"]}, M={p["M"]}, K={p["K"]}. No parameter is frozen. '+('The owner must accept this row with reasons or skip it and inspect the next eligible row.' if recommendation['requires_review'] else 'The owner must confirm this complete row in writing, tied to this report SHA-256.'))
    else:
        lines.append('No selectable candidate is released. Retain the complete findings and stop; new candidates, seeds or thresholds require an approved protocol amendment.')
    lines+=['','The workflow stops here. Only after confirmation are exam descriptions frozen and the §13 framework/isolation prerequisites completed. No development/formal data seeds, tested models, API credentials, publication or PRs are used in this stage.','',
            '## Evidence identities and reproduction','',
            '| Artifact | SHA-256 |','|---|---|']
    for label,path in [('Main initial registration',ROOT/'manifests/main_initial.json'),('Independent initial registration',ROOT/'manifests/independent_initial.json'),('Main summary',directory/'main/summary.json'),('Independent summary',directory/'independent/summary.json'),('Full comparison',directory/'comparison.json'),('Dependency lock',ROOT/'uv.lock')]:
        lines.append(f'| {label} | `{sha(path)}` |')
    lines+=['','All per-repetition files are fingerprinted in their evidence.sha256.json; COMPLETE contains that manifest hash. Public reference evidence has its own manifest and is additionally pinned by the main external-evidence manifest. Input protocol/configuration/environment identities are in run.json; raw evidence is never overwritten.','',
            'Verified command details and the precise project interpreter/environment are provided in docs/reproduction.md. Report reconstruction reads saved evidence and does not rerun simulation.','']
    return '\n'.join(lines),recommendation


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--output-name',default='CALIBRATION_REPORT.md')
    args=parser.parse_args()
    directory=ROOT/'results/calibration'/args.run_id
    text,recommendation=render(args.run_id)
    path=directory/args.output_name
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        stream.write(text)
    receipt={'report':str(path),'report_sha256':sha(path),'candidate_pending_confirmation':recommendation,'parameter_frozen':False,'exam_datasets_generated':False,'tested_model_calls':0}
    write_json(directory/(args.output_name+'.receipt.json'),receipt)
    print(json.dumps(receipt))


if __name__=='__main__':
    main()
