# Meliora

Meliora is a Python library for statistical model validation, accompanying
*Statistical Tests for Credit Risk*. It provides **60 statistical tests and
measures** for probability of default (PD), loss given default (LGD), rating
models, time series, residuals, calibration, forecast comparison, distributions,
structural breaks, survival and cointegration.

Use `import meliora as m` for every method. Each method has a reference page and
executed examples in both notebooks. See the [method reference](docs/README.md)
for hypotheses, assumptions, inputs and results.

## Installation

Python 3.11 or later is required. Clone the repository and install from its root:

```bash
git clone https://github.com/at621/meliora.git
cd meliora
python -m pip install -e .
```

The base dependencies are NumPy >=1.26, pandas >=2.1, SciPy >=1.11 and
scikit-learn >=1.3. Install the optional time-series dependencies for ADF, KPSS,
BDS, fitted-normal Anderson-Darling, Phillips-Perron, Engle-Granger and Johansen:

```bash
python -m pip install -e ".[timeseries]"
```

This extra installs statsmodels >=0.14.4,<0.15 and arch >=7.2,<8. Statsmodels
excludes pandas 2.1.0, so the extra selects pandas 2.1.1 or later. These optional
dependencies are loaded only when a method needs them.

For tests or notebooks, use `python -m pip install -e ".[timeseries,test]"` or
`python -m pip install -e ".[timeseries,notebook]"`, respectively.

## Contents

| File or folder | Contents |
|---|---|
| [meliora/core.py](meliora/core.py) | Credit-risk discrimination, calibration, association and loss measures |
| [meliora/timeseries.py](meliora/timeseries.py) | Serial dependence, residual diagnostics and stationarity tests |
| [meliora/calibration.py](meliora/calibration.py) | Calibration, paired AUC and forecast-loss comparisons |
| [meliora/distributions.py](meliora/distributions.py) | Distributional and categorical tests |
| [meliora/structural.py](meliora/structural.py) | Structural breaks, survival and cointegration tests |
| [meliora/__init__.py](meliora/__init__.py) | Exposes the methods through `import meliora as m` |
| [tests/](tests/) | Checks of numerical results and input handling |
| [docs/examples/examples.ipynb](docs/examples/examples.ipynb) | 60 worked examples in catalogue order |
| [docs/examples/detailed_examples.ipynb](docs/examples/detailed_examples.ipynb) | 60 detailed case studies with synthetic datasets, graphs and interpretation |
| [docs/reference/](docs/reference/) | Detailed references for all 60 public functions |
| [docs/extensions.md](docs/extensions.md) | Tabular inference results, input checks and statistical conventions |
| [docs/extension_verification.md](docs/extension_verification.md) | Verification results and tested dependency versions |
| [pyproject.toml](pyproject.toml) | Package metadata, dependencies and test settings |

## All 60 functions

