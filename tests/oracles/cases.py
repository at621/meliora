"""Shared cross-language test cases for the 29 Meliora methods.

This module is the single source of truth for the cross-language comparison:

* ``generate_data`` writes every input dataset as CSV so that Python, R, SAS and
  MATLAB read identical bytes.
* ``CASES`` maps a case id to a function that runs the Meliora method on those
  datasets and returns a flat ``{field: value}`` dictionary. Table outputs are
  flattened to ``field.<label>`` keys so no language has to agree on row order.
* ``compute_all`` returns the long ``(case, field, value)`` records that every
  oracle must reproduce, and ``data_hash`` fingerprints the CSVs so a frozen
  oracle file can be detected as stale.

Each oracle script (``r/oracle.R``, ``sas/oracle.sas``, ``matlab/oracle.m``)
implements the same case ids and field names in its own language.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import meliora as m

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
SEED = 20260919


# ---------------------------------------------------------------------------
# Datasets
# ---------------------------------------------------------------------------


def _write(out: Path, name: str, columns: dict) -> pd.DataFrame:
    frame = pd.DataFrame(columns)
    frame.to_csv(out / f"{name}.csv", index=False, float_format="%.17g", lineterminator="\n")
    return frame


def generate_data(out: Path = DATA_DIR) -> None:
    """Write all worked-example and synthetic datasets as CSV files."""
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # Worked examples from the book (identical to the existing regression tests).
    _write(out, "pd_small", {"grade": ["A"] * 4 + ["B"] * 4, "y": [0, 0, 1, 1] * 2, "pd": [0.2] * 4 + [0.6] * 4})
    _write(out, "jeffreys_small", {"grade": ["A"] * 4, "y": [0, 0, 1, 1], "pd": [0.5] * 4})
    _write(out, "score_small", {"y": [0, 0, 1, 1], "score": [1, 2, 2, 3]})
    _write(out, "score_small_noties", {"y": [0, 0, 1, 1], "score": [1, 2, 3, 4]})
    _write(out, "clar_small", {"p": [1, 2, 3, 3, 4], "y": [1, 3, 2, 4, 4]})
    _write(out, "lcr_small", {"ead": [1, 1, 1], "p": [0.1, 0.4, 0.9], "y": [0.1, 0.4, 0.9]})
    _write(out, "iv_small", {"bin": ["A"] * 4 + ["B"] * 4, "y": [0, 0, 0, 1, 0, 1, 1, 1]})
    _write(
        out,
        "lgd_small",
        {
            "ead": [100, 200, 100, 100],
            "predicted": [0.2, 0.4, 0.6, 0.8],
            "realised": [0.1, 0.5, 0.4, 0.9],
            "segment": ["A", "A", "B", "B"],
        },
    )
    _write(out, "migration_small", {"start": [1] * 4 + [2] * 4 + [3] * 4, "end": [1, 1, 2, 3, 1, 2, 2, 3, 1, 2, 3, 3]})
    _write(out, "psi_small", {"period": ["old"] * 4 + ["new"] * 4, "bin": ["A", "A", "A", "B", "A", "B", "B", "B"]})
    _write(out, "assoc_small", {"x": [1, 2, 3, 4], "y": [1, 2, 4, 8]})
    # Row-wise expansion of the contingency table [[3, 1], [1, 3]].
    _write(out, "somers_small", {"x": [0, 0, 0, 0, 1, 1, 1, 1], "y": [0, 0, 0, 1, 0, 1, 1, 1]})
    _write(out, "grades_small_initial", {"grade": ["A"] * 4 + ["B"] * 2})
    _write(out, "grades_small_current", {"grade": ["A"] * 5 + ["B"]})
    _write(out, "entropy_small", {"rate": [0, 1], "n": [10, 10]})
    _write(out, "normal_small", {"predicted": [0.1] * 4, "realised": [0.1, 0.2, 0.3, 0.4]})
    _write(out, "redelmeier_small", {"y": [0, 1, 1, 0], "p1": [0.1, 0.4, 0.7, 0.3], "p2": [0.2, 0.6, 0.6, 0.1]})

    # Synthetic PD portfolio: 2,000 obligors, six grades with a common grade PD,
    # outcomes drawn from a miscalibrated PD, a continuous tie-free score and a
    # second obligor-level PD for the Redelmeier comparison.
    n = 2000
    grades = np.array([f"G{i}" for i in range(1, 7)])
    base = np.array([0.005, 0.01, 0.02, 0.04, 0.08, 0.15])
    index = rng.choice(6, n, p=[0.15, 0.2, 0.25, 0.2, 0.12, 0.08])
    grade_pd = base[index]
    y = (rng.random(n) < grade_pd * 1.3).astype(int)
    score = np.round(np.log(grade_pd / (1 - grade_pd)) + rng.normal(0, 0.8, n), 9)
    assert len(np.unique(score)) == n, "synthetic score must be tie-free"
    pd2 = np.clip(grade_pd * (1 + rng.normal(0, 0.3, n)), 0.001, 0.999)
    _write(out, "pd_large", {"grade": grades[index], "y": y, "pd": grade_pd, "score": score, "pd2": np.round(pd2, 6)})

    # Synthetic LGD sample: 600 facilities, three segments, rounded LGDs so that
    # ties occur in the association measures, plus ordinal loss grades for CLAR.
    n = 600
    segment = rng.choice(["S1", "S2", "S3"], n, p=[0.5, 0.3, 0.2])
    ead = np.round(rng.lognormal(10, 1, n), 2)
    predicted = np.round(rng.beta(2, 3, n), 4)
    realised = np.round(np.clip(predicted + rng.normal(0.05, 0.2, n), 0, 1), 4)
    to_grade = lambda v: np.clip(np.ceil(v * 5), 1, 5).astype(int)  # noqa: E731
    _write(
        out,
        "lgd_large",
        {
            "ead": ead,
            "predicted": predicted,
            "realised": realised,
            "segment": segment,
            "pgrade": to_grade(predicted),
            "rgrade": to_grade(realised),
        },
    )

    # Synthetic migration matrix: 1,500 obligors on seven grades, plus an initial
    # cohort count per grade that exceeds the matched row totals (departures).
    n = 1500
    labels = np.array([f"G{i}" for i in range(1, 8)])
    start = rng.choice(7, n, p=[0.1, 0.15, 0.2, 0.2, 0.15, 0.12, 0.08])
    shift = rng.choice([-2, -1, 0, 1, 2], n, p=[0.03, 0.12, 0.7, 0.12, 0.03])
    end = np.clip(start + shift, 0, 6)
    _write(out, "migration_large", {"start": labels[start], "end": labels[end]})
    totals = np.bincount(start, minlength=7)
    _write(out, "migration_large_initial_counts", {"grade": labels, "count": totals + rng.integers(0, 40, 7)})

    # Synthetic PSI sample: bin B8 is present in the old period only.
    bins = np.array([f"B{i}" for i in range(1, 9)])
    old = rng.choice(8, 1200, p=[0.1, 0.15, 0.2, 0.2, 0.15, 0.1, 0.07, 0.03])
    new = rng.choice(8, 900, p=[0.14, 0.18, 0.22, 0.18, 0.13, 0.09, 0.06, 0.0])
    _write(out, "psi_large", {"period": ["old"] * 1200 + ["new"] * 900, "bin": np.r_[bins[old], bins[new]]})

    # Synthetic concentration samples: G8 is empty in the current period.
    labels = np.array([f"G{i}" for i in range(1, 9)])
    initial = rng.choice(8, 1000, p=[0.08, 0.12, 0.18, 0.22, 0.18, 0.12, 0.07, 0.03])
    current = rng.choice(8, 1300, p=[0.05, 0.1, 0.15, 0.3, 0.22, 0.12, 0.06, 0.0])
    _write(out, "grades_large_initial", {"grade": labels[initial]})
    _write(out, "grades_large_current", {"grade": labels[current]})

    # Grade-level default rates including a zero-rate grade.
    _write(
        out,
        "entropy_large",
        {"rate": [0, 0.004, 0.011, 0.025, 0.05, 0.09, 0.2, 0.45], "n": [120, 400, 650, 500, 300, 150, 60, 20]},
    )

    # Twenty-four annual cohorts.
    predicted = np.round(rng.uniform(0.01, 0.03, 24), 5)
    realised = np.round(np.clip(predicted + rng.normal(0.003, 0.008, 24), 0, 1), 5)
    _write(out, "normal_large", {"predicted": predicted, "realised": realised})


# ---------------------------------------------------------------------------
# Result flattening helpers
# ---------------------------------------------------------------------------


def _py(value):
    """Convert numpy/pandas scalars to plain JSON-compatible Python values."""
    if value is pd.NA or value is None:
        return None
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    if isinstance(value, (int, np.integer)):
        return int(value)
    value = float(value)
    return None if np.isnan(value) else value


def _by_label(frame: pd.DataFrame, mapping: dict[str, str]) -> dict:
    """Flatten labelled rows: ``{field: column}`` becomes ``field.<label>`` keys."""
    out = {}
    for field, column in mapping.items():
        for label, value in frame[column].items():
            out[f"{field}.{label}"] = _py(value)
    return out


def _matrix(frame: pd.DataFrame, field: str) -> dict:
    """Flatten the off-diagonal cells of a square labelled table."""
    out = {}
    for i in frame.index:
        for j in frame.columns:
            if i != j:
                out[f"{field}.{i}.{j}"] = _py(frame.loc[i, j])
    return out


CASES: dict[str, callable] = {}


def case(name: str):
    def register(function):
        CASES[name] = function
        return function

    return register


# ---------------------------------------------------------------------------
# Discrimination
# ---------------------------------------------------------------------------


@case("roc_auc_small")
def _(d):
    return {"auc": m.roc_auc(d("score_small"), "y", "score")}


@case("roc_auc_large")
def _(d):
    return {"auc": m.roc_auc(d("pd_large"), "y", "score")}


@case("gini_small")
def _(d):
    return {"gini": m.gini(d("score_small"), "y", "score")}


@case("gini_large")
def _(d):
    return {"gini": m.gini(d("pd_large"), "y", "score")}


def _ks(frame):
    result = m.kolmogorov_smirnov_stat(frame, "y", "score")
    return {"statistic": _py(result.statistic), "pvalue": _py(result.pvalue)}


@case("ks_small_noties")
def _(d):
    return _ks(d("score_small_noties"))


@case("ks_small_ties")
def _(d):
    return _ks(d("score_small"))


@case("ks_large")
def _(d):
    return _ks(d("pd_large"))


@case("bayesian_error_rate_small")
def _(d):
    return {"error": m.bayesian_error_rate(d("score_small"), "y", "score")}


@case("bayesian_error_rate_large")
def _(d):
    return {"error": m.bayesian_error_rate(d("pd_large"), "y", "score")}


def _iv(table, iv):
    out = _by_label(table, {"good": "good", "bad": "bad", "good_share": "good_share", "bad_share": "bad_share", "woe": "WoE"})
    out["iv"] = _py(iv)
    return out


@case("information_value_small")
def _(d):
    return _iv(*m.information_value(d("iv_small"), "bin", "y", smoothing=0))


@case("information_value_declared")
def _(d):
    return _iv(*m.information_value(d("iv_small"), "bin", "y", smoothing=0.5, bin_order=["A", "B", "C"]))


@case("information_value_large")
def _(d):
    return _iv(*m.information_value(d("pd_large"), "grade", "y"))


@case("cier_small")
def _(d):
    return {"ratio": m.conditional_information_entropy_ratio(d("entropy_small"), "rate", "n")}


@case("cier_large")
def _(d):
    return {"ratio": m.conditional_information_entropy_ratio(d("entropy_large"), "rate", "n")}


@case("mutual_information_small")
def _(d):
    return {"mi": m.kullback_leibler_dist(d("entropy_small"), "rate", "n")}


@case("mutual_information_large")
def _(d):
    return {"mi": m.kullback_leibler_dist(d("entropy_large"), "rate", "n")}


@case("clar_small")
def _(d):
    return {"clar": m.cumulative_lgd_accuracy_ratio(d("clar_small"), "p", "y")}


@case("clar_large")
def _(d):
    return {"clar": m.cumulative_lgd_accuracy_ratio(d("lgd_large"), "pgrade", "rgrade")}


@case("loss_capture_ratio_small")
def _(d):
    frame = d("lcr_small")
    return {"lcr": m.loss_capture_ratio(frame.ead, frame.p, frame.y)}


@case("loss_capture_ratio_large")
def _(d):
    frame = d("lgd_large")
    return {"lcr": m.loss_capture_ratio(frame.ead, frame.predicted, frame.realised)}


# ---------------------------------------------------------------------------
# Calibration
# ---------------------------------------------------------------------------

_GRADE_FIELDS = {
    "predicted_pd": "Predicted PD",
    "n": "Total count",
    "defaults": "Defaults",
    "default_rate": "Actual Default Rate",
    "p_value": "p_value",
    "reject": "Reject H0",
}


@case("binomial_small")
def _(d):
    return _by_label(m.binomial_test(d("pd_small"), "grade", "y", "pd").set_index("Rating class"), _GRADE_FIELDS)


@case("binomial_large")
def _(d):
    return _by_label(m.binomial_test(d("pd_large"), "grade", "y", "pd").set_index("Rating class"), _GRADE_FIELDS)


@case("jeffreys_small")
def _(d):
    return _by_label(m.jeffreys_test(d("jeffreys_small"), "grade", "y", "pd").set_index("Rating class"), _GRADE_FIELDS)


@case("jeffreys_large")
def _(d):
    return _by_label(m.jeffreys_test(d("pd_large"), "grade", "y", "pd").set_index("Rating class"), _GRADE_FIELDS)


def _hosmer(frame, **kwargs):
    p_value, reject = m.hosmer_test(frame, "grade", "y", "pd", **kwargs)
    return {"p_value": _py(p_value), "reject": _py(reject)}


@case("hosmer_small")
def _(d):
    return _hosmer(d("pd_small"))


@case("hosmer_large")
def _(d):
    return _hosmer(d("pd_large"))


@case("hosmer_large_ddof2")
def _(d):
    return _hosmer(d("pd_large"), ddof=2)


def _spiegelhalter(frame):
    z, reject = m.spiegelhalter_test(frame, "grade", "y", "pd")
    return {"z": _py(z), "reject": _py(reject)}


@case("spiegelhalter_small")
def _(d):
    return _spiegelhalter(d("pd_small"))


@case("spiegelhalter_large")
def _(d):
    return _spiegelhalter(d("pd_large"))


@case("brier_small")
def _(d):
    return {"brier": m.brier_score(d("pd_small"), "grade", "y", "pd")}


@case("brier_large")
def _(d):
    return {"brier": m.brier_score(d("pd_large"), "grade", "y", "pd")}


@case("redelmeier_small")
def _(d):
    z, p = m.redelmeier_test(d("redelmeier_small"), default_flag="y", first_pd="p1", second_pd="p2")
    return {"z": _py(z), "p_value": _py(p)}


@case("redelmeier_large")
def _(d):
    z, p = m.redelmeier_test(d("pd_large"), default_flag="y", first_pd="pd", second_pd="pd2")
    return {"z": _py(z), "p_value": _py(p)}


def _normal(frame):
    row = m.normal_test(frame.predicted, frame.realised).iloc[0]
    return {"estimate": _py(row.estimate), "z": _py(row.t_stat), "p_value": _py(row.p_value), "reject": _py(row.outcome)}


@case("normal_test_small")
def _(d):
    return _normal(d("normal_small"))


@case("normal_test_large")
def _(d):
    return _normal(d("normal_large"))


# ---------------------------------------------------------------------------
# Association
# ---------------------------------------------------------------------------


@case("kendall_small")
def _(d):
    frame = d("assoc_small")
    tau, p = m.kendall_tau(frame.x, frame.y)
    return {"tau": _py(tau), "p_value": _py(p)}


@case("kendall_large")
def _(d):
    frame = d("lgd_large")
    tau, p = m.kendall_tau(frame.predicted, frame.realised)
    return {"tau": _py(tau), "p_value": _py(p)}


@case("kendall_large_tau_c")
def _(d):
    frame = d("lgd_large")
    tau, _ = m.kendall_tau(frame.pgrade, frame.rgrade, variant="c")
    return {"tau": _py(tau)}


@case("somersd_small_table")
def _(d):
    return {"d": _py(m.somersd([[3, 1], [1, 3]]).statistic)}


@case("somersd_large")
def _(d):
    frame = d("lgd_large")
    return {"d": _py(m.somersd(frame.pgrade, frame.rgrade).statistic)}


@case("spearman_small")
def _(d):
    frame = d("assoc_small")
    result = m.spearman_correlation(frame.x, frame.y)
    return {"rho": _py(result.statistic), "p_value": _py(result.pvalue)}


@case("spearman_large")
def _(d):
    frame = d("lgd_large")
    result = m.spearman_correlation(frame.predicted, frame.realised)
    return {"rho": _py(result.statistic), "p_value": _py(result.pvalue)}


@case("pearson_small")
def _(d):
    frame = d("assoc_small")
    result = m.pearson_correlation(frame.x, frame.y)
    return {"r": _py(result.statistic), "p_value": _py(result.pvalue)}


@case("pearson_large")
def _(d):
    frame = d("lgd_large")
    result = m.pearson_correlation(frame.predicted, frame.realised)
    return {"r": _py(result.statistic), "p_value": _py(result.pvalue)}


# ---------------------------------------------------------------------------
# Stability
# ---------------------------------------------------------------------------


def _hhi(frame, **kwargs):
    cv, hhi = m.herfindahl_test(frame, "grade", **kwargs)
    return {"cv": _py(cv), "hhi": _py(hhi)}


@case("herfindahl_small")
def _(d):
    return _hhi(d("grades_small_initial"))


@case("herfindahl_declared")
def _(d):
    return _hhi(d("grades_small_initial"), rating_order=["A", "B", "C"])


@case("herfindahl_large")
def _(d):
    return _hhi(d("grades_large_initial"))


def _hhi_multi(initial, current):
    result = m.herfindahl_multiple_period_test(initial, current, "grade")
    total = result.loc["total"]
    out = _by_label(result.drop(index="total"), {"n_initial": "N_initial", "n_current": "N_current"})
    out.update(
        {
            "h_initial": _py(total.h_initial),
            "h_current": _py(total.h_current),
            "z": _py(total.z_stat),
            "p_value": _py(total.p_value),
            "reject": _py(total.reject),
        }
    )
    return out


@case("herfindahl_multi_small")
def _(d):
    return _hhi_multi(d("grades_small_initial"), d("grades_small_current"))


@case("herfindahl_multi_large")
def _(d):
    return _hhi_multi(d("grades_large_initial"), d("grades_large_current"))


def _psi(table, psi):
    out = _by_label(table, {"expected": "expected", "actual": "actual"})
    out["psi"] = _py(psi)
    return out


@case("psi_small")
def _(d):
    return _psi(*m.population_stability_index(d("psi_small"), "period", "bin", expected="old", actual="new", smoothing=0))


@case("psi_declared")
def _(d):
    return _psi(
        *m.population_stability_index(
            d("psi_small"), "period", "bin", expected="old", actual="new", bin_order=["A", "B", "C"]
        )
    )


@case("psi_large")
def _(d):
    return _psi(*m.population_stability_index(d("psi_large"), "period", "bin", expected="old", actual="new"))


@case("migration_bandwidth_small")
def _(d):
    upper, lower = m.migration_matrices_statistics(d("migration_small"), "start", "end")
    return {"upper": _py(upper), "lower": _py(lower)}


@case("migration_bandwidth_large")
def _(d):
    upper, lower = m.migration_matrices_statistics(d("migration_large"), "start", "end")
    return {"upper": _py(upper), "lower": _py(lower)}


def _stability(frame, **kwargs):
    z, cdf = m.migration_matrix_stability(frame, "start", "end", **kwargs)
    return {**_matrix(z, "z"), **_matrix(cdf, "cdf")}


@case("migration_stability_small")
def _(d):
    return _stability(d("migration_small"))


@case("migration_stability_large")
def _(d):
    return _stability(d("migration_large"))


@case("migration_stability_large_initial_counts")
def _(d):
    counts = d("migration_large_initial_counts").set_index("grade")["count"]
    return _stability(d("migration_large"), initial_counts=counts)


# ---------------------------------------------------------------------------
# LGD validation
# ---------------------------------------------------------------------------

_T_FIELDS = {
    "n": "N",
    "realised_mean": "realised_lgd_mean",
    "pred_mean": "pred_lgd_mean",
    "s2": "s2",
    "mean_error": "mean_error",
    "t": "t_stat",
    "p_value": "p_value",
}


def _lgd_t(frame, **kwargs):
    return _by_label(m.lgd_t_test(frame, "realised", "predicted", **kwargs).set_index("segment"), _T_FIELDS)


@case("lgd_t_test_portfolio_small")
def _(d):
    return _lgd_t(d("lgd_small"))


@case("lgd_t_test_segment_small")
def _(d):
    return _lgd_t(d("lgd_small"), level="segment", segment_col="segment")


@case("lgd_t_test_portfolio_large")
def _(d):
    return _lgd_t(d("lgd_large"))


@case("lgd_t_test_segment_large")
def _(d):
    return _lgd_t(d("lgd_large"), level="segment", segment_col="segment")


def _elbe(frame):
    row = m.elbe_t_test(frame, "realised", "predicted").iloc[0]
    return {
        "facilities": _py(row.facilities),
        "lgd_mean": _py(row.lgd_mean),
        "elbe_mean": _py(row.elbe_mean),
        "t": _py(row.t_stat),
        "p_value": _py(row.p_value),
    }


@case("elbe_t_test_small")
def _(d):
    return _elbe(d("lgd_small"))


@case("elbe_t_test_large")
def _(d):
    return _elbe(d("lgd_large"))


@case("loss_shortfall_small")
def _(d):
    return {"shortfall": m.loss_shortfall(d("lgd_small"), "ead", "predicted", "realised")}


@case("loss_shortfall_large")
def _(d):
    return {"shortfall": m.loss_shortfall(d("lgd_large"), "ead", "predicted", "realised")}


@case("mean_absolute_deviation_small")
def _(d):
    return {"mad": m.mean_absolute_deviation(d("lgd_small"), "ead", "predicted", "realised")}


@case("mean_absolute_deviation_large")
def _(d):
    return {"mad": m.mean_absolute_deviation(d("lgd_large"), "ead", "predicted", "realised")}


# ---------------------------------------------------------------------------
# Execution and provenance
# ---------------------------------------------------------------------------


def make_loader(data_dir: Path = DATA_DIR):
    cache: dict[str, pd.DataFrame] = {}

    def load(name: str) -> pd.DataFrame:
        if name not in cache:
            cache[name] = pd.read_csv(data_dir / f"{name}.csv")
        return cache[name].copy()

    return load


def compute_all(data_dir: Path = DATA_DIR) -> dict[str, dict[str, object]]:
    """Run every case against Meliora and return ``{case: {field: value}}``."""
    load = make_loader(data_dir)
    return {name: {field: _py(value) for field, value in function(load).items()} for name, function in CASES.items()}


def to_records(results: dict[str, dict[str, object]]) -> list[dict]:
    return [{"case": case, "field": field, "value": value} for case, fields in results.items() for field, value in fields.items()]


def from_records(records: list[dict]) -> dict[str, dict[str, object]]:
    out: dict[str, dict[str, object]] = {}
    for record in records:
        out.setdefault(record["case"], {})[record["field"]] = record["value"]
    return out


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def data_hash(data_dir: Path = DATA_DIR) -> str:
    """SHA-256 over every CSV in name order, so any data change is detected."""
    digest = hashlib.sha256()
    for path in sorted(data_dir.glob("*.csv")):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def python_meta() -> dict:
    import scipy
    import sklearn

    return {
        "language": "python",
        "version": sys.version.split()[0],
        "packages": {
            "meliora": m.__version__,
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit-learn": sklearn.__version__,
        },
        "generated": dt.date.today().isoformat(),
        "data_sha256": data_hash(),
        "script_sha256": file_hash(HERE / "cases.py"),
    }


if __name__ == "__main__":
    generate_data()
    results = compute_all()
    target = HERE / "python" / "results.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps({"meta": python_meta(), "results": to_records(results)}, indent=1), encoding="utf-8")
    print(f"{len(results)} cases, {sum(len(v) for v in results.values())} fields -> {target}")
