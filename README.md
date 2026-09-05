# Meliora

[![CI](https://github.com/at621/meliora/actions/workflows/CI.yml/badge.svg)](https://github.com/at621/meliora/actions/workflows/CI.yml) [![PyPI](https://badge.fury.io/py/meliora.svg)](https://pypi.org/project/meliora/)

**Meliora is a Python library for assessing the performance of credit-risk models.** It brings together statistical tests and performance measures that help practitioners compare model predictions with observed defaults and losses, assess how well a model ranks risk, and monitor changes in a portfolio over time.

The library is intended for credit-risk modellers, model validators and researchers working with **probability of default (PD)** and **loss given default (LGD)** models in IRB, IFRS 9 and other credit-risk settings. Its purpose is to make commonly used validation methods available in one documented, reusable toolkit, so practitioners can spend more time understanding their models and less time reimplementing statistical calculations.

## What can you use Meliora for?

Meliora supports checks used during model development, independent validation and ongoing performance monitoring. For example, you can investigate whether predicted default rates are too low, whether higher-risk borrowers receive higher scores, whether LGD estimates match realised losses, or whether the distribution of rating grades has changed.

The current library provides **29 methods**:

| Validation task | Question it helps answer | Available methods |
|---|---|---|
| PD calibration | Are predicted default probabilities consistent with observed defaults? | Binomial, Jeffreys, Hosmer, Spiegelhalter and normal tests |
| Probability forecast accuracy | How accurate are the probability forecasts, and how do two sets of forecasts compare? | Brier score and Redelmeier-style paired Brier comparison |
| Default discrimination | Does the model distinguish defaulting from non-defaulting borrowers? | ROC AUC, Gini, Kolmogorov–Smirnov statistic, empirical Bayesian error rate and information value |
| Association | How strongly do two scores, rankings or measurements agree? | Kendall's tau, Somers' D, Spearman and Pearson correlations |
| LGD discrimination | Does the model rank facilities by loss severity? | Cumulative LGD accuracy ratio and loss capture ratio |
| LGD prediction error | How far are predicted losses from realised losses? | LGD and ELBE paired t tests, loss shortfall and exposure-weighted mean absolute deviation |
| Portfolio stability | How have grade concentration, population composition and rating migrations changed? | Single- and multiple-period Herfindahl measures, population stability index and two migration-matrix methods |
| Information in rating grades | How much does knowing a grade tell us about default outcomes? | Conditional information entropy ratio and grade/default mutual information (`kullback_leibler_dist`) |

Each method explains its inputs, statistical definition, assumptions and interpretation. The implementations draw on the statistical literature and, where applicable, validation material from the Basel Committee and the ECB. The [worked notebooks](examples/examples.ipynb) show how to apply every method to reproducible data and interpret the result.

The broader aim of the project is to support common validation tasks across PD, LGD, exposure at default (EAD) and prepayment models. The implemented methods currently focus on PD, LGD, association and portfolio stability.

## Getting started

From a checkout of this repository, install the package using **Python 3.11 or newer**:

```bash
python -m pip install .
```

This README describes the **0.2 development API**. If you are moving from 0.1.2, consult the [migration guide](docs/source/migration.md) for changes to calculations and function arguments.

### Example: assessing default predictions

Suppose a portfolio contains two rating grades, with predicted PDs of 10% and 60%. Each row represents a borrower; `default` is 1 if the borrower defaulted during the observation period and 0 otherwise.

```python
import pandas as pd
import meliora as m

portfolio = pd.DataFrame({
    'grade': ['A'] * 4 + ['B'] * 4,
    'default': [0, 0, 0, 1, 0, 1, 1, 1],
    'pd': [0.10] * 4 + [0.60] * 4,
})

brier = m.brier_score(portfolio, 'grade', 'default', 'pd')
auc = m.roc_auc(portfolio, 'default', 'pd')

print(f'Brier score: {brier:.3f}')  # Brier score: 0.210
print(f'ROC AUC: {auc:.3f}')       # ROC AUC: 0.750
```

The **Brier score** measures the mean squared error of individual probability forecasts; lower values indicate more accurate forecasts. **ROC AUC** measures how well scores rank defaults above non-defaults, giving half credit to ties. Here, AUC is 0.75, above the random-ordering baseline of 0.5. Together, the two measures describe different aspects of model performance.

For calibration tests, LGD examples and migration analysis, start with the [complete example notebook](examples/examples.ipynb). It includes expected results, interpretation and the assumptions relevant to each method.

## Documentation and examples

- [Getting started and usage](docs/source/usage.md)
- [Jupyter examples for all 29 methods](examples/examples.ipynb)
- [API reference](docs/source/index.rst)
- [Method acceptance checklist and numerical evidence](docs/method_checklist.md)
- [Changelog](CHANGELOG.md) and [migration guide](docs/source/migration.md)

To install the notebook and documentation dependencies, run `python -m pip install ".[docs]"`. From the repository root, `python scripts/run_notebooks.py` executes the supported examples using your current Python environment.

## Project background

Meliora grew out of its contributors' experience developing statistical credit models at financial institutions, dating back to 2003. It makes those recurring modelling and validation tasks easier to reproduce and share through an open-source Python library.

The package builds on **NumPy, pandas, SciPy and scikit-learn**. Some methods adapt established implementations from these libraries; others provide calculations specific to credit-risk validation. Every public method has automated regression tests and a worked notebook example. See the [validation guide](docs/source/validation.md) for the numerical evidence and how to reproduce the checks.

## Contributing and getting help

Contributions are welcome, including improvements to statistical methods, documentation and examples. The [contribution guide](CONTRIBUTING.md) explains the development setup and requirements for adding or changing a method.

For questions or bug reports, [open a GitHub issue](https://github.com/at621/meliora/issues). For usage questions, you can also contact [anton.treialt@aistat.com](mailto:anton.treialt@aistat.com).

## License

Meliora is released under the [MIT License](LICENSE).
