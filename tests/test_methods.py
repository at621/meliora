"""Numerical regression tests with small independent, explainable oracles.

Each test states what would constitute a regression. No external CSV, saved
notebook output, network request, or generated implementation snapshot is used.
"""

import itertools
import math

import numpy as np
import pandas as pd
import pytest
from scipy import integrate, stats

import meliora as m


@pytest.fixture
def credit():
    """Two four-obligor grades with two defaults each and fixed PDs 0.2/0.6."""
    return pd.DataFrame({"g": ["A"] * 4 + ["B"] * 4, "y": [0, 0, 1, 1] * 2, "p": [0.2] * 4 + [0.6] * 4})


@pytest.fixture
def loss():
    """Unequal exposures and offsetting errors distinguish weighted/equal means."""
    return pd.DataFrame(
        {
            "w": [100, 200, 100, 100],
            "p": [0.2, 0.4, 0.6, 0.8],
            "y": [0.1, 0.5, 0.4, 0.9],
            "s": ["A", "A", "B", "B"],
        }
    )


@pytest.fixture
def migration():
    """Count matrix [[2,1,1],[1,2,1],[1,1,2]] on three ordered grades."""
    return pd.DataFrame({"a": [1] * 4 + [2] * 4 + [3] * 4, "b": [1, 1, 2, 3, 1, 2, 2, 3, 1, 2, 3, 3]})


def test_binomial_test(credit):
    """Exact enumeration of default counts verifies the upper tail and table schema."""
    result = m.binomial_test(credit, "g", "y", "p", alpha_level=0.2)
    expected = [sum(math.comb(4, k) * p**k * (1 - p) ** (4 - k) for k in range(2, 5)) for p in [0.2, 0.6]]
    assert result.columns.tolist() == [
        "Rating class",
        "Predicted PD",
        "Total count",
        "Defaults",
        "Actual Default Rate",
        "p_value",
        "Reject H0",
    ]
    assert result["Rating class"].tolist() == ["A", "B"]
    np.testing.assert_allclose(
        result[["Predicted PD", "Total count", "Defaults", "Actual Default Rate"]],
        [[0.2, 4, 2, 0.5], [0.6, 4, 2, 0.5]],
    )
    np.testing.assert_allclose(result.p_value, expected)
    assert result["Reject H0"].tolist() == [True, False]
    boundary = pd.DataFrame({"g": ["zero", "one"], "y": [0, 1], "p": [0, 1]})
    np.testing.assert_allclose(m.binomial_test(boundary, "g", "y", "p").p_value, [1, 1])


def test_brier_score(credit):
    """Squared observation errors, not grade mean errors, define Brier scoring."""
    assert m.brier_score(credit, "g", "y", "p") == pytest.approx(0.30)
    credit["p"] = 0.5
    assert m.brier_score(credit, "g", "y", "p") == 0.25
    credit["p"] = credit.y
    assert m.brier_score(credit, "g", "y", "p") == 0
    credit["p"] = 1 - credit.y
    assert m.brier_score(credit, "g", "y", "p") == 1


def test_herfindahl_test():
    """Shares 2/3 and 1/3 yield HHI 5/9 and CV 1/3; empty grades change CV."""
    data = pd.DataFrame({"g": ["A", "A", "B"]})
    np.testing.assert_allclose(m.herfindahl_test(data, "g"), [1 / 3, 5 / 9])
    np.testing.assert_allclose(
        m.herfindahl_test(data, "g", rating_order=["A", "B", "C"]), [math.sqrt(2 / 3), 5 / 9]
    )
    assert m.herfindahl_test(data.iloc[:1], "g") == (0, 1)


