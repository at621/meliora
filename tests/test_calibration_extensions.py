import itertools

import numpy as np
import pandas as pd
import pytest
from scipy import stats

from meliora import calibration as c


@pytest.mark.parametrize('alternative', ['less', 'greater', 'two-sided'])
def test_poisson_binomial_enumeration_and_binomial_reduction(alternative):
    p = [.1, .4, .8]
    pmf = np.zeros(4)
    for events in itertools.product([0, 1], repeat=3):
        pmf[sum(events)] += np.prod([q if e else 1-q for q, e in zip(p, events)])
    expected = pmf[:2].sum() if alternative == 'less' else pmf[1:].sum() if alternative == 'greater' else pmf[pmf <= pmf[1]*(1+1e-12)].sum()
    assert c.poisson_binomial_test(p, 1, alternative=alternative).pvalue[0] == pytest.approx(expected)
    assert c.poisson_binomial_test([.3]*8, 3, alternative=alternative).pvalue[0] == pytest.approx(stats.binomtest(3, 8, .3, alternative=alternative).pvalue)


def test_boundaries_and_impossible_count():
    assert c.poisson_binomial_test([0, 1], 1).pvalue[0] == 1
    assert c.poisson_binomial_test([0, 1], 0).pvalue[0] == 0


def test_delong_hand_ties():
    # Positive placements A=[.75,1], B=[.5,.5]; negative placements A=[1,.75], B=[1,0].
    r = c.delong_test([1, 1, 0, 0], [1, 2, 0, 1], [1, 1, 0, 2]).iloc[0]
    assert r.auc_a == .875 and r.auc_b == .5
    assert r.variance == pytest.approx(.03125+.25-.125)
    assert r.statistic == pytest.approx(.375/np.sqrt(.15625))
    identical = c.delong_test([1, 1, 0, 0], [1, 2, 0, 1], [1, 2, 0, 1]).iloc[0]
    assert identical.status == 'undefined' and pd.isna(identical.reject)


def test_logistic_grouped_hand_likelihood():
    # Equal 50% observed event rates at two distinct PDs: unrestricted fit is a=b=0.
    r = c.logistic_calibration_lr_test([0, 1, 0, 1], [.2, .2, .8, .8]).iloc[0]
    assert r.statistic == pytest.approx(2*(-4*np.log(2)-2*np.log(.2)-2*np.log(.8)))
    assert r.intercept == pytest.approx(0, abs=1e-6)
    assert r.slope == pytest.approx(0, abs=1e-6)


def test_logistic_separation_and_boundary():
    for p in [[.1, .2, .8, .9], [0, .2, .2, .9]]:
        with pytest.raises(ValueError):
            c.logistic_calibration_lr_test([0, 0, 1, 1], p)


def test_logistic_nonconvergence_remains_unavailable():
    r = c.logistic_calibration_lr_test([0, 1, 0, 1], [.2, .2, .8, .8], maxiter=1).iloc[0]
    assert r.status == 'nonconvergence' and pd.isna(r.reject)


def test_dm_manual_and_identical():
    r = c.diebold_mariano_test([1, 3, 2, 5], [0, 1, 1, 2], bandwidth=0).iloc[0]
    # HLN h=1 converts divisor-n variance to the usual paired-t statistic.
    assert r.statistic == pytest.approx(1.75/(np.std([1, 2, 1, 3], ddof=1)/2))
    r = c.diebold_mariano_test([1, 2, 3], [1, 2, 3]).iloc[0]
    assert r.status == 'undefined' and pd.isna(r.reject)
