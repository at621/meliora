# Per-method acceptance checklist

Validated for the 0.2.0.dev0 development cleanup on 5 September 2026.

The original audit found that no method met every criterion. All 29 methods now
meet the eight criteria below for their **documented conventions and tested
fixtures**. This is software/formula validation, not regulatory certification or
proof that asymptotic inference is appropriate for a particular portfolio.

- [x] **M — Method explanation:** purpose, formula, assumptions, direction/null where relevant, interpretation, limitations, traceable source.
- [x] **D — Docstring:** real parameter names, domains/defaults, returns, errors, side effects, notes, reference and working example.
- [x] **N — Notebook call:** a real public function call in an identifiable code cell.
- [x] **W — Worked notebook:** fixed data, explanation, asserted expected result, visible output, interpretation and successful clean Run All.
- [x] **T — Regression:** a non-placeholder automated test calls the method and checks numerical results.
- [x] **R — Numerical evidence:** a hand derivation, independent enumeration/integration, or a standard reference matched to the exact fixture and convention.
- [x] **E — Edges/contracts:** relevant boundaries, options, degeneracy, renamed columns, invariants and invalid inputs; every export also checks missing/empty data and non-mutation.
- [x] **L — Documentation link:** method-specific Sphinx page resolves to the actual exported symbol and builds without warnings.

Private helpers have documented internal contracts and coverage through callers;
they do not need separate user tutorials. M and R include human mathematical
review. `scripts/check_catalog.py` checks structural links, signatures and example
calls; pytest, Sphinx and the notebook runner provide separate execution gates.

## Results by method

Notebook cell numbers count both markdown and code cells, starting from one.
Every method also has an interpretation cell immediately after its code cell.