def test_herfindahl_multiple_period_test():
    """The ECB CV formula uses one union, including grades new in the current period."""
    initial = pd.DataFrame({"g": ["A"] * 4 + ["B"] * 2})
    current = pd.DataFrame({"g": ["A"] * 5 + ["B"]})
    result = m.herfindahl_multiple_period_test(initial, current, "g", alpha_level=0.4)
    assert result.index.tolist() == ["A", "B", "total"]
    np.testing.assert_allclose(result[["N_initial", "N_current"]], [[4, 5], [2, 1], [6, 6]])
    z = 3 / math.sqrt(34)
    np.testing.assert_allclose(
        result.loc["total", ["h_initial", "h_current", "z_stat", "p_value"]].to_numpy(dtype=float),
        [5 / 9, 26 / 36, z, math.erfc(z / math.sqrt(2)) / 2],
    )
    assert bool(result.loc["total", "reject"])
    assert result.loc["A", ["h_initial", "h_current", "z_stat", "p_value", "reject"]].isna().all()
    current.loc[5, "g"] = "C"
    changed = m.herfindahl_multiple_period_test(initial, current, "g")
    assert changed.loc["C", "N_initial"] == 0
    assert changed.loc["B", "N_current"] == 0
    with pytest.raises(ValueError, match="CV"):
        m.herfindahl_multiple_period_test(initial, pd.DataFrame({"g": ["A", "B"]}), "g")
    with pytest.raises(ValueError, match="reserved"):
        m.herfindahl_multiple_period_test(pd.DataFrame({"g": ["total"]}), current, "g")


def test_hosmer_test(credit):
    """For df=2 the chi-square survival has closed form exp(-Q/2)."""
    p, reject = m.hosmer_test(credit, "g", "y", "p")
    assert p == pytest.approx(math.exp(-(2.25 + 1 / 6) / 2))
    assert reject is False
    p1, _ = m.hosmer_test(credit, "g", "y", "p", ddof=1)
    assert p1 == pytest.approx(math.erfc(math.sqrt((2.25 + 1 / 6) / 2)))
    for invalid in [-1, 2, 1.5, True]:
        with pytest.raises(ValueError, match="ddof"):
            m.hosmer_test(credit, "g", "y", "p", ddof=invalid)
    credit.loc[:3, "p"] = 0
    with pytest.raises(ValueError, match="strictly"):
        m.hosmer_test(credit, "g", "y", "p")


def test_spiegelhalter_test(credit):
    """Enumerated Bernoulli variance and alpha changes catch reversal/aggregation bugs."""
    z, reject = m.spiegelhalter_test(credit, "g", "y", "p")
    assert z == pytest.approx(0.8 / math.sqrt(0.2688))
    assert reject is False
    assert m.spiegelhalter_test(credit, "g", "y", "p", alpha_level=0.2)[1] is True
    # The complete 2^8 null enumeration is independent of the variance implementation.
    terms = []
    for outcomes in itertools.product([0, 1], repeat=8):
        mass = math.prod(p if y else 1 - p for p, y in zip(credit.p, outcomes, strict=True))
        numerator = sum((y - p) * (1 - 2 * p) for p, y in zip(credit.p, outcomes, strict=True))
        terms.append(mass * numerator**2)
    assert sum(terms) == pytest.approx(0.2688)
    credit["p"] = 0.5
    with pytest.raises(ValueError, match="variance"):
        m.spiegelhalter_test(credit, "g", "y", "p")


def test_jeffreys_test(credit):
    """Integrating the unnormalized posterior density checks tails without beta.cdf."""
    result = m.jeffreys_test(credit, "g", "y", "p", alpha_level=0.2)

    def density(x):
        """Beta(2.5,2.5) density up to its normalizing constant."""
        return x**1.5 * (1 - x) ** 1.5

    normalizer = integrate.quad(density, 0, 1)[0]
    expected = [integrate.quad(density, 0, p)[0] / normalizer for p in [0.2, 0.6]]
    np.testing.assert_allclose(result.p_value, expected, rtol=1e-8)
    assert result["Reject H0"].tolist() == [True, False]
    assert result["Defaults"].tolist() == [2, 2]


def test_roc_auc():
    """Pairwise concordance gives 3.5/4; arbitrary finite scores are permitted."""
    data = pd.DataFrame({"y": [0, 0, 1, 1], "p": [-2, 0, 0, 5]})
    assert m.roc_auc(data, "y", "p") == 0.875
    assert m.roc_auc(data.assign(p=-data.p), "y", "p") == 0.125
    assert m.roc_auc(data.assign(p=0), "y", "p") == 0.5


def test_gini():
    """Perfect, reversed and constant ordering map to Gini 1, -1 and 0."""
    data = pd.DataFrame({"y": [0, 0, 1, 1], "p": [1, 2, 3, 4]})
    assert m.gini(data, "y", "p") == 1
    assert m.gini(data.assign(p=-data.p), "y", "p") == -1
    assert m.gini(data.assign(p=0), "y", "p") == 0


