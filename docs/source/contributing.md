# Contributing

Install the development extra and run the commands in [Validation](validation.md). Run `ruff check .` and `ruff format --check src tests scripts` as well.

For each public method, add or update its static NumPy-style docstring, method catalogue entry (`docs/method_catalog.json`), Sphinx page, independently explained numerical regression test, input/edge tests and complete notebook section. The catalogue gate prevents missing exports, parameter drift and disconnected notebook examples. Record behavioral changes in the changelog.

Keep examples self-contained and deterministic. Use small fixtures with an auditable derivation, not saved output as the numerical oracle. Expected-value tolerances should reflect floating-point calculations; use absolute tolerance near zero. Do not turn failing numerical tests into placeholders or silently change the statistical hypothesis.

Run `python scripts/run_notebooks.py --write` when intentionally refreshing notebook outputs. Commit source and rendered outputs together. Keep examples focused on the public API and cite statistical sources directly in method documentation.

Publishing to PyPI is a separate maintainer decision. Do not add credentials or uploads to ordinary test workflows.
