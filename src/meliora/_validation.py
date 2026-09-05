"""Shared validation for finite, nonempty, positionally paired input data."""

from collections.abc import Sequence

import numpy as np
import pandas as pd


def vector(values, name: str, *, minimum: int = 1) -> np.ndarray:
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


def probabilities(values, name: str, *, minimum: int = 1) -> np.ndarray:
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
    result = vector(values, name, minimum=minimum)
    if ((result < 0) | (result > 1)).any():
        raise ValueError(f"{name} must be between 0 and 1")
    return result


def binary(values, name: str, *, both: bool = False) -> np.ndarray:
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
    result = vector(values, name)
    if not np.isin(result, [0, 1]).all():
        raise ValueError(f"{name} must contain only 0 and 1")
    if both and np.unique(result).size != 2:
        raise ValueError(f"{name} must contain both outcomes 0 and 1")
    return result


def frame(data, columns: Sequence[str]) -> None:
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


def level(value: float, name: str = "alpha") -> float:
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


def paired(first, second, *, minimum: int = 2, bounded: bool = False):
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
    validate = probabilities if bounded else vector
    x = validate(first, "first", minimum=minimum)
    y = validate(second, "second", minimum=minimum)
    if x.size != y.size:
        raise ValueError("Paired arrays must have the same length")
    return x, y


def ordered_labels(first, second=None, order=None) -> list:
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


def smoothing(value: float) -> float:
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
