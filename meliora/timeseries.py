"""Residual and time-series tests. See docs/reference for inference contracts."""
import warnings

import numpy as np
import pandas as pd
from scipy import stats

from ._inference import (aligned, choice, design, integer, lagged, lm_rows,
                         optional, residuals, result, tail, time_index, vector)


def _portmanteau(x, lags, model_df, alpha, box):
    x = vector(x, temporal=True)
    n = len(x)
    integer(model_df, "model_df")
    lags = list(range(1, integer(lags, "lags", 1, n-1)+1)) if np.isscalar(lags) else list(lags)
    if not lags or len(set(lags)) != len(lags):
        raise ValueError("lags must be nonempty and unique")
    for lag in lags:
        integer(lag, "lag", 1, n-1)
    x -= x.mean()
    acf = np.array([x[j:] @ x[:-j] / (x @ x) for j in range(1, max(lags)+1)])
    terms = n * acf**2 if box else n * (n+2) * acf**2 / (n-np.arange(1, max(lags)+1))
    return pd.concat([result("Box-Pierce" if box else "Ljung-Box", terms[:h].sum(),
                            stats.chi2.sf(terms[:h].sum(), h-model_df) if h > model_df else np.nan,
                            n, df=h-model_df, lag=h, model_df=model_df, alpha=alpha,
                            reference_distribution="chi-square") for h in lags], ignore_index=True)


def ljung_box_test(x, lags=10, *, model_df=0, alpha=0.05):
    """Joint autocorrelation test; integer lags requests every lag through lags."""
    return _portmanteau(x, lags, model_df, alpha, False)


def box_pierce_test(x, lags=10, *, model_df=0, alpha=0.05):
    """Box-Pierce joint autocorrelation test with model-df adjustment."""
    return _portmanteau(x, lags, model_df, alpha, True)


def breusch_godfrey_test(y, x, lags=1, *, alpha=0.05):
    """OLS regression serial-correlation LM/F tests; initial lag residuals are zero."""
    aligned(y, x)
    time_index(x)
    y = vector(y, temporal=True)
    x = design(x, len(y))
    h = integer(lags, "lags", 1, len(y)-x.shape[1]-1)
    e = residuals(y, x)
    z = np.column_stack([x, lagged(np.r_[np.zeros(h), e], h)])
    design(z, len(y))
    return lm_rows("Breusch-Godfrey", e, z, h, alpha, lag=h, padding="zero")


