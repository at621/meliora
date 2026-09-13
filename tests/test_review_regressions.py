"""Independent counterexamples from the September 2026 companion reviews."""
import numpy as np
import pandas as pd
import pytest
from scipy import stats

import meliora as m


@pytest.mark.parametrize('dtype', ['int64', 'float64', 'bool', 'boolean', 'str', 'string', 'category', 'mixed'])
def test_information_value_preserves_binary_counts_across_dtypes(dtype):
    outcomes = pd.Series([0, 0, 0, 1, 0, 1, 1, 1])
    y = outcomes.astype(dtype) if dtype != 'mixed' else pd.Series([0, '0', 0, '1', 0, '1', 1, 1])
    data = pd.DataFrame({'bin': ['A']*4 + ['B']*4, 'y': y})
    data.index = [4, 1, 4, 9, 2, 3, 7, 2]
    before = data.copy(deep=True)
    table, value = m.information_value(data, 'bin', 'y')
    np.testing.assert_array_equal(table[['good', 'bad']], [[3, 1], [1, 3]])
    assert table[['good', 'bad']].to_numpy().sum() == len(data)
    assert all(pd.api.types.is_integer_dtype(table[c]) for c in ['good', 'bad'])
    assert value == pytest.approx(0.8*np.log(7/3))
    assert m.information_value(data, 'bin', 'y', smoothing=0)[1] == pytest.approx(np.log(3))
    pd.testing.assert_frame_equal(data, before)


def test_calibration_returns_integer_counts():
    data = pd.DataFrame({'g': ['A']*3, 'p': [0.2]*3, 'y': pd.Series([False, False, True], dtype='boolean')})
    for function in [m.binomial_test, m.jeffreys_test]:
        table = function(data, 'g', 'y', 'p')
        assert pd.api.types.is_integer_dtype(table.Defaults)
        assert table.Defaults.tolist() == [1]


@pytest.mark.parametrize('categorical', [False, True])
def test_psi_explicit_labels_ignore_unobserved_periods(categorical):
    periods = [2019]*4 + ['current']*4
    if categorical:
        periods = pd.Categorical(periods, categories=['future', 'current', 2019], ordered=True)
    data = pd.DataFrame({'period': periods, 'bin': ['A','A','A','B','A','B','B','B']})
    table, value = m.population_stability_index(data, 'period', 'bin', expected=2019, actual='current', smoothing=0)
    np.testing.assert_allclose(table[['expected', 'actual']], [[.75, .25], [.25, .75]])
    assert value == pytest.approx(np.log(3))


def test_psi_requires_direction_unless_period_order_is_declared():
    data = pd.DataFrame({'period': ['old']*4 + ['new']*4, 'bin': ['A','A','A','B','A','B','B','B']})
    with pytest.raises(ValueError, match='Specify expected and actual'):
        m.population_stability_index(data, 'period', 'bin')
    data.period = pd.Categorical(data.period, categories=['unused', 'old', 'new'], ordered=True)
    table, _ = m.population_stability_index(data, 'period', 'bin', smoothing=0)
    np.testing.assert_allclose(table[['expected', 'actual']], [[.75, .25], [.25, .75]])


def test_migration_keeps_initial_population_in_multinomial_variance():
    data = pd.DataFrame({'start': [3]*14, 'end': [1]*10 + [2]*4})
    counts = pd.Series({3: 100, 1: 0, 4: 8, 2: 0})
    original = counts.copy()
    z, p = m.migration_matrix_stability(data, 'start', 'end', rating_order=[1,2,3,4], initial_counts=counts)
    expected_z = (4-10)/np.sqrt(10+4-(4-10)**2/100)
    assert z.loc[3,1] == pytest.approx(expected_z)
    assert p.loc[3,1] == pytest.approx(stats.norm.cdf(expected_z))
    assert p.loc[3,1] > .05
    assert z.loc[4].isna().all()  # All eight initial customers left the performing scale.
    assert m.migration_matrix_stability(data, 'start', 'end', rating_order=[1,2,3,4])[1].loc[3,1] < .05
    pd.testing.assert_series_equal(counts, original)


@pytest.mark.parametrize('counts', [
    [0, 0, 100], {1:0, 2:0}, {1:0, 2:0, 3:13}, {1:0, 2:0, 3:14.5},
    {1:-1, 2:0, 3:100}, {1:0, 2:0, 3:np.inf}, {1:0, 2:0, 3:np.nan},
    {1:0, 2:0, 3:100, 4:0}, pd.Series([0, 0, 100], index=[1,1,3]),
    {1:0, 2:0, 3:100+1j},
])
def test_migration_rejects_invalid_initial_counts(counts):
    data = pd.DataFrame({'start': [3]*14, 'end': [1]*10 + [2]*4})
    with pytest.raises(ValueError, match='initial_counts'):
        m.migration_matrix_stability(data, 'start', 'end', rating_order=[1,2,3], initial_counts=counts)


@pytest.mark.parametrize('table', [
    np.array([[3+8j,1],[1,3]]),
    np.array([['2020-01-01','2020-01-02'],['2020-01-03','2020-01-04']], dtype='datetime64[D]'),
    np.array([[3,1],[1,3]], dtype='timedelta64[D]'),
])
def test_somers_rejects_nonreal_count_tables(table):
    with pytest.raises(ValueError, match='real numeric'):
        m.somersd(table)
