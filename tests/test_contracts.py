"""Input contracts and non-mutation checks shared across all 29 public methods."""

from copy import deepcopy

import numpy as np
import pandas as pd
import pytest

import meliora as m
from meliora.core import _validate_vector

CREDIT = pd.DataFrame({"g": ["A"] * 4 + ["B"] * 4, "y": [0, 0, 1, 1] * 2, "p": [0.2] * 4 + [0.6] * 4})
LOSS = pd.DataFrame({"w": [1, 2, 3], "p": [0.1, 0.4, 0.8], "y": [0.2, 0.3, 0.9]})
MIGRATION = pd.DataFrame({"a": [1, 1, 1, 2, 2], "b": [1, 1, 2, 1, 2]})
ENTROPY = pd.DataFrame({"p": [0.2, 0.8], "n": [10, 10]})
PSI = pd.DataFrame({"sample": ["old", "old", "new", "new"], "bin": ["A", "B", "A", "B"]})
CASES = (
    [
        (name, [CREDIT, "g", "y", "p"], {})
        for name in ["binomial_test", "brier_score", "hosmer_test", "spiegelhalter_test", "jeffreys_test"]
    ]
    + [
        (name, [CREDIT, "y", "p"], {})
        for name in ["roc_auc", "gini", "kolmogorov_smirnov_stat", "bayesian_error_rate"]
    ]
    + [
        ("herfindahl_test", [MIGRATION, "a"], {}),
        ("herfindahl_multiple_period_test", [MIGRATION, MIGRATION, "a"], {}),
        ("cumulative_lgd_accuracy_ratio", [MIGRATION, "a", "b"], {}),
        ("loss_capture_ratio", [[1, 2, 3], [0.1, 0.4, 0.8], [0.2, 0.3, 0.9]], {}),
        ("information_value", [CREDIT, "g", "y"], {}),
        ("lgd_t_test", [LOSS, "y", "p"], {}),
        ("migration_matrix_stability", [MIGRATION, "a", "b"], {}),
        ("population_stability_index", [PSI, "sample", "bin"], {}),
        ("kendall_tau", [[1, 2, 3, 4], [1, 3, 2, 4]], {}),
        ("somersd", [[1, 2, 3, 4], [1, 3, 2, 4]], {}),
        ("spearman_correlation", [[1, 2, 3, 4], [1, 3, 2, 4]], {}),
        ("pearson_correlation", [[1, 2, 3, 4], [1, 3, 2, 4]], {}),
        ("migration_matrices_statistics", [MIGRATION, "a", "b"], {}),
        ("conditional_information_entropy_ratio", [ENTROPY, "p", "n"], {}),
        ("kullback_leibler_dist", [ENTROPY, "p", "n"], {}),
        ("loss_shortfall", [LOSS, "w", "p", "y"], {}),
        ("mean_absolute_deviation", [LOSS, "w", "p", "y"], {}),
        ("elbe_t_test", [LOSS, "y", "p"], {}),
        ("normal_test", [[0.1] * 4, [0.1, 0.2, 0.3, 0.4]], {}),
        (
            "redelmeier_test",
            [pd.DataFrame({"DEFAULT_FLAG": [0, 1], "ADJUSTED_PD": [0.2, 0.5], "min_PD": [0.1, 0.7]})],
            {},
        ),
    ]
)


@pytest.mark.parametrize("name,args,kwargs", CASES, ids=[c[0] for c in CASES])
def test_no_input_mutation(name, args, kwargs):
    """Every public function must leave caller-owned arrays and tables unchanged."""
    local = deepcopy(args)
    getattr(m, name)(*local, **kwargs)
    for before, after in zip(args, local, strict=True):
        if isinstance(before, pd.DataFrame):
            pd.testing.assert_frame_equal(before, after)
        else:
            assert before == after


@pytest.mark.parametrize("name,args,kwargs", CASES, ids=[c[0] for c in CASES])
@pytest.mark.parametrize("failure", ["empty", "missing"])
def test_invalid_data_is_rejected(name, args, kwargs, failure):
    """No public method silently accepts empty data or missing required observations."""
    local = deepcopy(args)
    if isinstance(local[0], pd.DataFrame):
        local[0] = local[0].iloc[:0] if failure == "empty" else local[0].astype(object)
        if failure == "missing":
            local[0].iloc[0, :] = None
    else:
        local[0] = [] if failure == "empty" else [np.nan, *local[0][1:]]
    with pytest.raises(ValueError):
        getattr(m, name)(*local, **kwargs)


@pytest.mark.parametrize("name", ["roc_auc", "gini", "kolmogorov_smirnov_stat", "bayesian_error_rate"])
@pytest.mark.parametrize("values", [[0] * 8, [2] * 8])
def test_discrimination_requires_binary_classes(name, values):
    """Undefined one-class discrimination and multiclass targets must fail clearly."""
    with pytest.raises(ValueError):
        getattr(m, name)(CREDIT.assign(y=values), "y", "p")


@pytest.mark.parametrize(
    "name", ["binomial_test", "brier_score", "hosmer_test", "spiegelhalter_test", "jeffreys_test"]
)
def test_calibration_checks_probabilities_and_outcomes(name):
    """All calibration entry points reject invalid probabilities and binary flags."""
    for data in [CREDIT.assign(p=1.1), CREDIT.assign(y=0.5)]:
        with pytest.raises(ValueError):
            getattr(m, name)(data, "g", "y", "p")


