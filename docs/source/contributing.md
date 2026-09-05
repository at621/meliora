# Contributing

Install the development extra and run the commands in [Validation](validation.md). Run `ruff check .` and `ruff format --check src tests scripts` as well.

For each public method, add or update its static NumPy-style docstring, method catalogue entry (`docs/method_catalog.json`), independently explained numerical regression test, input/edge tests and complete notebook section. Run `python scripts/render_reference.py` to refresh the complete Markdown reference pages from the docstrings and catalogue. Update the README method list and Sphinx index when adding a method. The catalogue gate prevents missing exports, parameter drift, stale reference pages and disconnected notebook examples. Record behavioral changes in the changelog.

Keep examples self-contained and deterministic. Use small fixtures with an auditable derivation, not saved output as the numerical oracle. Expected-value tolerances should reflect floating-point calculations; use absolute tolerance near zero. Do not turn failing numerical tests into placeholders or silently change the statistical hypothesis.

Run `python scripts/run_notebooks.py --write` when intentionally refreshing notebook outputs. Commit source and rendered outputs together. Keep examples focused on the public API and cite statistical sources directly in method documentation.

Publishing to PyPI is a separate maintainer decision. Do not add credentials or uploads to ordinary test workflows.

## Preparing and publishing a release

Set the final version in `src/meliora/__init__.py`, update the changelog and point the README and package documentation links at the matching tag. Run the validation commands, merge the changes into `main` and create that tag (for example, `v0.2`).

In GitHub Actions, run **Release to PyPI** from `main`, enter the tag and leave **Upload the validated packages to PyPI** unchecked. The workflow builds the packages, validates the documentation and examples, and tests the built wheel on Python 3.11–3.14 and Windows. Its `release-distributions` artifact contains the checked packages.

When publishing is intended, run the same workflow with the upload option checked. The workflow validates the release again before uploading the tested artifacts. The existing `PYPI_PASSWORD` GitHub repository secret must contain a valid PyPI API token scoped to `meliora`; GitHub does not expose secret values for local verification. Branch pushes, pull requests and tag creation do not trigger uploads.
