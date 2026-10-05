"""Registered finite-pool generation using unchanged main numerical algorithms."""
import os
for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_key] = '1'
import argparse
import fcntl
import json
import math
import shutil
import subprocess
import uuid
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
import numpy as np
from scripts import data_pipeline as original
from src.data.generator import TAG, WORLD_CODES, uniform, ranked
from src.calibration.storage import sha, write_json, validate_complete

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/quality_checks/data'
CONFIG = 'configs/data_generation.json'
INITIALS = ('manifests/generation_main_initial.json', 'manifests/generation_independent_initial.json')


def load(path):
    return json.loads((ROOT / path).read_text())


def write_once(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if json.loads(path.read_text()) != value: raise RuntimeError('Immutable evidence differs: ' + str(path))
    else:
        write_json(path, value)
        path.chmod(0o444)


def check_gate(initials=True):
    cfg = load(CONFIG)
    frozen = original.check_generation_gate()
    authorization = load('manifests/data_authorization.json')
    if authorization['config_sha256'] != sha(ROOT / CONFIG): raise RuntimeError('Frozen configuration changed')
    if cfg['generation_protocol_sha256'] != sha(ROOT / cfg['generation_protocol']): raise RuntimeError('Generation protocol changed')
    if authorization['generation_protocol_sha256'] != cfg['generation_protocol_sha256']: raise RuntimeError('Authorization differs')
    if cfg['parameters'] != original.PARAMETERS or cfg['pool_count'] != 60 or cfg['selected_count'] != 12: raise RuntimeError('Frozen scope differs')
    if cfg['selected_parameters_sha256'] != sha(ROOT / 'configs/selected_parameters.json'): raise RuntimeError('K1 identity differs')
    if cfg['materials'] != frozen['materials']: raise RuntimeError('Material registration differs')
    original.verify_files(cfg['materials'])
    framework = load('manifests/offline_framework.json')
    if not all(framework['checks'][k] for k in ('ACC-5-reference','ACC-7-reference')): raise RuntimeError('Reference isolation incomplete')
    original.verify_files(framework['files'])
    if initials:
        for path in INITIALS:
            if not (ROOT / path).exists(): raise RuntimeError('Both program selftests required: ' + path)
            record = load(path)
            if not record['passed'] or not original.initial_environment_matches(record['environment']): raise RuntimeError('Initial verification failed')
            if record['config_sha256'] != sha(ROOT / CONFIG): raise RuntimeError('Initial configuration differs')
            original.verify_files(record['files'])
    return cfg

def case_matrix():
    cfg = load(CONFIG)
    rows = []
    for phase in ('development', 'formal'):
        spec = cfg['phases'][phase]
        expected = list(range(730001, 730011)) if phase == 'development' else list(range(740001, 740011))
        if spec['seeds'] != expected or spec['purpose'] != (2 if phase == 'development' else 3): raise RuntimeError('Finite pool differs')
        for world in cfg['worlds']:
            for seed in expected:
                rows.append(dict(phase=phase, world=world, seed=seed, purpose=spec['purpose'], case_id=f'{phase}-{world}-{seed}'))
    return rows


class PoolExhausted(RuntimeError):
    pass


def select_cases(records):
    expected = {(r['phase'], r['world'], r['seed']) for r in case_matrix()}
    actual = [(r['phase'], r['world'], r['seed']) for r in records]
    if len(actual) != 60 or set(actual) != expected: raise ValueError('Missing, additional or duplicate pool case')
    for record in records:
        methods = ('primary', 'D1', 'D2') if record['world'] == 'B' else ('primary',)
        if any(record[m]['status'] != 'ok' for m in methods): raise RuntimeError('Numerical failure requires investigation')
    selected, counts = [], {}
    cfg = load(CONFIG)
    for phase in ('development', 'formal'):
        for world in cfg['worlds']:
            eligible = sorted((r for r in records if r['phase'] == phase and r['world'] == world and all(g['passed'] is True for g in r['GEN'].values() if g['applicable'])), key=lambda r:r['seed'])
            quota = cfg['phases'][phase]['quota_per_world']
            counts[phase + '/' + world] = len(eligible)
            if len(eligible) < quota: raise PoolExhausted('Insufficient qualified candidates: ' + phase + '/' + world)
            selected.extend(eligible[:quota])
    return selected, counts


def generate_data(p, world, seed, purpose):
    if world not in WORLD_CODES: raise ValueError('Unknown world')
    if purpose == 4 and 709000 <= seed <= 709009:
        pass
    elif any(c['world'] == world and c['seed'] == seed and c['purpose'] == purpose for c in case_matrix()):
        cfg = check_gate()
        if p != {'id': 'K1', **cfg['parameters']}: raise RuntimeError('Unconfirmed parameter configuration')
    else:
        raise ValueError('Unregistered screened-data seed or purpose')
    # Main-owned arithmetic preserved from its calibrated generator.
    n, K, M = 2000, p['K'], p['M']
    entropies = {}
    def stream(v):
        entropy = [TAG, purpose, seed, WORLD_CODES[world], v]
        entropies[str(v)] = entropy
        return uniform(entropy, n)
    y = p['a'] + 30 * stream(1)
    u = math.sqrt(3.0) * (2 * stream(2) - 1)
    eps = p['b_multiplier'] * math.sqrt(3.0) * (2 * stream(3) - 1)
    mu = p['a'] + 15
    m = 10 + p['gamma'] * (y - mu) + 2 * u
    z0 = m + eps
    z1 = z0 + .1 * m
    x = np.zeros(n, dtype=np.int64)
    out = dict(y=y, u=u, epsilon=eps, m=m, z0=z0, z1=z1, x=x, entropy=entropies)
    if world == 'A':
        lottery = stream(4)
        x[np.lexsort((np.arange(n), lottery))[:K]] = 1
    else:
        G = -np.log(-np.log(stream(5)))
        application_tie, admission_tie = stream(6), stream(7)
        w = (p['beta'] * (y - mu)) / 15
        if world == 'C':
            w = w + p['kappa'] * u
        w = w + G
        applicant = np.zeros(n, dtype=np.int64)
        ids = ranked(w, application_tie)[:M]
        applicant[ids] = 1
        order = np.lexsort((ids, -admission_tie[ids], -y[ids]))
        x[ids[order[:K]]] = 1
        out.update(G=G, w=w, applicant=applicant, admitted=x.copy())
    out['z'] = np.where(x == 1, z1, z0)
    out['T'] = float(.1 * np.mean(m[x == 1]))
    return out


def run_case(case, selftest=False, resume=False):
    base = BASE / 'main'
    storage = base / 'selftest_storage' if selftest else BASE / 'candidate_storage/main'
    directory = base / case['phase'] / case['case_id']
    if directory.exists():
        if not resume: raise RuntimeError('Existing case requires --resume')
        if validate_complete(directory):
            original.verify_files(json.loads((directory / 'external_evidence.sha256.json').read_text()), ROOT)
            return json.loads((directory / 'record.json').read_text())
        if (directory / 'COMPLETE').exists(): raise RuntimeError('Sealed evidence changed')
        archive = base / 'invalidated' / uuid.uuid4().hex
        archive.mkdir(parents=True)
        for name, path in {'case':directory, 'public':storage/'public'/case['phase']/case['case_id'], 'ground_truth':storage/'ground_truth'/case['case_id']}.items():
            if path.exists(): shutil.move(str(path), str(archive/name))
        write_once(archive/'reason.json', {'reason':'Incomplete original-seed recovery','case':case})
    original.generate_data = generate_data
    original.isolation._PROBE = None
    return original.execute_case({'id':'K1', **load(CONFIG)['parameters']}, case, base, storage)


def code_files():
    paths = sorted((ROOT/'src').rglob('*.py')) + [Path(__file__), ROOT/'scripts/data_pipeline.py', ROOT/'tests/test_data_generation.py', ROOT/'tests/test_final_data_audit.py']
    return {str(p.relative_to(ROOT)):sha(p) for p in paths if '__pycache__' not in p.parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selftest', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    if args.workers not in (1,2): parser.error('Only one or two single-thread workers permitted')
    check_gate(initials=not args.selftest)
    base = BASE / 'main'
    base.mkdir(parents=True, exist_ok=True)
    files = code_files()
    code = {'files':files, 'config_sha256':sha(ROOT/CONFIG), 'environment':original.environment(), 'candidate_draws_at_registration':0}
    if args.selftest:
        write_once(ROOT/'manifests/main_code.json', code)
        command = ['.venv/bin/python','-m','pytest','-q']
        tests = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        log = base/'selftest_tests.log'
        if not log.exists(): log.write_text(tests.stdout+tests.stderr)
        if tests.returncode: raise RuntimeError(tests.stdout+tests.stderr)
        cases = [dict(phase='selftest', world=w, seed=s, purpose=4, case_id=f'selftest-{w}-{s}') for w in 'ABC' for s in range(709000,709010)]
    else:
        cases = case_matrix()
    identity = {'files':files,'environment':original.environment(),'config_sha256':sha(ROOT/CONFIG),'cases':cases}
    if not args.selftest: identity['initials'] = {name:sha(ROOT/name) for name in INITIALS}
    with (base/('.selftest.lock' if args.selftest else '.run.lock')).open('a+b') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX|fcntl.LOCK_NB)
        write_once(base/('selftest_identity.json' if args.selftest else 'run_identity.json'), identity)
        if args.workers == 1:
            records = [run_case(case, args.selftest, args.resume) for case in cases]
        else:
            with ProcessPoolExecutor(max_workers=args.workers) as executor:
                futures = [executor.submit(run_case, case, args.selftest, args.resume) for case in cases]
                records = []
                for case, future in zip(cases,futures):
                    record = future.result();records.append(record)
                    print(json.dumps({'case_id':case['case_id'],'qualified':all(g['passed'] for g in record['GEN'].values() if g['applicable'])}),flush=True)
        summary={'scope':'selftest' if args.selftest else 'complete_unscreened_candidate_pool','cases':len(records),'references':2*len(records),'bootstrap_attempts':200*sum(r['world']=='B' for r in records),'qualified':sum(all(g['passed'] for g in r['GEN'].values() if g['applicable']) for r in records),'failed_cases':[r['case_id'] for r in records if any(g['passed'] is False for g in r['GEN'].values())],'selected_cases':0,'tested_model_calls':0}
        write_once(base/('selftest_summary.json' if args.selftest else 'summary.json'),summary)
        if args.selftest:
            write_once(ROOT/'manifests/generation_main_initial.json', {**code,'passed':True,'selftest_cases':30,'references':60,'bootstrap_attempts':2000,'test_command':' '.join(command),'test_log_sha256':sha(log),'selftest_identity_sha256':sha(base/'selftest_identity.json')})
        print(json.dumps(summary),flush=True)


if __name__ == '__main__': main()
