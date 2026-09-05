# Meliora

[![CI](https://github.com/at621/meliora/actions/workflows/CI.yml/badge.svg)](https://github.com/at621/meliora/actions/workflows/CI.yml) [![PyPI](https://badge.fury.io/py/meliora.svg)](https://pypi.org/project/meliora/)

Statistical tools for credit-risk model validation: **29 public methods** covering PD calibration, discrimination, ordinal association, population stability, migration and LGD errors.

This checkout contains **0.2.0.dev0**, with corrected statistical calculations and input handling. PyPI 0.1.2 does not contain these changes. Read the [migration guide](docs/source/migration.md) before comparing results with the previous version.

```bash
# Python 3.11 or newer, from a checkout
python -m pip install -e ".[dev]"
```

```python
import meliora as m
import pandas as pd

portfolio = pd.DataFrame({
    'grade': ['A', 'A', 'B', 'B'],
    'default': [0, 1, 0, 1],
    'pd': [.2, .2, .6, .6],
})
print(m.brier_score(portfolio, 'grade', 'default', 'pd'))  # 0.30
```

- [Worked Jupyter examples for every method](examples/examples.ipynb): fixed data, formulas, assumptions, checked outputs and interpretation.
- [Per-method acceptance checklist](docs/method_checklist.md): evidence for all eight criteria.
- [Method catalogue](docs/method_catalog.json) and [API documentation source](docs/source/index.rst).
- [Validation commands and numerical evidence](docs/source/validation.md).
- [Changelog](CHANGELOG.md) and [contribution guide](CONTRIBUTING.md).

Run `python -m pytest --cov=meliora` and `python scripts/run_notebooks.py` from the repository root. Build the docs with `python -m sphinx -W -b html docs/source docs/_build/html`.

Runtime dependencies are NumPy, pandas, SciPy and scikit-learn. Inputs are validated and never modified. Each method documents its statistical assumptions; descriptive metrics do not invent p-values or universal acceptance thresholds. The automated suite validates documented formulas and contracts, not regulatory suitability.

Exploratory notebooks are under [examples/research](examples/research/README.md). Historical datasets and reference material remain available in the repository but are excluded from distributions. GitHub CI validates tests, docs, notebooks and builds; it does not publish to PyPI.