def test_kolmogorov_smirnov_stat():
    """Separated score distributions have D=1 and exact p=2/binom(4,2)."""
    data = pd.DataFrame({"y": [0, 0, 1, 1], "p": [1, 2, 3, 4]})
    result = m.kolmogorov_smirnov_stat(data, "y", "p")
    assert result.statistic == 1
    assert result.pvalue == pytest.approx(1 / 3)
    result = m.kolmogorov_smirnov_stat(data.assign(p=[1, 2, 1, 2]), "y", "p")
    assert result.statistic == 0
    assert result.pvalue == 1


def test_cumulative_lgd_accuracy_ratio():
    """Explicit VUROCS threshold areas and row permutations test ties and ordering."""
    data = pd.DataFrame({"p": [1, 2, 3, 3, 4], "y": [1, 3, 2, 4, 4]})
    # Threshold points: (0,0),(.2,.2),(.6,.4),(.8,.8),(1,1).
    expected = 2 * (0.02 + 0.12 + 0.12 + 0.18)
    assert m.cumulative_lgd_accuracy_ratio(data, "p", "y") == pytest.approx(expected)
    assert m.cumulative_lgd_accuracy_ratio(data.sample(frac=1, random_state=42), "p", "y") == pytest.approx(
        expected
    )
    assert m.cumulative_lgd_accuracy_ratio(data.assign(y=data.p), "p", "y") == 1
    labels = {1: "low", 2: "medium", 3: "high", 4: "severe"}
    labelled = data.replace(labels)
    assert m.cumulative_lgd_accuracy_ratio(
        labelled, "p", "y", rating_order=list(labels.values())
    ) == pytest.approx(expected)


def test_loss_capture_ratio():
    """Perfect/reverse/tied ranking invariants and unequal EAD check the area convention."""
    y = np.array([0.1, 0.4, 0.9])
    w = np.array([1, 2, 3])
    assert m.loss_capture_ratio(w, y, y) == pytest.approx(1)
    assert m.loss_capture_ratio(w, 1 - y, y) == pytest.approx(-1)
    assert m.loss_capture_ratio(w, np.full(3, 0.5), y) == pytest.approx(0)
    # Model order [1,0,2]: exposure knots 0,2/6,3/6,1 and loss knots 0,8/36,9/36,1.
    model_area = (2 / 6) * (8 / 36) / 2 + (1 / 6) * (17 / 36) / 2 + 0.5 * (1 + 9 / 36) / 2
    # Ideal order [2,1,0]: knots x=0,3/6,5/6,1; y=0,27/36,35/36,1.
    ideal_area = 0.5 * (27 / 36) / 2 + (2 / 6) * (62 / 36) / 2 + (1 / 6) * (1 + 35 / 36) / 2
    assert m.loss_capture_ratio(w, [0.5, 0.9, 0.1], y) == pytest.approx(
        (model_area - 0.5) / (ideal_area - 0.5)
    )
    tied = m.loss_capture_ratio(w, [0.5, 0.5, 0.9], y)
    assert m.loss_capture_ratio(w[::-1], [0.9, 0.5, 0.5], y[::-1]) == pytest.approx(tied)
    assert m.loss_capture_ratio([0, 1, 2, 3], [1, *y], [1, *y]) == pytest.approx(1)
    for weights, pred, actual in [
        ([0, 0], [0.1, 0.2], [0.1, 0.2]),
        ([1, 1], [0.1, 0.2], [0, 0]),
        ([1, 1], [0.1, 0.2], [0.2, 0.2]),
    ]:
        with pytest.raises(ValueError):
            m.loss_capture_ratio(weights, pred, actual)


def test_bayesian_error_rate():
    """Brute-force threshold classification checks custom column names and ties."""
    data = pd.DataFrame({"custom_y": [0, 1, 0, 1, 1, 0, 0], "score": [0.1, 0.2, 0.3, 0.4, 0.5, 0.5, 0.8]})
    expected = min(
        np.mean((data.score >= threshold) != data.custom_y) for threshold in [-np.inf, *data.score, np.inf]
    )
    assert m.bayesian_error_rate(data, "custom_y", "score") == pytest.approx(expected)
    assert m.bayesian_error_rate(data.assign(score=0), "custom_y", "score") == pytest.approx(3 / 7)


