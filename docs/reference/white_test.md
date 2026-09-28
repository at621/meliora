# white_test

```python
white_test(resid, variance_design, *, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Regression errors have constant variance against the quadratic variance alternative. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Create every Z_i Z_j for i<=j, including linear terms through the constant. Regress squared residuals on an orthonormal basis of that space; LM=n R², chi-square(rank-1), plus auxiliary F with n-rank denominator df.

## Inputs, settings and limitations

Residuals and original variance design with explicit constant. The input design must be full rank, but collinear squares/interactions are handled through effective SVD rank. Saturated auxiliary designs and constant squares are rejected. Independent errors and sufficient finite moments are needed; many regressors can consume sample size rapidly. Broader alternative than a specified linear BP variance design.

Uses base NumPy/SciPy dependencies. See the [shared contracts](../extensions.md) for missing data,
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

result = m.white_test(Y, X)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `8.33152126, 4.47565756`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
