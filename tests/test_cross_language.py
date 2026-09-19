"""Cross-language comparison of all 29 methods against R, SAS and MATLAB.

Unlike ``test_methods.py``, which uses only self-contained oracles, this module
deliberately compares Meliora with frozen result files produced by independent
implementations in other languages. The inputs are the CSV datasets in
``tests/oracles/data`` and the case definitions in ``tests/oracles/cases.py``;
each language has an oracle script under ``tests/oracles/<language>/`` whose
output is committed as ``results.json`` together with a provenance stamp.

Three layers of tests:

* ``test_oracle_is_current`` refuses a frozen file whose stamp does not match
  the current datasets, case definitions or oracle script.
* ``test_matches_oracle`` compares every field of every case with the oracle,
  except fields listed in ``KNOWN_DIVERGENCE``.
* ``test_known_divergence`` checks that each documented divergence still
  diverges, so the list cannot silently go stale.

Set ``MELIORA_ORACLES=r,matlab`` to regenerate the frozen files live before the
comparison (``tests/oracles/run_oracles.py`` documents how each language is
located). A language whose results file is absent is skipped, not failed.
"""

from __future__ import annotations

import fnmatch
import json
import math
import os
import subprocess
import sys

import pytest

from tests.oracles import cases

LANGUAGES = ("r", "sas", "matlab")
SCRIPTS = {"r": "r/oracle.R", "sas": "sas/oracle.sas", "matlab": "matlab/oracle.m"}
# Relative tolerance for every nonzero value, including tiny p-values, so that
# a p-value of 1e-13 cannot "match" 3e-13; an absolute floor only for values
# that are zero up to floating-point noise (p-values below the floor, such as
# 1e-78, therefore count as equal whatever algorithm produced them).
REL_TOL = 1e-8
ZERO_TOL = 1e-14

# (language, case glob, field glob) -> why the oracle legitimately differs.
# Statistics agree in every case; the entries below are p-value algorithms.
KNOWN_DIVERGENCE: dict[tuple[str, str, str], str] = {
    ("r", "ks_small_ties", "pvalue"): "R uses the asymptotic distribution with ties; SciPy uses the exact tie-free distribution",
    ("matlab", "ks_*", "pvalue"): "kstest2 only offers the asymptotic p-value; SciPy uses the exact distribution",
    ("matlab", "spearman_small", "p_value"): "MATLAB uses the exact permutation distribution for n=4; SciPy uses the t approximation",
    ("sas", "ks_*", "pvalue"): "PROC NPAR1WAY reports the asymptotic p-value; SciPy uses the exact distribution",
    ("sas", "kendall_small", "p_value"): "PROC CORR uses the asymptotic Kendall p-value; SciPy is exact for n<50 without ties",
}

EXPECTED = cases.compute_all()


def _oracle_path(language: str):
    return cases.HERE / language / "results.json"


def _oracle(language: str) -> dict:
    path = _oracle_path(language)
    if not path.exists():
        pytest.skip(f"{language} oracle not generated: run tests/oracles/run_oracles.py {language}")
    return json.loads(path.read_text(encoding="utf-8"))


def _number(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    return float(value)


def _close(expected, actual) -> bool:
    expected, actual = _number(expected), _number(actual)
    if expected is None or actual is None:
        return expected is None and actual is None
    if max(abs(expected), abs(actual)) < ZERO_TOL:
        return True
    return math.isclose(expected, actual, rel_tol=REL_TOL, abs_tol=0)


def _divergence(language: str, case: str, field: str) -> str | None:
    for (lang, case_glob, field_glob), reason in KNOWN_DIVERGENCE.items():
        if lang == language and fnmatch.fnmatchcase(case, case_glob) and fnmatch.fnmatchcase(field, field_glob):
            return reason
    return None


@pytest.mark.parametrize("language", LANGUAGES)
def test_regenerate_oracle(language):
    """Opt-in live regeneration; runs before the comparisons in this module."""
    wanted = [item.strip() for item in os.environ.get("MELIORA_ORACLES", "").split(",") if item.strip()]
    if language not in wanted:
        pytest.skip("set MELIORA_ORACLES=<language,...> to regenerate live")
    subprocess.run([sys.executable, str(cases.HERE / "run_oracles.py"), language], check=True)
    assert _oracle_path(language).exists()


@pytest.mark.parametrize("language", LANGUAGES)
def test_oracle_is_current(language):
    meta = _oracle(language)["meta"]
    stale = []
    if meta.get("data_sha256") != cases.data_hash():
        stale.append("datasets")
    if meta.get("cases_sha256") != cases.file_hash(cases.HERE / "cases.py"):
        stale.append("cases.py")
    if meta.get("script_sha256") != cases.file_hash(cases.HERE / SCRIPTS[language]):
        stale.append(SCRIPTS[language])
    assert not stale, f"{language} oracle is stale for {stale}; run tests/oracles/run_oracles.py {language}"


@pytest.mark.parametrize("language", LANGUAGES)
def test_oracle_covers_every_case(language):
    actual = cases.from_records(_oracle(language)["results"])
    missing = sorted(set(EXPECTED) - set(actual))
    extra = sorted(set(actual) - set(EXPECTED))
    assert not missing and not extra, f"missing cases {missing}; unexpected cases {extra}"


@pytest.mark.parametrize("case", list(EXPECTED))
@pytest.mark.parametrize("language", LANGUAGES)
def test_matches_oracle(language, case):
    actual = cases.from_records(_oracle(language)["results"]).get(case)
    assert actual is not None, f"{case} missing from the {language} oracle"
    problems = []
    for field, expected in EXPECTED[case].items():
        if _divergence(language, case, field):
            continue
        if field not in actual:
            problems.append(f"{field}: missing from oracle")
        elif not _close(expected, actual[field]):
            problems.append(f"{field}: meliora={expected!r} {language}={actual[field]!r}")
    unexpected = sorted(set(actual) - set(EXPECTED[case]))
    if unexpected:
        problems.append(f"fields not produced by Meliora: {unexpected}")
    assert not problems, "\n".join(problems)


def _divergent_fields():
    for language in LANGUAGES:
        for case, fields in EXPECTED.items():
            for field in fields:
                reason = _divergence(language, case, field)
                if reason:
                    yield pytest.param(language, case, field, reason, id=f"{language}-{case}-{field}")


@pytest.mark.parametrize("language, case, field, reason", list(_divergent_fields()))
def test_known_divergence(language, case, field, reason):
    """A documented divergence that no longer diverges must be removed from the list."""
    actual = cases.from_records(_oracle(language)["results"]).get(case, {})
    if field not in actual:
        pytest.xfail(f"{reason} (oracle does not emit the field)")
    if _close(EXPECTED[case][field], actual[field]):
        pytest.fail(f"{language} now matches Meliora for {case}.{field}; remove the KNOWN_DIVERGENCE entry")
    pytest.xfail(f"{reason}: meliora={EXPECTED[case][field]!r} {language}={actual[field]!r}")
