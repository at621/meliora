"""Structural stability, right-censored survival and cointegration tests."""
import warnings

import numpy as np
import pandas as pd
from scipy import stats

from ._inference import (aligned, array, choice, design, integer, optional,
                         residuals, result, significance, time_index, vector)


def cusum_test(resid, *, model_df=0, alpha=0.05):
    """OLS residual CUSUM with Brownian-bridge supremum reference distribution."""
    e = vector(resid, temporal=True)
    integer(model_df, "model_df", 0, len(e)-1)
    scale = np.sqrt(e@e*len(e)/(len(e)-model_df))
    s = np.max(np.abs(np.cumsum(e)))/scale
    return result("OLS CUSUM", s, stats.kstwobign.sf(s), len(e), model_df=model_df,
                  reference_distribution="sup absolute Brownian bridge", alpha=alpha)


def _regression(y, x):
    aligned(y, x)
    time_index(x)
    y = vector(y, temporal=True)
    return y, design(x, len(y))


def _chow(y, x, breakpoint):
    n, k = x.shape
    integer(breakpoint, "breakpoint", k+1, n-k-1)
    design(x[:breakpoint], breakpoint)
    design(x[breakpoint:], n-breakpoint)
    pooled = residuals(y, x)
    first = residuals(y[:breakpoint], x[:breakpoint])
    second = residuals(y[breakpoint:], x[breakpoint:])
    sse = first@first+second@second
    return max(0., pooled@pooled-sse)/k/(sse/(n-2*k))


def chow_test(y, x, breakpoint, *, alpha=0.05):
    """Classical fixed-break F test, breakpoint is the first row of the second segment."""
    y, x = _regression(y, x)
    s = _chow(y, x, breakpoint)
    n, k = x.shape
    return result("Chow", s, stats.f.sf(s, k, n-2*k), n, df=k, df_denom=n-2*k,
                  breakpoint=breakpoint, method="classical F", reference_distribution="F", alpha=alpha)


def sup_f_test(y, x, *, trim=0.15, min_segment=None, simulations=999, seed=0, alpha=0.05):
    """Sup-F search with fixed-design Gaussian null simulation of the entire search."""
    alpha = significance(alpha)
    y, x = _regression(y, x)
    n, k = x.shape
    if not np.isscalar(trim) or not np.isfinite(trim) or not 0 < trim < .5:
        raise ValueError("trim must be between zero and one half")
    minimum = max(k+1, int(np.ceil(n*trim)))
    if min_segment is not None:
        minimum = max(minimum, integer(min_segment, "min_segment", k+1))
    if 2*minimum > n:
        raise ValueError("no admissible breakpoints")
    integer(simulations, "simulations", 99)
    integer(seed, "seed")
    candidates = np.arange(minimum, n-minimum+1)
    # Validate every segment before starting simulation, never silently skip dates.
    values = np.array([_chow(y, x, int(b)) for b in candidates])
    observed = values.max()
    rng = np.random.default_rng(seed)
    # Projection matrices are independent of y and shared across simulations.
    q = np.linalg.qr(x, mode='reduced')[0]
    segments = [(np.linalg.qr(x[:b], mode='reduced')[0], np.linalg.qr(x[b:], mode='reduced')[0]) for b in candidates]
    exceed = 0
    simulated_maxima = []
    for start in range(0, simulations, 128):
        z = rng.normal(size=(n, min(128, simulations-start)))
        pooled = np.sum((z-q@(q.T@z))**2, axis=0)
        maxima = np.zeros(z.shape[1])
        for b, (qa, qb) in zip(candidates, segments):
            sse = np.sum((z[:b]-qa@(qa.T@z[:b]))**2, axis=0)+np.sum((z[b:]-qb@(qb.T@z[b:]))**2, axis=0)
            maxima = np.maximum(maxima, (pooled-sse)/k/(sse/(n-2*k)))
        exceed += np.count_nonzero(maxima >= observed)
        simulated_maxima.extend(maxima)
    p = (exceed+1)/(simulations+1)
    return result("Sup-F", observed, p, n, df=k, df_denom=n-2*k,
                  breakpoint=int(candidates[values.argmax()]), trim=trim, min_segment=minimum,
                  search_start=int(candidates[0]), search_end=int(candidates[-1]),
                  critical_values={str(alpha): float(np.quantile(simulated_maxima, 1-alpha))},
                  simulations=simulations, seed=seed, method="search-adjusted Monte Carlo",
                  reference_distribution="Gaussian fixed-design supremum F", alpha=alpha)


