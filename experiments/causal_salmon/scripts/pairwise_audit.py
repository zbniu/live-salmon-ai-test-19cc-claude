"""Read-only paired evidence audit and fixed-batch qualification report.

This program never generates, selects, replaces or alters study datasets.
"""
import argparse
import csv
import hashlib
import io
import json
import math
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def compare_value(a, b, label):
    if a is None or b is None:
        assert a is None and b is None, label + ': null-mask mismatch'
    elif isinstance(a, bool) or isinstance(b, bool) or isinstance(a, str):
        assert type(a) is type(b) and a == b, label + ': discrete mismatch'
    elif isinstance(a, (int, float)):
        assert math.isfinite(a) and math.isfinite(b), label + ': nonfinite value'
        assert abs(a - b) <= 1e-8 * max(1, abs(a)), label + ': numeric mismatch'
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), label + ': vector length mismatch'
        for i, (x, y) in enumerate(zip(a, b)):
            compare_value(x, y, f'{label}[{i}]')
    elif isinstance(a, dict):
        assert isinstance(b, dict), label + ': object mismatch'
        for key in a:
            assert key in b, label + ': missing key ' + key
            compare_value(a[key], b[key], label + '.' + key)
    else:
        raise AssertionError('Unsupported evidence type: ' + label)


def hidden_table(path):
    reader = csv.DictReader(io.StringIO(Path(path).read_text()))
    rows = list(reader)
    return {key: [float(row[key]) for row in rows] for key in reader.fieldnames}


def assert_public_projection(blob, hidden, expected_n=2000):
    assert blob.startswith(b'x,y,z\n') and blob.endswith(b'\n')
    assert b'\r' not in blob and b'"' not in blob and b' ' not in blob
    rows = list(csv.reader(io.StringIO(blob.decode('utf-8'))))
    assert rows[0] == ['x', 'y', 'z'] and len(rows) == expected_n + 1
    observed_x = []
    for index, row in enumerate(rows[1:]):
        assert len(row) == 3 and row[0] in ('0', '1')
        x, y, z = int(row[0]), float(row[1]), float(row[2])
        assert math.isfinite(y) and math.isfinite(z) and 0 <= y + z <= 100
        for value, encoded in ((y, row[1]), (z, row[2])):
            assert encoded == ('0' if value == 0 else format(value, '.17g'))
        assert struct.pack('d', y) == struct.pack('d', hidden['y'][index])
        assert struct.pack('d', z) == struct.pack('d', hidden['z1' if x else 'z0'][index])
        observed_x.append(x)
    return observed_x


def verify_case(directory):
    manifest = directory / 'evidence.sha256.json'
    assert (directory / 'COMPLETE').read_text().strip() == sha(manifest), str(directory)
    hashes = read(manifest)
    hashes = hashes.get('files', hashes)
    for name, expected in hashes.items():
        assert sha(directory / name) == expected, str(directory / name)
    external = directory / 'external_evidence.sha256.json'
    if external.exists():
        for name, expected in read(external).items():
            assert sha(name) == expected, name


def inspect_pair(phase, world, seed, main_dir, independent_dir, main_private, public_path):
    verify_case(main_dir)
    verify_case(independent_dir)
    a, b = read(main_dir / 'record.json'), read(independent_dir / 'record.json')
    blob = public_path.read_bytes()
    assert blob == (main_dir / 'data.csv').read_bytes() == (independent_dir / 'data.csv').read_bytes()
    ah, bh = hidden_table(main_private / 'students.csv'), hidden_table(independent_dir / 'students.csv')
    x = assert_public_projection(blob, ah)
    assert x == a['x'] == b['x']
    assert sum(x) == 600
    assert a['world'] == b['world'] == world and a['seed'] == b['seed'] == seed
    assert a['purpose'] == b['purpose'] == (4 if phase == 'selftest' else 2 if phase == 'development' else 3)
    assert a['csv_sha256'] == b['csv_sha256'] == hashlib.sha256(blob).hexdigest()
    for key in ah:
        if key in bh and key != 'i':
            compare_value(ah[key], bh[key], 'hidden.' + key)
    for key in ('candidate', 'n', 'participants', 'applicants', 'T', 'identity_error', 'N', 'invariants', 'bins'):
        compare_value(a[key], b[key], key)
    for method in ('primary', 'D1', 'D2'):
        for key in ('status', 'E', 'se', 'ci', 'covered'):
            compare_value(a[method][key], b[method][key], method + '.' + key)
    for key in a['GEN']:
        for field in ('applicable', 'passed'):
            compare_value(a['GEN'][key][field], b['GEN'][key][field], key + '.' + field)
    for version in ('named', 'anonymized'):
        inputs = main_dir / version / 'inputs'
        assert sorted(p.name for p in inputs.iterdir()) == ['STUDY_DESCRIPTION.md', 'data.csv']
        assert (inputs / 'data.csv').read_bytes() == (independent_dir / version / 'data.csv').read_bytes() == blob
        assert (inputs / 'STUDY_DESCRIPTION.md').read_bytes() == (independent_dir / version / 'STUDY_DESCRIPTION.md').read_bytes() == (ROOT / f'materials/{version}/{world}.md').read_bytes()
        for key in ('input_hashes', 'method', 'correct', 'format_valid', 'input_boundary_passed', 'numeric'):
            compare_value(a['reference'][version][key], b['reference'][version][key], version + '.' + key)
        main_report = (main_dir / version / 'report.md').read_text()
        independent_report = (independent_dir / version / 'report.md').read_text()
        assert main_report.count('## Final report') == independent_report.count('## Final report') == 1
    at, bt = read(main_private / 'truth.json'), read(independent_dir / 'truth.json')
    compare_value(at['entropy'], bt['streams'], 'entropy')
    compare_value(at['SATT'], bt['SATT'], 'SATT')
    assert at['csv_sha256'] == bt['csv_sha256'] == a['csv_sha256']
    assert len(at['leakage_probe']) > 20 and len(bt['leakage_probe']) > 20
    for source in (main_dir, independent_dir):
        for version in ('named', 'anonymized'):
            for path in (source / version).rglob('*'):
                if path.is_file():
                    assert at['leakage_probe'].encode() not in path.read_bytes()
                    assert bt['leakage_probe'].encode() not in path.read_bytes()
    ab, bb = read(main_dir / 'bootstrap.json'), read(independent_dir / 'bootstrap.json')
    assert len(ab) == len(bb) == (200 if world == 'B' else 0)
    for i, (u, v) in enumerate(zip(ab, bb)):
        for key in ('index', 'status', 'E'):
            compare_value(u[key], v[key], f'bootstrap[{i}].{key}')
    failures = {k: value['reasons'] for k, value in a['GEN'].items() if value['passed'] is False}
    return {'phase': phase, 'world': world, 'seed': seed, 'csv_sha256': a['csv_sha256'],
            'T': a['T'], 'N': a['N'], 'E': a['primary']['E'], 'se': a['primary']['se'],
            'ci': a['primary']['ci'], 'GEN': a['GEN'], 'quality_passed': not failures,
            'failure_reasons': failures, 'independent_comparison_passed': True,
            'private_probe': at['leakage_probe']}


def write_once(path, text):
    if path.exists():
        assert path.read_text() == text, 'Existing audit output differs: ' + str(path)
    else:
        with path.open('x') as stream:
            stream.write(text)

