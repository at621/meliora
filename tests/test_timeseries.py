"""Formula checks independent of the implementation's optional backends."""
import numpy as np
import pandas as pd
import pytest
from scipy import stats

from meliora import timeseries as t


def sample():
    rng = np.random.default_rng(812)
    x = np.column_stack([np.ones(80), np.linspace(-1, 1, 80)])
    y = x @ [1, 2] + rng.normal(size=80)
    return y, x


def test_portmanteau_hand_calculation():
    # Centred values [-2,-1,0,1,2], denominator 10, lag-one product 4.
    lb = t.ljung_box_test([1, 2, 3, 4, 5], [1, 2], model_df=1)
    assert lb.statistic[0] == pytest.approx(5*7*.4**2/4)
    assert pd.isna(lb.reject[0])
    assert lb.df.tolist() == [0, 1]
    assert t.box_pierce_test([1, 2, 3, 4, 5], [1]).statistic[0] == pytest.approx(.8)


def test_jb_hand_moments():
    r = t.jarque_bera_test([-2, -1, 0, 1, 2]).iloc[0]
    assert r.skewness == 0
    assert r["kurtosis"] == pytest.approx(1.7)
    assert r.statistic == pytest.approx(5/24*1.3**2)


def test_auxiliary_regressions():
    y, x = sample()
    e = y-x@np.linalg.solve(x.T@x, x.T@y)
    z = np.column_stack([x, np.r_[0, e[:-1]]])
    u = e-z@np.linalg.solve(z.T@z, z.T@e)
    expected = len(y)*(1-u@u/(e@e))
    assert t.breusch_godfrey_test(y, x).statistic[0] == pytest.approx(expected)
    squared = e**2
    z = np.column_stack([np.ones(79), squared[:-1]])
    target = squared[1:]
    u = target-z@np.linalg.solve(z.T@z, z.T@target)
    r2 = 1-u@u/np.sum((target-target.mean())**2)
    arch = t.arch_lm_test(e, model_df=2)
    assert arch.statistic[0] == pytest.approx(77*r2)
    assert arch.nobs[0] == 79
    for variant in ['classical', 'koenker']:
        r = t.breusch_pagan_test(e, x, variant=variant)
        target = squared/squared.mean()
        fitted = x@np.linalg.solve(x.T@x, x.T@target)
        ess = np.sum((fitted-target.mean())**2)
        expected = ess/2 if variant == 'classical' else 80*ess/np.sum((target-target.mean())**2)
        assert r.statistic[0] == pytest.approx(expected)


def test_reset_nested_f_and_white_rank():
    y, x = sample()
    e = y-x@np.linalg.lstsq(x, y, rcond=None)[0]
    z = np.column_stack([x, x[:, 1]**2, x[:, 1]**3])
    u = y-z@np.linalg.lstsq(z, y, rcond=None)[0]
    assert t.reset_test(y, x).statistic[0] == pytest.approx((e@e-u@u)/2/(u@u/76))
    assert t.reset_test(y, x, covariance='HC3').method[0] == 'Wald'
    assert t.white_test(e, x).df[0] == 2


def test_adf_manual_regression():
    pytest.importorskip('statsmodels')
    y, _ = sample()
    target = np.diff(y)
    x = np.column_stack([y[:-1], np.ones(79)])
    b = np.linalg.solve(x.T@x, x.T@target)
    e = target-x@b
    se = np.sqrt(e@e/77*np.linalg.inv(x.T@x)[0, 0])
    r = t.adf_test(y, maxlag=0, autolag=None).iloc[0]
    assert r.statistic == pytest.approx(b[0]/se)
    assert r.nobs == 79 and r.lag == 0


def test_kpss_manual_partial_sums():
    pytest.importorskip('statsmodels')
    y, _ = sample()
    e = y-y.mean()
    expected = np.sum(np.cumsum(e)**2)/len(e)**2/np.mean(e**2)
    r = t.kpss_test(y, bandwidth=0).iloc[0]
    assert r.statistic == pytest.approx(expected)
    assert r.status == 'bounded'


