"""Statistical tools for credit-risk validation.

Input checks are defined first in this file and called before each calculation.
Arrays are paired by position; caller DataFrames are never mutated. See each
function for its statistical convention.
"""

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy import special, stats
from sklearn.metrics import roc_auc_score, roc_curve

# Input checks
# These helpers validate the data supplied to the statistical functions below.
# They raise clear errors for unsuitable inputs and leave caller-owned data unchanged.


def _validate_vector(values, name: str, *, minimum: int = 1) -> np.ndarray:
    """Return a finite float vector, preserving positional order.

    Parameters
    ----------
    values : array-like
        One-dimensional values convertible to real numbers; Series indices are
        ignored. Missing, infinite, complex, and datetime values are rejected.
    name : str
        Input name used in error messages.
    minimum : int, default 1
        Required number of observations.

    Returns
    -------
    numpy.ndarray
        One-dimensional float array. The input is never modified.

    Raises
    ------
    ValueError
        If conversion, dimensionality, size, or finiteness checks fail.
    """
    try:
        raw = np.asarray(values)
        if raw.dtype.kind in "cMm":
            raise ValueError(f"{name} must contain real numeric values")
        result = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain real numeric values") from exc
    if result.ndim != 1 or result.size < minimum:
        raise ValueError(f"{name} must be a one-dimensional array with at least {minimum} values")
    if not np.isfinite(result).all():
        raise ValueError(f"{name} must contain only finite, non-missing values")
    return result


def _validate_probabilities(values, name: str, *, minimum: int = 1) -> np.ndarray:
    """Validate a real vector of probabilities or bounded LGDs in [0, 1].

    Parameters
    ----------
    values : array-like
        Positionally ordered observations; no missing values are allowed.
    name : str
        Input label for error messages.
    minimum : int, default 1
        Required observation count.

    Returns
    -------
    numpy.ndarray
        Validated float vector, with no input mutation.

    Raises
    ------
    ValueError
        If vector validation fails or a value lies outside [0, 1].
    """
    result = _validate_vector(values, name, minimum=minimum)
    if ((result < 0) | (result > 1)).any():
        raise ValueError(f"{name} must be between 0 and 1")
    return result


def _validate_binary(values, name: str, *, both: bool = False) -> np.ndarray:
    """Validate a binary 0/1 outcome vector, optionally requiring both classes.

    Parameters
    ----------
    values : array-like
        Outcomes, with booleans treated as 0/1.
    name : str
        Input label for errors.
    both : bool, default False
        Require at least one observation of each outcome.

    Returns
    -------
    numpy.ndarray
        Finite float outcome vector, without changing the input.

    Raises
    ------
    ValueError
        If the outcomes are invalid or a required class is absent.
    """
    result = _validate_vector(values, name)
    if not np.isin(result, [0, 1]).all():
        raise ValueError(f"{name} must contain only 0 and 1")
    if both and np.unique(result).size != 2:
        raise ValueError(f"{name} must contain both outcomes 0 and 1")
    return result


