# Getting started

Use Python 3.11 or newer. From a repository checkout:

```bash
python -m venv .venv
# Activate .venv for your shell, then:
python -m pip install -e ".[dev]"
```

The changes documented here are the **0.2.0.dev0 development API**. PyPI 0.1.2 does not include these fixes.

```python
import pandas as pd
import meliora as m

portfolio = pd.DataFrame({
    'grade': ['A', 'A', 'B', 'B'],
    'default': [0, 1, 0, 1],
    'pd': [.2, .2, .6, .6],
})
score = m.brier_score(portfolio, 'grade', 'default', 'pd')
assert abs(score - .30) < 1e-12
```

All methods are available both from `meliora` and `meliora.core`. Required observations must be non-missing; numeric inputs must be finite. Arrays are paired by position, ignoring Series indices. Functions never modify input data. Errors use `ValueError` or, for a wrong table type, `TypeError`.

## Worked examples

[examples.ipynb](https://github.com/at621/meliora/blob/main/examples/examples.ipynb) contains a self-contained section for every public method: purpose, formula, assumptions, fixed data, public call, asserted expected result, visible output and interpretation.

Execute every supported notebook from the repository root with:

```bash
python scripts/run_notebooks.py
```

The runner uses the current Python interpreter, creates a fresh kernel, and writes results to `.cache/executed/`. Use `--write` to refresh the committed outputs. No external datasets, random seeds, R installation or user kernel configuration are needed.

## Choosing a method

Use calibration tests for PD level errors, AUC/Gini or ordinal measures for discrimination, migration/PSI/concentration metrics for population changes, and paired LGD tests or exposure-weighted errors for LGD validation. A metric without a sampling model has no p-value. A large p-value does not prove model validity. Grade/segment/cell tests do not automatically adjust for multiple testing.

Read each method's assumptions before using a decision threshold. No generic traffic-light cutoffs are applied.
