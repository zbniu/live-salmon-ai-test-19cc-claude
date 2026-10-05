import copy
import numpy as np
import pytest

from scripts import generate_data as screened
from scripts import data_pipeline as original


def pool():
    return [{**case, 'primary': {'status': 'ok'},
             'D1': {'status': 'ok' if case['world'] == 'B' else 'not_applicable'},
             'D2': {'status': 'ok' if case['world'] == 'B' else 'not_applicable'},
             'GEN': {'GEN-1': {'applicable': True, 'passed': True}}}
            for case in screened.case_matrix()]


def test_registered_pool_and_original_seed_disjointness():
    rows = screened.case_matrix()
    assert len(rows) == 60
    assert len({(r['phase'], r['world'], r['seed']) for r in rows}) == 60
    assert {r['seed'] for r in rows}.isdisjoint({710001, 720001, 720002, 720003})
    assert rows[0]['case_id'] == 'development-A-730001'
    assert rows[-1]['case_id'] == 'formal-C-740010'


def test_selection_uses_lowest_qualifying_seeds_and_retains_pool():
    rows = pool()
    rows[0]['GEN']['GEN-1']['passed'] = False
    before = copy.deepcopy(rows)
    selected, counts = screened.select_cases(list(reversed(rows)))
    assert len(selected) == 12 and selected[0]['seed'] == 730002
    assert [r['seed'] for r in selected if r['phase'] == 'formal' and r['world'] == 'A'] == [740001, 740002, 740003]
    assert rows == before and counts['development/A'] == 9


def test_insufficient_pool_cannot_add_seeds():
    rows = pool()
    for r in rows:
        if r['world'] == 'A' and r['phase'] == 'formal' and r['seed'] < 740009:
            r['GEN']['GEN-1']['passed'] = False
    with pytest.raises(screened.PoolExhausted):
        screened.select_cases(rows)


def test_missing_or_duplicate_candidate_rejected():
    rows = pool()
    with pytest.raises(ValueError): screened.select_cases(rows[:-1])
    with pytest.raises(ValueError): screened.select_cases(rows[:-1] + [rows[0]])


def test_numerical_failure_stops_selection():
    rows = pool()
    rows[15]['D2']['status'] = 'failed'
    with pytest.raises(RuntimeError): screened.select_cases(rows)


@pytest.mark.parametrize('world', list('ABC'))
@pytest.mark.parametrize('seed', [709000, 709001, 709009])
def test_generation_arithmetic_matches_frozen_main(world, seed):
    p = {'id': 'K1', **original.PARAMETERS}
    a = original.generate_data(p, world, seed, 4)
    b = screened.generate_data(p, world, seed, 4)
    assert a.keys() == b.keys()
    for key in a:
        if isinstance(a[key], np.ndarray):
            assert a[key].dtype == b[key].dtype
            assert a[key].tobytes() == b[key].tobytes()
        else: assert a[key] == b[key]


def test_old_final_seed_and_unknown_new_seed_rejected():
    p = {'id': 'K1', **original.PARAMETERS}
    for seed, purpose in [(720001, 3), (730011, 2), (740001, 2)]:
        with pytest.raises(ValueError): screened.generate_data(p, 'A', seed, purpose)


def test_candidate_draw_requires_both_initial_registrations(monkeypatch):
    # Isolate the registration check from historical public display copies.
    # This is a test fixture only; production evidence checks remain unchanged.
    registered_load = screened.load
    def fixture_load(path):
        record = registered_load(path)
        if path == 'manifests/offline_framework.json':
            record['files'] = {name: original.sha(screened.ROOT / name)
                               for name in record['files']}
        return record
    monkeypatch.setattr(screened, 'load', fixture_load)
    monkeypatch.setattr(screened, 'INITIALS', ('manifests/missing_initial.json', 'manifests/generation_independent_initial.json'))
    monkeypatch.setattr(screened, 'uniform', lambda *args: pytest.fail('Draw before both registrations'))
    with pytest.raises(RuntimeError, match='selftests required'):
        screened.generate_data({'id': 'K1', **original.PARAMETERS}, 'A', 730001, 2)


def test_redacted_display_copies_cannot_replace_original_evidence():
    redactions = screened.load('manifests/path_redaction.json')['files']
    name, record = next(iter(redactions.items()))
    assert original.sha(screened.ROOT / name) == record['public_copy_sha256']
    assert record['public_copy_sha256'] != record['original_sha256']
    with pytest.raises(RuntimeError, match='Evidence/code fingerprint differs'):
        original.verify_files({name: record['original_sha256']})
