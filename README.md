# Meliora

Meliora accompanies *Statistical Tests for Credit Risk*. It contains 29 statistical
tests and measures for probability of default (PD), loss given default (LGD) and
rating models. Use the book for the explanations and Meliora to run the calculations.

## Contents

| File or folder | Contents |
|---|---|
| [meliora/core.py](meliora/core.py) | All 29 methods and their input checks |
| [meliora/__init__.py](meliora/__init__.py) | Exposes the methods through `import meliora as m` |
| [tests/](tests/) | Checks of numerical results and input handling |
| [docs/examples/examples.ipynb](docs/examples/examples.ipynb) | 29 worked examples in the book's order |
| [docs/reference/](docs/reference/) | Detailed references for all 29 methods |
| [pyproject.toml](pyproject.toml) | Local installation, dependencies and test settings |

## The 29 methods

Names, order and areas follow the book. The estimate column reflects the book's
worked examples. Select a method name for its detailed reference and sources.

| # | Method | Area | Estimate | Explanation |
|---|---|---|---|---|
| 1 | [ROC AUC](docs/reference/roc_auc.md) | Discrimination | PD | Measures how well a score ranks defaulters above survivors. |
| 2 | [Gini coefficient](docs/reference/gini.md) | Discrimination | PD | Rescales ROC AUC into an accuracy ratio, with zero for random ranking and one for perfect ranking. |
| 3 | [Kolmogorov-Smirnov statistic](docs/reference/kolmogorov_smirnov_stat.md) | Discrimination | PD | Measures the largest gap between the score distributions of defaulters and survivors. |
| 4 | [Minimum empirical threshold error](docs/reference/bayesian_error_rate.md) | Discrimination | PD | Finds the lowest classification error across score cut-offs, giving false alarms and missed defaults equal cost. |
| 5 | [Information value](docs/reference/information_value.md) | Discrimination | PD | Measures how differently defaulters and survivors are distributed across grades or bins. |
| 6 | [Conditional information entropy ratio](docs/reference/conditional_information_entropy_ratio.md) | Discrimination | PD | Measures the share of uncertainty about default removed by knowing the rating grade. |
| 7 | [Mutual information](docs/reference/kullback_leibler_dist.md) | Discrimination | PD | Measures the reduction in uncertainty about default from knowing the grade, expressed in nats. |
| 8 | [Cumulative LGD accuracy ratio](docs/reference/cumulative_lgd_accuracy_ratio.md) | Discrimination | LGD | Summarises asymmetric agreement between predicted and realised loss grades across grade thresholds. |
| 9 | [Loss capture ratio](docs/reference/loss_capture_ratio.md) | Discrimination | LGD | Measures how quickly realised monetary losses accumulate when facilities are ordered by predicted LGD. |
| 10 | [Binomial test](docs/reference/binomial_test.md) | Calibration | PD | Tests whether a grade PD is too low relative to its observed number of defaults. |
| 11 | [Jeffreys test](docs/reference/jeffreys_test.md) | Calibration | PD | Assesses PD underestimation using a Jeffreys posterior for the grade default rate. |
| 12 | [Hosmer test](docs/reference/hosmer_test.md) | Calibration | PD | Jointly compares fixed grade PDs with observed default counts using a chi-square statistic. |
| 13 | [Spiegelhalter test](docs/reference/spiegelhalter_test.md) | Calibration | PD | Compares squared forecast errors with their expectation under calibrated PDs. |
| 14 | [Brier score](docs/reference/brier_score.md) | Calibration | PD | Measures the mean squared difference between predicted PDs and observed default outcomes. |
| 15 | [Redelmeier test](docs/reference/redelmeier_test.md) | Calibration | PD | Compares paired Brier scores under the assumption that each true PD is the midpoint of the two forecasts. |
| 16 | [Normal test for annual default rates](docs/reference/normal_test.md) | Calibration | PD | Tests whether realised portfolio default rates exceed predicted rates on average across years. |
| 17 | [Kendall's tau](docs/reference/kendall_tau.md) | Association | LGD | Measures agreement between predicted and realised rankings by comparing concordant and discordant pairs. |
| 18 | [Somers' D](docs/reference/somersd.md) | Association | LGD | Measures how well realised outcomes support the ordering of pairs distinguished by the predictions. |
| 19 | [Spearman's rho](docs/reference/spearman_correlation.md) | Association | LGD | Measures association between predicted and realised LGD using their ranks. |
| 20 | [Pearson's r](docs/reference/pearson_correlation.md) | Association | LGD | Measures linear association between predicted and realised LGD using their numerical values. |
| 21 | [Herfindahl index](docs/reference/herfindahl_test.md) | Stability | PD | Measures how concentrated the portfolio is across rating grades. |
| 22 | [Multiple-period Herfindahl test](docs/reference/herfindahl_multiple_period_test.md) | Stability | PD | Compares current grade concentration with a fixed development benchmark using the ECB statistic. |
| 23 | [Population stability index](docs/reference/population_stability_index.md) | Stability | PD | Measures the change in grade or bin proportions between two samples. |
| 24 | [Migration bandwidth](docs/reference/migration_matrices_statistics.md) | Stability | PD | Measures migration distances relative to possible distances, separately for upgrades and downgrades. |
| 25 | [Adjacent-cell shape checks](docs/reference/migration_matrix_stability.md) | Stability | PD | Checks whether transition probabilities decline away from the diagonal within one migration matrix. |
| 26 | [LGD t-test](docs/reference/lgd_t_test.md) | LGD validation | LGD | Tests whether mean realised LGD exceeds mean predicted LGD on completed default episodes. |
| 27 | [ELBE t-test](docs/reference/elbe_t_test.md) | LGD validation | LGD | Tests whether mean realised loss differs from the expected loss best estimate in either direction. |
| 28 | [Loss shortfall](docs/reference/loss_shortfall.md) | LGD validation | LGD | Measures the gap between realised and predicted monetary losses as a fraction of realised loss. |
| 29 | [Exposure-weighted mean absolute error](docs/reference/mean_absolute_deviation.md) | LGD validation | LGD | Measures the size of individual LGD forecast errors, weighted by exposure, without cancelling opposite errors. |

## One example: Brier score

Install Meliora from the repository root:

```bash
python -m pip install .
```

pandas creates the input table; Meliora calculates the Brier score. Each PD is
compared with an observed outcome: 1 for a default and 0 for a non-default.

```python
import pandas as pd
import meliora as m

portfolio = pd.DataFrame({
    "grade": ["A", "A", "B", "B"],
    "default": [0, 1, 0, 1],
    "pd": [0.2, 0.2, 0.6, 0.6],
})

score = m.brier_score(
    portfolio,
    ratings="grade",
    default_flag="default",
    predicted_pd="pd",
)
print(f"Brier score: {score:.3f}")
```

Output:

```text
Brier score: 0.300
```

The score is the mean squared difference between each predicted PD and its
observed outcome. The [example notebook](docs/examples/examples.ipynb) covers all 29 methods.

License: [MIT](LICENSE).