def arch_lm_test(resid, lags=1, *, center=False, model_df=0, alpha=0.05):
    """ARCH LM/F using squared residuals after dropping the first lags rows."""
    e = vector(resid, temporal=True)
    h = integer(lags, "lags", 1, (len(e)-2)//2)
    integer(model_df, "model_df", 0, len(e)-h-1)
    if not isinstance(center, (bool, np.bool_)):
        raise ValueError("center must be boolean")
    if center:
        e -= e.mean()
    squared = e**2
    z = np.column_stack([np.ones(len(e)-h), lagged(squared, h)])
    design(z, len(z))
    return lm_rows("ARCH", squared[h:], z, h, alpha, scale=len(z)-model_df,
                   lag=h, center=center, model_df=model_df)


def breusch_pagan_test(resid, variance_design, *, variant="koenker", alpha=0.05):
    """Classical normal-error BP or studentised Koenker variance test."""
    aligned(resid, variance_design)
    e = vector(resid)
    x = design(variance_design, len(e))
    choice(variant, ("classical", "koenker"), "variant")
    q = x.shape[1]-1
    if q < 1:
        raise ValueError("variance design needs a nonconstant regressor")
    out = lm_rows("Breusch-Pagan", e**2, x, q, alpha, variant=variant)
    if variant == "classical":
        y = e**2 / np.mean(e**2)
        fitted = x @ np.linalg.lstsq(x, y, rcond=None)[0]
        lm = np.sum((fitted-y.mean())**2)/2
        out.loc[0, ["statistic", "pvalue", "reject"]] = [lm, stats.chi2.sf(lm, q), stats.chi2.sf(lm, q) < alpha]
    return out


def jarque_bera_test(x, *, alpha=0.05):
    """Asymptotic normality test using biased central moments (divisor n)."""
    x = vector(x)
    s, k = stats.skew(x, bias=True), stats.kurtosis(x, fisher=False, bias=True)
    jb = len(x)/6 * (s*s + (k-3)**2/4)
    return result("Jarque-Bera", jb, stats.chi2.sf(jb, 2), len(x), df=2,
                  skewness=s, kurtosis=k, reference_distribution="chi-square", alpha=alpha)


def adf_test(x, *, maxlag=None, regression="c", autolag="AIC", alpha=0.05):
    """ADF with MacKinnon unit-root calibration and explicit lag selection."""
    x = vector(x, minimum=5, temporal=True)
    choice(regression, ("n", "c", "ct", "ctt"), "regression")
    choice(autolag, (None, "AIC", "BIC", "t-stat"), "autolag")
    if maxlag is not None:
        integer(maxlag, "maxlag", 0)
    r = optional("statsmodels.tsa.stattools").adfuller(x, maxlag=maxlag, regression=regression, autolag=autolag)
    return result("ADF", r[0], r[1], r[3], lag=r[2], maxlag=maxlag,
                  deterministic=regression, autolag=autolag, critical_values=r[4],
                  reference_distribution="MacKinnon unit-root", alternative="stationary", alpha=alpha)


def kpss_test(x, *, regression="c", bandwidth="auto", alpha=0.05):
    """KPSS stationarity test; p-values outside the reference table remain bounds."""
    x = vector(x, minimum=5, temporal=True)
    choice(regression, ("c", "ct"), "regression")
    if bandwidth not in ("auto", "legacy"):
        integer(bandwidth, "bandwidth", 0, len(x)-1)
    sm = optional("statsmodels.tsa.stattools")
    iw = optional("statsmodels.tools.sm_exceptions").InterpolationWarning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", iw)
        r = sm.kpss(x, regression=regression, nlags=bandwidth)
    bounds = {"pvalue_upper": r[1]} if r[1] == .01 else {"pvalue_lower": r[1]} if r[1] == .1 else {}
    return result("KPSS", r[0], r[1], len(x), bandwidth=r[2], deterministic=regression,
                  critical_values=r[3], reference_distribution="KPSS table",
                  alternative="nonstationary", alpha=alpha, **bounds)


def reset_test(y, x, *, powers=(2, 3), covariance="nonrobust", alpha=0.05):
    """RESET adds powers of OLS fitted values; classical F or HC3 Wald chi-square."""
    aligned(y, x)
    y = vector(y)
    x = design(x, len(y))
    powers = tuple(powers)
    if not powers or len(set(powers)) != len(powers):
        raise ValueError("powers must be nonempty and unique")
    for power in powers:
        integer(power, "power", 2)
    choice(covariance, ("nonrobust", "HC3"), "covariance")
    e = residuals(y, x)
    fitted = y-e
    if np.ptp(fitted) <= np.finfo(float).eps * max(1., abs(fitted).max()):
        raise ValueError("RESET needs varying fitted values")
    fitted = (fitted-fitted.mean())/fitted.std()
    z = np.column_stack([x, *[fitted**p for p in powers]])
    design(z, len(y))
    u = residuals(y, z)
    q, d = len(powers), len(y)-z.shape[1]
    if covariance == "nonrobust":
        statistic = max(0., (e@e-u@u))/q/(u@u/d)
        p, ref, method = stats.f.sf(statistic, q, d), "F", "F"
    else:
        inv = np.linalg.pinv(z)
        h = np.sum(z*inv.T, axis=1)
        if np.any(h >= 1-1e-12):
            raise ValueError("HC3 undefined at unit leverage")
        cov = (inv*(u/(1-h))**2) @ inv.T
        b = inv@y
        v = cov[-q:, -q:]
        if np.linalg.cond(v) > 1e12:
            raise ValueError("ill-conditioned covariance")
        statistic = b[-q:] @ np.linalg.solve(v, b[-q:])
        p, ref, method = stats.chi2.sf(statistic, q), "chi-square", "Wald"
    return result("RESET", statistic, p, len(y), df=q, df_denom=d,
                  powers=powers, covariance=covariance, augmentation="fitted values",
                  method=method, reference_distribution=ref, alpha=alpha)


def durbin_watson_test(y, x, *, alternative="two-sided", simulations=9999,
                       seed=0, lagged_dependent=False, alpha=0.05):
    """Design-conditional Gaussian Monte Carlo inference for OLS Durbin-Watson."""
    aligned(y, x)
    time_index(x)
    y = vector(y, temporal=True)
    x = design(x, len(y))
    if lagged_dependent:
        raise ValueError("Durbin-Watson inference excludes lagged dependent regressors")
    choice(alternative, ("two-sided", "less", "greater"), "alternative")
    integer(simulations, "simulations", 99)
    integer(seed, "seed")
    e = residuals(y, x)
    observed = np.diff(e) @ np.diff(e)/(e@e)
    rng = np.random.default_rng(seed)
    q = np.linalg.qr(x, mode="reduced")[0]
    low = high = 0
    for start in range(0, simulations, 256):
        errors = rng.normal(size=(len(y), min(256, simulations-start)))
        errors -= q @ (q.T @ errors)
        simulated = np.sum(np.diff(errors, axis=0)**2, axis=0)/np.sum(errors**2, axis=0)
        low += np.count_nonzero(simulated <= observed)
        high += np.count_nonzero(simulated >= observed)
    # Alternatives refer to error autocorrelation, hence reversed DW tails.
    p = min(1., 2*(min(low, high)+1)/(simulations+1)) if alternative == "two-sided" else ((low if alternative == "greater" else high)+1)/(simulations+1)
    return result("Durbin-Watson", observed, p, len(y), alternative=alternative,
                  method="conditional Monte Carlo", reference_distribution="Gaussian fixed-design null",
                  simulations=simulations, seed=seed, alpha=alpha)


def bds_test(x, *, max_dim=2, epsilon=None, distance=1.5, residuals=False, alpha=0.05):
    """BDS iid test for observed data only; fitted-residual calibration is unsupported."""
    x = vector(x, minimum=5, temporal=True)
    integer(max_dim, "max_dim", 2, len(x)-2)
    if residuals:
        raise ValueError("estimated residuals require model-specific bootstrap calibration")
    if epsilon is None:
        epsilon = distance*np.std(x, ddof=1)
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be positive")
    with np.errstate(divide="ignore", invalid="ignore"):
        s, p = optional("statsmodels.tsa.stattools").bds(x, max_dim=max_dim, epsilon=epsilon)
    return pd.concat([result("BDS", a, b if np.isfinite(a) else np.nan, len(x)-d+1, dimension=d, epsilon=epsilon,
                             reference_distribution="normal", alpha=alpha)
                      for d, a, b in zip(range(2, max_dim+1), np.atleast_1d(s), np.atleast_1d(p))], ignore_index=True)


def white_test(resid, variance_design, *, alpha=0.05):
    """White LM/F with all squares/interactions and rank-based auxiliary degrees of freedom."""
    aligned(resid, variance_design)
    e = vector(resid)
    x = design(variance_design, len(e))
    z = np.column_stack([x[:, i]*x[:, j] for i in range(x.shape[1]) for j in range(i, x.shape[1])])
    u, s, _ = np.linalg.svd(z, full_matrices=False)
    rank = np.linalg.matrix_rank(z)
    if rank <= 1 or rank >= len(e):
        raise ValueError("quadratic design requires positive model and residual degrees of freedom")
    return lm_rows("White", e**2, u[:, :rank], rank-1, alpha, design_rank=rank)


def shapiro_wilk_test(x, *, alpha=0.05):
    """Shapiro-Wilk; p-value unavailable beyond the validated n<=5000 range."""
    x = vector(x)
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=".*N > 5000.*", category=UserWarning)
        s, p = stats.shapiro(x)
    return result("Shapiro-Wilk", s, p if len(x) <= 5000 else np.nan, len(x),
                  method="fitted-normal calibration", reference_distribution="Shapiro-Wilk",
                  ties=len(np.unique(x)) < len(x), alpha=alpha)


