# Contributing to Meliora

See the [contribution guide](docs/source/contributing.md) and [validation commands](docs/source/validation.md). Every public statistical method must satisfy the [eight-item checklist](docs/method_checklist.md).

Use Python 3.11+ and `python -m pip install -e ".[dev]"`. Run `ruff check .`, `ruff format --check src tests scripts`, the test suite, catalogue check, Sphinx builds, notebook execution and package checks before submitting changes.
