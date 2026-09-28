# Statistical extensions

The [extension catalogue](extension_catalogue.md) adds 31 functions representing
the plan's 30 entries (Stuart-Maxwell and McNemar have separate APIs). The original
29 book-aligned functions retain their signatures and return types.
See the [verification record](extension_verification.md) for executed checks,
dependency versions and implementation boundaries.

## Installation and compatibility

The base requirements remain Python 3.11+, NumPy 1.26+, pandas 2.1+, SciPy 1.11+
and scikit-learn 1.3+. Install `pip install 'meliora[timeseries]'` for ADF, KPSS,
BDS, fitted-normal Anderson-Darling, Phillips-Perron, Engle-Granger and Johansen.
The extra uses statsmodels >=0.14.4,<0.15 and arch >=7.2,<8. Statsmodels excludes
pandas 2.1.0; the resolver selects pandas 2.1.1 or later for this extra. Optional
imports occur inside the relevant functions and cannot block the base import.

## Shared input contract

- Numeric inputs must be real, nonempty and finite. Missing values are rejected;
  no observations are dropped, filled or reordered. Inputs are copied or read
  without mutation. Complex values, datetime arrays used as observations and
  numeric strings are rejected.
- Paired inputs have matching lengths. When multiple inputs carry pandas
  indexes, their indexes must match exactly. A mixture of indexed and unindexed
  inputs is interpreted positionally; the caller asserts alignment.
- For temporal tests, arrays assert that rows are in equally spaced temporal
  order. Indexed inputs require unique, increasing numeric or temporal indexes.
  Numeric/timedelta gaps must be equal; datetime indexes must have an inferable
  calendar frequency (monthly and business-day frequencies are allowed).
  Period indexes require consecutive periods. No silent sorting or gap filling.
- Regression designs are supplied explicitly, including a nonzero constant
  column. Full column rank, condition number <=1e12 and positive residual df
  are required. There is no formula parser or automatic intercept insertion.
  White's expanded design and paired categorical covariance deliberately use
  effective rank; their original input designs still obey their own contracts.
- Constant observations are rejected when variance is needed. Comparisons with
  zero variance return unavailable inference where documented. Exact count
  tests allow boundary probabilities and zero cells where mathematically valid.
- `alpha` is finite and strictly between zero and one. Johansen permits only
  .10, .05 or .01 because its backend provides critical values at those levels.

## Common result schema

All new APIs return a pandas DataFrame. The stable shared columns are:

| Field | Meaning |
|---|---|
| `test`, `statistic` | Test name and observed statistic |
| `pvalue` | Numerical p-value, tabulated boundary, or NaN |
| `nobs` | Effective sample size after method-specific truncation |
| `df` | Reference degrees of freedom, or NaN when inapplicable |
| `alternative` | Requested direction or named alternative |
| `method`, `reference_distribution` | Inference variant and reference law |
| `status` | `ok`, `bounded`, `undefined`, `nonconvergence`, `critical-values-only`, or `sparse-asymptotic-unreliable` |
| `alpha`, `reject` | Threshold and pandas nullable boolean decision |

Method-specific columns include selected lag/bandwidth, deterministic terms,
covariance estimator, degrees of freedom in the denominator, critical values,
breakpoint endpoints, random seed and number of simulations. No p-value is
invented from critical values. Johansen's decision is computed directly from
its matching critical value. A rejection means evidence against the specified
null under its assumptions; nonrejection does not establish the model is correct.

For bounded p-values, a decision is made only if the entire allowable interval
is on one side of alpha. For unavailable inference, `reject` is `pd.NA`, never
False. `pvalue_lower` and `pvalue_upper` identify the bound; a missing lower/upper
bound means 0/1 respectively.

```python
import pandas as pd
import meliora as m

# One requested lag minus one estimated dynamic parameter leaves zero df.
undefined = m.ljung_box_test([1, 2, 3, 4, 5], [1], model_df=1)
assert pd.isna(undefined.reject.iloc[0])

# A capped .25 p-value means p>=.25, so alpha=.30 cannot decide rejection.
bounded = m.anderson_darling_ksample_test([[1, 2, 3, 4], [1, 2, 3, 4]], alpha=.30)
assert bounded.status.iloc[0] == 'bounded'
assert pd.isna(bounded.reject.iloc[0])

# Identical forecast losses supply no variance for a DM comparison.
degenerate = m.diebold_mariano_test([1, 2, 3], [1, 2, 3])
assert pd.isna(degenerate.reject.iloc[0])
```

## Independently explainable examples

| Calculation | Expected result |
|---|---|
| Ljung-Box, [1,2,3,4,5], lag 1 | centred sum of squares 10, lag product 4; Q=5*7*.4²/4=1.4 |
| Jarque-Bera, [-2,-1,0,1,2] | skewness 0, Pearson kurtosis 1.7; JB=5*1.3²/24 |
| Poisson-binomial, p=[0,1], count=1 | deterministic count: p-value 1 |
| Fisher, [[3,1],[1,3]] | conditional masses [1,16,36,16,1]/70; two-sided p=34/70 |
| Stuart-Maxwell/McNemar, [[12,7],[3,20]] | uncorrected chi-square=(7-3)²/(7+3)=1.6 |
| DM, horizon=1, bandwidth=0, HLN | exactly the one-sample t statistic of paired loss differences |

The four numerical test files contain independent regression, risk-set, moment,
tail-enumeration and eigenvalue checks. The
[R oracle](../tests/oracles/extensions/README.md) supplies a separate-language
calculation for every added API, with conventions and precision recorded.
Normality checks require appropriate continuous-model residual assumptions;
raw Bernoulli default residuals are not normally distributed.

## Running verification

```powershell
python -m pytest -q -p no:cacheprovider
$env:MELIORA_SLOW = '1'
python -m pytest tests/test_extension_simulations.py -q -p no:cacheprovider
```

The slow suite uses 300 seeded repetitions per scenario, binomial Monte Carlo
tolerances for null rejection rates, and aggregate power checks. It is separate
from the fast suite. Monte Carlo Durbin-Watson, sup-F and AD permutation tests
return seeds and use +1 tail corrections. Finite simulation uncertainty remains
near the significance threshold.
