"""Main-owned generation arithmetic, reference execution and evidence storage."""
import os
for _key in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_key] = '1'

import argparse
import fcntl
import hashlib
import json
import math
import platform
import shutil
import uuid
from pathlib import Path

import numpy as np

from src.calibration import isolation
from src.calibration.quality import qualify
from src.calibration.run import hidden_table, read_hidden
from src.calibration.statistics import (adjusted_ols, bin_counts, mean_difference,
                                       not_applicable, segmented_difference,
                                       weighted_diagnostic, with_interval)
from src.calibration.storage import seal, sha, validate_complete, write_json
from src.data.generator import (TAG, WORLD_CODES, bit_equal, check_hidden,
                                csv_bytes, parse_csv, ranked, uniform)
from src.data.materials import anonymize, protocol_bytes

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = 'f85fedf447c734d9d5e7a2cb630284fe18c7091c5cf653610adbc43ec8e7144c'
PARAMETERS = dict(n=2000, a=45, b_multiplier=3, gamma=.25, beta=.5,
                  kappa=1.2, M=900, K=600, m_intercept=10, effect_fraction=.1)



def load(relative):
    return json.loads((ROOT / relative).read_text())


def environment():
    return dict(python=platform.python_version(), numpy=np.__version__,
                platform=platform.platform(), numerical_threads=1)


def initial_environment_matches(metadata):
    actual = environment()
    return all(metadata.get(key) == actual[key] for key in ('python', 'numpy', 'platform'))


def verify_files(files, root=ROOT):
    for rel, expected in files.items():
        path = Path(root) / rel
        if not path.is_file() or sha(path) != expected:
            raise RuntimeError('Evidence/code fingerprint differs: ' + rel)


def check_generation_gate():
    frozen = load('configs/frozen_study.json')
    if hashlib.sha256(protocol_bytes()).hexdigest() != PROTOCOL or frozen['parameters'] != PARAMETERS:
        raise RuntimeError('Frozen numerical specification differs')
    verify_files(frozen['materials'])
    return frozen

def case_matrix():
    raise RuntimeError('Use scripts.generate_data for the registered finite pool')

def generate_data(p, world, seed, purpose):
    if world not in WORLD_CODES:
        raise ValueError('Unknown registered world')
    if purpose == 4 and 709000 <= seed <= 709999:
        pass
    else:
        raise ValueError('Unregistered fixed-data seed or purpose')
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