@pytest.mark.parametrize("value", [0, 1, -0.1, np.nan, np.inf, [], None, "bad"])
def test_significance_level_validation(value):
    """A threshold must be a finite scalar strictly between 0 and 1."""
    with pytest.raises(ValueError):
        m.binomial_test(CREDIT, "g", "y", "p", alpha_level=value)


@pytest.mark.parametrize("value", [-1, np.inf, np.nan, [], None, "bad"])
def test_smoothing_validation(value):
    """Negative, nonfinite and nonscalar pseudo-counts cannot define distributions."""
    with pytest.raises(ValueError):
        m.information_value(CREDIT, "g", "y", smoothing=value)


@pytest.mark.parametrize("name", ["kendall_tau", "somersd", "spearman_correlation", "pearson_correlation"])
def test_association_rejects_constant_or_unpaired_data(name):
    """Constant, nonfinite, multidimensional and mismatched pairs are undefined."""
    function = getattr(m, name)
    for first, second in [
        ([1, 1, 1], [1, 2, 3]),
        ([1, 2, 3], [1, 1, 1]),
        ([1, 2], [1, 2, 3]),
        ([1, np.inf], [1, 2]),
        ([[1, 2]], [1, 2]),
    ]:
        with pytest.raises(ValueError):
            function(first, second)
    if name != "kendall_tau":
        with pytest.raises(ValueError, match="alternative"):
            function([1, 2, 3], [1, 2, 3], alternative="invalid")


@pytest.mark.parametrize(
    "value", [[1 + 1j], np.array(["2020-01-01"], dtype="datetime64[D]"), ["bad"], [object()], [[1, 2]]]
)
def test_numeric_vectors_reject_nonreal_or_nonnumeric_values(value):
    """Shared conversion must not drop complex components or reinterpret dates."""
    with pytest.raises(ValueError):
        _validate_vector(value, "example")


def test_dataframe_contract():
    """Table type, duplicate labels and missing columns produce deliberate exceptions."""
    with pytest.raises(TypeError):
        m.brier_score([1, 2], "g", "y", "p")
    with pytest.raises(ValueError, match="unique"):
        m.brier_score(pd.DataFrame([[1, 2]], columns=["g", "g"]), "g", "y", "p")
    with pytest.raises(ValueError, match="Missing column"):
        m.brier_score(CREDIT, "absent", "y", "p")


def test_rating_order_contract():
    """Explicit and ordered-category grades must agree and contain all observed labels."""
    data = pd.DataFrame({"g": ["A", "B", "B"]})
    for order in [[], ["A"], ["A", "A", "B"], ["A", "B", None]]:
        with pytest.raises(ValueError, match="rating_order"):
            m.herfindahl_test(data, "g", rating_order=order)
    mixed = pd.DataFrame({"g": ["A", 1, 1]})
    with pytest.raises(ValueError, match="explicit"):
        m.herfindahl_test(mixed, "g")
    assert m.herfindahl_test(mixed, "g", rating_order=["A", 1])[1] == pytest.approx(5 / 9)
    ordered = data.assign(g=pd.Categorical(data.g, categories=["B", "A", "C"], ordered=True))
    np.testing.assert_allclose(m.herfindahl_test(ordered, "g"), [np.sqrt(2 / 3), 5 / 9])
    inconsistent = ordered.copy()
    inconsistent["other"] = pd.Categorical(data.g, categories=["A", "B", "C"], ordered=True)
    with pytest.raises(ValueError, match="agree"):
        m.migration_matrices_statistics(inconsistent, "g", "other")


def test_exposure_alignment_and_bounds():
    """Exposures cannot be negative or misaligned, and LGDs use the fraction scale."""
    for weights, predicted, actual in [
        ([1], [0.1, 0.2], [0.2, 0.3]),
        ([-1, 2], [0.1, 0.2], [0.2, 0.3]),
        ([1, 2], [0.1, 2], [0.2, 0.3]),
    ]:
        with pytest.raises(ValueError):
            m.loss_capture_ratio(weights, predicted, actual)


def test_public_catalogue_matches_contract_cases():
    """New exports must gain non-mutation and invalid-input coverage."""
    assert set(m.__all__) == {case[0] for case in CASES}


def test_exact_constant_errors_do_not_become_roundoff_variance():
    """Three identical nonzero errors must not yield a huge spurious test statistic."""
    data = pd.DataFrame({"p": [0.1] * 3, "y": [0.2] * 3})
    with pytest.raises(ValueError, match="variance"):
        m.lgd_t_test(data, "y", "p")
    with pytest.raises(ValueError, match="variance"):
        m.normal_test(data.p, data.y)


def test_all_default_entropy_is_exactly_degenerate():
    """A three-grade all-default portfolio has no marginal uncertainty to explain."""
    data = pd.DataFrame({"p": [1, 1, 1], "n": [1, 1, 1]})
    assert m.kullback_leibler_dist(data, "p", "n") == 0
    with pytest.raises(ValueError, match="undefined"):
        m.conditional_information_entropy_ratio(data, "p", "n")
