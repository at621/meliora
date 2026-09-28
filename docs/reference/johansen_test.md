# johansen_test

```python
johansen_test(series, *, det_order=0, k_ar_diff=1, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Trace: cointegration rank is at most r. Maximum eigenvalue: rank r against rank r+1. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Trace=-T sum_(i>r)log(1-lambda_i); max-eigen=-T log(1-lambda_(r+1)). Johansen critical values at 10%, 5%, 1%; no p-values supplied or invented.

## Inputs, settings and limitations

Ordered matrix of 2..12 noncollinear varying I(1) series. k_ar_diff is the number of lagged differences (VAR level order minus one); det_order=-1/0/1 uses statsmodels no-deterministic/constant/linear-trend detrending convention. This is not the complete set of restricted/unrestricted VECM deterministic cases. Return both tests for every rank, effective nobs, critical values and decisions only for alpha=.10/.05/.01. Short samples, near-singular covariance and lag/deterministic misspecification can distort inference.

Requires `pip install 'meliora[timeseries]'`. See the [shared contracts](../extensions.md) for missing data,
time indexes, non-mutation, result fields and nullable decisions. Only the
alternatives shown in the signature/description are supported; omnibus tests
have no directional switch. All tests use `alpha=0.05` unless specified.

## Result and worked example

Returns a pandas DataFrame: `test`, `statistic`, `pvalue`, `nobs`, `df`,
`alternative`, `method`, `reference_distribution`, `status`, `alpha`, `reject`,
plus the method-specific settings described above. `df` is NaN where inapplicable;
`reject` uses pandas nullable boolean. Multiple hypotheses/variants return multiple rows.

```python
import numpy as np
import meliora as m
Y = np.random.default_rng(812).normal(size=80) + np.linspace(0, 2, 80)
X = np.column_stack([np.ones(80), np.linspace(-1, 1, 80)])
WALK = np.cumsum(np.random.default_rng(921).normal(size=(80, 2)), axis=0)

result = m.johansen_test(WALK)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `8.59795955, 0.000623948839, 8.5973356, 0.000623948839`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/generated/statsmodels.tsa.vector_ar.vecm.coint_johansen.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