def test_information_value():
    """Known bin proportions give IV log(3); symmetric smoothing keeps zero cells finite."""
    data = pd.DataFrame({"x": ["A"] * 4 + ["B"] * 4, "y": [0, 0, 0, 1, 0, 1, 1, 1]})
    table, iv = m.information_value(data, "x", "y", smoothing=0)
    np.testing.assert_allclose(
        table[["good", "bad", "good_share", "bad_share"]], [[3, 1, 0.75, 0.25], [1, 3, 0.25, 0.75]]
    )
    np.testing.assert_allclose(table.WoE, [math.log(3), -math.log(3)])
    assert iv == pytest.approx(math.log(3))
    separated = pd.DataFrame({"x": ["A", "B"], "y": [0, 1]})
    smooth, iv = m.information_value(separated, "x", "y")
    assert np.isfinite(smooth.to_numpy()).all()
    assert iv == pytest.approx(math.log(3))
    assert m.information_value(data.assign(y=1 - data.y), "x", "y", smoothing=0)[1] == pytest.approx(iv)
    with pytest.raises(ValueError, match="smoothing"):
        m.information_value(separated, "x", "y", smoothing=0)


def test_lgd_t_test(loss):
    """Signed paired differences [-.1,.1,-.2,.1] determine means, variance and t tails."""
    result = m.lgd_t_test(loss, "y", "p")
    row = result.iloc[0]
    assert row.segment == "portfolio"
    np.testing.assert_allclose(
        row[["N", "realised_lgd_mean", "pred_lgd_mean", "s2", "mean_error", "t_stat"]].to_numpy(dtype=float),
        [4, 0.475, 0.5, 0.0225, -0.025, -1 / 3],
    )
    assert row.p_value == pytest.approx(stats.t.sf(-1 / 3, 3))
    grouped = m.lgd_t_test(loss, "y", "p", level="segment", segment_col="s")
    assert grouped.segment.tolist() == ["A", "B"]
    np.testing.assert_allclose(grouped.t_stat, [0, -1 / 3], atol=1e-15)
    pd.testing.assert_frame_equal(grouped, m.lgd_t_test(loss, "y", "p", level="pool", segment_col="s"))
    for kwargs in [{"level": "other"}, {"level": "segment"}]:
        with pytest.raises(ValueError):
            m.lgd_t_test(loss, "y", "p", **kwargs)
    with pytest.raises(ValueError, match="variance"):
        m.lgd_t_test(loss.assign(y=loss.p), "y", "p")
    with pytest.raises(ValueError):
        m.lgd_t_test(loss.iloc[:1], "y", "p")


def test_migration_matrix_stability(migration):
    """Check every off-diagonal against hand-derived z values, including undefined rows."""
    z, cdf = m.migration_matrix_stability(migration, "a", "b")
    a = 2 / math.sqrt(11)
    expected = np.array([[np.nan, a, 0], [a, np.nan, a], [0, a, np.nan]])
    np.testing.assert_allclose(z, expected, equal_nan=True)
    np.testing.assert_allclose(cdf, stats.norm.cdf(expected), equal_nan=True)
    assert z.index.tolist() == z.columns.tolist() == [1, 2, 3]
    z, cdf = m.migration_matrix_stability(migration, "a", "b", rating_order=[1, 2, 3, 4])
    assert z.loc[4].isna().all()
    assert cdf.loc[4].isna().all()
    stationary = pd.DataFrame({"a": [1, 2, 3], "b": [1, 2, 3]})
    z, _ = m.migration_matrix_stability(stationary, "a", "b")
    assert z.isna().all().all()


