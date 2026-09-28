"""Distributional and paired categorical hypothesis tests."""
import warnings
import inspect

import numpy as np
from scipy import special, stats

from ._inference import aligned, array, choice, integer, result, vector


def _counts(table, square=False):
    x = array(table, "table", ndim=2)
    if min(x.shape) < 2 or (square and x.shape[0] != x.shape[1]):
        raise ValueError("table must have at least two rows and columns and be square when paired")
    if np.any(x < 0) or np.any(x != np.floor(x)) or x.sum() == 0:
        raise ValueError("counts must be nonnegative integers with positive total")
    return x


def wilcoxon_signed_rank_test(x, y=None, *, zero_method="wilcox", alternative="two-sided",
                              method="auto", correction=False, alpha=0.05):
    """Test symmetric paired differences; exact inference requires no ties or zeroes."""
    a = vector(x, minimum=1, varying=False)
    if y is not None:
        aligned(x, y)
        a -= vector(y, minimum=1, varying=False)
    choice(zero_method, ("wilcox", "pratt", "zsplit"), "zero_method")
    choice(alternative, ("two-sided", "less", "greater"), "alternative")
    choice(method, ("auto", "exact", "approx"), "method")
    if not np.any(a):
        return result("Wilcoxon signed-rank", np.nan, np.nan, len(a), status="undefined", alpha=alpha)
    ties = len(np.unique(abs(a[a != 0]))) < np.count_nonzero(a)
    exact_ok = not ties and not np.any(a == 0)
    selected = ("exact" if exact_ok and len(a) <= 50 else "approx") if method == "auto" else method
    if selected == "exact" and not exact_ok:
        raise ValueError("exact signed-rank requires no ties or zero differences")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Sample size too small.*", category=UserWarning)
        r = stats.wilcoxon(a, zero_method=zero_method, alternative=alternative, method=selected, correction=correction)
    effective = int(np.count_nonzero(a)) if zero_method == 'wilcox' else len(a)
    return result("Wilcoxon signed-rank", r.statistic, r.pvalue, effective, total_pairs=len(a), alternative=alternative,
                  method=selected, zero_method=zero_method, correction=correction, ties=ties,
                  reference_distribution="signed-rank" if selected == "exact" else "normal", alpha=alpha)


def fisher_exact_test(table, *, alternative="two-sided", alpha=0.05):
    """Conditional 2x2 Fisher test with probability-ordered two-sided inference."""
    x = _counts(table)
    if x.shape != (2, 2):
        raise ValueError("Fisher requires a 2x2 table")
    choice(alternative, ("two-sided", "less", "greater"), "alternative")
    s, p = stats.fisher_exact(x.astype(np.int64), alternative=alternative)
    return result("Fisher exact", s, p, int(x.sum()), alternative=alternative,
                  method="exact probability ordering", reference_distribution="conditional hypergeometric",
                  degenerate_margins=bool(np.any(x.sum(axis=0) == 0) or np.any(x.sum(axis=1) == 0)), alpha=alpha)


def g_test(observed, probabilities=None, *, mode="goodness-of-fit", ddof=0, alpha=0.05):
    """Likelihood-ratio G for multinomial goodness of fit or table homogeneity."""
    choice(mode, ("goodness-of-fit", "homogeneity"), "mode")
    integer(ddof, "ddof")
    if mode == "goodness-of-fit":
        x = vector(observed, minimum=2, varying=False)
        if np.any(x < 0) or np.any(x != np.floor(x)) or x.sum() <= 0:
            raise ValueError("counts must be nonnegative integers with positive total")
        if probabilities is None:
            raise ValueError("goodness-of-fit requires specified probabilities")
        p = vector(probabilities, minimum=2, varying=False)
        aligned(x, p)
        if np.any(p <= 0) or not np.isclose(p.sum(), 1, rtol=0, atol=1e-12):
            raise ValueError("probabilities must be positive and sum to one")
        expected = x.sum()*p
        df = len(x)-1-ddof
    else:
        if probabilities is not None or ddof != 0:
            raise ValueError("homogeneity derives expectations and degrees of freedom from the table")
        x = _counts(observed)
        if np.any(x.sum(axis=0) == 0) or np.any(x.sum(axis=1) == 0):
            raise ValueError("remove structurally empty margins explicitly")
        expected = np.outer(x.sum(axis=1), x.sum(axis=0))/x.sum()
        df = (x.shape[0]-1)*(x.shape[1]-1)
    if df <= 0:
        raise ValueError("degrees of freedom must be positive")
    s = 2*np.sum(special.xlogy(x, x/expected))
    sparse = bool(np.any(expected < 5))
    return result("G-test", max(0., s), stats.chi2.sf(max(0., s), df) if not sparse else np.nan,
                  int(x.sum()), df=df, mode=mode, expected_counts=expected.tolist(), sparse=sparse,
                  status="sparse-asymptotic-unreliable" if sparse else "ok",
                  reference_distribution="chi-square", alpha=alpha)