The numbering matches the examples in both notebooks. The estimate column
identifies the input or modelling area. Select a name for its detailed reference
and sources.

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
| 30 | [Ljung-Box](docs/reference/ljung_box_test.md) | Serial dependence | Residuals | Tests whether autocorrelations through the selected lag are jointly zero. |
| 31 | [Breusch-Godfrey](docs/reference/breusch_godfrey_test.md) | Serial dependence | Regression | Tests regression errors for serial correlation using the original design. |
| 32 | [ARCH LM](docs/reference/arch_lm_test.md) | Variance | Residuals | Tests for dependence in squared residuals. |
| 33 | [Breusch-Pagan / Koenker](docs/reference/breusch_pagan_test.md) | Variance | Regression | Tests whether specified regressors explain changing error variance. |
| 34 | [Jarque-Bera](docs/reference/jarque_bera_test.md) | Normality | Continuous observations | Tests normal skewness and kurtosis. |
| 35 | [Augmented Dickey-Fuller](docs/reference/adf_test.md) | Unit roots | Time series | Tests a unit-root null against stationarity. |
| 36 | [KPSS](docs/reference/kpss_test.md) | Stationarity | Time series | Tests stationarity around a constant or trend. |
| 37 | [Ramsey RESET](docs/reference/reset_test.md) | Specification | Regression | Tests nonlinear fitted-value terms for omitted structure. |
| 38 | [Box-Pierce](docs/reference/box_pierce_test.md) | Serial dependence | Residuals | Tests joint autocorrelation with the Box-Pierce statistic. |
| 39 | [Durbin-Watson](docs/reference/durbin_watson_test.md) | Serial dependence | Regression | Uses design-conditional simulation to test first-order error autocorrelation. |
| 40 | [BDS](docs/reference/bds_test.md) | Independence | Observed time series | Tests whether observed data are independent and identically distributed. |
| 41 | [White](docs/reference/white_test.md) | Variance | Regression | Tests constant variance against squares and interactions of regressors. |
| 42 | [Shapiro-Wilk](docs/reference/shapiro_wilk_test.md) | Normality | Continuous observations | Tests normality using ordered observations. |
| 43 | [Fitted-normal Anderson-Darling](docs/reference/anderson_darling_normal_test.md) | Normality | Continuous observations | Tests normality with estimated mean and variance. |
| 44 | [Phillips-Perron](docs/reference/phillips_perron_test.md) | Unit roots | Time series | Tests a unit root using a long-run variance correction. |
| 45 | [Logistic calibration LR](docs/reference/logistic_calibration_lr_test.md) | Calibration | PD | Jointly tests calibration intercept zero and slope one. |
| 46 | [Exact Poisson-binomial](docs/reference/poisson_binomial_test.md) | Calibration | Event counts | Tests the total event count for heterogeneous independent probabilities. |
| 47 | [Paired DeLong](docs/reference/delong_test.md) | Discrimination | AUC | Tests equality of two AUCs on the same observations. |
| 48 | [Diebold-Mariano](docs/reference/diebold_mariano_test.md) | Forecast comparison | Forecast losses | Tests zero expected out-of-sample loss difference. |
| 49 | [Wilcoxon signed-rank](docs/reference/wilcoxon_signed_rank_test.md) | Paired differences | Continuous outcomes | Tests a paired-difference distribution symmetric about zero. |
| 50 | [Fisher exact](docs/reference/fisher_exact_test.md) | Categorical | 2×2 counts | Tests conditional odds ratio one using exact inference. |
| 51 | [Likelihood-ratio G-test](docs/reference/g_test.md) | Categorical | Counts | Tests specified category probabilities or group homogeneity. |
| 52 | [Stuart-Maxwell](docs/reference/stuart_maxwell_test.md) | Paired categorical | Category transitions | Tests equality of marginal distributions in paired categories. |
| 53 | [McNemar](docs/reference/mcnemar_test.md) | Paired categorical | Binary outcomes | Tests marginal equality for paired binary observations. |
| 54 | [Anderson-Darling k-sample](docs/reference/anderson_darling_ksample_test.md) | Distributional | Independent samples | Tests whether independent samples share a distribution. |
| 55 | [OLS CUSUM](docs/reference/cusum_test.md) | Structural stability | Regression | Tests coefficient stability using cumulative OLS residuals. |
| 56 | [Chow](docs/reference/chow_test.md) | Structural breaks | Regression | Tests coefficient equality at a prespecified breakpoint. |
| 57 | [Sup-F](docs/reference/sup_f_test.md) | Structural breaks | Regression | Searches for a break with search-adjusted simulation inference. |
| 58 | [Log-rank](docs/reference/logrank_test.md) | Survival | Right-censored outcomes | Tests equality of survival functions across groups. |
| 59 | [Engle-Granger](docs/reference/engle_granger_test.md) | Cointegration | Integrated series | Tests for cointegration with residual-based critical values. |
| 60 | [Johansen trace / maximum eigenvalue](docs/reference/johansen_test.md) | Cointegration | Integrated series | Tests each cointegration-rank hypothesis using matching critical values. |

## Using the methods