@pytest.mark.parametrize('index', [[0, 1, 1, 2, 3], [0, 2, 1, 3, 4], [0, 1, 2, 4, 5], list('abcde')])
def test_bad_time_indexes(index):
    with pytest.raises(ValueError):
        t.ljung_box_test(pd.Series(range(5), index=index), 1)


def test_regular_calendar_and_alignment():
    t.ljung_box_test(pd.Series(range(6), index=pd.date_range('2020-01-01', periods=6, freq='MS')), 1)
    with pytest.raises(ValueError, match='aligned'):
        t.reset_test(pd.Series(range(5)), pd.DataFrame({'c': 1, 'x': range(5)}, index=range(1, 6)))


def test_dw_reproducible_design_inference():
    y, x = sample()
    a = t.durbin_watson_test(y, x, simulations=199)
    pd.testing.assert_frame_equal(a, t.durbin_watson_test(y, x, simulations=199))
    e = y-x@np.linalg.lstsq(x, y, rcond=None)[0]
    assert a.statistic[0] == pytest.approx(np.sum(np.diff(e)**2)/np.sum(e**2))
    assert 0 < a.pvalue[0] <= 1
    with pytest.raises(ValueError, match='lagged'):
        t.durbin_watson_test(y, x, lagged_dependent=True)


def test_normal_ad_statistic():
    pytest.importorskip('statsmodels')
    y, _ = sample()
    cdf = stats.norm.cdf((np.sort(y)-y.mean())/y.std(ddof=1))
    n = len(y)
    expected = -n-np.sum((2*np.arange(1, n+1)-1)*(np.log(cdf)+np.log(1-cdf[::-1])))/n
    assert t.anderson_darling_normal_test(y).statistic[0] == pytest.approx(expected)


def test_shapiro_three_point_exact_statistic():
    assert t.shapiro_wilk_test([-1, 0, 1]).statistic[0] == pytest.approx(1)
    assert pd.isna(t.shapiro_wilk_test(np.arange(5001)).pvalue[0])


@pytest.mark.parametrize('regression', ['n', 'c', 'ct'])
@pytest.mark.parametrize('statistic', ['tau', 'rho'])
def test_pp_independent_regression_and_lrv(regression, statistic):
    pytest.importorskip('arch.unitroot')
    y, _ = sample()
    n = len(y)-1
    x = y[:-1, None]
    if regression != 'n':
        x = np.column_stack([x, np.ones(n)])
    if regression == 'ct':
        x = np.column_stack([x, np.arange(1, n+1)])
    b = np.linalg.solve(x.T@x, x.T@y[1:])
    e = y[1:]-x@b
    gamma0 = e@e/n
    s2 = e@e/(n-x.shape[1])
    se2 = s2*np.linalg.inv(x.T@x)[0,0]
    lrv = gamma0+2*sum((1-j/3)*(e[j:]@e[:-j])/n for j in (1,2))
    expected = (np.sqrt(gamma0/lrv)*(b[0]-1)/np.sqrt(se2)
                -.5*(lrv-gamma0)/np.sqrt(lrv)*n*np.sqrt(se2/s2)) if statistic == 'tau' else n*(b[0]-1)-.5*n*n*se2/s2*(lrv-gamma0)
    r = t.phillips_perron_test(y, bandwidth=2, regression=regression, statistic=statistic).iloc[0]
    assert r.statistic == pytest.approx(expected)
    assert set(r.critical_values) == {'1%', '5%', '10%'}


@pytest.mark.parametrize('function', [t.ljung_box_test, t.arch_lm_test, t.jarque_bera_test, t.adf_test, t.kpss_test, t.shapiro_wilk_test])
def test_constants_rejected(function):
    with pytest.raises(ValueError, match='variance'):
        function(np.ones(30))