def test_population_stability_index():
    """Known shares yield log(3); labels, symmetry and normalization remain explicit."""
    data = pd.DataFrame(
        {"period": ["old"] * 4 + ["new"] * 4, "bin": ["A", "A", "A", "B", "A", "B", "B", "B"]}
    )
    table, psi = m.population_stability_index(
        data, "period", "bin", expected="old", actual="new", smoothing=0
    )
    np.testing.assert_allclose(table[["expected", "actual"]], [[0.75, 0.25], [0.25, 0.75]])
    assert psi == pytest.approx(math.log(3))
    assert m.population_stability_index(data, "period", "bin", smoothing=0)[1] == pytest.approx(psi)
    separated = pd.DataFrame({"period": ["old", "new"], "bin": ["A", "B"]})
    result, value = m.population_stability_index(separated, "period", "bin")
    assert np.isfinite(result.to_numpy()).all()
    assert value == pytest.approx(math.log(3))
    with pytest.raises(ValueError, match="smoothing"):
        m.population_stability_index(separated, "period", "bin", smoothing=0)
    with pytest.raises(ValueError, match="exactly two"):
        m.population_stability_index(data.iloc[:4], "period", "bin")
    for kwargs in [
        {"expected": "old"},
        {"expected": "x", "actual": "new"},
        {"expected": "old", "actual": "old"},
    ]:
        with pytest.raises(ValueError, match="distinct"):
            m.population_stability_index(data, "period", "bin", **kwargs)


def test_kendall_tau():
    """Tie-free exact p-values and tied b/c normalization exercise the current SciPy API."""
    np.testing.assert_allclose(m.kendall_tau([1, 2, 3, 4], [1, 2, 4, 8]), [1, 1 / 12])
    # Five concordant pairs, one x tie: tau_b=5/sqrt(5*6), tau_c=15/16.
    b = m.kendall_tau([1, 1, 2, 3], [1, 2, 3, 4], variant="b")
    c = m.kendall_tau([1, 1, 2, 3], [1, 2, 3, 4], variant="c")
    assert b[0] == pytest.approx(5 / math.sqrt(30))
    assert c[0] == pytest.approx(15 / 16)
    assert b[1] == c[1]
    with pytest.raises(ValueError, match="variant"):
        m.kendall_tau([1, 2], [1, 2], variant="a")


def test_somersd():
    """Table/ranking equivalence, asymmetric normalization and directional tails matter."""
    x = [0, 0, 0, 1, 1, 1, 1]
    y = [0, 0, 1, 0, 1, 1, 1]
    table = np.array([[2, 1], [1, 3]])
    result = m.somersd(table)
    assert result.statistic == pytest.approx(5 / 12)
    np.testing.assert_array_equal(result.table, table)
    assert m.somersd(x, y).statistic == result.statistic
    # Asymmetric table has different row/column untied-pair denominators.
    asymmetric = np.array([[4, 1, 0], [0, 2, 1]])
    assert m.somersd(asymmetric).statistic != m.somersd(asymmetric.T).statistic
    greater = m.somersd(x, y, alternative="greater").pvalue
    less = m.somersd(x, y, alternative="less").pvalue
    assert greater + less == pytest.approx(1)
    assert result.pvalue == pytest.approx(2 * greater)
    assert m.somersd(table, alternative="greater").pvalue == pytest.approx(greater)
    for invalid in [[[1, -1], [1, 1]], [[1, 0.5], [1, 1]], [[1, 0], [0, 0]], [1, 2], [[np.nan, 1], [1, 1]]]:
        with pytest.raises(ValueError):
            m.somersd(invalid)
    with pytest.raises(ValueError, match="alternative"):
        m.somersd(table, alternative="invalid")


def test_spearman_correlation():
    """Ranks produce 1 for nonlinear monotone data; one-sided arguments affect inference."""
    assert m.spearman_correlation([1, 2, 3, 4], [1, 2, 4, 8]).statistic == 1
    x = [1, 2, 3, 4, 5]
    y = [2, 1, 3, 5, 4]
    result = m.spearman_correlation(x, y)
    assert result.statistic == pytest.approx(0.8)
    assert m.spearman_correlation(x, y, alternative="greater").pvalue == pytest.approx(result.pvalue / 2)
    with pytest.raises(ValueError, match="three"):
        m.spearman_correlation([1, 2], [1, 2])


def test_pearson_correlation():
    """Centered cross-products differ from Spearman on a nonlinear monotone example."""
    x = [1, 2, 3, 4]
    y = [1, 2, 4, 8]
    result = m.pearson_correlation(x, y)
    assert result.statistic == pytest.approx(11.5 / math.sqrt(143.75))
    assert result.statistic < 1
    assert m.pearson_correlation(x, y, alternative="greater").pvalue == pytest.approx(result.pvalue / 2)
    assert (
        m.pearson_correlation(pd.Series(x, index=[9, 8, 7, 6]), pd.Series(y, index=[1, 2, 3, 4])).statistic
        == result.statistic
    )


