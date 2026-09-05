# Migrating from 0.1.2

The 0.2 development series corrects statistical behavior and invalid-input handling. Recalculate stored results; this is not a drop-in numerical patch. No release is published by the GitHub CI workflow.

| Method | Corrected behavior |
|---|---|
| Brier | Mean squared **individual** errors replaces a sum of squared grade-mean errors. |
| Spiegelhalter | Correct outcome/forecast orientation; individual observations; two-sided rule honors alpha. |
| Pearson | Uses Pearson, previously Spearman; the SciPy result exposes `statistic` and `pvalue`. |
| Kendall / Spearman / Somers D | Current SciPy calls honor variants/alternatives; Somers D accepts a single contingency table. |
| KS | Compares score distributions conditional on class, replacing comparison of labels with predictions. |
| CLAR | Ordered shared grade thresholds, complete tie bands and origin; follows the VUROCS ordinal convention and remains in [0,1]. |
| LCR | Explicit cumulative **EAD** horizontal axis, pooled score ties, and model/ideal gains above the diagonal. Old account-axis results are not comparable. |
| BER | Honors the supplied target column and returns full precision; represents empirical threshold-optimized error, not irreducible Bayes error. |
| HHI | Uses a common grade universe across periods. Single-period `herfindahl_test` removes unused `alpha_level`; add `rating_order` to retain empty grades. Current uniform shares make the comparison undefined. Summary grade `total` is reserved. |
| Hosmer | Default `ddof=0` documents the fixed-PD chi-square test; explicitly choose `ddof=2` for the fitted-logistic approximation. Boundary grade PDs are rejected. |
| Migration statistics | Correct ECB distance normalization and directional denominators; zero migration in a direction returns 0. |
| Migration stability | Complete ordered matrices; undefined cells return NaN without divide-by-zero warnings. Returned values are **normal CDFs**, not upper-tail or two-sided p-values. |
| IV / PSI | Symmetric additive smoothing (default 0.5) followed by normalization; zero smoothing requires positive cells. No bins are silently dropped. IV removes unused `pr`; its table now explicitly names raw counts, shares, WoE and contributions. PSI supports explicit `expected` and `actual` sample labels. |
| Entropy / KL | Zero-rate boundary terms are handled without warnings or input mutation. CIER rejects zero marginal entropy; historical KL name means grade/default mutual information in nats. |
| LGD t test | `level='segment'` works; `'pool'` remains an alias. Invalid levels fail, and signed realised-minus-predicted errors are tested. |
| ELBE | Signed two-sided paired inference; `lgd_mean` now means realised LGD, and `elbe_mean` is added. |
| Normal test | Correct sample error variance and upper normal tail; `outcome` is a boolean. Historical `t_stat` column contains the **normal z statistic**. Inputs are annual grade-level rates. |
| Redelmeier | Correct symmetric variance for a documented **midpoint-Bernoulli null**, signed Brier-loss difference, two-sided probability, configurable columns, no printing. Identical forecasts return (0,1). This convention is not an unrestricted equal-average-Brier test. |
| Loss shortfall / MAD | Validated exposure weights and LGD fractions; examples now pass the intended columns. Shortfall sign is positive for underestimated loss. |

All 29 functions are exported at package root. Arbitrary limits on grade counts are removed. Missing columns, nonfinite data, invalid options and undefined inference fail deliberately. This replaces assertions, incidental KeyErrors, silent fallbacks and some historical NaN results. The unused private calculation helpers are consolidated into documented validation, grouping, entropy and curve helpers; private functions are not a stable API.

Python support is now 3.11+. Runtime requirements are NumPy, pandas, SciPy and scikit-learn. Documentation and test dependencies are optional extras. Research/data payloads are excluded from the wheel and source distribution.