def logrank_test(durations, events, groups, *, alpha=0.05):
    """Multigroup log-rank for independent right censoring; events must be 0/1."""
    aligned(durations, events, groups)
    t = vector(durations, minimum=2, varying=False)
    e = vector(events, minimum=2, varying=False)
    g = np.asarray(groups)
    if g.ndim != 1 or pd.isna(g).any() or np.any(t < 0) or not np.isin(e, [0, 1]).all():
        raise ValueError("nonnegative durations, binary events and complete groups required; competing events are unsupported")
    labels, code = np.unique(g, return_inverse=True)
    k = len(labels)
    if k < 2:
        raise ValueError("at least two groups required")
    difference = np.zeros(k)
    cov = np.zeros((k, k))
    for time in np.unique(t[e == 1]):
        risk = np.bincount(code[t >= time], minlength=k)
        deaths = np.bincount(code[(t == time) & (e == 1)], minlength=k)
        n, d = risk.sum(), deaths.sum()
        p = risk/n
        difference += deaths-d*p
        if n > 1:
            cov += d*(n-d)/(n-1)*(np.diag(p)-np.outer(p, p))
    rank = np.linalg.matrix_rank(cov)
    s = difference@np.linalg.pinv(cov)@difference if rank else 0.
    return result("Log-rank", s, stats.chi2.sf(s, rank) if rank else np.nan,
                  len(t), df=rank, groups=labels.tolist(), observed_minus_expected=difference.tolist(),
                  covariance=cov.tolist(), reference_distribution="chi-square", alpha=alpha)


def engle_granger_test(y, x, *, regression="c", maxlag=None, autolag="aic", alpha=0.05):
    """Engle-Granger two-step inference with cointegration-specific MacKinnon calibration."""
    aligned(y, x)
    time_index(x)
    y = vector(y, minimum=8, temporal=True)
    x = np.asarray(x)
    x = vector(x, minimum=8)[:, None] if x.ndim == 1 else array(x, "x", ndim=2)
    if np.linalg.matrix_rank(x) != x.shape[1] or np.any(np.ptp(x, axis=0) == 0):
        raise ValueError("singular or constant cointegration regressors")
    choice(regression, ("n", "c", "ct", "ctt"), "regression")
    choice(autolag, (None, "aic", "bic", "t-stat"), "autolag")
    if maxlag is not None:
        integer(maxlag, "maxlag")
    sm = optional("statsmodels.tsa.stattools")
    z = x if regression == "n" else optional("statsmodels.tsa.tsatools").add_trend(x, trend=regression)
    z = design(z, len(y), constant=regression != "n")
    e = residuals(y, z)
    adf = sm.adfuller(e, maxlag=maxlag, autolag=autolag, regression="n")
    warning = optional("statsmodels.tools.sm_exceptions").CollinearityWarning
    with warnings.catch_warnings():
        warnings.simplefilter("error", warning)
        try:
            s, p, cv = sm.coint(y, x, trend=regression, maxlag=maxlag, autolag=autolag)
        except warning as exc:
            raise ValueError("near-perfect cointegration regression") from exc
    return result("Engle-Granger", s, p, adf[3], lag=adf[2], deterministic=regression,
                  maxlag=maxlag, autolag=autolag, critical_values=dict(zip(["1%", "5%", "10%"], cv)),
                  alternative="cointegrated", reference_distribution="MacKinnon cointegration", alpha=alpha)


def johansen_test(series, *, det_order=0, k_ar_diff=1, alpha=0.05):
    """Johansen trace/max-eigenvalue rank hypotheses; critical values only, no p-values."""
    time_index(series)
    x = array(series, "series", ndim=2)
    n, k = x.shape
    if not 2 <= k <= 12 or np.linalg.matrix_rank(x-x.mean(axis=0)) < k:
        raise ValueError("Johansen requires 2..12 noncollinear varying series")
    integer(det_order, "det_order", -1, 1)
    integer(k_ar_diff, "k_ar_diff", 0)
    if n-k_ar_diff-1 <= k*(k_ar_diff+1)+2:
        raise ValueError("insufficient observations for Johansen lag specification")
    if alpha not in (.1, .05, .01):
        raise ValueError("Johansen critical values support alpha .1, .05 or .01")
    r = optional("statsmodels.tsa.vector_ar.vecm").coint_johansen(x, det_order, k_ar_diff)
    rows = []
    for method, statistics, critical in [("trace", r.lr1, r.cvt), ("max-eigenvalue", r.lr2, r.cvm)]:
        for rank in range(k):
            cv = dict(zip([.1, .05, .01], critical[rank]))
            row = result("Johansen", statistics[rank], np.nan, n-k_ar_diff-1,
                         method=method, rank=rank, deterministic=det_order, lag=k_ar_diff,
                         critical_values=cv, status="critical-values-only",
                         alternative=f"rank > {rank}" if method == "trace" else f"rank = {rank+1}",
                         reference_distribution="Johansen rank table", alpha=alpha)
            row.loc[0, 'reject'] = bool(statistics[rank] > cv[alpha])
            rows.append(row)
    return pd.concat(rows, ignore_index=True)
