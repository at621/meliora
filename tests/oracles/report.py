"""Write RESULTS.md and RESULTS.csv: one row per field with the value from every language.

Usage::

    python tests/oracles/report.py

The comparison logic is imported from tests/test_cross_language.py so the
report and the test suite can never disagree.
"""

from __future__ import annotations

import csv
import datetime as dt
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))

from tests import test_cross_language as tcl  # noqa: E402
from tests.oracles import cases  # noqa: E402

# Book numbering and names, in the README order. Prefixes are matched longest first.
METHODS = [
    (1, "ROC AUC", "roc_auc"),
    (2, "Gini coefficient", "gini"),
    (3, "Kolmogorov-Smirnov statistic", "ks"),
    (4, "Minimum empirical threshold error", "bayesian_error_rate"),
    (5, "Information value", "information_value"),
    (6, "Conditional information entropy ratio", "cier"),
    (7, "Mutual information", "mutual_information"),
    (8, "Cumulative LGD accuracy ratio", "clar"),
    (9, "Loss capture ratio", "loss_capture_ratio"),
    (10, "Binomial test", "binomial"),
    (11, "Jeffreys test", "jeffreys"),
    (12, "Hosmer test", "hosmer"),
    (13, "Spiegelhalter test", "spiegelhalter"),
    (14, "Brier score", "brier"),
    (15, "Redelmeier test", "redelmeier"),
    (16, "Normal test for annual default rates", "normal_test"),
    (17, "Kendall's tau", "kendall"),
    (18, "Somers' D", "somersd"),
    (19, "Spearman's rho", "spearman"),
    (20, "Pearson's r", "pearson"),
    (21, "Herfindahl index", "herfindahl"),
    (22, "Multiple-period Herfindahl test", "herfindahl_multi"),
    (23, "Population stability index", "psi"),
    (24, "Migration bandwidth", "migration_bandwidth"),
    (25, "Adjacent-cell shape checks", "migration_stability"),
    (26, "LGD t-test", "lgd_t_test"),
    (27, "ELBE t-test", "elbe_t_test"),
    (28, "Loss shortfall", "loss_shortfall"),
    (29, "Exposure-weighted mean absolute error", "mean_absolute_deviation"),
]
LANGUAGES = [("Python", "python"), ("R", "r"), ("MATLAB", "matlab"), ("SAS", "sas")]


def method_of(case: str):
    for number, name, prefix in sorted(METHODS, key=lambda m: -len(m[2])):
        if case == prefix or case.startswith(prefix + "_"):
            return number, name
    raise KeyError(case)


def load(language: str):
    path = HERE / language / "results.json"
    if not path.exists():
        return None, None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload["meta"], cases.from_records(payload["results"])


def fmt(value) -> str:
    """Twelve significant digits for the Markdown table; the CSV keeps full precision."""
    if value is None:
        return "NaN"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return str(value)
    return f"{value:.12g}"


def raw(value) -> str:
    if value is None:
        return "NaN"
    if isinstance(value, bool):
        return str(value)
    return repr(value)


def cell(language: str, case: str, field: str, expected, actual) -> str:
    """The oracle's own value; a trailing marker shows how it compares with Meliora."""
    if actual is None:
        return "not run"
    fields = actual.get(case, {})
    if field not in fields:
        return "missing"
    value = fields[field]
    if tcl._close(expected, value):
        return fmt(value)
    marker = "(documented)" if tcl._divergence(language, case, field) else "**DIFFERS**"
    return f"{fmt(value)} {marker}"


def main() -> None:
    expected = cases.compute_all()
    loaded = {key: load(key) for _, key in LANGUAGES}
    loaded["python"] = (cases.python_meta(), expected)
    totals = {key: {"match": 0, "differs": 0, "documented": 0, "not run": 0} for _, key in LANGUAGES}
    rows = []
    for case, fields in expected.items():
        number, name = method_of(case)
        for field, value in fields.items():
            cells, raws = [], []
            for _, key in LANGUAGES:
                _, actual = loaded[key]
                if key == "python":
                    cells.append(fmt(value))
                    raws.append(raw(value))
                    continue
                text = cell(key, case, field, value, actual)
                cells.append(text)
                raws.append("" if actual is None or field not in actual.get(case, {}) else raw(actual[case][field]))
                bucket = (
                    "not run" if text == "not run"
                    else "documented" if text.endswith("(documented)")
                    else "differs" if text.endswith("**DIFFERS**") or text == "missing"
                    else "match"
                )
                totals[key][bucket] += 1
            rows.append((number, name, case, field, cells, raws))
    rows.sort(key=lambda r: (r[0], r[2]))

    lines = [
        "# Cross-language test results",
        "",
        f"Generated {dt.date.today().isoformat()} by `python tests/oracles/report.py` from the frozen oracle files.",
        "Every value is the number the named language produced; Python is Meliora itself.",
        f"A value that differs from Meliora by more than relative tolerance {tcl.REL_TOL:g} is marked",
        "**DIFFERS**, or (documented) when the field is listed in `KNOWN_DIVERGENCE` in",
        "`tests/test_cross_language.py`. Values are shown to 12 significant digits;",
        "`RESULTS.csv` holds the same table at full precision.",
        "",
        "## Summary",
        "",
        "| Language | Version | Fields matching | Fields differing | Documented divergences | Not run |",
        "|---|---|---|---|---|---|",
    ]
    for label, key in LANGUAGES:
        meta = loaded[key][0]
        version = "" if meta is None else str(meta.get("version", ""))
        if key == "python":
            lines.append(f"| {label} | {version} | reference ({len(rows)} fields, {len(expected)} cases) | | | |")
        else:
            t = totals[key]
            counts = " | ".join(str(t[bucket]) for bucket in ("match", "differs", "documented", "not run"))
            lines.append(f"| {label} | {version} | {counts} |")
    lines += [
        "",
        "## Values by test",
        "",
        "| # | Method | Case | Field | Python | R | MATLAB | SAS |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for number, name, case, field, cells, _ in rows:
        lines.append(f"| {number} | {name} | `{case}` | `{field}` | " + " | ".join(cells) + " |")
    lines.append("")
    with (HERE / "RESULTS.md").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("\n".join(lines))

    with (HERE / "RESULTS.csv").open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["number", "method", "case", "field", "python", "r", "matlab", "sas"])
        for number, name, case, field, _, raws in rows:
            writer.writerow([number, name, case, field, *raws])
    print(f"{len(rows)} fields, {len(expected)} cases -> RESULTS.md and RESULTS.csv")


if __name__ == "__main__":
    main()
