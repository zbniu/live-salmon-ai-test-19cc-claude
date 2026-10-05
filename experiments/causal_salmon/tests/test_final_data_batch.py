"""Final-purpose gates and unchanged numerical generation on selftest seeds."""
import json
from pathlib import Path

import numpy as np
import pytest

from scripts import data_pipeline as final
from scripts import generate_data as pool_program
from src.data.generator import generate as original

ROOT = Path(__file__).resolve().parents[1]
PARAMETERS = {'id': 'K1', **json.loads((ROOT / 'configs/selected_parameters.json').read_text())['parameters']}


@pytest.mark.parametrize('world', list('ABC'))
@pytest.mark.parametrize('seed', range(709000, 709010))
def test_new_entry_preserves_registered_arithmetic(world, seed):
    expected = original(PARAMETERS, world, seed, 4)
    actual = final.generate_data(PARAMETERS, world, seed, 4)
    assert actual.keys() == expected.keys()
    for key in expected:
        if isinstance(expected[key], np.ndarray):
            assert np.array_equal(actual[key], expected[key])
        else:
            assert actual[key] == expected[key]


@pytest.mark.parametrize('seed,purpose', [(710002, 2), (720004, 3), (710001, 3), (720001, 2), (710900, 5)])
def test_wrong_final_purpose_rejected_before_random_draw(monkeypatch, seed, purpose):
    monkeypatch.setattr(final, 'uniform', lambda *args: pytest.fail('Unapproved random draw'))
    with pytest.raises(ValueError):
        final.generate_data(PARAMETERS, 'A', seed, purpose)


def test_final_generation_requires_actual_gate_before_random_draw(monkeypatch):
    def blocked(*args, **kwargs):
        raise RuntimeError('Missing actual authorization')
    monkeypatch.setattr(pool_program, 'check_gate', blocked)
    monkeypatch.setattr(pool_program, 'uniform', lambda *args: pytest.fail('Premature random draw'))
    with pytest.raises(RuntimeError, match='authorization'):
        pool_program.generate_data(PARAMETERS, 'A', 730001, 2)


def test_exact_registered_matrix():
    rows = pool_program.case_matrix()
    assert len(rows) == 60
    assert [(r['phase'], r['world'], r['seed'], r['purpose']) for r in rows] == [
        *[('development', w, s, 2) for w in 'ABC' for s in range(730001,730011)],
        *[('formal', w, s, 3) for w in 'ABC' for s in range(740001,740011)],
    ]


def test_manifest_tampering_is_rejected(tmp_path):
    p = tmp_path / 'evidence.txt'
    p.write_text('original')
    files = {'evidence.txt': final.sha(p)}
    final.verify_files(files, tmp_path)
    p.write_text('modified')
    with pytest.raises(RuntimeError, match='fingerprint'):
        final.verify_files(files, tmp_path)


def test_incomplete_recovery_preserves_original_attempt(tmp_path, monkeypatch):
    monkeypatch.setattr(final, 'ROOT', tmp_path)
    case = {'phase': 'development', 'world': 'A', 'seed': 710001, 'purpose': 2, 'case_id': 'development-A-710001'}
    base = tmp_path / 'evidence'
    directory = base / 'development' / case['case_id']
    directory.mkdir(parents=True)
    (directory / 'partial.txt').write_text('interrupted evidence')
    archive = final.retain_incomplete(directory, case, base)
    assert not directory.exists()
    assert (archive / 'case/partial.txt').read_text() == 'interrupted evidence'
    assert json.loads((archive / 'reason.json').read_text())['case']['seed'] == 710001


def test_changed_sealed_case_cannot_be_recovered_as_interruption(tmp_path):
    (tmp_path / 'COMPLETE').write_text('sealed')
    with pytest.raises(RuntimeError, match='Sealed case changed'):
        final.retain_incomplete(tmp_path, {}, tmp_path)


def test_independent_extra_environment_metadata_is_compatible():
    metadata = {**final.environment(), 'machine': 'arm64', 'executable': '/locked/python'}
    metadata.pop('numerical_threads')
    assert final.initial_environment_matches(metadata)


def test_required_environment_version_mismatch_is_rejected():
    assert not final.initial_environment_matches({**final.environment(), 'numpy': 'different'})
