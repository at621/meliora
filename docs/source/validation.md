# Validation and acceptance checklist

The [per-method checklist](https://github.com/at621/meliora/blob/main/docs/method_checklist.md) covers all 29 exported functions. Its eight criteria distinguish explanatory documentation, functioning examples, passing regression tests and independent numerical evidence. Every method has a dedicated explained regression test; shared contract tests cover invalid data and non-mutation for every export.

```bash
python -m pytest --cov=meliora --cov-report=term-missing
python scripts/check_catalog.py
python -m sphinx -W --keep-going -b html docs/source docs/_build/html
python -m sphinx -W -b doctest docs/source docs/_build/doctest
python scripts/run_notebooks.py
python -m build
python -m twine check dist/*
python scripts/check_distribution.py
```

CI runs tests on Python 3.11–3.14 on Linux and Python 3.13 on Windows. Warnings are test failures, and branch coverage must be at least 95%. The catalogue check also verifies that every committed Markdown reference matches its function docstring and has a matching README link. The docs job executes those reference examples, builds the documentation without warnings, runs the notebooks and checks distribution content. CI has read-only repository permissions and no publishing step.

## Numerical evidence

Tests use explicit small count tables, closed-form probabilities, integration of a posterior density, complete Bernoulli enumeration, pairwise concordance, hand-derived curve areas, sample variances and invariants. Expected results are not copied from package outputs. See the docstring of each `test_<method>` in `tests/test_methods.py` for its calculation. SciPy wrapper tests check coefficient formulas or known results and verify directional options.

The regression scope is the documented formula and API contract. It does not certify regulatory suitability, justify asymptotic inference on small samples, or establish equivalence with every similarly named external implementation. In particular, LCR's exposure axis and Redelmeier's midpoint null are explicit conventions.
