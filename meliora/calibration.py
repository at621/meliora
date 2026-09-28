"""Calibration and paired forecast-comparison extensions."""
import numpy as np
from scipy import optimize, special, stats

from ._inference import aligned, choice, integer, result, tail, vector


def logistic_calibration_lr_test(outcomes, probabilities, *, alpha=0.05, maxiter=1000):
    """Joint LR of intercept=0, slope=1; reject boundary PDs and separated data."""
    aligned(outcomes, probabilities)
    y = vector(outcomes, "outcomes", minimum=4)
    p = vector(probabilities, "probabilities", minimum=4)
    integer(maxiter, "maxiter", 1)
    if not np.isin(y, [0, 1]).all() or np.any((p <= 0) | (p >= 1)):
        raise ValueError("binary outcomes and strictly interior probabilities required")
    z = special.logit(p)
    # With one predictor, disjoint (or just touching) class intervals imply
    # complete (or quasi-complete) separation, including a zero-slope boundary.
    if max(z[y == 0]) <= min(z[y == 1]) or max(z[y == 1]) <= min(z[y == 0]):
        raise ValueError("complete or quasi-complete separation")
    x = np.column_stack([np.ones(len(y)), z])
    if np.linalg.cond(x) > 1e12:
        raise ValueError("ill-conditioned calibration design")
    def objective(b):
        eta = x@b
        return np.sum(np.logaddexp(0, eta)-y*eta)
    def jac(b):
        return x.T@(special.expit(x@b)-y)
    def hess(b):
        mu = special.expit(x@b)
        return (x.T*(mu*(1-mu)))@x
    fitted = optimize.minimize(objective, [0., 1.], jac=jac, hess=hess,
                               method="Newton-CG", options={"maxiter": maxiter, "xtol": 1e-10})
    # Newton-CG can report line-search precision loss at a valid optimum.
    # Verify the convex likelihood's score/information criterion independently
    # instead of interpreting its termination flag as statistical failure.
    information = hess(fitted.x)
    if np.linalg.cond(information) > 1e12:
        raise ValueError("ill-conditioned fitted information matrix")
    score = jac(fitted.x)
    decrement = score @ np.linalg.solve(information, score)
    if not np.isfinite(decrement) or decrement > 1e-12 or np.max(np.abs(score)) > 1e-5:
        return result("Logistic calibration LR", np.nan, np.nan, len(y), df=2,
                      status="nonconvergence", alpha=alpha)
    lr = max(0., 2*(objective(np.array([0., 1.]))-fitted.fun))
    return result("Logistic calibration LR", lr, stats.chi2.sf(lr, 2), len(y), df=2,
                  intercept=fitted.x[0], slope=fitted.x[1], score_norm=float(np.max(np.abs(score))),
                  iterations=fitted.nit, method="likelihood ratio",
                  reference_distribution="chi-square", alpha=alpha)


def poisson_binomial_test(probabilities, count, *, alternative="two-sided", alpha=0.05):
    """Exact convolution; two-sided p sums outcomes no more probable than observed."""
    p = vector(probabilities, "probabilities", minimum=1, varying=False)
    integer(count, "count", 0, len(p))
    choice(alternative, ("two-sided", "less", "greater"), "alternative")
    if np.any((p < 0) | (p > 1)):
        raise ValueError("probabilities must lie in [0,1]")
    pmf = np.array([1.])
    for probability in p:
        pmf = np.convolve(pmf, [1-probability, probability])
    pmf /= pmf.sum()
    value = (pmf[:count+1].sum() if alternative == "less" else pmf[count:].sum()
             if alternative == "greater" else pmf[pmf <= pmf[count]*(1+1e-12)].sum())
    return result("Poisson-binomial", count, min(1., value), len(p), alternative=alternative,
                  method="exact probability ordering", reference_distribution="Poisson-binomial",
                  expected_count=p.sum(), alpha=alpha)


def delong_test(outcomes, scores_a, scores_b, *, alternative="two-sided", alpha=0.05):
    """Paired DeLong; larger scores indicate outcome 1, ties receive half credit."""
    aligned(outcomes, scores_a, scores_b)
    y = vector(outcomes, minimum=4)
    a = vector(scores_a, minimum=4, varying=False)
    b = vector(scores_b, minimum=4, varying=False)
    choice(alternative, ("two-sided", "less", "greater"), "alternative")
    if not np.isin(y, [0, 1]).all() or min(sum(y == 0), sum(y == 1)) < 2:
        raise ValueError("at least two observations in each binary class required")
    pos, neg = [], []
    for s in [a, b]:
        comparison = (s[y == 1, None] > s[y == 0]).astype(float)
        comparison += .5*(s[y == 1, None] == s[y == 0])
        pos.append(comparison.mean(axis=1))
        neg.append(comparison.mean(axis=0))
    auc = np.mean(pos, axis=1)
    cov = np.cov(pos, ddof=1)/sum(y == 1)+np.cov(neg, ddof=1)/sum(y == 0)
    variance = np.array([1., -1.])@cov@np.array([1., -1.])
    z = (auc[0]-auc[1])/np.sqrt(variance) if variance > 1e-15 else np.nan
    return result("Paired DeLong", z, tail(z, alternative), len(y), alternative=alternative,
                  auc_a=auc[0], auc_b=auc[1], difference=auc[0]-auc[1], variance=variance,
                  covariance=cov.tolist(), reference_distribution="normal", alpha=alpha)


def diebold_mariano_test(loss_a, loss_b, *, horizon=1, bandwidth=None,
                         estimator="bartlett", correction=True, alternative="two-sided", alpha=0.05):
    """Mean aligned out-of-sample loss A minus B; optional Harvey-Leybourne-Newbold correction."""
    aligned(loss_a, loss_b)
    a = vector(loss_a, temporal=True, varying=False)
    b = vector(loss_b, temporal=True, varying=False)
    n = len(a)
    integer(horizon, "horizon", 1, n-1)
    bandwidth = horizon-1 if bandwidth is None else integer(bandwidth, "bandwidth", 0, n-1)
    choice(estimator, ("bartlett", "acf"), "estimator")
    choice(alternative, ("two-sided", "less", "greater"), "alternative")
    if not isinstance(correction, (bool, np.bool_)):
        raise ValueError("correction must be boolean")
    d = a-b
    e = d-d.mean()
    lrv = e@e/n
    for j in range(1, bandwidth+1):
        weight = 1-j/(bandwidth+1) if estimator == "bartlett" else 1
        lrv += 2*weight*(e[j:]@e[:-j])/n
    statistic = d.mean()/np.sqrt(lrv/n) if lrv > 0 else np.nan
    if correction:
        statistic *= np.sqrt((n+1-2*horizon+horizon*(horizon-1)/n)/n)
    distribution = stats.t(df=n-1) if correction else stats.norm
    return result("Diebold-Mariano", statistic, tail(statistic, alternative, distribution), n,
                  df=n-1 if correction else np.nan, alternative=alternative, horizon=horizon,
                  bandwidth=bandwidth, estimator=estimator, correction="HLN" if correction else "none",
                  long_run_variance=lrv, mean_difference=d.mean(),
                  reference_distribution="t" if correction else "normal", alpha=alpha)
