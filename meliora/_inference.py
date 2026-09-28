"""Contracts shared by the extension APIs (not the book-aligned API)."""
import importlib

import numpy as np
import pandas as pd
from scipy import stats


def integer(value, name, minimum=0, maximum=None):
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, (int, np.integer)):
        raise ValueError(f"{name} must be an integer")
    if value < minimum or (maximum is not None and value > maximum):
        raise ValueError(f"{name} out of range")
    return int(value)


def choice(value, options, name):
    if value not in options:
        raise ValueError(f"{name} must be one of {options}")
    return value


def array(value, name, ndim=1):
    raw = np.asarray(value)
    if raw.dtype.kind not in "biuf" or raw.ndim != ndim or not raw.size:
        raise ValueError(f"{name} must be a nonempty real numeric {ndim}-dimensional array")
    out = raw.astype(float, copy=True)
    if not np.isfinite(out).all():
        raise ValueError(f"{name} must contain only finite observations")
    return out


def time_index(value):
    if not isinstance(value, (pd.Series, pd.DataFrame)):
        return
    index = value.index
    if not index.is_unique or not index.is_monotonic_increasing or index.hasnans:
        raise ValueError("time index must be unique, increasing and complete")
    if isinstance(index, pd.DatetimeIndex):
        if len(index) >= 3 and pd.infer_freq(index) is None:
            raise ValueError("time index must be regular; use a regular calendar frequency")
    elif isinstance(index, pd.PeriodIndex):
        if len(index) > 1 and not np.all(np.diff(index.asi8) == 1):
            raise ValueError("time index must be regular")
    elif pd.api.types.is_numeric_dtype(index.dtype) or isinstance(index, pd.TimedeltaIndex):
        delta = np.diff(index.to_numpy())
        if len(delta) and not np.all(delta == delta[0]):
            raise ValueError("time index must be equally spaced")
    else:
        raise ValueError("ambiguous time index; provide an ordered numeric or temporal index")


def vector(value, name="observations", minimum=3, temporal=False, varying=True):
    if temporal:
        time_index(value)
    x = array(value, name)
    if len(x) < minimum:
        raise ValueError(f"{name} requires at least {minimum} observations")
    if varying and np.ptp(x) == 0:
        raise ValueError(f"{name} must have positive variance")
    return x


def aligned(*values):
    try:
        lengths = {len(v) for v in values}
    except TypeError as exc:
        raise ValueError("observations must be nonempty vectors or tables") from exc
    if len(lengths) != 1:
        raise ValueError("observations must have equal lengths")
    indexes = [v.index for v in values if isinstance(v, (pd.Series, pd.DataFrame))]
    if indexes and any(not indexes[0].equals(i) for i in indexes[1:]):
        raise ValueError("pandas indexes must be aligned exactly")


def design(value, n, constant=True, full_rank=True):
    x = array(value, "design", ndim=2)
    if x.shape[0] != n or x.shape[1] >= n:
        raise ValueError("design needs matching rows and positive residual degrees of freedom")
    rank = np.linalg.matrix_rank(x)
    if full_rank and (rank != x.shape[1] or np.linalg.cond(x) > 1e12):
        raise ValueError("singular or ill-conditioned design")
    if constant and not any(np.ptp(c) == 0 and c[0] != 0 for c in x.T):
        raise ValueError("design must include an explicit nonzero constant column")
    return x


def residuals(y, x):
    e = y - x @ np.linalg.lstsq(x, y, rcond=None)[0]
    if e @ e <= np.finfo(float).eps * max(y @ y, 1):
        raise ValueError("zero residual variance")
    return e


def significance(alpha):
    if isinstance(alpha, (bool, str, complex)) or not isinstance(alpha, (int, float, np.number)) or not np.isfinite(alpha) or not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between zero and one")
    return float(alpha)


def result(name, statistic, pvalue, nobs, *, df=np.nan, alternative="two-sided",
           method="asymptotic", reference_distribution="", alpha=0.05,
           status="ok", pvalue_lower=None, pvalue_upper=None, **metadata):
    alpha = significance(alpha)
    reject = pd.NA
    if pvalue_lower is not None or pvalue_upper is not None:
        lo = 0 if pvalue_lower is None else pvalue_lower
        hi = 1 if pvalue_upper is None else pvalue_upper
        if hi < alpha:
            reject = True
        elif lo >= alpha:
            reject = False
        status = "bounded" if status == "ok" else status
    elif np.isfinite(pvalue) and status == "ok":
        reject = bool(pvalue < alpha)
    elif status == "ok":
        status = "undefined"
    row = dict(test=name, statistic=statistic, pvalue=pvalue, nobs=nobs, df=df,
               alternative=alternative, method=method, status=status,
               reference_distribution=reference_distribution, alpha=alpha,
               reject=reject, **metadata)
    if pvalue_lower is not None:
        row["pvalue_lower"] = pvalue_lower
    if pvalue_upper is not None:
        row["pvalue_upper"] = pvalue_upper
    frame = pd.DataFrame([row])
    frame["reject"] = frame["reject"].astype("boolean")
    return frame


def optional(module):
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        raise ImportError("This method requires pip install 'meliora[timeseries]'") from exc


def tail(z, alternative, distribution=stats.norm):
    choice(alternative, ("two-sided", "less", "greater"), "alternative")
    return (2 * distribution.sf(abs(z)) if alternative == "two-sided" else
            distribution.cdf(z) if alternative == "less" else distribution.sf(z))


def lagged(x, lag):
    return np.column_stack([x[lag - j:len(x) - j] for j in range(1, lag + 1)])


def lm_rows(name, y, x, q, alpha, scale=None, **metadata):
    e = residuals(y, x)
    sse = e @ e
    tss = np.sum((y - y.mean()) ** 2)
    if tss <= 0:
        raise ValueError("auxiliary response has zero variance")
    r2 = max(0., 1 - sse / tss)
    n, k = x.shape
    lm = (n if scale is None else scale) * r2
    f = (tss - sse) / q / (sse / (n - k))
    return pd.concat([
        result(name, lm, stats.chi2.sf(lm, q), n, df=q, method="LM",
               reference_distribution="chi-square", alpha=alpha, **metadata),
        result(name, f, stats.f.sf(f, q, n-k), n, df=q, df_denom=n-k,
               method="F", reference_distribution="F", alpha=alpha, **metadata),
    ], ignore_index=True)
