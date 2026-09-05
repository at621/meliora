# Changelog

## 0.2 — 2026-09-05

- Correct observation-level Brier and Spiegelhalter calculations, Pearson correlation, class-conditional KS, ordinal CLAR, exposure-based LCR, migration formulas, normal-test inference and paired Brier comparison variance.
- Honor named columns, variants, alternatives and significance levels; validate undefined and invalid inputs; avoid caller-data mutation.
- Document smoothing, grade order, ties, inference direction and all return schemas. Export all 29 methods from `meliora`.
- Replace stale examples and placeholder tests with explained numerical regressions, contract checks and a complete executable notebook.
- Remove unrelated research notebooks, legacy datasets, archived R/MATLAB code and reference-paper copies. Keep statistical source links in method documentation.
- Remove unused editor/publishing configuration, stylesheets, redundant documentation build wrappers and the unused Matplotlib dependency. Repair references and retain the supported examples and validation tools.
- Replace the 29 Sphinx method stubs with complete Markdown references readable on GitHub. Add a documentation directory, update README links and check that reference pages stay synchronized with the function docstrings.
- Require Python 3.11 or newer; Python 3.9 and 3.10 are no longer supported. Minimum dependencies are NumPy 1.26, pandas 2.1, SciPy 1.11 and scikit-learn 1.3.
- Add CI gates for tests, docs, examples and packages. Replace automatic publishing with a manual release workflow that defaults to validation only. Remove template synchronization.
- Prepare the 0.2 release metadata and PyPI README, including permanent documentation links and package installation instructions.

This release changes statistical results and some function arguments; the method reference documents the current behavior.
