# Cross-language test results

Generated 2026-09-19 by `python tests/oracles/report.py` from the frozen oracle files.
Every value is the number the named language produced; Python is Meliora itself.
A value that differs from Meliora by more than relative tolerance 1e-08 is marked
**DIFFERS**, or (documented) when the field is listed in `KNOWN_DIVERGENCE` in
`tests/test_cross_language.py`. Values are shown to 12 significant digits;
`RESULTS.csv` holds the same table at full precision.

## Summary

| Language | Version | Fields matching | Fields differing | Documented divergences | Not run |
|---|---|---|---|---|---|
| Python | 3.13.1 | reference (519 fields, 67 cases) | | | |
| R | R version 4.3.1 (2023-06-16 ucrt) | 518 | 0 | 1 | 0 |
| MATLAB | 9.10.0.1602886 (R2021a) | 515 | 0 | 4 | 0 |
| SAS |  | 0 | 0 | 0 | 519 |

## Values by test

| # | Method | Case | Field | Python | R | MATLAB | SAS |
|---|---|---|---|---|---|---|---|
| 1 | ROC AUC | `roc_auc_large` | `auc` | 0.740864760326 | 0.740864760326 | 0.740864760326 | not run |
| 1 | ROC AUC | `roc_auc_small` | `auc` | 0.875 | 0.875 | 0.875 | not run |
| 2 | Gini coefficient | `gini_large` | `gini` | 0.481729520652 | 0.481729520652 | 0.481729520652 | not run |
| 2 | Gini coefficient | `gini_small` | `gini` | 0.75 | 0.75 | 0.75 | not run |
| 3 | Kolmogorov-Smirnov statistic | `ks_large` | `statistic` | 0.398756734356 | 0.398756734356 | 0.398756734356 | not run |
| 3 | Kolmogorov-Smirnov statistic | `ks_large` | `pvalue` | 1.79563629e-13 | 1.79563629e-13 | 2.85474084364e-13 (documented) | not run |
| 3 | Kolmogorov-Smirnov statistic | `ks_small_noties` | `statistic` | 1 | 1 | 1 | not run |
| 3 | Kolmogorov-Smirnov statistic | `ks_small_noties` | `pvalue` | 0.333333333333 | 0.333333333333 | 0.0970268975952 (documented) | not run |
| 3 | Kolmogorov-Smirnov statistic | `ks_small_ties` | `statistic` | 0.5 | 0.5 | 0.5 | not run |
| 3 | Kolmogorov-Smirnov statistic | `ks_small_ties` | `pvalue` | 1 | 0.963945243665 (documented) | 0.843819824542 (documented) | not run |
| 4 | Minimum empirical threshold error | `bayesian_error_rate_large` | `error` | 0.0475 | 0.0475 | 0.0475 | not run |
| 4 | Minimum empirical threshold error | `bayesian_error_rate_small` | `error` | 0.25 | 0.25 | 0.25 | not run |
| 5 | Information value | `information_value_declared` | `good.A` | 3 | 3 | 3 | not run |
| 5 | Information value | `information_value_declared` | `good.B` | 1 | 1 | 1 | not run |
| 5 | Information value | `information_value_declared` | `good.C` | 0 | 0 | 0 | not run |
| 5 | Information value | `information_value_declared` | `bad.A` | 1 | 1 | 1 | not run |
| 5 | Information value | `information_value_declared` | `bad.B` | 3 | 3 | 3 | not run |
| 5 | Information value | `information_value_declared` | `bad.C` | 0 | 0 | 0 | not run |
| 5 | Information value | `information_value_declared` | `good_share.A` | 0.636363636364 | 0.636363636364 | 0.636363636364 | not run |
| 5 | Information value | `information_value_declared` | `good_share.B` | 0.272727272727 | 0.272727272727 | 0.272727272727 | not run |
| 5 | Information value | `information_value_declared` | `good_share.C` | 0.0909090909091 | 0.0909090909091 | 0.0909090909091 | not run |
| 5 | Information value | `information_value_declared` | `bad_share.A` | 0.272727272727 | 0.272727272727 | 0.272727272727 | not run |
| 5 | Information value | `information_value_declared` | `bad_share.B` | 0.636363636364 | 0.636363636364 | 0.636363636364 | not run |
| 5 | Information value | `information_value_declared` | `bad_share.C` | 0.0909090909091 | 0.0909090909091 | 0.0909090909091 | not run |
| 5 | Information value | `information_value_declared` | `woe.A` | 0.847297860387 | 0.847297860387 | 0.847297860387 | not run |
| 5 | Information value | `information_value_declared` | `woe.B` | -0.847297860387 | -0.847297860387 | -0.847297860387 | not run |
| 5 | Information value | `information_value_declared` | `woe.C` | 0 | 0 | 0 | not run |
| 5 | Information value | `information_value_declared` | `iv` | 0.616216625736 | 0.616216625736 | 0.616216625736 | not run |
| 5 | Information value | `information_value_large` | `good.G1` | 291 | 291 | 291 | not run |
| 5 | Information value | `information_value_large` | `good.G2` | 413 | 413 | 413 | not run |
| 5 | Information value | `information_value_large` | `good.G3` | 453 | 453 | 453 | not run |
| 5 | Information value | `information_value_large` | `good.G4` | 382 | 382 | 382 | not run |
| 5 | Information value | `information_value_large` | `good.G5` | 237 | 237 | 237 | not run |
| 5 | Information value | `information_value_large` | `good.G6` | 129 | 129 | 129 | not run |
| 5 | Information value | `information_value_large` | `bad.G1` | 1 | 1 | 1 | not run |
| 5 | Information value | `information_value_large` | `bad.G2` | 5 | 5 | 5 | not run |
| 5 | Information value | `information_value_large` | `bad.G3` | 12 | 12 | 12 | not run |
| 5 | Information value | `information_value_large` | `bad.G4` | 19 | 19 | 19 | not run |
| 5 | Information value | `information_value_large` | `bad.G5` | 28 | 28 | 28 | not run |
| 5 | Information value | `information_value_large` | `bad.G6` | 30 | 30 | 30 | not run |
| 5 | Information value | `information_value_large` | `good_share.G1` | 0.152777777778 | 0.152777777778 | 0.152777777778 | not run |
| 5 | Information value | `information_value_large` | `good_share.G2` | 0.216719077568 | 0.216719077568 | 0.216719077568 | not run |
| 5 | Information value | `information_value_large` | `good_share.G3` | 0.237683438155 | 0.237683438155 | 0.237683438155 | not run |
| 5 | Information value | `information_value_large` | `good_share.G4` | 0.200471698113 | 0.200471698113 | 0.200471698113 | not run |
| 5 | Information value | `information_value_large` | `good_share.G5` | 0.124475890985 | 0.124475890985 | 0.124475890985 | not run |
| 5 | Information value | `information_value_large` | `good_share.G6` | 0.0678721174004 | 0.0678721174004 | 0.0678721174004 | not run |
| 5 | Information value | `information_value_large` | `bad_share.G1` | 0.015306122449 | 0.015306122449 | 0.015306122449 | not run |
| 5 | Information value | `information_value_large` | `bad_share.G2` | 0.0561224489796 | 0.0561224489796 | 0.0561224489796 | not run |
| 5 | Information value | `information_value_large` | `bad_share.G3` | 0.127551020408 | 0.127551020408 | 0.127551020408 | not run |
| 5 | Information value | `information_value_large` | `bad_share.G4` | 0.198979591837 | 0.198979591837 | 0.198979591837 | not run |
| 5 | Information value | `information_value_large` | `bad_share.G5` | 0.290816326531 | 0.290816326531 | 0.290816326531 | not run |
| 5 | Information value | `information_value_large` | `bad_share.G6` | 0.311224489796 | 0.311224489796 | 0.311224489796 | not run |
| 5 | Information value | `information_value_large` | `woe.G1` | 2.30073152434 | 2.30073152434 | 2.30073152434 | not run |
| 5 | Information value | `information_value_large` | `woe.G2` | 1.35106604889 | 1.35106604889 | 1.35106604889 | not run |
| 5 | Information value | `information_value_large` | `woe.G3` | 0.622423251909 | 0.622423251909 | 0.622423251909 | not run |
| 5 | Information value | `information_value_large` | `woe.G4` | 0.00747081435923 | 0.00747081435923 | 0.00747081435923 | not run |
| 5 | Information value | `information_value_large` | `woe.G5` | -0.848579837138 | -0.848579837138 | -0.848579837138 | not run |
| 5 | Information value | `information_value_large` | `woe.G6` | -1.52288917581 | -1.52288917581 | -1.52288917581 | not run |
| 5 | Information value | `information_value_large` | `iv` | 1.11357398195 | 1.11357398195 | 1.11357398195 | not run |
| 5 | Information value | `information_value_small` | `good.A` | 3 | 3 | 3 | not run |
| 5 | Information value | `information_value_small` | `good.B` | 1 | 1 | 1 | not run |
| 5 | Information value | `information_value_small` | `bad.A` | 1 | 1 | 1 | not run |
| 5 | Information value | `information_value_small` | `bad.B` | 3 | 3 | 3 | not run |
| 5 | Information value | `information_value_small` | `good_share.A` | 0.75 | 0.75 | 0.75 | not run |
| 5 | Information value | `information_value_small` | `good_share.B` | 0.25 | 0.25 | 0.25 | not run |
| 5 | Information value | `information_value_small` | `bad_share.A` | 0.25 | 0.25 | 0.25 | not run |
| 5 | Information value | `information_value_small` | `bad_share.B` | 0.75 | 0.75 | 0.75 | not run |
| 5 | Information value | `information_value_small` | `woe.A` | 1.09861228867 | 1.09861228867 | 1.09861228867 | not run |
| 5 | Information value | `information_value_small` | `woe.B` | -1.09861228867 | -1.09861228867 | -1.09861228867 | not run |
| 5 | Information value | `information_value_small` | `iv` | 1.09861228867 | 1.09861228867 | 1.09861228867 | not run |
| 6 | Conditional information entropy ratio | `cier_large` | `ratio` | 0.178434220922 | 0.178434220922 | 0.178434220922 | not run |
| 6 | Conditional information entropy ratio | `cier_small` | `ratio` | 1 | 1 | 1 | not run |
| 7 | Mutual information | `mutual_information_large` | `mi` | 0.0253678293089 | 0.0253678293089 | 0.0253678293089 | not run |
| 7 | Mutual information | `mutual_information_small` | `mi` | 0.69314718056 | 0.69314718056 | 0.69314718056 | not run |
| 8 | Cumulative LGD accuracy ratio | `clar_large` | `clar` | 0.870875 | 0.870875 | 0.870875 | not run |
| 8 | Cumulative LGD accuracy ratio | `clar_small` | `clar` | 0.88 | 0.88 | 0.88 | not run |
| 9 | Loss capture ratio | `loss_capture_ratio_large` | `lcr` | 0.712725215999 | 0.712725215999 | 0.712725215999 | not run |
| 9 | Loss capture ratio | `loss_capture_ratio_small` | `lcr` | 1 | 1 | 1 | not run |
| 10 | Binomial test | `binomial_large` | `predicted_pd.G2` | 0.01 | 0.01 | 0.01 | not run |
| 10 | Binomial test | `binomial_large` | `predicted_pd.G5` | 0.08 | 0.08 | 0.08 | not run |
| 10 | Binomial test | `binomial_large` | `predicted_pd.G4` | 0.04 | 0.04 | 0.04 | not run |
| 10 | Binomial test | `binomial_large` | `predicted_pd.G6` | 0.15 | 0.15 | 0.15 | not run |
| 10 | Binomial test | `binomial_large` | `predicted_pd.G3` | 0.02 | 0.02 | 0.02 | not run |
| 10 | Binomial test | `binomial_large` | `predicted_pd.G1` | 0.005 | 0.005 | 0.005 | not run |
| 10 | Binomial test | `binomial_large` | `n.G2` | 418 | 418 | 418 | not run |
| 10 | Binomial test | `binomial_large` | `n.G5` | 265 | 265 | 265 | not run |
| 10 | Binomial test | `binomial_large` | `n.G4` | 401 | 401 | 401 | not run |
| 10 | Binomial test | `binomial_large` | `n.G6` | 159 | 159 | 159 | not run |
| 10 | Binomial test | `binomial_large` | `n.G3` | 465 | 465 | 465 | not run |
| 10 | Binomial test | `binomial_large` | `n.G1` | 292 | 292 | 292 | not run |
| 10 | Binomial test | `binomial_large` | `defaults.G2` | 5 | 5 | 5 | not run |
| 10 | Binomial test | `binomial_large` | `defaults.G5` | 28 | 28 | 28 | not run |
| 10 | Binomial test | `binomial_large` | `defaults.G4` | 19 | 19 | 19 | not run |
| 10 | Binomial test | `binomial_large` | `defaults.G6` | 30 | 30 | 30 | not run |
| 10 | Binomial test | `binomial_large` | `defaults.G3` | 12 | 12 | 12 | not run |
| 10 | Binomial test | `binomial_large` | `defaults.G1` | 1 | 1 | 1 | not run |
| 10 | Binomial test | `binomial_large` | `default_rate.G2` | 0.011961722488 | 0.011961722488 | 0.011961722488 | not run |
| 10 | Binomial test | `binomial_large` | `default_rate.G5` | 0.105660377358 | 0.105660377358 | 0.105660377358 | not run |
| 10 | Binomial test | `binomial_large` | `default_rate.G4` | 0.0473815461347 | 0.0473815461347 | 0.0473815461347 | not run |
| 10 | Binomial test | `binomial_large` | `default_rate.G6` | 0.188679245283 | 0.188679245283 | 0.188679245283 | not run |
| 10 | Binomial test | `binomial_large` | `default_rate.G3` | 0.0258064516129 | 0.0258064516129 | 0.0258064516129 | not run |
| 10 | Binomial test | `binomial_large` | `default_rate.G1` | 0.00342465753425 | 0.00342465753425 | 0.00342465753425 | not run |
| 10 | Binomial test | `binomial_large` | `p_value.G2` | 0.406457600058 | 0.406457600058 | 0.406457600058 | not run |
| 10 | Binomial test | `binomial_large` | `p_value.G5` | 0.0808713657023 | 0.0808713657023 | 0.0808713657023 | not run |
| 10 | Binomial test | `binomial_large` | `p_value.G4` | 0.257601863365 | 0.257601863365 | 0.257601863365 | not run |
| 10 | Binomial test | `binomial_large` | `p_value.G6` | 0.107015190981 | 0.107015190981 | 0.107015190981 | not run |
| 10 | Binomial test | `binomial_large` | `p_value.G3` | 0.225247406294 | 0.225247406294 | 0.225247406294 | not run |
| 10 | Binomial test | `binomial_large` | `p_value.G1` | 0.768612668399 | 0.768612668399 | 0.768612668399 | not run |
| 10 | Binomial test | `binomial_large` | `reject.G2` | False | 0 | False | not run |
| 10 | Binomial test | `binomial_large` | `reject.G5` | False | 0 | False | not run |
| 10 | Binomial test | `binomial_large` | `reject.G4` | False | 0 | False | not run |
| 10 | Binomial test | `binomial_large` | `reject.G6` | False | 0 | False | not run |
| 10 | Binomial test | `binomial_large` | `reject.G3` | False | 0 | False | not run |
| 10 | Binomial test | `binomial_large` | `reject.G1` | False | 0 | False | not run |
| 10 | Binomial test | `binomial_small` | `predicted_pd.A` | 0.2 | 0.2 | 0.2 | not run |
| 10 | Binomial test | `binomial_small` | `predicted_pd.B` | 0.6 | 0.6 | 0.6 | not run |
| 10 | Binomial test | `binomial_small` | `n.A` | 4 | 4 | 4 | not run |
| 10 | Binomial test | `binomial_small` | `n.B` | 4 | 4 | 4 | not run |
| 10 | Binomial test | `binomial_small` | `defaults.A` | 2 | 2 | 2 | not run |
| 10 | Binomial test | `binomial_small` | `defaults.B` | 2 | 2 | 2 | not run |
| 10 | Binomial test | `binomial_small` | `default_rate.A` | 0.5 | 0.5 | 0.5 | not run |
| 10 | Binomial test | `binomial_small` | `default_rate.B` | 0.5 | 0.5 | 0.5 | not run |
| 10 | Binomial test | `binomial_small` | `p_value.A` | 0.1808 | 0.1808 | 0.1808 | not run |
| 10 | Binomial test | `binomial_small` | `p_value.B` | 0.8208 | 0.8208 | 0.8208 | not run |
| 10 | Binomial test | `binomial_small` | `reject.A` | False | 0 | False | not run |
| 10 | Binomial test | `binomial_small` | `reject.B` | False | 0 | False | not run |
| 11 | Jeffreys test | `jeffreys_large` | `predicted_pd.G2` | 0.01 | 0.01 | 0.01 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `predicted_pd.G5` | 0.08 | 0.08 | 0.08 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `predicted_pd.G4` | 0.04 | 0.04 | 0.04 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `predicted_pd.G6` | 0.15 | 0.15 | 0.15 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `predicted_pd.G3` | 0.02 | 0.02 | 0.02 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `predicted_pd.G1` | 0.005 | 0.005 | 0.005 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `n.G2` | 418 | 418 | 418 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `n.G5` | 265 | 265 | 265 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `n.G4` | 401 | 401 | 401 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `n.G6` | 159 | 159 | 159 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `n.G3` | 465 | 465 | 465 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `n.G1` | 292 | 292 | 292 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `defaults.G2` | 5 | 5 | 5 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `defaults.G5` | 28 | 28 | 28 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `defaults.G4` | 19 | 19 | 19 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `defaults.G6` | 30 | 30 | 30 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `defaults.G3` | 12 | 12 | 12 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `defaults.G1` | 1 | 1 | 1 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `default_rate.G2` | 0.011961722488 | 0.011961722488 | 0.011961722488 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `default_rate.G5` | 0.105660377358 | 0.105660377358 | 0.105660377358 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `default_rate.G4` | 0.0473815461347 | 0.0473815461347 | 0.0473815461347 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `default_rate.G6` | 0.188679245283 | 0.188679245283 | 0.188679245283 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `default_rate.G3` | 0.0258064516129 | 0.0258064516129 | 0.0258064516129 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `default_rate.G1` | 0.00342465753425 | 0.00342465753425 | 0.00342465753425 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `p_value.G2` | 0.318965674717 | 0.318965674717 | 0.318965674717 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `p_value.G5` | 0.0663669661491 | 0.0663669661491 | 0.0663669661491 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `p_value.G4` | 0.220130907259 | 0.220130907259 | 0.220130907259 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `p_value.G6` | 0.0889864466866 | 0.0889864466866 | 0.0889864466866 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `p_value.G3` | 0.182066851732 | 0.182066851732 | 0.182066851732 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `p_value.G1` | 0.596636972779 | 0.596636972779 | 0.596636972779 | not run |
| 11 | Jeffreys test | `jeffreys_large` | `reject.G2` | False | 0 | False | not run |
| 11 | Jeffreys test | `jeffreys_large` | `reject.G5` | False | 0 | False | not run |
| 11 | Jeffreys test | `jeffreys_large` | `reject.G4` | False | 0 | False | not run |
| 11 | Jeffreys test | `jeffreys_large` | `reject.G6` | False | 0 | False | not run |
| 11 | Jeffreys test | `jeffreys_large` | `reject.G3` | False | 0 | False | not run |
| 11 | Jeffreys test | `jeffreys_large` | `reject.G1` | False | 0 | False | not run |
| 11 | Jeffreys test | `jeffreys_small` | `predicted_pd.A` | 0.5 | 0.5 | 0.5 | not run |
| 11 | Jeffreys test | `jeffreys_small` | `n.A` | 4 | 4 | 4 | not run |
| 11 | Jeffreys test | `jeffreys_small` | `defaults.A` | 2 | 2 | 2 | not run |
| 11 | Jeffreys test | `jeffreys_small` | `default_rate.A` | 0.5 | 0.5 | 0.5 | not run |
| 11 | Jeffreys test | `jeffreys_small` | `p_value.A` | 0.5 | 0.5 | 0.5 | not run |
| 11 | Jeffreys test | `jeffreys_small` | `reject.A` | False | 0 | False | not run |
| 12 | Hosmer test | `hosmer_large` | `p_value` | 0.432948375006 | 0.432948375006 | 0.432948375006 | not run |
| 12 | Hosmer test | `hosmer_large` | `reject` | False | 0 | False | not run |
| 12 | Hosmer test | `hosmer_large_ddof2` | `p_value` | 0.205701260077 | 0.205701260077 | 0.205701260077 | not run |
| 12 | Hosmer test | `hosmer_large_ddof2` | `reject` | False | 0 | False | not run |
| 12 | Hosmer test | `hosmer_small` | `p_value` | 0.298694689289 | 0.298694689289 | 0.298694689289 | not run |
| 12 | Hosmer test | `hosmer_small` | `reject` | False | 0 | False | not run |
| 13 | Spiegelhalter test | `spiegelhalter_large` | `z` | 2.20596309398 | 2.20596309398 | 2.20596309398 | not run |
| 13 | Spiegelhalter test | `spiegelhalter_large` | `reject` | True | 1 | True | not run |
| 13 | Spiegelhalter test | `spiegelhalter_small` | `z` | 1.54303349962 | 1.54303349962 | 1.54303349962 | not run |
| 13 | Spiegelhalter test | `spiegelhalter_small` | `reject` | False | 0 | False | not run |
| 14 | Brier score | `brier_large` | `brier` | 0.0427801 | 0.0427801 | 0.0427801 | not run |
| 14 | Brier score | `brier_small` | `brier` | 0.3 | 0.3 | 0.3 | not run |
| 15 | Redelmeier test | `redelmeier_large` | `z` | -1.95024886348 | -1.95024886348 | -1.95024886348 | not run |
| 15 | Redelmeier test | `redelmeier_large` | `p_value` | 0.0511464643483 | 0.0511464643483 | 0.0511464643483 | not run |
| 15 | Redelmeier test | `redelmeier_small` | `z` | 0.637193092864 | 0.637193092864 | 0.637193092864 | not run |
| 15 | Redelmeier test | `redelmeier_small` | `p_value` | 0.523999076235 | 0.523999076235 | 0.523999076235 | not run |
| 16 | Normal test for annual default rates | `normal_test_large` | `estimate` | 0.00474333333333 | 0.00474333333333 | 0.00474333333333 | not run |
| 16 | Normal test for annual default rates | `normal_test_large` | `z` | 2.70050303789 | 2.70050303789 | 2.70050303789 | not run |
| 16 | Normal test for annual default rates | `normal_test_large` | `p_value` | 0.00346173523653 | 0.00346173523653 | 0.00346173523653 | not run |
| 16 | Normal test for annual default rates | `normal_test_large` | `reject` | True | 1 | True | not run |
| 16 | Normal test for annual default rates | `normal_test_small` | `estimate` | 0.15 | 0.15 | 0.15 | not run |
| 16 | Normal test for annual default rates | `normal_test_small` | `z` | 2.32379000772 | 2.32379000772 | 2.32379000772 | not run |
| 16 | Normal test for annual default rates | `normal_test_small` | `p_value` | 0.0100683757752 | 0.0100683757752 | 0.0100683757752 | not run |
| 16 | Normal test for annual default rates | `normal_test_small` | `reject` | True | 1 | True | not run |
| 17 | Kendall's tau | `kendall_large` | `tau` | 0.510576580538 | 0.510576580538 | 0.510576580538 | not run |
| 17 | Kendall's tau | `kendall_large` | `p_value` | 6.7747787287e-78 | 6.7747787287e-78 | 6.80070756524e-78 | not run |
| 17 | Kendall's tau | `kendall_large_tau_c` | `tau` | 0.527631944444 | 0.527631944444 | 0.527631944444 | not run |
| 17 | Kendall's tau | `kendall_small` | `tau` | 1 | 1 | 1 | not run |
| 17 | Kendall's tau | `kendall_small` | `p_value` | 0.0833333333333 | 0.0833333333333 | 0.0833333333333 | not run |
| 18 | Somers' D | `somersd_large` | `d` | 0.576240206897 | 0.576240206897 | 0.576240206897 | not run |
| 18 | Somers' D | `somersd_small_table` | `d` | 0.5 | 0.5 | 0.5 | not run |
| 19 | Spearman's rho | `spearman_large` | `rho` | 0.705605227212 | 0.705605227212 | 0.705605227212 | not run |
| 19 | Spearman's rho | `spearman_large` | `p_value` | 1.60655054792e-91 | 1.60655054792e-91 | 1.60655054792e-91 | not run |
| 19 | Spearman's rho | `spearman_small` | `rho` | 1 | 1 | 1 | not run |
| 19 | Spearman's rho | `spearman_small` | `p_value` | 0 | 0 | 0.0833333333333 (documented) | not run |
| 20 | Pearson's r | `pearson_large` | `r` | 0.713638910311 | 0.713638910311 | 0.713638910311 | not run |
| 20 | Pearson's r | `pearson_large` | `p_value` | 1.65347540408e-94 | 1.65347540408e-94 | 1.65347540408e-94 | not run |
| 20 | Pearson's r | `pearson_small` | `r` | 0.959166304663 | 0.959166304663 | 0.959166304663 | not run |
| 20 | Pearson's r | `pearson_small` | `p_value` | 0.0408336953375 | 0.0408336953375 | 0.0408336953375 | not run |
| 21 | Herfindahl index | `herfindahl_declared` | `cv` | 0.816496580928 | 0.816496580928 | 0.816496580928 | not run |
| 21 | Herfindahl index | `herfindahl_declared` | `hhi` | 0.555555555556 | 0.555555555556 | 0.555555555556 | not run |
| 21 | Herfindahl index | `herfindahl_large` | `cv` | 0.479899989581 | 0.479899989581 | 0.479899989581 | not run |
| 21 | Herfindahl index | `herfindahl_large` | `hhi` | 0.153788 | 0.153788 | 0.153788 | not run |
| 21 | Herfindahl index | `herfindahl_small` | `cv` | 0.333333333333 | 0.333333333333 | 0.333333333333 | not run |
| 21 | Herfindahl index | `herfindahl_small` | `hhi` | 0.555555555556 | 0.555555555556 | 0.555555555556 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_initial.G1` | 80 | 80 | 80 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_initial.G2` | 117 | 117 | 117 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_initial.G3` | 160 | 160 | 160 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_initial.G4` | 218 | 218 | 218 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_initial.G5` | 190 | 190 | 190 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_initial.G6` | 135 | 135 | 135 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_initial.G7` | 75 | 75 | 75 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_initial.G8` | 25 | 25 | 25 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_current.G1` | 64 | 64 | 64 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_current.G2` | 149 | 149 | 149 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_current.G3` | 195 | 195 | 195 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_current.G4` | 373 | 373 | 373 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_current.G5` | 283 | 283 | 283 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_current.G6` | 157 | 157 | 157 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_current.G7` | 79 | 79 | 79 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `n_current.G8` | 0 | 0 | 0 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `h_initial` | 0.153788 | 0.153788 | 0.153788 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `h_current` | 0.186053254438 | 0.186053254438 | 0.186053254438 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `z` | 0.83381894427 | 0.83381894427 | 0.83381894427 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `p_value` | 0.202191509175 | 0.202191509175 | 0.202191509175 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_large` | `reject` | False | 0 | False | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `n_initial.A` | 4 | 4 | 4 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `n_initial.B` | 2 | 2 | 2 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `n_current.A` | 5 | 5 | 5 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `n_current.B` | 1 | 1 | 1 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `h_initial` | 0.555555555556 | 0.555555555556 | 0.555555555556 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `h_current` | 0.722222222222 | 0.722222222222 | 0.722222222222 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `z` | 0.514495755428 | 0.514495755428 | 0.514495755428 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `p_value` | 0.303452713609 | 0.303452713609 | 0.303452713609 | not run |
| 22 | Multiple-period Herfindahl test | `herfindahl_multi_small` | `reject` | False | 0 | False | not run |
| 23 | Population stability index | `psi_declared` | `expected.A` | 0.636363636364 | 0.636363636364 | 0.636363636364 | not run |
| 23 | Population stability index | `psi_declared` | `expected.B` | 0.272727272727 | 0.272727272727 | 0.272727272727 | not run |
| 23 | Population stability index | `psi_declared` | `expected.C` | 0.0909090909091 | 0.0909090909091 | 0.0909090909091 | not run |
| 23 | Population stability index | `psi_declared` | `actual.A` | 0.272727272727 | 0.272727272727 | 0.272727272727 | not run |
| 23 | Population stability index | `psi_declared` | `actual.B` | 0.636363636364 | 0.636363636364 | 0.636363636364 | not run |
| 23 | Population stability index | `psi_declared` | `actual.C` | 0.0909090909091 | 0.0909090909091 | 0.0909090909091 | not run |
| 23 | Population stability index | `psi_declared` | `psi` | 0.616216625736 | 0.616216625736 | 0.616216625736 | not run |
| 23 | Population stability index | `psi_large` | `expected.B1` | 0.106727574751 | 0.106727574751 | 0.106727574751 | not run |
| 23 | Population stability index | `psi_large` | `expected.B2` | 0.133305647841 | 0.133305647841 | 0.133305647841 | not run |
| 23 | Population stability index | `psi_large` | `expected.B3` | 0.193106312292 | 0.193106312292 | 0.193106312292 | not run |
| 23 | Population stability index | `psi_large` | `expected.B4` | 0.21303986711 | 0.21303986711 | 0.21303986711 | not run |
| 23 | Population stability index | `psi_large` | `expected.B5` | 0.138289036545 | 0.138289036545 | 0.138289036545 | not run |
| 23 | Population stability index | `psi_large` | `expected.B6` | 0.104235880399 | 0.104235880399 | 0.104235880399 | not run |
| 23 | Population stability index | `psi_large` | `expected.B7` | 0.0710132890365 | 0.0710132890365 | 0.0710132890365 | not run |
| 23 | Population stability index | `psi_large` | `expected.B8` | 0.0402823920266 | 0.0402823920266 | 0.0402823920266 | not run |
| 23 | Population stability index | `psi_large` | `actual.B1` | 0.137721238938 | 0.137721238938 | 0.137721238938 | not run |
| 23 | Population stability index | `psi_large` | `actual.B2` | 0.167588495575 | 0.167588495575 | 0.167588495575 | not run |
| 23 | Population stability index | `psi_large` | `actual.B3` | 0.231747787611 | 0.231747787611 | 0.231747787611 | not run |
| 23 | Population stability index | `psi_large` | `actual.B4` | 0.189712389381 | 0.189712389381 | 0.189712389381 | not run |
| 23 | Population stability index | `psi_large` | `actual.B5` | 0.152101769912 | 0.152101769912 | 0.152101769912 | not run |
| 23 | Population stability index | `psi_large` | `actual.B6` | 0.0669247787611 | 0.0669247787611 | 0.0669247787611 | not run |
| 23 | Population stability index | `psi_large` | `actual.B7` | 0.0536504424779 | 0.0536504424779 | 0.0536504424779 | not run |
| 23 | Population stability index | `psi_large` | `actual.B8` | 0.000553097345133 | 0.000553097345133 | 0.000553097345133 | not run |
| 23 | Population stability index | `psi_large` | `psi` | 0.218581795049 | 0.218581795049 | 0.218581795049 | not run |
| 23 | Population stability index | `psi_small` | `expected.A` | 0.75 | 0.75 | 0.75 | not run |
| 23 | Population stability index | `psi_small` | `expected.B` | 0.25 | 0.25 | 0.25 | not run |
| 23 | Population stability index | `psi_small` | `actual.A` | 0.25 | 0.25 | 0.25 | not run |
| 23 | Population stability index | `psi_small` | `actual.B` | 0.75 | 0.75 | 0.75 | not run |
| 23 | Population stability index | `psi_small` | `psi` | 1.09861228867 | 1.09861228867 | 1.09861228867 | not run |
| 24 | Migration bandwidth | `migration_bandwidth_large` | `upper` | 0.284198113208 | 0.284198113208 | 0.284198113208 | not run |
| 24 | Migration bandwidth | `migration_bandwidth_large` | `lower` | 0.289707750953 | 0.289707750953 | 0.289707750953 | not run |
| 24 | Migration bandwidth | `migration_bandwidth_small` | `upper` | 0.8 | 0.8 | 0.8 | not run |
| 24 | Migration bandwidth | `migration_bandwidth_small` | `lower` | 0.8 | 0.8 | 0.8 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G1.G2` | 17.9781630416 | 17.9781630416 | 17.9781630416 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G1.G3` | 2.02702825274 | 2.02702825274 | 2.02702825274 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G1.G4` | 2.02702825274 | 2.02702825274 | 2.02702825274 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G1.G5` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G1.G6` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G1.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G2.G1` | 12.4580930175 | 12.4580930175 | 12.4580930175 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G2.G3` | 11.2420060003 | 11.2420060003 | 11.2420060003 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G2.G4` | 4.04372899513 | 4.04372899513 | 4.04372899513 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G2.G5` | 2.88009216442 | 2.88009216442 | 2.88009216442 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G2.G6` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G2.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G3.G1` | 3.46311342467 | 3.46311342467 | 3.46311342467 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G3.G2` | 13.4895013667 | 13.4895013667 | 13.4895013667 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G3.G4` | 14.4408327953 | 14.4408327953 | 14.4408327953 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G3.G5` | 3.46370950448 | 3.46370950448 | 3.46370950448 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G3.G6` | 3.21785797217 | 3.21785797217 | 3.21785797217 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G3.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G4.G1` | 3.21239611784 | 3.21239611784 | 3.21239611784 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G4.G2` | 4.36603883194 | 4.36603883194 | 4.36603883194 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G4.G3` | 15.3699244263 | 15.3699244263 | 15.3699244263 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G4.G5` | 16.7741211352 | 16.7741211352 | 16.7741211352 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G4.G6` | 4.22292091936 | 4.22292091936 | 4.22292091936 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G4.G7` | 2.67489500563 | 2.67489500563 | 2.67489500563 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G5.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G5.G2` | 2.88105353709 | 2.88105353709 | 2.88105353709 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G5.G3` | 2.73943928906 | 2.73943928906 | 2.73943928906 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G5.G4` | 12.5897500774 | 12.5897500774 | 12.5897500774 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G5.G6` | 11.4977082634 | 11.4977082634 | 11.4977082634 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G5.G7` | 2.37224501287 | 2.37224501287 | 2.37224501287 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G6.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G6.G2` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G6.G3` | 1.7476317883 | 1.7476317883 | 1.7476317883 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G6.G4` | 3.22540948279 | 3.22540948279 | 3.22540948279 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G6.G5` | 13.3689164774 | 13.3689164774 | 13.3689164774 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G6.G7` | 12.7246500348 | 12.7246500348 | 12.7246500348 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G7.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G7.G2` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G7.G3` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G7.G4` | 1.75430504956 | 1.75430504956 | 1.75430504956 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G7.G5` | 1.97294788692 | 1.97294788692 | 1.97294788692 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `z.G7.G6` | 15.4608372704 | 15.4608372704 | 15.4608372704 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G1.G2` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G1.G3` | 0.9786702383 | 0.9786702383 | 0.9786702383 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G1.G4` | 0.9786702383 | 0.9786702383 | 0.9786702383 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G1.G5` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G1.G6` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G1.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G2.G1` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G2.G3` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G2.G4` | 0.999973696138 | 0.999973696138 | 0.999973696138 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G2.G5` | 0.998012205324 | 0.998012205324 | 0.998012205324 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G2.G6` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G2.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G3.G1` | 0.999733018372 | 0.999733018372 | 0.999733018372 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G3.G2` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G3.G4` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G3.G5` | 0.999733609234 | 0.999733609234 | 0.999733609234 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G3.G6` | 0.999354241235 | 0.999354241235 | 0.999354241235 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G3.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G4.G1` | 0.999341836283 | 0.999341836283 | 0.999341836283 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G4.G2` | 0.999993674 | 0.999993674 | 0.999993674 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G4.G3` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G4.G5` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G4.G6` | 0.999987942177 | 0.999987942177 | 0.999987942177 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G4.G7` | 0.996262367149 | 0.996262367149 | 0.996262367149 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G5.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G5.G2` | 0.998018258444 | 0.998018258444 | 0.998018258444 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G5.G3` | 0.996922795991 | 0.996922795991 | 0.996922795991 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G5.G4` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G5.G6` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G5.G7` | 0.991159818981 | 0.991159818981 | 0.991159818981 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G6.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G6.G2` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G6.G3` | 0.959736096391 | 0.959736096391 | 0.959736096391 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G6.G4` | 0.999371036966 | 0.999371036966 | 0.999371036966 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G6.G5` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G6.G7` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G7.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G7.G2` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G7.G3` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G7.G4` | 0.960310874496 | 0.960310874496 | 0.960310874496 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G7.G5` | 0.975749250011 | 0.975749250011 | 0.975749250011 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large` | `cdf.G7.G6` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G1.G2` | 16.8904015373 | 16.8904015373 | 16.8904015373 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G1.G3` | 2.02531746352 | 2.02531746352 | 2.02531746352 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G1.G4` | 2.02531746352 | 2.02531746352 | 2.02531746352 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G1.G5` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G1.G6` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G1.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G2.G1` | 11.9947143921 | 11.9947143921 | 11.9947143921 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G2.G3` | 10.8979854492 | 10.8979854492 | 10.8979854492 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G2.G4` | 4.02705631347 | 4.02705631347 | 4.02705631347 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G2.G5` | 2.87404986067 | 2.87404986067 | 2.87404986067 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G2.G6` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G2.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G3.G1` | 3.46030949401 | 3.46030949401 | 3.46030949401 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G3.G2` | 13.3265871219 | 13.3265871219 | 13.3265871219 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G3.G4` | 14.2414876239 | 14.2414876239 | 14.2414876239 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G3.G5` | 3.46090412688 | 3.46090412688 | 3.46090412688 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G3.G6` | 3.21560819355 | 3.21560819355 | 3.21560819355 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G3.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G4.G1` | 3.21085619784 | 3.21085619784 | 3.21085619784 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G4.G2` | 4.36217508 | 4.36217508 | 4.36217508 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G4.G3` | 15.2038680417 | 15.2038680417 | 15.2038680417 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G4.G5` | 16.5589310257 | 16.5589310257 | 16.5589310257 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G4.G6` | 4.21942450845 | 4.21942450845 | 4.21942450845 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G4.G7` | 2.67400574952 | 2.67400574952 | 2.67400574952 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G5.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G5.G2` | 2.87805243884 | 2.87805243884 | 2.87805243884 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G5.G3` | 2.73685895271 | 2.73685895271 | 2.73685895271 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G5.G4` | 12.3461880924 | 12.3461880924 | 12.3461880924 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G5.G6` | 11.3112952797 | 11.3112952797 | 11.3112952797 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G5.G7` | 2.37056882241 | 2.37056882241 | 2.37056882241 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G6.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G6.G2` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G6.G3` | 1.74642491966 | 1.74642491966 | 1.74642491966 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G6.G4` | 3.21784142931 | 3.21784142931 | 3.21784142931 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G6.G5` | 12.8588512943 | 12.8588512943 | 12.8588512943 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G6.G7` | 12.282479125 | 12.282479125 | 12.282479125 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G7.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G7.G2` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G7.G3` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G7.G4` | 1.75374748812 | 1.75374748812 | 1.75374748812 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G7.G5` | 1.97215489381 | 1.97215489381 | 1.97215489381 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `z.G7.G6` | 15.0925829992 | 15.0925829992 | 15.0925829992 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G1.G2` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G1.G3` | 0.97858261178 | 0.97858261178 | 0.97858261178 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G1.G4` | 0.97858261178 | 0.97858261178 | 0.97858261178 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G1.G5` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G1.G6` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G1.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G2.G1` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G2.G3` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G2.G4` | 0.999971760245 | 0.999971760245 | 0.999971760245 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G2.G5` | 0.997973775095 | 0.997973775095 | 0.997973775095 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G2.G6` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G2.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G3.G1` | 0.999730222569 | 0.999730222569 | 0.999730222569 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G3.G2` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G3.G4` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G3.G5` | 0.999730817747 | 0.999730817747 | 0.999730817747 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G3.G6` | 0.999349157915 | 0.999349157915 | 0.999349157915 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G3.G7` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G4.G1` | 0.999338299291 | 0.999338299291 | 0.999338299291 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G4.G2` | 0.999993561212 | 0.999993561212 | 0.999993561212 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G4.G3` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G4.G5` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G4.G6` | 0.999987753664 | 0.999987753664 | 0.999987753664 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G4.G7` | 0.996252441675 | 0.996252441675 | 0.996252441675 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G5.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G5.G2` | 0.997999306906 | 0.997999306906 | 0.997999306906 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G5.G3` | 0.996898555898 | 0.996898555898 | 0.996898555898 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G5.G4` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G5.G6` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G5.G7` | 0.991119631499 | 0.991119631499 | 0.991119631499 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G6.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G6.G2` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G6.G3` | 0.959631428548 | 0.959631428548 | 0.959631428548 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G6.G4` | 0.999354203991 | 0.999354203991 | 0.999354203991 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G6.G5` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G6.G7` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G7.G1` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G7.G2` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G7.G3` | NaN | NaN | NaN | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G7.G4` | 0.960263107731 | 0.960263107731 | 0.960263107731 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G7.G5` | 0.975704036472 | 0.975704036472 | 0.975704036472 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_large_initial_counts` | `cdf.G7.G6` | 1 | 1 | 1 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `z.1.2` | 0.603022689156 | 0.603022689156 | 0.603022689156 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `z.1.3` | 0 | 0 | 0 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `z.2.1` | 0.603022689156 | 0.603022689156 | 0.603022689156 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `z.2.3` | 0.603022689156 | 0.603022689156 | 0.603022689156 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `z.3.1` | 0 | 0 | 0 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `z.3.2` | 0.603022689156 | 0.603022689156 | 0.603022689156 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `cdf.1.2` | 0.726753202297 | 0.726753202297 | 0.726753202297 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `cdf.1.3` | 0.5 | 0.5 | 0.5 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `cdf.2.1` | 0.726753202297 | 0.726753202297 | 0.726753202297 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `cdf.2.3` | 0.726753202297 | 0.726753202297 | 0.726753202297 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `cdf.3.1` | 0.5 | 0.5 | 0.5 | not run |
| 25 | Adjacent-cell shape checks | `migration_stability_small` | `cdf.3.2` | 0.726753202297 | 0.726753202297 | 0.726753202297 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_large` | `n.portfolio` | 600 | 600 | 600 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_large` | `realised_mean.portfolio` | 0.4545255 | 0.4545255 | 0.4545255 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_large` | `pred_mean.portfolio` | 0.404998666667 | 0.404998666667 | 0.404998666667 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_large` | `s2.portfolio` | 0.0327972312153 | 0.0327972312153 | 0.0327972312153 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_large` | `mean_error.portfolio` | 0.0495268333333 | 0.0495268333333 | 0.0495268333333 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_large` | `t.portfolio` | 6.69880900084 | 6.69880900084 | 6.69880900084 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_large` | `p_value.portfolio` | 2.42501373748e-11 | 2.42501373748e-11 | 2.42501373748e-11 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_small` | `n.portfolio` | 4 | 4 | 4 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_small` | `realised_mean.portfolio` | 0.475 | 0.475 | 0.475 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_small` | `pred_mean.portfolio` | 0.5 | 0.5 | 0.5 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_small` | `s2.portfolio` | 0.0225 | 0.0225 | 0.0225 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_small` | `mean_error.portfolio` | -0.025 | -0.025 | -0.025 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_small` | `t.portfolio` | -0.333333333333 | -0.333333333333 | -0.333333333333 | not run |
| 26 | LGD t-test | `lgd_t_test_portfolio_small` | `p_value.portfolio` | 0.619589812243 | 0.619589812243 | 0.619589812243 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `n.S3` | 109 | 109 | 109 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `n.S2` | 176 | 176 | 176 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `n.S1` | 315 | 315 | 315 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `realised_mean.S3` | 0.468733944954 | 0.468733944954 | 0.468733944954 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `realised_mean.S2` | 0.44606875 | 0.44606875 | 0.44606875 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `realised_mean.S1` | 0.454333968254 | 0.454333968254 | 0.454333968254 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `pred_mean.S3` | 0.415257798165 | 0.415257798165 | 0.415257798165 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `pred_mean.S2` | 0.409215340909 | 0.409215340909 | 0.409215340909 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `pred_mean.S1` | 0.399092698413 | 0.399092698413 | 0.399092698413 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `s2.S3` | 0.0373560129443 | 0.0373560129443 | 0.0373560129443 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `s2.S2` | 0.0359180965597 | 0.0359180965597 | 0.0359180965597 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `s2.S1` | 0.029570606699 | 0.029570606699 | 0.029570606699 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `mean_error.S3` | 0.053476146789 | 0.053476146789 | 0.053476146789 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `mean_error.S2` | 0.0368534090909 | 0.0368534090909 | 0.0368534090909 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `mean_error.S1` | 0.0552412698413 | 0.0552412698413 | 0.0552412698413 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `t.S3` | 2.88863784705 | 2.88863784705 | 2.88863784705 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `t.S2` | 2.57974836069 | 2.57974836069 | 2.57974836069 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `t.S1` | 5.70149585089 | 5.70149585089 | 5.70149585089 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `p_value.S3` | 0.00233797835587 | 0.00233797835587 | 0.00233797835587 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `p_value.S2` | 0.00535413368275 | 0.00535413368275 | 0.00535413368274 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_large` | `p_value.S1` | 1.37003523933e-08 | 1.37003523933e-08 | 1.37003523933e-08 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `n.A` | 2 | 2 | 2 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `n.B` | 2 | 2 | 2 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `realised_mean.A` | 0.3 | 0.3 | 0.3 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `realised_mean.B` | 0.65 | 0.65 | 0.65 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `pred_mean.A` | 0.3 | 0.3 | 0.3 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `pred_mean.B` | 0.7 | 0.7 | 0.7 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `s2.A` | 0.02 | 0.02 | 0.02 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `s2.B` | 0.045 | 0.045 | 0.045 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `mean_error.A` | -1.38777878078e-17 | -1.38777878078e-17 | -1.38777878078e-17 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `mean_error.B` | -0.05 | -0.05 | -0.05 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `t.A` | -1.38777878078e-16 | -1.38777878078e-16 | -1.38777878078e-16 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `t.B` | -0.333333333333 | -0.333333333333 | -0.333333333333 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `p_value.A` | 0.5 | 0.5 | 0.5 | not run |
| 26 | LGD t-test | `lgd_t_test_segment_small` | `p_value.B` | 0.60241638235 | 0.60241638235 | 0.60241638235 | not run |
| 27 | ELBE t-test | `elbe_t_test_large` | `facilities` | 600 | 600 | 600 | not run |
| 27 | ELBE t-test | `elbe_t_test_large` | `lgd_mean` | 0.4545255 | 0.4545255 | 0.4545255 | not run |
| 27 | ELBE t-test | `elbe_t_test_large` | `elbe_mean` | 0.404998666667 | 0.404998666667 | 0.404998666667 | not run |
| 27 | ELBE t-test | `elbe_t_test_large` | `t` | 6.69880900084 | 6.69880900084 | 6.69880900084 | not run |
| 27 | ELBE t-test | `elbe_t_test_large` | `p_value` | 4.85002747495e-11 | 4.85002747495e-11 | 4.85002747495e-11 | not run |
| 27 | ELBE t-test | `elbe_t_test_small` | `facilities` | 4 | 4 | 4 | not run |
| 27 | ELBE t-test | `elbe_t_test_small` | `lgd_mean` | 0.475 | 0.475 | 0.475 | not run |
| 27 | ELBE t-test | `elbe_t_test_small` | `elbe_mean` | 0.5 | 0.5 | 0.5 | not run |
| 27 | ELBE t-test | `elbe_t_test_small` | `t` | -0.333333333333 | -0.333333333333 | -0.333333333333 | not run |
| 27 | ELBE t-test | `elbe_t_test_small` | `p_value` | 0.760820375515 | 0.760820375515 | 0.760820375515 | not run |
| 28 | Loss shortfall | `loss_shortfall_large` | `shortfall` | 0.116823637066 | 0.116823637066 | 0.116823637066 | not run |
| 28 | Loss shortfall | `loss_shortfall_small` | `shortfall` | 0 | 0 | 0 | not run |
| 29 | Exposure-weighted mean absolute error | `mean_absolute_deviation_large` | `mad` | 0.161105203607 | 0.161105203607 | 0.161105203607 | not run |
| 29 | Exposure-weighted mean absolute error | `mean_absolute_deviation_small` | `mad` | 0.12 | 0.12 | 0.12 | not run |