def _validate_frame(data, columns: Sequence[str]) -> None:
    """Check a nonempty DataFrame and its required, non-missing columns.

    Parameters
    ----------
    data : pandas.DataFrame
        Caller-owned data; additional columns are permitted and not inspected.
    columns : sequence of str
        Required column labels.

    Returns
    -------
    None
        Validation only; data is not modified.

    Raises
    ------
    TypeError
        If data is not a pandas DataFrame.
    ValueError
        If rows are absent, column labels are duplicated, or required columns
        are absent or contain missing values.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")
    if data.empty or data.columns.has_duplicates:
        raise ValueError("data must be nonempty with unique column labels")
    for column in columns:
        if column not in data.columns:
            raise ValueError(f"Missing column: {column!r}")
        if data[column].isna().any():
            raise ValueError(f"Missing values in {column!r}")


def _validate_level(value: float, name: str = "alpha") -> float:
    """Validate a scalar significance level strictly between zero and one.

    Parameters
    ----------
    value : float
        Significance level, not a confidence level.
    name : str, default 'alpha'
        Input label for errors.

    Returns
    -------
    float
        Validated level.

    Raises
    ------
    ValueError
        If value is non-scalar, non-finite, or outside (0, 1).
    """
    if not np.isscalar(value):
        raise ValueError(f"{name} must be a scalar strictly between 0 and 1")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be strictly between 0 and 1") from exc
    if not 0 < number < 1:
        raise ValueError(f"{name} must be strictly between 0 and 1")
    return number


def _validate_pairs(first, second, *, minimum: int = 2, bounded: bool = False):
    """Validate equal-length vectors paired by position, not by Series index.

    Parameters
    ----------
    first, second : array-like
        Finite one-dimensional inputs.
    minimum : int, default 2
        Minimum length of each array.
    bounded : bool, default False
        Require both arrays to be within [0, 1].

    Returns
    -------
    tuple of numpy.ndarray
        The two validated float vectors, without input mutation.

    Raises
    ------
    ValueError
        If a vector is invalid or lengths differ.
    """
    validate = _validate_probabilities if bounded else _validate_vector
    x = validate(first, "first", minimum=minimum)
    y = validate(second, "second", minimum=minimum)
    if x.size != y.size:
        raise ValueError("Paired arrays must have the same length")
    return x, y


def _rating_order(first, second=None, order=None) -> list:
    """Resolve a complete grade order for ordinal comparisons.

    Parameters
    ----------
    first, second : pandas.Series
        Non-missing grade labels. Second may be None for one sample.
    order : sequence, optional
        Unique labels from lowest to highest grade; must include every observed
        value. Unobserved grades may be retained. Otherwise ordered categorical
        metadata is used when consistent, then natural sorting.

    Returns
    -------
    list
        Complete ordered grade universe; inputs remain unchanged.

    Raises
    ------
    ValueError
        If labels cannot be sorted, category orders disagree, or an explicit
        order is incomplete, empty, duplicated, or contains missing labels.
    """
    series = [first] if second is None else [first, second]
    observed = list(pd.unique(pd.concat(series, ignore_index=True)))
    if order is None:
        categories = [
            list(s.cat.categories)
            for s in series
            if isinstance(s.dtype, pd.CategoricalDtype) and s.cat.ordered
        ]
        if categories:
            if any(c != categories[0] for c in categories[1:]):
                raise ValueError("Ordered categorical grade universes must agree")
            order = categories[0]
        else:
            try:
                order = sorted(observed)
            except TypeError as exc:
                raise ValueError("Supply an explicit rating_order for mixed grade labels") from exc
    labels = pd.Index(list(order))
    if (
        len(labels) == 0
        or labels.has_duplicates
        or labels.isna().any()
        or not pd.Index(observed).isin(labels).all()
    ):
        raise ValueError("rating_order must be unique, non-missing, and contain all observed grades")
    return labels.tolist()


def _validate_smoothing(value: float) -> float:
    """Validate a finite nonnegative additive pseudo-count.

    Parameters
    ----------
    value : float
        Count added symmetrically to contingency-table cells.

    Returns
    -------
    float
        Nonnegative scalar, including zero for unsmoothed calculations.

    Raises
    ------
    ValueError
        If value is not a finite, nonnegative scalar.
    """
    if not np.isscalar(value):
        raise ValueError("smoothing must be a finite nonnegative scalar")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("smoothing must be a finite nonnegative scalar") from exc
    if not np.isfinite(number) or number < 0:
        raise ValueError("smoothing must be a finite nonnegative scalar")
    return number


# Statistical methods and calculation helpers


def _calibration(data, ratings, default_flag, predicted_pd):
    """Validate observation data and construct per-grade calibration counts.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty observation data, without missing required values.
    ratings, default_flag, predicted_pd : str
        Grade, binary outcome, and probability column names.

    Returns
    -------
    pandas.DataFrame
        Rating class, Predicted PD, Total count, Defaults, Actual Default Rate.
        Only observed grades are included, in first-observed order.

    Raises
    ------
    TypeError
        If data is not a DataFrame.
    ValueError
        If columns, binary outcomes, or probabilities are invalid.
    """
    _validate_frame(data, [ratings, default_flag, predicted_pd])
    y = _validate_binary(data[default_flag], default_flag)
    p = _validate_probabilities(data[predicted_pd], predicted_pd)
    clean = pd.DataFrame({"grade": data[ratings].to_numpy(), "y": y, "p": p})
    result = clean.groupby("grade", observed=True, sort=False).agg(
        **{
            "Predicted PD": ("p", "mean"),
            "Total count": ("y", "size"),
            "Defaults": ("y", "sum"),
            "Actual Default Rate": ("y", "mean"),
        }
    )
    return result.rename_axis("Rating class").reset_index()


def binomial_test(data, ratings, default_flag, predicted_pd, alpha_level=0.05):
    """Test for underestimated default probability in each grade.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    ratings : str
        Name of the non-missing rating-grade column. Calibration grouping uses observed
        grades only.
    default_flag : str
        Binary 0/1 outcome column name; booleans are accepted.
    predicted_pd : str
        Finite predicted probability column name, values in [0, 1].
    alpha_level : float, default 0.05
        Tail threshold strictly between 0 and 1. Reject for a strictly smaller documented
        tail probability.

    Returns
    -------
    pandas.DataFrame
        One row per observed grade: Rating class, Predicted PD (mean), Total count, Defaults, Actual Default Rate, p_value, Reject H0 (boolean).

    Raises
    ------
    ValueError
        Invalid columns, binary outcomes, probabilities, or significance level.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    p_value = P[Binomial(N, mean predicted PD) >= D]. The alternative is underestimated
    default probability; reject when p_value < alpha_level. Requires independent obligors
    with a common PD per grade. Averaging heterogeneous PDs is an approximation, not a
    Poisson-binomial test. Grade-wise decisions are unadjusted for multiplicity.

    References
    ----------
    https://www.bis.org/publ/bcbs_wp14.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'grade': ['A'] * 4 + ['B'] * 4, 'outcome': [0, 0, 1, 1] * 2, 'pd': [.2] * 4 + [.6] * 4})
    >>> result = m.binomial_test(data, 'grade', 'outcome', 'pd')
    >>> assert np.allclose(result.p_value, [.1808, .8208])
    >>> assert result['Reject H0'].tolist() == [False, False]
    """
    alpha = _validate_level(alpha_level)
    result = _calibration(data, ratings, default_flag, predicted_pd)
    result["p_value"] = stats.binom.sf(result["Defaults"] - 1, result["Total count"], result["Predicted PD"])
    result["Reject H0"] = result["p_value"] < alpha
    return result


def brier_score(data, ratings, default_flag, predicted_pd):
    """Calculate the observation-level mean squared probability error.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    ratings : str
        Grade column name, validated for compatibility. The statistic uses individual
        observations without grade aggregation.
    default_flag : str
        Binary 0/1 outcome column name; booleans are accepted.
    predicted_pd : str
        Finite predicted probability column name, values in [0, 1].

    Returns
    -------
    float
        Mean squared error in [0, 1]; lower is better.

    Raises
    ------
    ValueError
        Invalid columns, nonbinary outcomes, or PDs outside [0, 1].
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    Brier = mean((outcome - predicted PD)**2) over individual observations. Grades are
    validated but do not alter weighting; ratings is retained for compatibility. This proper
    scoring rule measures calibration and discrimination, depends on prevalence, and has no
    null hypothesis or p-value.

    References
    ----------
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'grade': ['A'] * 4 + ['B'] * 4, 'outcome': [0, 0, 1, 1] * 2, 'pd': [.2] * 4 + [.6] * 4})
    >>> result = m.brier_score(data, 'grade', 'outcome', 'pd')
    >>> assert np.isclose(result, .30)
    """
    _validate_frame(data, [ratings, default_flag, predicted_pd])
    y = _validate_binary(data[default_flag], default_flag)
    p = _validate_probabilities(data[predicted_pd], predicted_pd)
    return float(np.mean((y - p) ** 2))


def _concentration(counts):
    """Calculate concentration for validated nonnegative grade counts.

    Parameters
    ----------
    counts : array-like
        Nonnegative counts on a fixed grade universe, with positive total.
        Callers validate counts and retain any explicitly supplied empty grades.

    Returns
    -------
    tuple of float
        Coefficient of variation and classic Herfindahl index (sum of shares
        squared). The input is not changed.
    """
    shares = np.asarray(counts, dtype=float) / np.sum(counts)
    return float(np.sqrt(len(shares) * np.sum((shares - 1 / len(shares)) ** 2))), float(shares @ shares)


def herfindahl_test(data1, ratings, *, rating_order=None):
    """Measure concentration of one portfolio across rating grades.

    Parameters
    ----------
    data1 : pandas.DataFrame
        Nonempty initial/single-period portfolio with a non-missing grade column; not
        modified.
    ratings : str
        Name of the non-missing rating-grade column. Calibration grouping uses observed
        grades only.
    rating_order : sequence, optional
        Unique complete grade labels from lowest to highest; unobserved grades are retained.
        Otherwise use consistent ordered categorical metadata, then naturally sort the
        observed union. Specify business order explicitly.

    Returns
    -------
    tuple of float
        (coefficient_of_variation, classic_Herfindahl_index).

    Raises
    ------
    ValueError
        Missing grades or invalid/incomplete rating order.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    For K grades and shares s, CV=sqrt(K*sum((s-1/K)**2)); HHI=sum(s**2), ranging from 1/K
    to 1. Larger means more concentration. This classic HHI differs from the logarithmic ECB
    transformation. No p-value or alpha parameter applies. Empty grades in rating_order
    affect K and CV.

    References
    ----------
    https://www.bankingsupervision.europa.eu/activities/internal_models/shared/pdf/instructions_validation_reporting_credit_risk.en.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'grade': ['A'] * 4 + ['B'] * 2})
    >>> result = m.herfindahl_test(data, 'grade')
    >>> assert np.allclose(result, [1 / 3, 5 / 9])
    """
    _validate_frame(data1, [ratings])
    labels = _rating_order(data1[ratings], order=rating_order)
    return _concentration(data1[ratings].value_counts().reindex(labels, fill_value=0))


def herfindahl_multiple_period_test(data1, data2, ratings, alpha_level=0.05, *, rating_order=None):
    """Test whether grade concentration increased using the ECB CV statistic.

    Parameters
    ----------
    data1 : pandas.DataFrame
        Nonempty initial/single-period portfolio with a non-missing grade column; not
        modified.
    data2 : pandas.DataFrame
        Nonempty current portfolio. Its size may differ from data1; not modified.
    ratings : str
        Name of the non-missing rating-grade column. Calibration grouping uses observed
        grades only.
    alpha_level : float, default 0.05
        Tail threshold strictly between 0 and 1. Reject for a strictly smaller documented
        tail probability.
    rating_order : sequence, optional
        Unique complete grade labels from lowest to highest; unobserved grades are retained.
        Otherwise use consistent ordered categorical metadata, then naturally sort the
        observed union. Specify business order explicitly.

    Returns
    -------
    pandas.DataFrame
        Grade-indexed N_initial and N_current. Summary row total also contains h_initial, h_current, z_stat, p_value and nullable-boolean reject; other statistic cells are missing.

    Raises
    ------
    ValueError
        Invalid data/order/alpha, fewer than two grades, uniform current shares, or reserved
        grade label 'total'.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    Use the union of grades, retaining zero counts, or rating_order. For initial/current CVs
    c1/c2, z=sqrt(K-1)*(c2-c1)/sqrt(c2**2*(0.5+c2**2)); p_value=normal.sf(z). Reject
    increased concentration when p_value < alpha_level. This is the ECB asymptotic CV
    comparison; HHI columns use classic squared shares. It is undefined for zero current CV
    and is not a paired-account test.

    Non-rejection is not reassurance: some benchmarks make rejection impossible.
    For K=7 and initial CV=0.615681, the minimum possible p-value is about 0.191.
    The tail is not monotone in current concentration and ignores obligor sample size.

    References
    ----------
    https://www.bankingsupervision.europa.eu/activities/internal_models/shared/pdf/instructions_validation_reporting_credit_risk.en.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> initial = pd.DataFrame({'grade': ['A'] * 4 + ['B'] * 2})
    >>> current = pd.DataFrame({'grade': ['A'] * 5 + ['B']})
    >>> result = m.herfindahl_multiple_period_test(initial, current, 'grade')
    >>> assert np.isclose(result.loc['total', 'z_stat'], 3 / np.sqrt(34))
    >>> assert np.isclose(result.loc['total', 'h_current'], 26 / 36)
    """
    alpha = _validate_level(alpha_level)
    _validate_frame(data1, [ratings])
    _validate_frame(data2, [ratings])
    labels = _rating_order(data1[ratings], data2[ratings], rating_order)
    if "total" in labels:
        raise ValueError("The grade label 'total' is reserved for the summary row")
    n1 = data1[ratings].value_counts().reindex(labels, fill_value=0)
    n2 = data2[ratings].value_counts().reindex(labels, fill_value=0)
    c1, h1 = _concentration(n1)
    c2, h2 = _concentration(n2)
    if len(labels) < 2 or c2 == 0:
        raise ValueError(
            "The ECB concentration statistic requires at least two grades and nonzero current CV"
        )
    z = np.sqrt(len(labels) - 1) * (c2 - c1) / np.sqrt(c2**2 * (0.5 + c2**2))
    result = pd.DataFrame({"N_initial": n1, "N_current": n2})
    result.loc["total"] = [n1.sum(), n2.sum()]
    result["h_initial"] = np.nan
    result["h_current"] = np.nan
    result["z_stat"] = np.nan
    result["p_value"] = np.nan
    result["reject"] = pd.Series(pd.NA, index=result.index, dtype="boolean")
    result.loc["total", ["h_initial", "h_current", "z_stat", "p_value"]] = [h1, h2, z, stats.norm.sf(z)]
    result.loc["total", "reject"] = stats.norm.sf(z) < alpha
    return result


def hosmer_test(data, ratings, default_flag, predicted_pd, alpha_level=0.05, *, ddof=0):
    """Apply a grouped chi-square calibration test to grade-level default counts.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    ratings : str
        Name of the non-missing rating-grade column. Calibration grouping uses observed
        grades only.
    default_flag : str
        Binary 0/1 outcome column name; booleans are accepted.
    predicted_pd : str
        Finite predicted probability column name, values in [0, 1].
    alpha_level : float, default 0.05
        Tail threshold strictly between 0 and 1. Reject for a strictly smaller documented
        tail probability.
    ddof : int, default 0
        Degrees of freedom deducted from observed grade count K; 0 <= ddof < K. Zero tests
        fixed external PDs; 2 selects fitted-logistic Hosmer-Lemeshow inference.

    Returns
    -------
    list
        [p_value, reject], with boolean rejection.

    Raises
    ------
    ValueError
        Invalid data/alpha, boundary grade mean PDs, or noninteger ddof outside 0 <= ddof <
        K.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    Q=sum((D-N*p)**2/(N*p*(1-p))); p_value=chi2.sf(Q,K-ddof). Default ddof=0 tests fixed
    externally specified grade PDs with K degrees of freedom. Explicit ddof=2 selects the
    conventional fitted-logistic Hosmer-Lemeshow approximation with appropriate grouping.
    Requires independent outcomes, homogeneous grade PDs and sufficiently large expected
    default/nondefault counts. Reject any departure when p_value < alpha_level.

    References
    ----------
    https://www.bis.org/publ/bcbs_wp14.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'grade': ['A'] * 4 + ['B'] * 4, 'outcome': [0, 0, 1, 1] * 2, 'pd': [.2] * 4 + [.6] * 4})
    >>> result = m.hosmer_test(data, 'grade', 'outcome', 'pd')
    >>> assert np.isclose(result[0], np.exp(-(2.25 + 1 / 6) / 2))
    >>> assert result[1] is False
    """
    alpha = _validate_level(alpha_level)
    result = _calibration(data, ratings, default_flag, predicted_pd)
    k = len(result)
    if isinstance(ddof, (bool, np.bool_)) or not isinstance(ddof, (int, np.integer)) or not 0 <= ddof < k:
        raise ValueError("ddof must be an integer from 0 to the number of observed grades minus 1")
    p, n, d = (result[c].to_numpy() for c in ["Predicted PD", "Total count", "Defaults"])
    if ((p == 0) | (p == 1)).any():
        raise ValueError("Each grade must have a predicted PD strictly between 0 and 1")
    statistic = np.sum((d - n * p) ** 2 / (n * p * (1 - p)))
    p_value = float(stats.chi2.sf(statistic, k - ddof))
    return [p_value, p_value < alpha]


def spiegelhalter_test(data, ratings, default_flag, predicted_pd, alpha_level=0.05):
    """Test probability calibration with the observation-level Spiegelhalter z statistic.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    ratings : str
        Grade column name, validated for compatibility. The statistic uses individual
        observations without grade aggregation.
    default_flag : str
        Binary 0/1 outcome column name; booleans are accepted.
    predicted_pd : str
        Finite predicted probability column name, values in [0, 1].
    alpha_level : float, default 0.05
        Tail threshold strictly between 0 and 1. Reject for a strictly smaller documented
        tail probability.

    Returns
    -------
    tuple
        (z_statistic, reject), with two-sided boolean rejection.

    Raises
    ------
    ValueError
        Invalid data/alpha or zero null variance.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    z=sum((y-p)*(1-2*p))/sqrt(sum(p*(1-p)*(1-2*p)**2)), using individual observations. Under
    independent Bernoulli outcomes with correct fixed PDs the statistic is approximately
    normal. Reject when 2*normal.sf(abs(z)) < alpha_level. Calibration errors can cancel.
    PDs of 0, 0.5 or 1 contribute zero null variance; entirely zero variance makes inference
    undefined.

    References
    ----------
    https://doi.org/10.1002/sim.4780050506

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'grade': ['A'] * 4 + ['B'] * 4, 'outcome': [0, 0, 1, 1] * 2, 'pd': [.2] * 4 + [.6] * 4})
    >>> result = m.spiegelhalter_test(data, 'grade', 'outcome', 'pd')
    >>> assert np.isclose(result[0], .8 / np.sqrt(.2688))
    >>> assert result[1] is False
    """
    alpha = _validate_level(alpha_level)
    _validate_frame(data, [ratings, default_flag, predicted_pd])
    y = _validate_binary(data[default_flag], default_flag)
    p = _validate_probabilities(data[predicted_pd], predicted_pd)
    variance = np.sum(p * (1 - p) * (1 - 2 * p) ** 2)
    if variance <= 0:
        raise ValueError("Spiegelhalter statistic is undefined when its null variance is zero")
    z = float(np.sum((y - p) * (1 - 2 * p)) / np.sqrt(variance))
    return z, bool(2 * stats.norm.sf(abs(z)) < alpha)


def jeffreys_test(data, ratings, default_flag, predicted_pd, alpha_level=0.05):
    """Calculate a Jeffreys-posterior lower-tail probability for each rating grade.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    ratings : str
        Name of the non-missing rating-grade column. Calibration grouping uses observed
        grades only.
    default_flag : str
        Binary 0/1 outcome column name; booleans are accepted.
    predicted_pd : str
        Finite predicted probability column name, values in [0, 1].
    alpha_level : float, default 0.05
        Tail threshold strictly between 0 and 1. Reject for a strictly smaller documented
        tail probability.

    Returns
    -------
    pandas.DataFrame
        Grade summary columns as in binomial_test, plus posterior lower-tail p_value and boolean Reject H0.

    Raises
    ------
    ValueError
        Invalid columns, outcomes, probabilities, or significance level.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    A Beta(1/2,1/2) prior and D defaults in N independent trials yield Beta(D+1/2,N-D+1/2).
    Return its CDF at mean predicted PD. A small tail indicates predicted PD lies below most
    posterior mass; Reject H0 uses p_value < alpha_level. This is a Bayesian posterior tail, not a
    frequentist p-value. Common grade PDs and independence are assumed; no
    multiplicity adjustment is applied.

    References
    ----------
    https://www.bis.org/publ/bcbs_wp14.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'grade': ['A'] * 4, 'outcome': [0, 0, 1, 1], 'pd': [.5] * 4})
    >>> result = m.jeffreys_test(data, 'grade', 'outcome', 'pd')
    >>> assert np.isclose(result.p_value.iloc[0], .5)
    """
    alpha = _validate_level(alpha_level)
    result = _calibration(data, ratings, default_flag, predicted_pd)
    result["p_value"] = stats.beta.cdf(
        result["Predicted PD"], result["Defaults"] + 0.5, result["Total count"] - result["Defaults"] + 0.5
    )
    result["Reject H0"] = result["p_value"] < alpha
    return result


def _classification(data, target, prediction):
    """Validate data for discrimination metrics requiring both binary classes.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty data; inputs are not changed.
    target, prediction : str
        Binary outcome and finite numeric score columns. Larger scores mean
        greater likelihood of outcome 1; scores need not be probabilities.

    Returns
    -------
    tuple of numpy.ndarray
        Outcome vector and score vector, in row order.

    Raises
    ------
    TypeError
        If data is not a DataFrame.
    ValueError
        If required columns, finite scores, or both binary classes are absent.
    """
    _validate_frame(data, [target, prediction])
    return _validate_binary(data[target], target, both=True), _validate_vector(data[prediction], prediction)


def roc_auc(data, target, prediction):
    """Calculate binary ROC area, assigning half credit to tied scores.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    target : str
        Binary target column name, with both 0 and 1 present.
    prediction : str
        Finite numeric score column name. Larger means outcome 1; scores need not be
        probabilities.

    Returns
    -------
    float
        AUC in [0, 1]; 0.5 means random pairwise ordering.

    Raises
    ------
    ValueError
        Invalid columns, nonfinite scores, nonbinary target or an absent class.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    AUC=P(score of outcome 1 > score of outcome 0)+0.5*P(tie). Larger finite scores must
    mean greater default risk; scores need not be probabilities. Both binary classes are
    required. Uses scikit-learn ROC AUC. This descriptive measure has no p-value and does
    not measure calibration.

    References
    ----------
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'y': [0, 0, 1, 1], 'score': [1, 2, 2, 3]})
    >>> result = m.roc_auc(data, 'y', 'score')
    >>> assert np.isclose(result, .875)
    """
    y, p = _classification(data, target, prediction)
    return float(roc_auc_score(y, p))


def gini(df, target, prediction):
    """Calculate the normalized discrimination Gini as twice ROC AUC minus one.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    target : str
        Binary target column name, with both 0 and 1 present.
    prediction : str
        Finite numeric score column name. Larger means outcome 1; scores need not be
        probabilities.

    Returns
    -------
    float
        Normalized Gini in [-1, 1].

    Raises
    ------
    ValueError
        Invalid classification data; see roc_auc.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    Gini=2*ROC_AUC-1, with higher scores for outcome 1 and half credit for ties. Values 1, 0
    and -1 indicate perfect, random and reverse ordering. Requires both classes and finite
    scores. This is the discrimination Gini, not an income-inequality estimator or a
    calibration significance test.

    References
    ----------
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'y': [0, 0, 1, 1], 'score': [1, 2, 2, 3]})
    >>> result = m.gini(data, 'y', 'score')
    >>> assert np.isclose(result, .75)
    """
    return 2 * roc_auc(df, target, prediction) - 1


def kolmogorov_smirnov_stat(df, target, prediction):
    """Compare score distributions of the two outcome classes using two-sample KS.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    target : str
        Binary target column name, with both 0 and 1 present.
    prediction : str
        Finite numeric score column name. Larger means outcome 1; scores need not be
        probabilities.

    Returns
    -------
    object
        SciPy KstestResult with statistic, pvalue and location/sign metadata.

    Raises
    ------
    ValueError
        Invalid classification columns, scores or classes.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    D is the largest absolute difference between score CDFs conditional on outcome 0 and
    outcome 1. Null: equal score distributions; alternative: two-sided. SciPy ks_2samp
    selects exact/asymptotic inference automatically. It assumes independent samples;
    continuous-distribution p-values are approximate for tied/discrete scores. D measures
    separation irrespective of score direction, not PD calibration.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ks_2samp.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'y': [0, 0, 1, 1], 'score': [1, 2, 3, 4]})
    >>> result = m.kolmogorov_smirnov_stat(data, 'y', 'score')
    >>> assert np.isclose(result.statistic, 1)
    >>> assert np.isclose(result.pvalue, 1 / 3)
    """
    y, p = _classification(df, target, prediction)
    return stats.ks_2samp(p[y == 0], p[y == 1], alternative="two-sided", method="auto")


def cumulative_lgd_accuracy_ratio(df, predicted_ratings, realised_outcomes, *, rating_order=None):
    """Calculate the VUROCS cumulative LGD accuracy measure for ordinal grades.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    predicted_ratings : str
        Predicted ordinal loss-grade column name; higher grades mean greater loss.
    realised_outcomes : str
        Realised ordinal loss-grade column name, on the same scale as predictions.
    rating_order : sequence, optional
        Unique complete grade labels from lowest to highest; unobserved grades are retained.
        Otherwise use consistent ordered categorical metadata, then naturally sort the
        observed union. Specify business order explicitly.

    Returns
    -------
    float
        Twice the cumulative ordinal ROC area, in [0, 1].

    Raises
    ------
    ValueError
        Invalid columns, missing grades or invalid/ambiguous grade order.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    At each threshold from highest to lowest grade, x=P(predicted >= threshold),
    y=P(predicted >= threshold AND realised >= threshold). Include (0,0), integrate whole
    tied-grade bands by trapezoids and return twice the area. This follows VUROCS clar
    (Ozdemir and Miu convention). It is ordinal accuracy, not a chance-adjusted Gini.
    Predictions and outcomes share a grade scale, higher meaning more loss. Accounts have
    equal weight; no p-value applies.

    Constant lowest-grade predictions attain 1, even with no discrimination.
    Any predictions never exceeding their realised grades attain the maximum.
    This asymmetric threshold agreement is not a standalone model-quality criterion;
    inspect the cross-table and use a separate Somers/gAUC or LCR ranking assessment.

    References
    ----------
    https://cran.r-universe.dev/VUROCS/VUROCS.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'p': [1, 2, 3, 3, 4], 'y': [1, 3, 2, 4, 4]})
    >>> result = m.cumulative_lgd_accuracy_ratio(data, 'p', 'y')
    >>> assert np.isclose(result, .88)
    """
    _validate_frame(df, [predicted_ratings, realised_outcomes])
    labels = _rating_order(df[predicted_ratings], df[realised_outcomes], rating_order)
    p = pd.Categorical(df[predicted_ratings], categories=labels, ordered=True).codes
    y = pd.Categorical(df[realised_outcomes], categories=labels, ordered=True).codes
    x_curve, y_curve = [0.0], [0.0]
    for threshold in range(len(labels) - 1, -1, -1):
        selected = p >= threshold
        x_curve.append(float(np.mean(selected)))
        y_curve.append(float(np.mean(selected & (y >= threshold))))
    return float(2 * np.sum(np.diff(x_curve) * (np.array(y_curve[1:]) + y_curve[:-1]) / 2))


def _loss_arrays(ead, predicted, realised):
    """Validate aligned exposures and bounded predicted and realised LGDs.

    Parameters
    ----------
    ead : array-like
        Finite nonnegative exposures with positive total.
    predicted, realised : array-like
        Equal-length LGDs in [0, 1], paired by position with exposures.

    Returns
    -------
    tuple of numpy.ndarray
        Exposures, predicted LGDs, and realised LGDs, without input mutation.

    Raises
    ------
    ValueError
        If dimensions, finiteness, bounds, lengths, or total exposure are invalid.
    """
    p, y = _validate_pairs(predicted, realised, minimum=1, bounded=True)
    weights = _validate_vector(ead, "ead")
    if len(weights) != len(y) or (weights < 0).any() or weights.sum() <= 0:
        raise ValueError("Exposures must align with LGDs, be nonnegative, and have positive total")
    return weights, p, y


def _capture_area(weights, score, losses):
    """Integrate a cumulative loss curve over exposure, pooling tied scores.

    Parameters
    ----------
    weights : numpy.ndarray
        Validated nonnegative exposures with positive total.
    score : numpy.ndarray
        Validated aligned scores, sorted from highest to lowest internally.
    losses : numpy.ndarray
        Aligned nonnegative monetary losses with positive total.

    Returns
    -------
    float
        Trapezoidal area, including (0, 0) and (1, 1), with tie groups pooled.
        Inputs are not modified; callers validate all preconditions.
    """
    grouped = pd.DataFrame({"w": weights, "score": score, "loss": losses}).groupby("score").sum()
    grouped = grouped.sort_index(ascending=False)
    x = np.r_[0, grouped.w.cumsum().to_numpy() / weights.sum()]
    y = np.r_[0, grouped.loss.cumsum().to_numpy() / losses.sum()]
    return float(np.sum(np.diff(x) * (y[:-1] + y[1:]) / 2))


def loss_capture_ratio(ead, predicted_ratings, realised_outcomes):
    """Compare model and ideal loss-capture gains using cumulative exposure on the x axis.

    Parameters
    ----------
    ead : array-like
        Finite nonnegative exposures with positive total, positionally paired with LGDs.
    predicted_ratings : array-like
        Finite predicted LGD fractions in [0, 1], despite the historical ratings name.
    realised_outcomes : array-like
        Equal-length finite realised LGD fractions in [0, 1]. Series indices are ignored.

    Returns
    -------
    float
        Model/ideal area gain ratio in [-1, 1], up to floating-point error.

    Raises
    ------
    ValueError
        Invalid paired LGDs/exposures, nonpositive total EAD/loss, or zero ideal gain
        (constant LGD on positive exposures).

    Notes
    -----
    Sort predicted LGD descending; x=cumulative EAD share, y=cumulative realised monetary
    loss share. Pool tied scores and include the origin. The ideal curve sorts realised LGD;
    LCR=(area_model-0.5)/(area_ideal-0.5). This explicitly uses exposure on the x axis;
    account-count variants differ. Perfect/reverse ordering yields 1/-1; constant predicted
    scores yield 0. Zero EAD has no influence. This is descriptive with no p-value.

    References
    ----------
    https://aptivaa.com/pdf/ifrs9-model-risk-management-1594098423-1.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> result = m.loss_capture_ratio([1, 1, 1], [.1, .4, .9], [.1, .4, .9])
    >>> assert np.isclose(result, 1)
    """
    weights, p, y = _loss_arrays(ead, predicted_ratings, realised_outcomes)
    loss = weights * y
    if loss.sum() <= 0:
        raise ValueError("Total realised monetary loss must be positive")
    ideal_gain = _capture_area(weights, y, loss) - 0.5
    if ideal_gain <= np.finfo(float).eps:
        raise ValueError("Loss capture ratio is undefined when the ideal curve has no gain")
    return float((_capture_area(weights, p, loss) - 0.5) / ideal_gain)


def bayesian_error_rate(df, default_flag, prob_default):
    """Find the minimum empirical misclassification rate over score thresholds.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    default_flag : str
        Binary 0/1 outcome column name; booleans are accepted.
    prob_default : str
        Finite numeric score column name. Larger means outcome 1; unbounded scores are
        accepted despite the historical name.

    Returns
    -------
    float
        Minimum empirical misclassification fraction in [0, 0.5], unrounded.

    Raises
    ------
    ValueError
        Invalid classification data or an absent outcome class.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    For every threshold, error=(1-prevalence)*FPR+prevalence*(1-TPR). Return the minimum,
    including all/none-positive predictions. This is empirical threshold-optimized error
    with equal costs, not irreducible Bayes error. Higher scores mean outcome 1. Training-
    set optimization is optimistic: evaluate on held-out data. Requires both classes;
    returns no p-value.

    References
    ----------
    https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'y': [0, 0, 1, 1], 'score': [1, 2, 2, 3]})
    >>> result = m.bayesian_error_rate(data, 'y', 'score')
    >>> assert np.isclose(result, .25)
    """
    y, p = _classification(df, default_flag, prob_default)
    fpr, tpr, _ = roc_curve(y, p, drop_intermediate=False)
    prevalence = y.mean()
    return float(np.min((1 - prevalence) * fpr + prevalence * (1 - tpr)))


def information_value(df, feature, target, *, smoothing=0.5, bin_order=None):
    """Measure separation of pre-binned feature distributions between binary outcomes.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    feature : str
        Pre-binned feature column name; no automatic binning is performed.
    target : str
        Binary target column name, with both 0 and 1 present.
    smoothing : float, default 0.5
        Finite nonnegative pseudo-count added to every contingency cell. Zero requires
        positive raw cells.

    bin_order : sequence, optional
        Complete unique bin universe. Retain empty declared bins before smoothing;
        otherwise use the observed union. Must include every observed bin.

    Returns
    -------
    tuple
        (table, IV). Bin-indexed table columns: good, bad (raw counts), good_share, bad_share (smoothed), WoE, IV; the scalar sums contributions.

    Raises
    ------
    ValueError
        Invalid columns/classes/smoothing, or zero cells with smoothing=0.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    Pre-bin the feature. Add smoothing to every bin/class count and normalize classes
    separately. WoE=log(good_share/bad_share); IV=sum((good_share-bad_share)*WoE). Outcome 0
    is good, 1 bad. Default smoothing=0.5 makes empty cells finite; smoothing=0 requires
    positive cells. Uses the union of observed bins. Descriptive and nonnegative, with no
    universal acceptance threshold or p-value. Sparse or selected bins can inflate IV.

    bin_order explicitly retains empty declared bins before smoothing. Omitting it
    preserves the observed-union convention, even for categorical inputs. An empty
    declared bin needs positive smoothing; normalization uses all declared bins.

    References
    ----------
    https://doi.org/10.1214/aoms/1177729694

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'bin': ['A'] * 4 + ['B'] * 4, 'y': [0, 0, 0, 1, 0, 1, 1, 1]})
    >>> result = m.information_value(data, 'bin', 'y', smoothing=0)
    >>> assert np.isclose(result[1], np.log(3))
    >>> assert np.allclose(result[0][["good_share", "bad_share"]].sum(), 1)
    """
    _validate_frame(df, [feature, target])
    _validate_binary(df[target], target, both=True)
    smooth = _validate_smoothing(smoothing)
    counts = pd.crosstab(df[feature], df[target]).reindex(columns=[0, 1], fill_value=0).astype(float)
    if bin_order is not None:
        labels = _rating_order(df[feature], order=bin_order)
        counts = counts.reindex(index=labels, fill_value=0)
    adjusted = counts + smooth
    if (adjusted == 0).any().any():
        raise ValueError("Zero class/bin counts require positive smoothing")
    proportions = adjusted / adjusted.sum(axis=0)
    result = pd.DataFrame(
        {"good": counts[0], "bad": counts[1], "good_share": proportions[0], "bad_share": proportions[1]}
    )
    result["WoE"] = np.log(result.good_share / result.bad_share)
    result["IV"] = (result.good_share - result.bad_share) * result.WoE
    return result, float(result.IV.sum())


def _paired_t(predicted, observed, *, alternative):
    """Calculate a paired t statistic with an explicit tail convention.

    Parameters
    ----------
    predicted, observed : array-like
        Equal-length finite LGDs in [0, 1], at least two observations.
    alternative : {'greater', 'two-sided'}
        Tail for the mean of observed minus predicted LGD. Internal callers
        supply only one of these values.

    Returns
    -------
    tuple
        Prediction array, observation array, sample error variance, t statistic,
        and p-value, using n-1 degrees of freedom. Inputs are unchanged.

    Raises
    ------
    ValueError
        If paired validation fails or sample error variance is zero.
    """
    p, y = _validate_pairs(predicted, observed, bounded=True)
    errors = y - p
    variance = float(np.var(errors, ddof=1))
    if np.ptp(errors) == 0 or variance <= 0:
        raise ValueError("Paired t test requires nonzero sample variance of the errors")
    statistic = float(errors.mean() / np.sqrt(variance / len(errors)))
    p_value = (
        stats.t.sf(statistic, len(errors) - 1)
        if alternative == "greater"
        else 2 * stats.t.sf(abs(statistic), len(errors) - 1)
    )
    return p, y, variance, statistic, float(p_value)


def lgd_t_test(df, observed_lgd, expected_lgd, level="portfolio", segment_col=None):
    """Test whether mean realised LGD exceeds mean expected LGD using paired errors.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    observed_lgd : str
        Realised LGD column name, finite fractions in [0, 1].
    expected_lgd : str
        Predicted LGD column name, finite fractions in [0, 1].
    level : {'portfolio', 'segment', 'pool'}, default 'portfolio'
        Test the whole portfolio or each segment; 'pool' aliases 'segment'.
    segment_col : str, optional
        Required segment column for segment/pool tests; ignored at portfolio level.

    Returns
    -------
    pandas.DataFrame
        Portfolio/segment rows: segment, N, realised_lgd_mean, pred_lgd_mean, s2 (sample error variance), mean_error (realised minus predicted), t_stat, p_value.

    Raises
    ------
    ValueError
        Invalid level/segment, columns/LGDs, fewer than two observations per group or zero
        error variance.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    Paired errors e=realised-expected LGD; t=mean(e)/sqrt(sample_variance(e)/N);
    p_value=t.sf(t,N-1). The one-sided alternative is underestimation (positive mean error).
    Independent normal errors give exact finite-sample t inference. Each segment needs at
    least two observations and nonzero error variance. Segment p-values are unadjusted. Each
    account has equal weight.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'ead': [100, 200, 100, 100], 'predicted': [.2, .4, .6, .8], 'realised': [.1, .5, .4, .9], 'segment': ['A', 'A', 'B', 'B']})
    >>> result = m.lgd_t_test(data, 'realised', 'predicted', level='segment', segment_col='segment')
    >>> assert result.segment.tolist() == ['A', 'B']
    >>> assert np.isclose(result.loc[0, 'p_value'], .5)
    >>> assert result.loc[1, 't_stat'] < 0
    """
    if level not in ("portfolio", "segment", "pool"):
        raise ValueError("level must be 'portfolio', 'segment', or the compatibility alias 'pool'")
    if level != "portfolio" and segment_col is None:
        raise ValueError("segment_col is required for a segment test")
    _validate_frame(df, [observed_lgd, expected_lgd] + ([] if level == "portfolio" else [segment_col]))
    groups = (
        [("portfolio", df)] if level == "portfolio" else df.groupby(segment_col, observed=True, sort=False)
    )
    rows = []
    for label, group in groups:
        p, y, variance, statistic, p_value = _paired_t(
            group[expected_lgd], group[observed_lgd], alternative="greater"
        )
        rows.append([label, len(y), y.mean(), p.mean(), variance, (y - p).mean(), statistic, p_value])
    return pd.DataFrame(
        rows,
        columns=[
            "segment",
            "N",
            "realised_lgd_mean",
            "pred_lgd_mean",
            "s2",
            "mean_error",
            "t_stat",
            "p_value",
        ],
    )


def _migration(data, initial, final, rating_order):
    """Build a full, ordered migration count matrix for paired observations.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty data with non-missing grade labels.
    initial, final : str
        Initial and final grade columns, respectively.
    rating_order : sequence or None
        Explicit grade universe; otherwise resolve ordered categoricals or sort
        the union naturally. Inputs are not changed.

    Returns
    -------
    pandas.DataFrame
        Square float count table, including zero rows and columns.

    Raises
    ------
    TypeError
        If data is not a DataFrame.
    ValueError
        If columns or grade order are invalid.
    """
    _validate_frame(data, [initial, final])
    labels = _rating_order(data[initial], data[final], rating_order)
    return (
        pd.crosstab(data[initial], data[final])
        .reindex(index=labels, columns=labels, fill_value=0)
        .astype(float)
    )


def migration_matrix_stability(df, initial_ratings_col, final_ratings_col, *, rating_order=None):
    """Calculate ECB adjacent-cell migration z statistics and their normal CDFs.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    initial_ratings_col : str
        Initial grade column name, paired by DataFrame row with final grades.
    final_ratings_col : str
        Final grade column name, on the same scale as initial grades.
    rating_order : sequence, optional
        Unique complete grade labels from lowest to highest; unobserved grades are retained.
        Otherwise use consistent ordered categorical metadata, then naturally sort the
        observed union. Specify business order explicitly.

    Returns
    -------
    tuple of pandas.DataFrame
        (z_table, normal_cdf_table), square with the same ordered grades. Diagonals, empty rows and zero-variance comparisons are NaN.

    Raises
    ------
    ValueError
        Invalid grade columns or rating order.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    For off-diagonal probability f and adjacent probability n one step nearer the diagonal,
    z=(n-f)/sqrt((f*(1-f)+n*(1-n)+2*f*n)/N_i). Return Phi(z), as in ECB 2019 instructions.
    Small CDFs indicate violations of decreasing off-diagonal mass. These are asymptotic
    multinomial comparisons, not time-series equality tests. Retain empty grades. NaN means
    undefined, not passed. Cell probabilities are not multiplicity-adjusted.

    References
    ----------
    https://www.bankingsupervision.europa.eu/activities/internal_models/shared/pdf/instructions_validation_reporting_credit_risk.en.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'start': [1] * 4 + [2] * 4 + [3] * 4, 'end': [1, 1, 2, 3, 1, 2, 2, 3, 1, 2, 3, 3]})
    >>> result = m.migration_matrix_stability(data, 'start', 'end')
    >>> assert np.isclose(result[0].loc[1, 2], 2 / np.sqrt(11))
    >>> assert np.isnan(np.diag(result[0])).all()
    """
    counts = _migration(df, initial_ratings_col, final_ratings_col, rating_order)
    z = np.full(counts.shape, np.nan)
    for i, row in enumerate(counts.to_numpy()):
        n = row.sum()
        if n == 0:
            continue
        p = row / n
        for j in range(len(row)):
            if i == j:
                continue
            near, far = p[j + 1 if j < i else j - 1], p[j]
            variance = (far * (1 - far) + near * (1 - near) + 2 * far * near) / n
            if variance > 0:
                z[i, j] = (near - far) / np.sqrt(variance)
    return (
        pd.DataFrame(z, index=counts.index, columns=counts.columns),
        pd.DataFrame(stats.norm.cdf(z), index=counts.index, columns=counts.columns),
    )


def population_stability_index(
    data, bin_flag, variable, *, expected=None, actual=None, smoothing=0.5, bin_order=None
):
    """Compare two distributions on a common set of pre-defined bins using PSI.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    bin_flag : str
        Sample/period column name, containing exactly two distinct labels.
    variable : str
        Shared pre-defined bin column name; uses the union of observed bins.
    expected : scalar, optional
        Reference sample label, specified together with actual. Defaults to the first sorted
        sample label.
    actual : scalar, optional
        Comparison sample label, distinct from expected. Defaults to the second sorted
        label.
    smoothing : float, default 0.5
        Finite nonnegative pseudo-count added to every contingency cell. Zero requires
        positive raw cells.

    bin_order : sequence, optional
        Complete unique bin universe. Retain empty declared bins before smoothing;
        otherwise use the observed union. Must include every observed bin.

    Returns
    -------
    tuple
        (table, PSI). Bin-indexed table columns: expected, actual (normalized smoothed shares), PSI contributions; scalar sums contributions.

    Raises
    ------
    ValueError
        Missing columns, other than two samples, invalid/partial sample labels, invalid
        smoothing or zero unsmoothed cells.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    Require exactly two samples and shared pre-defined bins. Add smoothing per sample/bin
    cell, normalize samples to shares E,A, then PSI=sum((A-E)*log(A/E)). Defaults choose
    expected/actual in natural or categorical order; explicit labels are clearer. Default
    smoothing=0.5; zero requires positive cells. PSI is symmetric and descriptive, not a
    significance test. Binning and smoothing change the value; no universal cutoffs are
    imposed.

    bin_order explicitly retains empty declared bins before smoothing. Omitting it
    preserves the observed-union convention, even for categorical inputs. An empty
    declared bin needs positive smoothing; normalization uses all declared bins.

    References
    ----------
    https://doi.org/10.1214/aoms/1177729694

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'period': ['old'] * 4 + ['new'] * 4, 'bin': ['A', 'A', 'A', 'B', 'A', 'B', 'B', 'B']})
    >>> result = m.population_stability_index(data, 'period', 'bin', expected='old', actual='new', smoothing=0)
    >>> assert np.isclose(result[1], np.log(3))
    >>> assert np.allclose(result[0][["expected", "actual"]].sum(), 1)
    """
    _validate_frame(data, [bin_flag, variable])
    smooth = _validate_smoothing(smoothing)
    labels = _rating_order(data[bin_flag])
    if len(labels) != 2:
        raise ValueError("PSI requires exactly two sample labels")
    if expected is None and actual is None:
        expected, actual = labels
    if expected not in labels or actual not in labels or expected == actual:
        raise ValueError("expected and actual must identify the two distinct sample labels")
    counts = pd.crosstab(data[variable], data[bin_flag]).reindex(columns=[expected, actual]).astype(float)
    if bin_order is not None:
        bins = _rating_order(data[variable], order=bin_order)
        counts = counts.reindex(index=bins, fill_value=0)
    adjusted = counts + smooth
    if (adjusted == 0).any().any():
        raise ValueError("Zero sample/bin counts require positive smoothing")
    shares = adjusted / adjusted.sum(axis=0)
    result = pd.DataFrame({"expected": shares[expected], "actual": shares[actual]})
    result["PSI"] = (result.actual - result.expected) * np.log(result.actual / result.expected)
    return result, float(result.PSI.sum())


def _association(first, second, alternative="two-sided"):
    """Validate nonconstant numeric vectors and an association-test alternative.

    Parameters
    ----------
    first, second : array-like
        Finite, equal-length one-dimensional arrays, with at least two entries.
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Direction of the alternative hypothesis against zero association.

    Returns
    -------
    tuple of numpy.ndarray
        Validated arrays, positionally paired and unchanged.

    Raises
    ------
    ValueError
        If pairing fails, either array is constant, or the alternative is invalid.
    """
    if alternative not in ("two-sided", "less", "greater"):
        raise ValueError("alternative must be two-sided, less, or greater")
    x, y = _validate_pairs(first, second)
    if np.unique(x).size < 2 or np.unique(y).size < 2:
        raise ValueError("Association requires two nonconstant arrays")
    return x, y


def kendall_tau(x, y, variant="b"):
    """Calculate Kendall ordinal association with the requested tie normalization.

    Parameters
    ----------
    x : array-like
        Finite nonconstant one-dimensional numeric vector, with at least two observations.
    y : array-like
        Equal-length finite nonconstant numeric vector, paired by position with x. Series
        indices are ignored.
    variant : {'b', 'c'}, default 'b'
        Kendall tie normalization.

    Returns
    -------
    tuple of float
        (tau, p_value), testing zero association two-sided.

    Raises
    ------
    ValueError
        Invalid/nonconstant paired vectors or unsupported variant.

    Notes
    -----
    Kendall tau compares concordant and discordant pairs. Variant b adjusts ties in both
    variables; c normalizes using distinct categories. Both equal tau-a without ties. The
    coefficient lies in [-1,1]. Independent pairs are needed for inference. SciPy selects
    exact/asymptotic inference as applicable; missing values are never silently omitted.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kendalltau.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> result = m.kendall_tau([1, 2, 3, 4], [1, 2, 4, 8])
    >>> assert np.isclose(result[0], 1)
    >>> assert np.isclose(result[1], 1 / 12)
    """
    x, y = _association(x, y)
    if variant not in ("b", "c"):
        raise ValueError("variant must be 'b' or 'c'")
    result = stats.kendalltau(x, y, variant=variant)
    return float(result.statistic), float(result.pvalue)


def somersd(array_1, array_2=None, alternative="two-sided"):
    """Calculate asymmetric Somers D of the second variable conditional on the first.

    Parameters
    ----------
    array_1 : array-like
        Numeric ranking vector or nonnegative integer contingency table with ordered rows
        and columns.
    array_2 : array-like, optional
        Equal-length ranking vector; omit when array_1 is a table.
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative against zero association: nonzero, negative, or positive.

    Returns
    -------
    object
        SciPy SomersDResult with statistic, pvalue and table. Statistic is D(second | first).

    Raises
    ------
    ValueError
        Invalid vectors/alternative/table; tables need nonnegative integer counts and at
        least two nonempty rows and columns.

    Notes
    -----
    Somers D divides concordance minus discordance by pairs untied in the first
    (row/independent) variable. Swapping inputs can change D. Accept ranking vectors or a
    contingency table with ordered rows/columns. The null is D=0, with two-
    sided/less/greater alternatives. SciPy uses asymptotic normal inference for independent
    pairs; sparse tables weaken the approximation.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.somersd.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> result = m.somersd([[3, 1], [1, 3]])
    >>> assert np.isclose(result.statistic, .5)
    """
    if array_2 is None:
        table = np.asarray(array_1, dtype=float)
        if (
            table.ndim != 2
            or min(table.shape) < 2
            or not np.isfinite(table).all()
            or (table < 0).any()
            or (table != np.floor(table)).any()
            or np.count_nonzero(table.sum(axis=0)) < 2
            or np.count_nonzero(table.sum(axis=1)) < 2
        ):
            raise ValueError(
                "Supply two ranking vectors or a nonnegative integer table with two nonempty rows and columns"
            )
        if alternative not in ("two-sided", "less", "greater"):
            raise ValueError("alternative must be two-sided, less, or greater")
        return stats.somersd(table, alternative=alternative)
    x, y = _association(array_1, array_2, alternative)
    return stats.somersd(x, y, alternative=alternative)


def spearman_correlation(array_1, array_2, *, alternative="two-sided"):
    """Calculate Spearman rank correlation and an asymptotic association p-value.

    Parameters
    ----------
    array_1 : array-like
        Finite nonconstant one-dimensional numeric vector, paired by position with array_2.
    array_2 : array-like
        Equal-length finite nonconstant numeric vector; Series indices are ignored.
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative against zero association: nonzero, negative, or positive.

    Returns
    -------
    object
        SciPy SignificanceResult with statistic and pvalue.

    Raises
    ------
    ValueError
        Invalid alternative/vectors, fewer than three pairs, or constant inputs.

    Notes
    -----
    Spearman correlation is Pearson correlation of average ranks. It measures monotone
    association and handles ties using average ranks. SciPy returns an asymptotic p-value
    for zero rank correlation under the chosen alternative. Small-sample p-values are
    unreliable; consider permutation inference. Require at least three independent pairs and
    no constant arrays.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.spearmanr.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> result = m.spearman_correlation([1, 2, 3, 4], [1, 2, 4, 8])
    >>> assert np.isclose(result.statistic, 1)
    """
    x, y = _association(array_1, array_2, alternative)
    if len(x) < 3:
        raise ValueError("Spearman inference requires at least three observations")
    return stats.spearmanr(x, y, alternative=alternative)


def pearson_correlation(array_1, array_2, *, alternative="two-sided"):
    """Calculate Pearson product-moment correlation and its association p-value.

    Parameters
    ----------
    array_1 : array-like
        Finite nonconstant one-dimensional numeric vector, paired by position with array_2.
    array_2 : array-like
        Equal-length finite nonconstant numeric vector; Series indices are ignored.
    alternative : {'two-sided', 'less', 'greater'}, default 'two-sided'
        Alternative against zero association: nonzero, negative, or positive.

    Returns
    -------
    object
        SciPy PearsonRResult with statistic, pvalue and standard result methods.

    Raises
    ------
    ValueError
        Invalid alternative/vectors, fewer than two pairs, or constant inputs.

    Notes
    -----
    Pearson r is the centered cross-product divided by the product of centered Euclidean
    norms, in [-1,1]. Calculation does not require normality; SciPy default p-values assume
    independent bivariate-normal pairs under zero correlation. Near-constant inputs can emit
    SciPy NearConstantInputWarning; inspect and rescale data. Alternatives are two-sided,
    less or greater.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> result = m.pearson_correlation([1, 2, 3, 4], [1, 2, 4, 8])
    >>> assert np.isclose(result.statistic, 11.5 / np.sqrt(143.75))
    >>> assert result.statistic < 1
    """
    x, y = _association(array_1, array_2, alternative)
    return stats.pearsonr(x, y, alternative=alternative)


def migration_matrices_statistics(df, period_1_ratings, period_2_ratings, *, rating_order=None):
    """Calculate ECB normalized migration-weighted bandwidth above and below the diagonal.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    period_1_ratings : str
        Initial grade column name.
    period_2_ratings : str
        Final grade column name, paired by row with initial grades.
    rating_order : sequence, optional
        Unique complete grade labels from lowest to highest; unobserved grades are retained.
        Otherwise use consistent ordered categorical metadata, then naturally sort the
        observed union. Specify business order explicitly.

    Returns
    -------
    tuple of float
        (upper_MWB, lower_MWB), each in [0, 1]. Directions without migrations return 0.

    Raises
    ------
    ValueError
        Invalid grade columns or rating order.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    For each side of the diagonal, divide sum(abs(i-j)*N_ij) by sum(max(i,K-1-i)*N_ij), using
    zero-based grades. This is ECB normalized migration-weighted bandwidth. Upper means a
    later grade in rating_order; economic direction depends on that order. A side with no
    migrations has bandwidth 0 by convention. Describes distance, not frequency or
    significance.

    References
    ----------
    https://www.bankingsupervision.europa.eu/activities/internal_models/shared/pdf/instructions_validation_reporting_credit_risk.en.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'start': [1] * 4 + [2] * 4 + [3] * 4, 'end': [1, 1, 2, 3, 1, 2, 2, 3, 1, 2, 3, 3]})
    >>> result = m.migration_matrices_statistics(data, 'start', 'end')
    >>> assert np.allclose(result, [.8, .8])
    """
    counts = _migration(df, period_1_ratings, period_2_ratings, rating_order).to_numpy()
    k = len(counts)
    i, j = np.indices(counts.shape)
    distance = np.abs(i - j)
    maximum = np.maximum(i, k - 1 - i)
    results = []
    for direction in (j > i, j < i):
        denominator = np.sum(counts * maximum * direction)
        results.append(float(np.sum(counts * distance * direction) / denominator) if denominator > 0 else 0.0)
    return tuple(results)


def _entropy(data, realised_pd, count):
    """Calculate marginal and weighted conditional binary entropy in natural units.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty grade-level data. No columns are added or modified.
    realised_pd : str
        Column of grade default rates in [0, 1].
    count : str
        Column of finite nonnegative weights with positive total; zero weights
        contribute nothing. Fractional weights are permitted.

    Returns
    -------
    tuple of float
        Marginal binary entropy H0 and weighted conditional entropy H1, using
        natural logarithms and the convention 0 log(0) = 0.

    Raises
    ------
    TypeError
        If data is not a DataFrame.
    ValueError
        If probabilities, columns, weights, or total weight are invalid.
    """
    _validate_frame(data, [realised_pd, count])
    p = _validate_probabilities(data[realised_pd], realised_pd)
    w = _validate_vector(data[count], count)
    if (w < 0).any() or w.sum() <= 0:
        raise ValueError("Counts must be nonnegative with a positive total")
    mean = (w @ p) / w.sum()
    w = w / w.sum()
    return float(special.entr(mean) + special.entr(1 - mean)), float(
        w @ (special.entr(p) + special.entr(1 - p))
    )


def conditional_information_entropy_ratio(data, realised_pd, count):
    """Measure the fraction of marginal default uncertainty explained by grades.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    realised_pd : str
        Grade-level realised default-rate column name, finite values in [0, 1].
    count : str
        Nonnegative finite count/weight column with positive total. Zero and fractional
        weights are allowed.

    Returns
    -------
    float
        (H0-H1)/H0 in [0, 1].

    Raises
    ------
    ValueError
        Invalid rates/counts/columns, nonpositive total count, or marginal rate 0 or 1.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    For rates p_i and normalized counts w_i, H0=h(sum(w_i*p_i)), H1=sum(w_i*h(p_i)),
    h(p)=-p*log(p)-(1-p)*log(1-p). Use natural logs and 0*log(0)=0. This is the fraction of
    binary uncertainty explained by grades. Zero counts contribute nothing; fractional
    weights are permitted. Descriptive, not a calibration p-value. A deterministic portfolio
    outcome makes the denominator zero.

    References
    ----------
    https://doi.org/10.1002/j.1538-7305.1948.tb01338.x

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'rate': [0, 1], 'n': [10, 10]})
    >>> result = m.conditional_information_entropy_ratio(data, 'rate', 'n')
    >>> assert np.isclose(result, 1)
    """
    h0, h1 = _entropy(data, realised_pd, count)
    if h0 == 0:
        raise ValueError("Entropy ratio is undefined when the portfolio default rate is 0 or 1")
    return float(max(0, h0 - h1) / h0)


def kullback_leibler_dist(data, realised_pd, count):
    """Calculate mutual information between rating grade and binary default outcome.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    realised_pd : str
        Grade-level realised default-rate column name, finite values in [0, 1].
    count : str
        Nonnegative finite count/weight column with positive total. Zero and fractional
        weights are allowed.

    Returns
    -------
    float
        H0-H1 in nats, between 0 and log(2): mutual information.

    Raises
    ------
    ValueError
        Invalid columns/rates/counts or nonpositive total count.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    The historical name denotes grade/default mutual information, not a general two-
    distribution KL function. Compute marginal minus count-weighted conditional binary
    entropy, with natural logs and 0*log(0)=0. Equivalently, average grade Bernoulli KL
    divergences from the portfolio Bernoulli distribution. Zero weights contribute nothing;
    all-zero/all-one outcomes return 0. No p-value applies.

    References
    ----------
    https://doi.org/10.1214/aoms/1177729694

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'rate': [0, 1], 'n': [10, 10]})
    >>> result = m.kullback_leibler_dist(data, 'rate', 'n')
    >>> assert np.isclose(result, np.log(2))
    """
    h0, h1 = _entropy(data, realised_pd, count)
    return float(max(0, h0 - h1))


def loss_shortfall(data, ead, predicted_lgd, realised_lgd):
    """Calculate relative underestimation of total exposure-weighted monetary loss.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    ead : str
        Finite nonnegative exposure column name, with positive total.
    predicted_lgd : str
        Predicted LGD column name, finite fractions in [0, 1].
    realised_lgd : str
        Realised LGD column name, finite fractions in [0, 1].

    Returns
    -------
    float
        1 - total predicted loss / total realised loss; at most 1, with no finite lower bound.

    Raises
    ------
    ValueError
        Invalid columns/LGDs/exposures or nonpositive total EAD/realised loss.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    Monetary loss is EAD*LGD. Positive means aggregate underestimation, zero equal totals,
    negative overestimation. Nonnegative exposures need positive total; realised total loss
    must be positive. This descriptive aggregate can hide offsetting errors and is not a
    significance test.

    References
    ----------
    https://www.bis.org/publ/bcbs_wp14.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'ead': [100, 200, 100, 100], 'predicted': [.2, .4, .6, .8], 'realised': [.1, .5, .4, .9], 'segment': ['A', 'A', 'B', 'B']})
    >>> result = m.loss_shortfall(data, 'ead', 'predicted', 'realised')
    >>> assert np.isclose(result, 0)
    """
    _validate_frame(data, [ead, predicted_lgd, realised_lgd])
    w, p, y = _loss_arrays(data[ead], data[predicted_lgd], data[realised_lgd])
    if w @ y <= 0:
        raise ValueError("Total realised monetary loss must be positive")
    return float(1 - (w @ p) / (w @ y))


def mean_absolute_deviation(data, ead, predicted_lgd, realised_lgd):
    """Calculate the exposure-weighted mean absolute LGD prediction error.

    Parameters
    ----------
    data : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    ead : str
        Finite nonnegative exposure column name, with positive total.
    predicted_lgd : str
        Predicted LGD column name, finite fractions in [0, 1].
    realised_lgd : str
        Realised LGD column name, finite fractions in [0, 1].

    Returns
    -------
    float
        Exposure-weighted mean absolute LGD error in [0, 1].

    Raises
    ------
    ValueError
        Invalid columns/LGDs/exposures, negative EAD or nonpositive total EAD.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    MAD=sum(EAD*abs(realised-predicted LGD))/sum(EAD). Zero exposures do not contribute.
    Both LGDs use [0,1] fractions. This descriptive score measures error magnitude without
    cancellation; no hypothesis or p-value applies.

    References
    ----------
    https://www.bis.org/publ/bcbs_wp14.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'ead': [100, 200, 100, 100], 'predicted': [.2, .4, .6, .8], 'realised': [.1, .5, .4, .9], 'segment': ['A', 'A', 'B', 'B']})
    >>> result = m.mean_absolute_deviation(data, 'ead', 'predicted', 'realised')
    >>> assert np.isclose(result, .12)
    """
    _validate_frame(data, [ead, predicted_lgd, realised_lgd])
    w, p, y = _loss_arrays(data[ead], data[predicted_lgd], data[realised_lgd])
    return float(w @ np.abs(y - p) / w.sum())


def elbe_t_test(df, lgd, elbe):
    """Test equality of mean realised LGD and ELBE using a two-sided paired t test.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    lgd : str
        Realised LGD column name, finite fractions in [0, 1].
    elbe : str
        Expected loss best estimate column name, finite LGD fractions in [0, 1].

    Returns
    -------
    pandas.DataFrame
        One row: facilities, lgd_mean (realised), elbe_mean (predicted), t_stat, p_value.

    Raises
    ------
    ValueError
        Invalid columns/LGDs, fewer than two pairs, or zero error variance.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    For paired realised LGD minus ELBE errors, t=mean(error)/sqrt(sample_variance(error)/N).
    Return a two-sided t p-value with N-1 degrees of freedom. Null: zero mean paired error.
    Independent normal errors support finite-sample inference; each facility has equal
    weight. Small p-values can indicate either underestimation or overestimation.

    References
    ----------
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_rel.html

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'ead': [100, 200, 100, 100], 'predicted': [.2, .4, .6, .8], 'realised': [.1, .5, .4, .9], 'segment': ['A', 'A', 'B', 'B']})
    >>> result = m.elbe_t_test(data, 'realised', 'predicted')
    >>> assert np.isclose(result.lgd_mean.iloc[0], .475)
    >>> assert result.t_stat.iloc[0] < 0
    >>> assert 0 < result.p_value.iloc[0] < 1
    """
    _validate_frame(df, [lgd, elbe])
    p, y, _, statistic, p_value = _paired_t(df[elbe], df[lgd], alternative="two-sided")
    return pd.DataFrame(
        {
            "facilities": [len(y)],
            "lgd_mean": [y.mean()],
            "elbe_mean": [p.mean()],
            "t_stat": [statistic],
            "p_value": [p_value],
        }
    )


def normal_test(predicted_pd, realised_pd, alpha=0.05):
    """Apply the Basel one-sided normal approximation to annual PD forecast errors.

    Parameters
    ----------
    predicted_pd : array-like
        At least two finite annual predicted rates in [0, 1] for one grade, in time order.
    realised_pd : array-like
        Equal-length realised annual rates in [0, 1], paired by position. Series indices are
        ignored.
    alpha : float, default 0.05
        One-sided significance level strictly between zero and one.

    Returns
    -------
    pandas.DataFrame
        One row: estimate (mean realised-minus-predicted PD), t_stat (historical name for normal z), p_value, outcome (boolean rejection).

    Raises
    ------
    ValueError
        Invalid alpha/rates/pairing, fewer than two years or zero annual-error variance.

    Notes
    -----
    For T annual observations of one grade, e=realised-predicted PD;
    s2=sum((e-mean(e))**2)/(T-1). Basel z=sum(e)/sqrt(T*s2); p_value=normal.sf(z).
    Alternative: PD underestimation; reject when p_value < alpha. Assumes independent annual
    errors with common finite variance and sufficient years. Uses a normal, not Student t,
    reference; preserves historical column t_stat. Not an obligor-level Bernoulli test.

    Six annual observations do not justify independence.

    References
    ----------
    https://www.bis.org/publ/bcbs_wp14.pdf

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> result = m.normal_test([.1, .1, .1, .1], [.1, .2, .3, .4])
    >>> assert np.isclose(result.t_stat.iloc[0], .6 / np.sqrt(1 / 15))
    >>> assert bool(result.outcome.iloc[0])
    """
    alpha = _validate_level(alpha)
    p, y = _validate_pairs(predicted_pd, realised_pd, bounded=True)
    errors = y - p
    variance = np.var(errors, ddof=1)
    if np.ptp(errors) == 0 or variance <= 0:
        raise ValueError("Normal test requires nonzero sample variance of annual errors")
    statistic = float(errors.sum() / np.sqrt(len(errors) * variance))
    p_value = float(stats.norm.sf(statistic))
    return pd.DataFrame(
        {
            "estimate": [errors.mean()],
            "t_stat": [statistic],
            "p_value": [p_value],
            "outcome": [p_value < alpha],
        }
    )


def redelmeier_test(df, *, default_flag="DEFAULT_FLAG", first_pd="ADJUSTED_PD", second_pd="min_PD"):
    """Compare paired Brier losses under an explicit midpoint-Bernoulli null model.

    Parameters
    ----------
    df : pandas.DataFrame
        Nonempty table with unique columns and no missing required values. Extra columns are
        ignored; input is not modified.
    default_flag : str, default 'DEFAULT_FLAG'
        Binary 0/1 outcome column name.
    first_pd : str, default 'ADJUSTED_PD'
        First fixed forecast probability column name, values in [0, 1].
    second_pd : str, default 'min_PD'
        Second fixed forecast probability column name, values in [0, 1].

    Returns
    -------
    tuple of float
        (z_statistic, two_sided_p_value). Identical prediction vectors return (0, 1).

    Raises
    ------
    ValueError
        Missing columns, nonbinary outcomes or invalid probabilities.
    TypeError
        If a required table is not a pandas DataFrame.

    Notes
    -----
    This Redelmeier-style comparison explicitly assumes independent Y_i~Bernoulli(q_i),
    q_i=(p1_i+p2_i)/2, with fixed forecasts. Paired squared-loss difference is
    (p1-p2)*(p1+p2-2Y), with null mean zero and variance (p1-p2)**2*(p1+p2)*(2-p1-p2). Sum
    differences and variances to form z; return 2*normal.sf(abs(z)). Positive z favors the
    second forecast. This normal approximation uses the stronger midpoint null, not
    unrestricted equality of average Brier scores. The variance is derived from this stated
    model; the original paper motivates paired Brier comparisons, not certification of this
    convention. Identical forecasts provide no comparative evidence.

    References
    ----------
    https://pubmed.ncbi.nlm.nih.gov/1941009/

    Examples
    --------
    >>> import numpy as np
    >>> import pandas as pd
    >>> import meliora as m
    >>> data = pd.DataFrame({'y': [0, 1, 1, 0], 'p1': [.1, .4, .7, .3], 'p2': [.2, .6, .6, .1]})
    >>> result = m.redelmeier_test(data, default_flag='y', first_pd='p1', second_pd='p2')
    >>> assert np.isclose(result[0], .18 / np.sqrt(.0798))
    >>> assert 0 < result[1] < 1
    """
    _validate_frame(df, [default_flag, first_pd, second_pd])
    y = _validate_binary(df[default_flag], default_flag)
    p1 = _validate_probabilities(df[first_pd], first_pd)
    p2 = _validate_probabilities(df[second_pd], second_pd)
    difference, total = p1 - p2, p1 + p2
    if np.all(difference == 0):
        return 0.0, 1.0
    variance = np.sum(difference**2 * total * (2 - total))
    z = float(np.sum(difference * (total - 2 * y)) / np.sqrt(variance))
    return z, float(2 * stats.norm.sf(abs(z)))