def mcnemar_test(table, *, exact=True, correction=True, alpha=0.05):
    """Binary paired marginal homogeneity; exact two-sided binomial or corrected chi-square."""
    x = _counts(table, square=True)
    if x.shape != (2, 2):
        raise ValueError("McNemar requires a 2x2 paired table")
    b, c = x[0, 1], x[1, 0]
    if exact:
        s = min(b, c)
        p = stats.binomtest(int(s), int(b+c), .5).pvalue if b+c else 1.
    else:
        s = max(0., abs(b-c)-int(correction))**2/(b+c) if b+c else 0.
        p = stats.chi2.sf(s, 1) if b+c else np.nan
    return result("McNemar", s, p, int(x.sum()), df=1,
                  method="exact" if exact else "asymptotic", correction=correction if not exact else False,
                  reference_distribution="binomial" if exact else "chi-square", alpha=alpha)


def stuart_maxwell_test(table, *, alpha=0.05):
    """Paired multicategory marginal homogeneity using effective covariance rank."""
    x = _counts(table, square=True)
    difference = x.sum(axis=1)-x.sum(axis=0)
    cov = -(x+x.T)
    np.fill_diagonal(cov, x.sum(axis=1)+x.sum(axis=0)-2*x.diagonal())
    eigenvalues, u = np.linalg.eigh(cov)
    keep = eigenvalues > max(1., eigenvalues.max())*1e-12
    rank = int(keep.sum())
    s = np.sum((u[:, keep].T@difference)**2/eigenvalues[keep]) if rank else 0.
    return result("Stuart-Maxwell", s, stats.chi2.sf(s, rank) if rank else np.nan,
                  int(x.sum()), df=rank, covariance_rank=rank,
                  reference_distribution="chi-square", alpha=alpha)


def anderson_darling_ksample_test(samples, *, midrank=True, method="asymptotic",
                                 permutations=9999, seed=0, alpha=0.05):
    """AD equality of independent distributions, with midrank ties or right-side EDF."""
    if len(samples) < 2:
        raise ValueError("at least two samples required")
    data = [vector(s, minimum=2, varying=False) for s in samples]
    if np.ptp(np.concatenate(data)) == 0:
        raise ValueError("pooled sample must contain distinct observations")
    choice(method, ("asymptotic", "permutation"), "method")
    integer(permutations, "permutations", 1)
    integer(seed, "seed")
    # SciPy 1.17 replaces midrank with variant and removes critical_values;
    # own permutation loop also supports SciPy 1.11 (before method= existed).
    kwargs = ({'variant': 'midrank' if midrank else 'right'}
              if 'variant' in inspect.signature(stats.anderson_ksamp).parameters else {'midrank': midrank})
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="p-value (capped|floored).*", category=UserWarning)
        r = stats.anderson_ksamp(data, **kwargs)
        pvalue = r.pvalue
        if method == 'permutation':
            rng = np.random.default_rng(seed)
            pooled = np.concatenate(data)
            cuts = np.cumsum([len(s) for s in data])[:-1]
            exceed = 0
            for _ in range(permutations):
                permuted = np.split(rng.permutation(pooled), cuts)
                exceed += stats.anderson_ksamp(permuted, **kwargs).statistic >= r.statistic-1e-12
            pvalue = (exceed+1)/(permutations+1)
    bounds = {}
    if method == "asymptotic":
        if r.pvalue == .001:
            bounds['pvalue_upper'] = .001
        elif r.pvalue == .25:
            bounds['pvalue_lower'] = .25
    return result("Anderson-Darling k-sample", r.statistic, pvalue, sum(map(len, data)),
                  method=method, midrank=midrank, seed=seed if method == "permutation" else None,
                  permutations=permutations if method == "permutation" else None,
                  critical_values=dict(zip([.25, .1, .05, .025, .01, .005, .001], getattr(r, 'critical_values', []))),
                  reference_distribution="permutation" if method == "permutation" else "Scholz-Stephens table",
                  alpha=alpha, **bounds)