def test_migration_matrices_statistics(migration):
    """Each side has weighted distance 4/max-distance 5; stationary sides are zero."""
    assert m.migration_matrices_statistics(migration, "a", "b") == (0.8, 0.8)
    data = pd.DataFrame({"a": [1, 1, 2, 3], "b": [3, 2, 2, 3]})
    assert m.migration_matrices_statistics(data, "a", "b") == (0.75, 0)
    # Reversing periods changes row-specific maximum distances: (2+1)/(2+1)=1.
    assert m.migration_matrices_statistics(data, "b", "a") == (0, 1)
    assert m.migration_matrices_statistics(data.assign(b=data.a), "a", "b") == (0, 0)
    assert m.migration_matrices_statistics(data.iloc[:1].assign(b=1), "a", "b") == (0, 0)


def test_conditional_information_entropy_ratio():
    """Perfect and absent separation anchor the ratio at 1/0; zero weights are harmless."""
    perfect = pd.DataFrame({"p": [0, 1, 0.3], "n": [10, 10, 0]})
    assert m.conditional_information_entropy_ratio(perfect, "p", "n") == 1
    assert m.conditional_information_entropy_ratio(perfect.assign(p=0.3), "p", "n") == pytest.approx(
        0, abs=1e-15
    )
    with pytest.raises(ValueError, match="undefined"):
        m.conditional_information_entropy_ratio(perfect.assign(p=0), "p", "n")


def test_kullback_leibler_dist():
    """Mutual information matches a direct Bernoulli KL sum and accepts boundary rates."""
    data = pd.DataFrame({"p": [0.1, 0.6], "n": [3, 2]})
    mean = 0.3
    expected = sum(
        w * (p * math.log(p / mean) + (1 - p) * math.log((1 - p) / (1 - mean)))
        for p, w in [(0.1, 0.6), (0.6, 0.4)]
    )
    assert m.kullback_leibler_dist(data, "p", "n") == pytest.approx(expected)
    assert m.kullback_leibler_dist(pd.DataFrame({"p": [0, 1], "n": [1, 1]}), "p", "n") == pytest.approx(
        math.log(2)
    )
    assert m.kullback_leibler_dist(data.assign(p=0), "p", "n") == 0
    for weights in [[0, 0], [-1, 2]]:
        with pytest.raises(ValueError, match="Counts"):
            m.kullback_leibler_dist(data.assign(n=weights), "p", "n")


def test_loss_shortfall(loss):
    """Equal monetary totals give zero; sign tracks aggregate under/overestimation."""
    assert m.loss_shortfall(loss, "w", "p", "y") == pytest.approx(0)
    assert m.loss_shortfall(loss.assign(p=loss.p / 2), "w", "p", "y") == pytest.approx(0.5)
    assert m.loss_shortfall(loss.assign(y=loss.y / 2), "w", "p", "y") == pytest.approx(-1)
    with pytest.raises(ValueError, match="realised"):
        m.loss_shortfall(loss.assign(y=0), "w", "p", "y")


def test_mean_absolute_deviation(loss):
    """Weighted absolute errors total 60 on EAD 500; input units are true LGD fractions."""
    assert m.mean_absolute_deviation(loss, "w", "p", "y") == pytest.approx(0.12)
    assert m.mean_absolute_deviation(loss.assign(p=loss.y), "w", "p", "y") == 0
    assert m.mean_absolute_deviation(loss.assign(w=loss.w * 100), "w", "p", "y") == pytest.approx(0.12)


def test_elbe_t_test(loss):
    """Two-sided paired inference preserves the signed statistic and correctly labelled means."""
    result = m.elbe_t_test(loss, "y", "p")
    np.testing.assert_allclose(result.iloc[0, :4], [4, 0.475, 0.5, -1 / 3])
    assert result.p_value.iloc[0] == pytest.approx(2 * stats.t.sf(1 / 3, 3))
    swapped = m.elbe_t_test(loss, "p", "y")
    assert swapped.t_stat.iloc[0] == pytest.approx(-result.t_stat.iloc[0])
    assert swapped.p_value.iloc[0] == pytest.approx(result.p_value.iloc[0])


