# Changelog

## 0.2.0.dev0 — unreleased

- Correct observation-level Brier and Spiegelhalter calculations, Pearson correlation, class-conditional KS, ordinal CLAR, exposure-based LCR, migration formulas, normal-test inference and paired Brier comparison variance.
- Honor named columns, variants, alternatives and significance levels; validate undefined and invalid inputs; avoid caller-data mutation.
- Document smoothing, grade order, ties, inference direction and all return schemas. Export all 29 methods from `meliora`.
- Replace stale examples and placeholder tests with explained numerical regressions, contract checks and a complete executable notebook.
- Remove the unrelated ECB GDP notebook; archive exploratory material, remove duplicate example data, repair Sphinx links and reduce distribution payloads.
- Modernize Python/dependency support and add CI gates for tests, docs, examples and packages. Remove automatic publishing and template synchronization workflows.

The [migration guide](docs/source/migration.md) lists behavioral and API changes. No PyPI release has been made for this development version.