def execute_case(p, case, base, dataset_root=None):
    phase, world, seed, purpose, case_id = (case[k] for k in ('phase', 'world', 'seed', 'purpose', 'case_id'))
    directory = base / phase / case_id
    dataset_root = Path(dataset_root) if dataset_root is not None else ROOT / 'datasets'
    public = dataset_root / 'public' / phase / case_id
    private = dataset_root / 'ground_truth' / case_id
    directory.mkdir(parents=True, exist_ok=False)
    public.mkdir(parents=True, exist_ok=False)
    private.mkdir(parents=True, exist_ok=False)
    try:
        d = generate_data(p, world, seed, purpose)
        blob = csv_bytes(d['x'], d['y'], d['z'])
        (public / 'data.csv').write_bytes(blob)
        (directory / 'data.csv').write_bytes(blob)
        students = hidden_table(d)
        (private / 'students.csv').write_bytes(students)
        restored = read_hidden(students)
        x, y, z = parse_csv(blob)
        for key in ('y', 'u', 'epsilon', 'm', 'z0', 'z1'):
            if not bit_equal(restored[key], d[key]):
                raise RuntimeError('Hidden CSV roundtrip differs: ' + key)
        restored.update(x=x, z=z)
        invariants = check_hidden(restored, p)
        truth = {
            'SATT': d['T'], 'parameters': {**p, 'b': float(p['b_multiplier'] * math.sqrt(3.0))},
            **case, 'study_tag': TAG, 'entropy': d['entropy'],
            'bootstrap_entropy': [[TAG, purpose, seed, WORLD_CODES[world], 20, i] for i in range(200)] if world == 'B' else [],
            'csv_sha256': sha(public / 'data.csv'), 'participants': int(x.sum()),
            'applicants': int(d['applicant'].sum()) if world != 'A' else None,
            'leakage_probe': 'SALMON_PRIVATE_' + uuid.uuid4().hex,
        }
        write_json(private / 'truth.json', truth)
        primary = with_interval(mean_difference(x, z) if world == 'A' else adjusted_ols(x, y, z), d['T'])
        D1, D2, bootstrap = not_applicable(), not_applicable(), []
        if world == 'B':
            D1 = with_interval(segmented_difference(x, y, z), d['T'])
            D2, bootstrap = weighted_diagnostic(x, y, z, p['a'] + 15, seed, purpose, WORLD_CODES[world])
            D2 = with_interval(D2, d['T'])
        refs = {}
        descriptions = {}
        for version in ('named', 'anonymized'):
            inputs = directory / version / 'inputs'
            inputs.mkdir(parents=True)
            (inputs / 'data.csv').write_bytes(blob)
            prose = (ROOT / f'materials/{version}/{world}.md').read_bytes()
            (inputs / 'STUDY_DESCRIPTION.md').write_bytes(prose)
            descriptions[version] = prose.decode()
            output, audit = isolation.reference(inputs)
            expected = {'N': float(np.mean(z[x == 1]) - np.mean(z[x == 0])),
                        'E': primary['E'], 'se': primary['se'], 'ci': primary['ci']}
            if primary['status'] == 'ok' and not all(np.array_equal(output['numeric'][key], expected[key]) for key in expected):
                raise RuntimeError('Public reference numerical execution differs')
            write_json(directory / version / 'output.json', output)
            write_json(directory / version / 'access_audit.json', audit)
            (directory / version / 'report.md').write_text(output['report'])
            refs[version] = {key: output[key] for key in ('input_hashes', 'method', 'correct', 'format_valid', 'input_boundary_passed', 'numeric')}
        record = {
            'candidate': 'K1', **case, 'csv_sha256': truth['csv_sha256'],
            'x': x.tolist(), 'n': 2000, 'participants': truth['participants'], 'applicants': truth['applicants'],
            'T': d['T'], 'identity_error': float(abs(np.mean(restored['z1'][x == 1] - restored['z0'][x == 1]) - .1 * np.mean(restored['m'][x == 1]))),
            'N': float(np.mean(z[x == 1]) - np.mean(z[x == 0])), 'primary': primary,
            'D1': D1, 'D2': D2, 'bins': None if world == 'A' else bin_counts(x, y),
            'invariants': invariants, 'reference': refs,
        }
        record['GEN'] = qualify(record, anonymize(descriptions['named']) == descriptions['anonymized'])
        write_json(directory / 'record.json', record)
        write_json(directory / 'bootstrap.json', bootstrap)
        write_json(directory / 'external_evidence.sha256.json', {str(path): sha(path) for path in [public / 'data.csv', private / 'students.csv', private / 'truth.json']})
        seal(directory)
        for path in list(public.iterdir()) + list(private.iterdir()) + list(directory.rglob('*')):
            if path.is_file():
                path.chmod(0o444)
        return record
    except Exception as error:
        write_json(directory / 'implementation_error.json', {'case': case, 'error': repr(error), 'classification': 'implementation_error', 'retain_for_original_seed_recovery': True})
        raise


def retain_incomplete(directory, case, base):
    """Keep interrupted evidence before retrying the identical case."""
    if (directory / 'COMPLETE').exists():
        raise RuntimeError('Sealed case changed; explicit investigation required')
    archive = base / 'invalidated' / uuid.uuid4().hex
    archive.mkdir(parents=True, exist_ok=False)
    paths = {'case': directory,
             'public': ROOT / 'datasets/public' / case['phase'] / case['case_id'],
             'ground_truth': ROOT / 'datasets/ground_truth' / case['case_id']}
    for name, path in paths.items():
        if path.exists():
            shutil.move(str(path), str(archive / name))
    write_json(archive / 'reason.json', {'reason': 'Interrupted incomplete case; identical run identity and original seed retained', 'case': case})
    return archive