def test_normal_test():
    """Basel annual errors use sample variance and a signed upper normal tail."""
    result = m.normal_test([0.1] * 4, [0.1, 0.2, 0.3, 0.4])
    z = 0.6 / math.sqrt(1 / 15)
    assert result.estimate.iloc[0] == pytest.approx(0.15)
    assert result.t_stat.iloc[0] == pytest.approx(z)
    assert result.p_value.iloc[0] == pytest.approx(math.erfc(z / math.sqrt(2)) / 2)
    assert bool(result.outcome.iloc[0])
    reverse = m.normal_test([0.1, 0.2, 0.3, 0.4], [0.1] * 4)
    assert reverse.t_stat.iloc[0] == pytest.approx(-z)
    assert reverse.p_value.iloc[0] > 0.5
    assert not bool(reverse.outcome.iloc[0])
    assert not bool(m.normal_test([0.1] * 4, [0.1, 0.2, 0.3, 0.4], alpha=0.001).outcome.iloc[0])
    with pytest.raises(ValueError, match="variance"):
        m.normal_test([0.1, 0.1], [0.1, 0.1])


def test_redelmeier_test(capsys):
    """Enumerating all Bernoulli outcomes independently verifies midpoint-null variance."""
    data = pd.DataFrame({"y": [0, 1, 1, 0], "p1": [0.1, 0.4, 0.7, 0.3], "p2": [0.2, 0.6, 0.6, 0.1]})
    probabilities = (data.p1 + data.p2) / 2
    variance = 0
    mean = 0
    for outcomes in itertools.product([0, 1], repeat=4):
        mass = math.prod(q if y else 1 - q for q, y in zip(probabilities, outcomes, strict=True))
        difference = sum(
            (p1 - y) ** 2 - (p2 - y) ** 2 for p1, p2, y in zip(data.p1, data.p2, outcomes, strict=True)
        )
        mean += mass * difference
        variance += mass * difference**2
    assert mean == pytest.approx(0, abs=1e-15)
    assert variance == pytest.approx(0.0798)
    z, p = m.redelmeier_test(data, default_flag="y", first_pd="p1", second_pd="p2")
    assert z == pytest.approx(0.18 / math.sqrt(variance))
    assert p == pytest.approx(math.erfc(abs(z) / math.sqrt(2)))
    swapped = m.redelmeier_test(data, default_flag="y", first_pd="p2", second_pd="p1")
    np.testing.assert_allclose(swapped, [-z, p])
    default = data.rename(columns={"y": "DEFAULT_FLAG", "p1": "ADJUSTED_PD", "p2": "min_PD"})
    assert m.redelmeier_test(default) == (z, p)
    assert m.redelmeier_test(default.assign(min_PD=default.ADJUSTED_PD)) == (0, 1)
    assert capsys.readouterr().out == ""


def test_declared_empty_bins_affect_only_explicit_policy():
    d = pd.DataFrame({"period": ["old"] * 4 + ["new"] * 4, "bin": ["A", "A", "A", "B", "A", "B", "B", "B"]})
    _, old = m.population_stability_index(d, "period", "bin", expected="old", actual="new")
    _, new = m.population_stability_index(
        d, "period", "bin", expected="old", actual="new", bin_order=["A", "B", "C"]
    )
    assert old == pytest.approx(0.677838288309763)
    assert new == pytest.approx(old * 5 / 5.5)
    iv = d.rename(columns={"period": "y"}).assign(y=[0] * 4 + [1] * 4)
    assert m.information_value(iv, "bin", "y", bin_order=["A", "B", "C"])[1] == pytest.approx(new)
    with pytest.raises(ValueError):
        m.information_value(iv, "bin", "y", bin_order=["A", "B", "C"], smoothing=0)
    with pytest.raises(ValueError):
        m.population_stability_index(
            d, "period", "bin", expected="old", actual="new", bin_order=["A", "B", "C"], smoothing=0
        )


def test_legacy_clar_constant_lowest_score_is_not_discrimination():
    d = pd.DataFrame({"p": [1, 1, 1, 1], "y": [1, 2, 3, 4]})
    assert m.cumulative_lgd_accuracy_ratio(d, "p", "y", rating_order=[1, 2, 3, 4]) == 1
