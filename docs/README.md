# Method reference

These pages explain all 60 functions: arguments, return values, hypotheses,
formulas, assumptions, examples and statistical sources.

See the [package README](../README.md) for installation and the numbered catalogue,
the [worked-example notebook](examples/examples.ipynb) for short executable examples,
and the [detailed notebook](examples/detailed_examples.ipynb) for synthetic case
studies, graphs and interpretation. Both notebooks cover every function, use the
same catalogue numbering, and include executed outputs.

Each method documents its input and return format. See also the
[tabular inference conventions](extensions.md) for nullable decisions and p-value bounds.

### Discrimination

- [ROC AUC](reference/roc_auc.md)
- [Gini coefficient](reference/gini.md)
- [Kolmogorov-Smirnov statistic](reference/kolmogorov_smirnov_stat.md)
- [Minimum empirical threshold error](reference/bayesian_error_rate.md)
- [Information value](reference/information_value.md)
- [Conditional information entropy ratio](reference/conditional_information_entropy_ratio.md)
- [Mutual information](reference/kullback_leibler_dist.md)
- [Cumulative LGD accuracy ratio](reference/cumulative_lgd_accuracy_ratio.md)
- [Loss capture ratio](reference/loss_capture_ratio.md)
- [Paired DeLong](reference/delong_test.md)

### Calibration

- [Binomial test](reference/binomial_test.md)
- [Jeffreys test](reference/jeffreys_test.md)
- [Hosmer test](reference/hosmer_test.md)
- [Spiegelhalter test](reference/spiegelhalter_test.md)
- [Brier score](reference/brier_score.md)
- [Redelmeier test](reference/redelmeier_test.md)
- [Normal test for annual default rates](reference/normal_test.md)
- [Logistic calibration LR](reference/logistic_calibration_lr_test.md)
- [Exact Poisson-binomial](reference/poisson_binomial_test.md)

### Association

- [Kendall's tau](reference/kendall_tau.md)
- [Somers' D](reference/somersd.md)
- [Spearman's rho](reference/spearman_correlation.md)
- [Pearson's r](reference/pearson_correlation.md)

### Stability

- [Herfindahl index](reference/herfindahl_test.md)
- [Multiple-period Herfindahl test](reference/herfindahl_multiple_period_test.md)
- [Population stability index](reference/population_stability_index.md)
- [Migration bandwidth](reference/migration_matrices_statistics.md)
- [Adjacent-cell shape checks](reference/migration_matrix_stability.md)

### LGD validation

- [LGD t-test](reference/lgd_t_test.md)
- [ELBE t-test](reference/elbe_t_test.md)
- [Loss shortfall](reference/loss_shortfall.md)
- [Exposure-weighted mean absolute error](reference/mean_absolute_deviation.md)

### Serial dependence

- [Ljung-Box](reference/ljung_box_test.md)
- [Breusch-Godfrey](reference/breusch_godfrey_test.md)
- [Box-Pierce](reference/box_pierce_test.md)
- [Durbin-Watson](reference/durbin_watson_test.md)

### Variance

- [ARCH LM](reference/arch_lm_test.md)
- [Breusch-Pagan / Koenker](reference/breusch_pagan_test.md)
- [White](reference/white_test.md)

### Normality

- [Jarque-Bera](reference/jarque_bera_test.md)
- [Shapiro-Wilk](reference/shapiro_wilk_test.md)
- [Fitted-normal Anderson-Darling](reference/anderson_darling_normal_test.md)

### Unit roots

- [Augmented Dickey-Fuller](reference/adf_test.md)
- [Phillips-Perron](reference/phillips_perron_test.md)

### Stationarity

- [KPSS](reference/kpss_test.md)

### Specification

- [Ramsey RESET](reference/reset_test.md)

### Independence

- [BDS](reference/bds_test.md)

### Forecast comparison

- [Diebold-Mariano](reference/diebold_mariano_test.md)

### Paired differences

- [Wilcoxon signed-rank](reference/wilcoxon_signed_rank_test.md)

### Categorical

- [Fisher exact](reference/fisher_exact_test.md)
- [Likelihood-ratio G-test](reference/g_test.md)

### Paired categorical

- [Stuart-Maxwell](reference/stuart_maxwell_test.md)
- [McNemar](reference/mcnemar_test.md)

### Distributional

- [Anderson-Darling k-sample](reference/anderson_darling_ksample_test.md)

### Structural stability

- [OLS CUSUM](reference/cusum_test.md)

### Structural breaks

- [Chow](reference/chow_test.md)
- [Sup-F](reference/sup_f_test.md)

### Survival

- [Log-rank](reference/logrank_test.md)

### Cointegration

- [Engle-Granger](reference/engle_granger_test.md)
- [Johansen trace / maximum eigenvalue](reference/johansen_test.md)
