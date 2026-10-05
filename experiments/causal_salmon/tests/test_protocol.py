import hashlib
import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def candidates():
    return json.loads((ROOT / 'configs/calibration_candidates.json').read_text())['candidates']


def test_raw_uniform_extremes_and_exact_midpoint():
    from src.data.generator import uniform_from_raw
    r = np.array([0, 2**64 - 1, 2**63], dtype=np.uint64)
    assert np.array_equal(uniform_from_raw(r), [2**-53, 1 - 2**-53, .5 + 2**-53])


def test_ties_use_distinct_keys_then_row_order():
    from src.data.generator import ranked
    assert ranked(np.array([2., 2., 2., 1.]), np.array([.1, .3, .3, .9])).tolist() == [1, 2, 0, 3]


@pytest.mark.parametrize('candidate', candidates(), ids=lambda p: p['id'])
@pytest.mark.parametrize('world', ['A', 'B', 'C'])
def test_selftest_streams_counts_precision_and_individual_truth(candidate, world):
    from src.data.generator import generate, csv_bytes, parse_csv, check_hidden
    for seed in range(709000, 709010):
        first = generate(candidate, world, seed, 4)
        second = generate(candidate, world, seed, 4)
        a = csv_bytes(first['x'], first['y'], first['z'])
        assert a == csv_bytes(second['x'], second['y'], second['z'])
        assert a.startswith(b'x,y,z\n') and a.endswith(b'\n') and b'\r' not in a
        x, y, z = parse_csv(a)
        assert np.array_equal(y.view(np.uint64), first['y'].view(np.uint64))
        assert np.array_equal(z.view(np.uint64), first['z'].view(np.uint64))
        assert x.sum() == candidate['K']
        if world != 'A':
            assert first['applicant'].sum() == candidate['M']
        assert all(check_hidden(first, candidate).values())
        assert hashlib.sha256(a).digest() == hashlib.sha256(csv_bytes(second['x'], y, z)).digest()


def test_exam_and_reserve_seeds_rejected_before_confirmation():
    from src.data.generator import generate
    for seed, purpose in [(710001, 2), (720001, 3), (704000, 1), (709000, 1)]:
        with pytest.raises(ValueError):
            generate(candidates()[0], 'A', seed, purpose)


def test_mean_difference_and_sample_variance_hand_array():
    from src.calibration.statistics import mean_difference
    r = mean_difference(np.array([1, 1, 0, 0]), np.array([2., 4., 0., 2.]))
    assert r['E'] == 2
    assert r['se'] == pytest.approx(np.sqrt(2))


def test_ols_standardization_and_hc3_hand_fixture():
    from src.calibration.statistics import adjusted_ols
    t = np.array([-2., -1., 0., 0., 1., 2.])
    residual = np.array([1., -1., 0., 0., -1., 1.])
    x = np.repeat([0, 1], 6)
    y = np.tile(t + 60, 2)
    z = np.concatenate([10 + .25 * t + residual, 12 + .275 * t + residual])
    result = adjusted_ols(x, y, z)
    expected_variance = 2 * (2 / Fraction(13, 30)**2 + 2 / Fraction(11, 15)**2) / 36
    assert result['status'] == 'ok'
    assert result['E'] == pytest.approx(2, abs=1e-12)
    assert result['se'] == pytest.approx(np.sqrt(float(expected_variance)), abs=1e-12)


def test_rank_deficiency_is_explicit():
    from src.calibration.statistics import adjusted_ols
    r = adjusted_ols(np.repeat([0, 1], 5), np.ones(10), np.arange(10.))
    assert r['status'] == 'unavailable' and r['E'] is None


def test_bins_rank_boundaries_are_not_interpolated():
    from src.calibration.statistics import bin_counts, segmented_difference
    x = np.r_[np.ones(10, dtype=int), np.zeros(6, dtype=int)]
    y = np.r_[np.arange(10.), [-1, 0, 2, 4, 8, 10]]
    bins = bin_counts(x, y)
    assert bins['edges'] == [0, 2, 4, 6, 8, 9]
    assert bins['treated'] == [2, 2, 2, 2, 2]
    assert bins['control'] == [1, 1, 1, 0, 1]
    assert segmented_difference(x, y, np.arange(16.))['status'] == 'unavailable'


def test_sigmoid_is_finite_at_extreme_arguments():
    from src.calibration.statistics import sigmoid
    with np.errstate(over='raise'):
        p = sigmoid(np.array([-1000., 0., 1000.]))
    assert np.array_equal(p, [0, .5, 1])


def test_materials_replacement_public_rules_and_report_extraction():
    from src.data.materials import templates, anonymize, description, identify_assignment
    from src.evaluation.extract import extract_report
    named, anonymous, prompt = templates()
    for world in 'ABC':
        assert anonymize(named[world]) == anonymous[world]
        for version in ['named', 'anonymized']:
            prose = description(world, version, 900, 600)
            assert '{{' not in prose
            assert identify_assignment(prose) == {'A':'random_difference','B':'standardized_ols','C':'insufficient_information'}[world]
    r = extract_report('```text\n## Final report\n```\r\n## Final report\r\nBody\r\n### More\r\nContent\r\n## End\r\n')
    assert r['status'] == 'ok' and r['report'] == 'Body\r\n### More\r\nContent\r\n'
    assert extract_report('## Final report\nA\n## Final report\nB')['reason'] == 'heading_count>1'
    assert extract_report('    ## Final report\nA')['reason'] == 'heading_count=0'
    assert extract_report('## Final report\n   ')['reason'] == 'empty_report'


def test_metric_bias_is_signed_and_closed_interval_boundaries():
    from src.calibration.statistics import with_interval
    from src.calibration.summary import metrics
    assert with_interval({'status':'ok','E':1.,'se':.5,'reason':None}, 1.98)['covered']
    m = metrics([{'status':'ok','E':0.,'se':1.,'ci':[-1.96,1.96],'covered':True},
                 {'status':'ok','E':2.,'se':1.,'ci':[.04,3.96],'covered':True}], np.array([1., 1.]), np.array([2., 3.]))
    assert m['bias'] == 0 and m['relative_bias'] == 0
