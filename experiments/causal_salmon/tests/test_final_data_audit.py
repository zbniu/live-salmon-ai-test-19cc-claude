"""Tolerance, missing-value and public/private projection checks."""
import pytest
from scripts.pairwise_audit import compare_value, assert_public_projection


def test_relative_numeric_tolerance():
    compare_value(100., 100.0000005, 'estimate')
    with pytest.raises(AssertionError):
        compare_value(100., 100.000002, 'estimate')


def test_missing_estimate_is_not_silently_compared_as_zero():
    with pytest.raises(AssertionError):
        compare_value(None, 0., 'estimate')


def test_discrete_decisions_are_exact():
    with pytest.raises(AssertionError):
        compare_value(True, False, 'GEN')


def test_public_projection_must_match_observed_potential_outcome():
    public = b'x,y,z\n1,60,11\n0,60,10\n'
    hidden = {'y': [60.,60.], 'z0': [10.,10.], 'z1': [11.,11.]}
    assert_public_projection(public, hidden, expected_n=2)
    with pytest.raises(AssertionError):
        assert_public_projection(public.replace(b'1,60,11',b'1,60,10'), hidden, expected_n=2)
