import itertools

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from meliora import distributions as d


def test_signed_rank_enumeration():
    # Absolute ranks 1,2,3,4; positive ranks 1+2+4=7, negative rank=3.
    r = d.wilcoxon_signed_rank_test([1, 2, -3, 4], method='exact').iloc[0]
    sums = [sum(i for i, sign in zip(range(1, 5), signs) if sign) for signs in itertools.product([0, 1], repeat=4)]
    assert r.statistic == 3
    assert r.pvalue == 2*sum(s <= 3 for s in sums)/16
    with pytest.raises(ValueError, match='ties'):
        d.wilcoxon_signed_rank_test([1, -1, 2], method='exact')
    assert pd.isna(d.wilcoxon_signed_rank_test([0, 0]).reject[0])


def test_fisher_enumerated_margins():
    # Fixed margins 4/4 and 4/4: probabilities [1,16,36,16,1]/70.
    r = d.fisher_exact_test([[3, 1], [1, 3]]).iloc[0]
    assert r.statistic == 9
    assert r.pvalue == pytest.approx(34/70)
    assert d.fisher_exact_test([[3, 1], [1, 3]], alternative='greater').pvalue[0] == pytest.approx(17/70)
    r = d.fisher_exact_test([[0, 0], [2, 3]]).iloc[0]
    assert r.pvalue == 1 and r.degenerate_margins


def test_g_modes_sparse_and_zero_cells():
    expected = 2*(10*np.log(10/15)+20*np.log(20/15))
    assert d.g_test([10, 20], [.5, .5]).statistic[0] == pytest.approx(expected)
    assert d.g_test([[10, 20], [20, 10]], mode='homogeneity').statistic[0] == pytest.approx(2*expected)
    assert d.g_test([0, 30], [.5, .5]).statistic[0] == pytest.approx(60*np.log(2))
    assert pd.isna(d.g_test([0, 3], [.5, .5]).reject[0])


def test_paired_reduction_singular_and_exact():
    table = [[12, 7], [3, 20]]
    a = d.stuart_maxwell_test(table).iloc[0]
    b = d.mcnemar_test(table, exact=False, correction=False).iloc[0]
    assert a.statistic == pytest.approx(1.6)
    assert a.statistic == pytest.approx(b.statistic)
    assert a.pvalue == pytest.approx(b.pvalue)
    assert d.mcnemar_test(table).pvalue[0] == pytest.approx(2*(1+10+45+120)/1024)
    assert d.stuart_maxwell_test([[12, 7, 0], [3, 20, 0], [0, 0, 4]]).df[0] == 1
    assert pd.isna(d.stuart_maxwell_test([[2, 0], [0, 3]]).reject[0])


def test_ad_ksample_bounds_and_reproducibility():
    samples = [[1, 2, 3, 4], [1, 2, 3, 4]]
    r = d.anderson_darling_ksample_test(samples)
    assert r.pvalue_lower[0] == .25
    assert not r.reject[0]
    a = d.anderson_darling_ksample_test(samples, method='permutation', permutations=99)
    b = d.anderson_darling_ksample_test(samples, method='permutation', permutations=99)
    pd.testing.assert_frame_equal(a, b)