def anderson_darling_normal_test(x, *, alpha=0.05):
    """Anderson-Darling fitted-normal test, estimating mean and sample variance."""
    x = vector(x, minimum=8)
    s, p = optional("statsmodels.stats.diagnostic").normal_ad(x)
    return result("Anderson-Darling normal", s, p, len(x),
                  method="Stephens fitted-normal", reference_distribution="fitted-normal AD", alpha=alpha)


def phillips_perron_test(x, *, bandwidth=None, regression="c", statistic="tau", alpha=0.05):
    """Phillips-Perron tau/rho unit-root test with Bartlett long-run variance."""
    x = vector(x, minimum=6, temporal=True)
    choice(regression, ("n", "c", "ct"), "regression")
    choice(statistic, ("tau", "rho"), "statistic")
    if bandwidth is not None:
        integer(bandwidth, "bandwidth", 0, len(x)-2)
    else:
        bandwidth = min(len(x)-2, int(np.ceil(12*(len(x)/100)**.25)))
    r = optional("arch.unitroot").PhillipsPerron(x, lags=bandwidth, trend=regression, test_type=statistic)
    return result("Phillips-Perron", r.stat, r.pvalue, r.nobs, bandwidth=r.lags,
                  deterministic=regression, statistic_type=statistic, critical_values=r.critical_values,
                  reference_distribution="MacKinnon unit-root", alternative="stationary", alpha=alpha)