| Method and API page | M | D | N | W | T | R | E | L | Notebook cell | Numerical regression |
|---|---|---|---|---|---|---|---|---|---:|---|
| [binomial_test](source/meliora/binomial_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 3 | [test_binomial_test](../tests/test_methods.py) |
| [brier_score](source/meliora/brier_score.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 6 | [test_brier_score](../tests/test_methods.py) |
| [herfindahl_test](source/meliora/herfindahl_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 9 | [test_herfindahl_test](../tests/test_methods.py) |
| [herfindahl_multiple_period_test](source/meliora/herfindahl_multiple_period_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 12 | [test_herfindahl_multiple_period_test](../tests/test_methods.py) |
| [hosmer_test](source/meliora/hosmer_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 15 | [test_hosmer_test](../tests/test_methods.py) |
| [spiegelhalter_test](source/meliora/spiegelhalter_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 18 | [test_spiegelhalter_test](../tests/test_methods.py) |
| [jeffreys_test](source/meliora/jeffreys_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 21 | [test_jeffreys_test](../tests/test_methods.py) |
| [roc_auc](source/meliora/roc_auc.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 24 | [test_roc_auc](../tests/test_methods.py) |
| [gini](source/meliora/gini.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 27 | [test_gini](../tests/test_methods.py) |
| [kolmogorov_smirnov_stat](source/meliora/kolmogorov_smirnov_stat.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 30 | [test_kolmogorov_smirnov_stat](../tests/test_methods.py) |
| [cumulative_lgd_accuracy_ratio](source/meliora/cumulative_lgd_accuracy_ratio.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 33 | [test_cumulative_lgd_accuracy_ratio](../tests/test_methods.py) |
| [loss_capture_ratio](source/meliora/loss_capture_ratio.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 36 | [test_loss_capture_ratio](../tests/test_methods.py) |
| [bayesian_error_rate](source/meliora/bayesian_error_rate.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 39 | [test_bayesian_error_rate](../tests/test_methods.py) |
| [information_value](source/meliora/information_value.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 42 | [test_information_value](../tests/test_methods.py) |
| [lgd_t_test](source/meliora/lgd_t_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 45 | [test_lgd_t_test](../tests/test_methods.py) |
| [migration_matrix_stability](source/meliora/migration_matrix_stability.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 48 | [test_migration_matrix_stability](../tests/test_methods.py) |
| [population_stability_index](source/meliora/population_stability_index.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 51 | [test_population_stability_index](../tests/test_methods.py) |
| [kendall_tau](source/meliora/kendall_tau.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 54 | [test_kendall_tau](../tests/test_methods.py) |
| [somersd](source/meliora/somersd.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 57 | [test_somersd](../tests/test_methods.py) |
| [spearman_correlation](source/meliora/spearman_correlation.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 60 | [test_spearman_correlation](../tests/test_methods.py) |
| [pearson_correlation](source/meliora/pearson_correlation.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 63 | [test_pearson_correlation](../tests/test_methods.py) |
| [migration_matrices_statistics](source/meliora/migration_matrices_statistics.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 66 | [test_migration_matrices_statistics](../tests/test_methods.py) |
| [conditional_information_entropy_ratio](source/meliora/conditional_information_entropy_ratio.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 69 | [test_conditional_information_entropy_ratio](../tests/test_methods.py) |
| [kullback_leibler_dist](source/meliora/kullback_leibler_dist.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 72 | [test_kullback_leibler_dist](../tests/test_methods.py) |
| [loss_shortfall](source/meliora/loss_shortfall.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 75 | [test_loss_shortfall](../tests/test_methods.py) |
| [mean_absolute_deviation](source/meliora/mean_absolute_deviation.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 78 | [test_mean_absolute_deviation](../tests/test_methods.py) |
| [elbe_t_test](source/meliora/elbe_t_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 81 | [test_elbe_t_test](../tests/test_methods.py) |
| [normal_test](source/meliora/normal_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 84 | [test_normal_test](../tests/test_methods.py) |
| [redelmeier_test](source/meliora/redelmeier_test.rst) | PASS | PASS | PASS | PASS | PASS | PASS | PASS | PASS | 87 | [test_redelmeier_test](../tests/test_methods.py) |

## Evidence and reproducibility

- [All-method notebook](../examples/examples.ipynb): 29 code cells executed in fresh Python kernels; every cell contains assertions against a stated expected result.
- [Numerical tests](../tests/test_methods.py): one explained regression per public method; closed-form tails, posterior integration, complete Bernoulli enumeration, concordance counts, explicit curve areas and invariants.
- [Contract tests](../tests/test_contracts.py): invalid inputs and caller-data preservation for every public export, plus shared validation branches.
- [Machine-readable catalogue](method_catalog.json): parameter contracts, statistical notes, sources, examples and test mappings.
- [Validation commands](source/validation.md): reproduce tests, examples, documentation and package checks.

The corrected suite passed 158 tests with 100% statement and branch
coverage on Python 3.13. The built wheel also passed all 158 tests with 100%
coverage on Python 3.11.9 using NumPy 1.26.0, pandas 2.1.0, SciPy 1.11.0 and
scikit-learn 1.3.0 (the declared dependency floors). The docstring build executed 185 examples without a
failure; all 29 notebook cells and all Sphinx pages passed. CI checks Python
3.11–3.14 on Linux and 3.13 on Windows; local runs do not substitute for remote CI.

Tolerances use NumPy/pytest floating-point comparisons; exact combinatorial values
and schemas are checked exactly where appropriate. Near-zero results use explicit
absolute tolerances. Tests check signed statistics and components, not only sums.

## Deliberate conventions and limits

- LCR uses cumulative exposure on the horizontal axis and pools ties. Its fixtures validate that convention, not every account-count implementation.
- Redelmeier uses the explicit midpoint-Bernoulli null. Its variance is checked by enumerating every outcome for a fixed four-observation fixture. This is not a general equal-average-Brier hypothesis or a claim of reproducing the original paper exactly.
- Hosmer defaults to a fixed-PD test with K degrees of freedom; fitted-logistic callers explicitly select ddof=2.
- Migration stability returns ECB normal CDFs and NaN for undefined cells. NaN must never be treated as a passed statistical test.
- IV/PSI smoothing and grade order are explicit; changing these choices can change results.
- Numerical evidence comes from the regression tests and supported examples. Method documentation links directly to statistical references; historical research files are not required to reproduce the checks.
