import numpy as np
import pandas as pd
import pytest
from scipy import stats

from meliora import structural as s


def regression():
    x = np.column_stack([np.ones(40), np.linspace(-1, 1, 40)])
    y = x@[1., 2.]+np.random.default_rng(149).normal(size=40)
    return y, x


def test_cusum_hand_scaling():
    r = s.cusum_test([1., 2., -1., -2.], model_df=1).iloc[0]
    assert r.statistic == pytest.approx(3/np.sqrt(40/3))


def test_chow_manual_anova():
    y, x = regression()
    def sse(y, x):
        e = y-x@np.linalg.solve(x.T@x, x.T@y)
        return e@e
    pooled = sse(y, x)
    split = sse(y[:20], x[:20])+sse(y[20:], x[20:])
    expected = (pooled-split)/2/(split/36)
    assert s.chow_test(y, x, 20).statistic[0] == pytest.approx(expected)
    with pytest.raises(ValueError):
        s.chow_test(y, x, 2)


def test_sup_f_search_inference_and_reproducibility():
    y, x = regression()
    a = s.sup_f_test(y, x, simulations=99)
    pd.testing.assert_frame_equal(a, s.sup_f_test(y, x, simulations=99))
    row = a.iloc[0]
    candidates = [s.chow_test(y, x, i).statistic[0] for i in range(6, 35)]
    assert row.statistic == pytest.approx(max(candidates))
    assert 6 <= row.breakpoint <= 34
    assert row.pvalue != pytest.approx(stats.f.sf(row.statistic, 2, 36))


def test_logrank_hand_risk_sets_and_ties():
    # At t=1, risks [2,2], deaths [1,0]: O-E=[.5,-.5], variance=.25.
    # At t=2, risks [1,2], deaths [0,1]: add [-1/3,1/3], variance=2/9.
    r = s.logrank_test([1, 3, 2, 3], [1, 0, 1, 0], ['a', 'a', 'b', 'b']).iloc[0]
    assert r.statistic == pytest.approx((1/6)**2/(.25+2/9))
    r = s.logrank_test([1, 2, 1, 2], [1, 0, 1, 0], ['a', 'a', 'b', 'b']).iloc[0]
    assert r.statistic == 0
    assert pd.isna(s.logrank_test([1, 2], [0, 0], ['a', 'b']).reject[0])
    with pytest.raises(ValueError, match='competing'):
        s.logrank_test([1, 2], [1, 2], ['a', 'b'])


def test_engle_granger_manual_residual_adf():
    pytest.importorskip('statsmodels')
    rng = np.random.default_rng(23)
    x = np.cumsum(rng.normal(size=100))
    y = 2*x+rng.normal(size=100)
    z = np.column_stack([x, np.ones(100)])
    e = y-z@np.linalg.lstsq(z, y, rcond=None)[0]
    b = np.dot(e[:-1], np.diff(e))/np.dot(e[:-1], e[:-1])
    u = np.diff(e)-b*e[:-1]
    expected = b/np.sqrt((u@u)/98/(e[:-1]@e[:-1]))
    r = s.engle_granger_test(y, x, maxlag=0, autolag=None).iloc[0]
    assert r.statistic == pytest.approx(expected)
    assert r.lag == 0 and r.nobs == 99


def test_johansen_eigenvalue_identities():
    pytest.importorskip('statsmodels')
    x = np.cumsum(np.random.default_rng(9).normal(size=(80, 2)), axis=0)
    r = s.johansen_test(x)
    trace = r[r.method == 'trace'].statistic.to_numpy()
    maximum = r[r.method == 'max-eigenvalue'].statistic.to_numpy()
    np.testing.assert_allclose(trace, np.cumsum(maximum[::-1])[::-1])
    assert r.pvalue.isna().all() and not r.reject.isna().any()
