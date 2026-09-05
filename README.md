# Meliora

[![CI](https://github.com/at621/meliora/actions/workflows/CI.yml/badge.svg)](https://github.com/at621/meliora/actions/workflows/CI.yml) [![PyPI](https://badge.fury.io/py/meliora.svg)](https://pypi.org/project/meliora/)

**Meliora is a Python library for developing, validating and monitoring credit-risk models.** It provides statistical tests and performance measures for comparing model predictions with observed defaults and losses, assessing risk rankings, and tracking changes in portfolios.

The library is intended for credit-risk modellers, validators and researchers working with **probability of default (PD)** and **loss given default (LGD)** models in IRB, IFRS 9 and other credit-risk settings. Its aim is to provide commonly used validation methods in one documented toolkit, reducing the need to implement the same calculations repeatedly.

## Tests and performance measures

Meliora includes the following **29 tests and measures**. Each has documented assumptions, automated tests and a worked Jupyter notebook example.

| # | Test or measure | Purpose |
|---|---|---|
| 1 | [Binomial test](docs/source/meliora/binomial_test.md) | Test whether grade PDs underestimate observed defaults. |
| 2 | [Jeffreys test](docs/source/meliora/jeffreys_test.md) | Assess grade PDs using a Bayesian posterior distribution. |
| 3 | [Hosmer calibration test](docs/source/meliora/hosmer_test.md) | Compare observed and expected defaults across grades. |
| 4 | [Spiegelhalter test](docs/source/meliora/spiegelhalter_test.md) | Assess calibration of individual PD forecasts. |
| 5 | [Normal test](docs/source/meliora/normal_test.md) | Test for underestimation in annual PD forecasts. |
| 6 | [Brier score](docs/source/meliora/brier_score.md) | Measure the squared error of probability forecasts. |
| 7 | [Redelmeier-style test](docs/source/meliora/redelmeier_test.md) | Compare two sets of paired probability forecasts. |
| 8 | [ROC AUC](docs/source/meliora/roc_auc.md) | Measure how well scores distinguish defaults from non-defaults. |
| 9 | [Gini coefficient](docs/source/meliora/gini.md) | Express discrimination on a scale derived from ROC AUC. |
| 10 | [Kolmogorov–Smirnov statistic](docs/source/meliora/kolmogorov_smirnov_stat.md) | Compare score distributions for defaults and non-defaults. |
| 11 | [Bayesian error rate](docs/source/meliora/bayesian_error_rate.md) | Find the lowest empirical classification error across score thresholds. |
| 12 | [Information value](docs/source/meliora/information_value.md) | Measure how a binned feature separates defaults and non-defaults. |
| 13 | [Kendall's tau](docs/source/meliora/kendall_tau.md) | Measure agreement between rankings, accounting for ties. |
| 14 | [Somers' D](docs/source/meliora/somersd.md) | Measure directional association between rankings. |
| 15 | [Spearman correlation](docs/source/meliora/spearman_correlation.md) | Measure monotone association between two variables. |
| 16 | [Pearson correlation](docs/source/meliora/pearson_correlation.md) | Measure linear association between two variables. |
| 17 | [Cumulative LGD accuracy ratio](docs/source/meliora/cumulative_lgd_accuracy_ratio.md) | Assess agreement between predicted and realised loss grades. |
| 18 | [Loss capture ratio](docs/source/meliora/loss_capture_ratio.md) | Assess loss rankings using exposure-weighted loss curves. |
| 19 | [LGD t-test](docs/source/meliora/lgd_t_test.md) | Test whether realised LGD exceeds expected LGD on average. |
| 20 | [Expected loss best estimate (ELBE) t-test](docs/source/meliora/elbe_t_test.md) | Test the mean difference between realised LGD and ELBE. |
| 21 | [Loss shortfall](docs/source/meliora/loss_shortfall.md) | Measure relative underestimation of total monetary loss. |
| 22 | [Mean absolute deviation](docs/source/meliora/mean_absolute_deviation.md) | Measure exposure-weighted absolute LGD prediction errors. |
| 23 | [Herfindahl index](docs/source/meliora/herfindahl_test.md) | Measure concentration across rating grades. |
| 24 | [Multiple-period Herfindahl test](docs/source/meliora/herfindahl_multiple_period_test.md) | Test whether grade concentration has increased. |
| 25 | [Population stability index](docs/source/meliora/population_stability_index.md) | Measure changes in a variable's distribution between two samples. |
| 26 | [Migration-weighted bandwidth](docs/source/meliora/migration_matrices_statistics.md) | Measure the distance of rating migrations in each direction. |
| 27 | [Migration matrix stability](docs/source/meliora/migration_matrix_stability.md) | Assess the pattern of probabilities around a migration matrix's diagonal. |
| 28 | [Conditional information entropy ratio](docs/source/meliora/conditional_information_entropy_ratio.md) | Measure the share of default uncertainty explained by grades. |
| 29 | [Kullback–Leibler information measure](docs/source/meliora/kullback_leibler_dist.md) | Measure information about defaults contained in rating grades. |

## Installation

Requires **Python 3.11 or newer**. From a checkout of this repository:

```bash
python -m pip install .
```

NumPy, pandas, SciPy and scikit-learn are installed as dependencies.

## Documentation and examples

The [example notebook](examples/examples.ipynb) covers every method with reproducible data, expected results and interpretation. Statistical definitions, assumptions and references are documented alongside each method.

- [Usage instructions](docs/source/usage.md)
- [Method reference](docs/README.md)
- [Validation checklist and numerical evidence](docs/method_checklist.md)
- [Release notes](CHANGELOG.md)

## Project background and aims

Meliora grew out of its contributors' experience developing statistical credit models at financial institutions, dating back to 2003. Its methods draw on the statistical literature and, where applicable, validation material from the Basel Committee and the ECB.

The broader aim is to support common validation tasks across PD, LGD, exposure at default (EAD) and prepayment models. The current methods focus on PD, LGD, association and portfolio stability.

## Help and contributions

For questions and bug reports, [open a GitHub issue](https://github.com/at621/meliora/issues) or contact [anton.treialt@aistat.com](mailto:anton.treialt@aistat.com).

Contributions to methods, documentation and examples are welcome. See the [contribution guide](CONTRIBUTING.md) for the development setup and validation requirements.

## License

Meliora is released under the [MIT License](LICENSE).