Each reference page documents the method's arguments and return format, which
may be a scalar, tuple or pandas DataFrame. Tabular hypothesis-test results
include the statistic, p-value, effective sample size, degrees of freedom where
applicable, inference method and rejection decision. Method-specific columns
record settings such as lag, bandwidth, deterministic terms and seed.

Missing observations are rejected. Tests that require temporal ordering preserve
that order and validate pandas time indexes; unindexed arrays assert equally
spaced order. In the tabular inference format, unavailable decisions use
`reject=pd.NA`, and bounded p-values or critical-value-only results are labelled
explicitly. See the [inference conventions](docs/extensions.md) and each method's
reference page for details.

## Example: exact heterogeneous event-count test

```python
import meliora as m

result = m.poisson_binomial_test([0.1, 0.4, 0.8], count=0, alternative="less")
print(f"P(no events): {result.pvalue.iloc[0]:.3f}")
print(f"Reject at 5%: {result.reject.iloc[0]}")
```

```text
P(no events): 0.108
Reject at 5%: False
```

Under independent Bernoulli events, the probability of no events is
`(1 - 0.1) * (1 - 0.4) * (1 - 0.8) = 0.108`. The function also supports
upper-tail and two-sided probability-ordered inference.

## Example: Brier score

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
observed outcome.

## Notebooks

The [worked-example notebook](docs/examples/examples.ipynb)
covers all 60 functions with short API examples. The
[detailed case-study notebook](docs/examples/detailed_examples.ipynb) covers the
same 60 functions, starting with 8,000 obligors across eight PD grades, 600 LGD observations,
24 annual cohorts, migration matrices, and a graph and takeaway for every method.
All inputs are synthetic and generated inside the notebook; executed outputs are
included for reading on GitHub.

Both notebooks include executed examples for every function. The detailed
notebook provides a graph, interpretation and suggested experiment for each one.
Its scenarios also cover 240 temporal observations, 600 validation PDs, paired
forecast losses, category counts and 300 right-censored survival observations.

To open the detailed notebook from the repository root, use an environment with
JupyterLab and Matplotlib available:

```bash
python -m jupyter lab docs/examples/detailed_examples.ipynb
```

The notebooks' setup cells locate Meliora in the cloned repository. Run the setup
cells once, then run any numbered example, or restart the kernel and run all cells
in order.

For PSI, pass `expected` and `actual` explicitly unless the period column is an
ordered categorical. Unused period categories are ignored; ordinary string labels
are not sorted into an implied chronology. For ECB migration shape checks with
defaults, exits or transfers, pass `initial_counts` keyed by grade so the original
cohort remains the probability and variance denominator. Omitting it uses the
matched performing rows and is conditional on remaining rated when customers leave.

## Verification

Run the suite from the repository root after installing the test extra:

```bash
python -m pytest -q -p no:cacheprovider
```

The latest recorded run (2026-09-28) had **566 passing checks and no unexpected
failures**. Every function has tests, and both notebooks ran successfully with
examples for all 60 functions.

The test report also lists checks that did not pass in the usual way:

| Report entry | Meaning |
|---|---|
| 76 skipped reference checks | These require an explicitly enabled external run or reference results that are not available. They were not verified in this run. |
| 5 skipped simulation studies | These slower studies are excluded from the default run. All five passed when run separately. |
| 5 expected failures | These checks reproduce documented differences between Python, R or MATLAB algorithms. They remain differences, rather than passing comparisons. |

Tests compare results with hand calculations, mathematical identities and saved
[independent R calculations](tests/oracles/extensions/README.md). R is not needed
to run the normal test suite. The [verification record](docs/extension_verification.md)
contains dependency versions and details of the checks.

The optional simulation studies repeatedly generate synthetic data to check how
often selected tests reject a true null hypothesis and detect a specified
departure from it. They cover five methods, not all 60 functions. To run them
in PowerShell:

```powershell
$env:MELIORA_SLOW = '1'
python -m pytest tests/test_extension_simulations.py -q -p no:cacheprovider
Remove-Item Env:MELIORA_SLOW
```

License: [MIT](LICENSE).
