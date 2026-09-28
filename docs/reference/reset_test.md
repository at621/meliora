# reset_test

```python
reset_test(y, x, *, powers=(2, 3), covariance='nonrobust', alpha=0.05)
```

## Hypotheses and calculation

**H0:** All selected nonlinear fitted-value augmentation coefficients are zero. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Add centred, standardised fitted-value powers to OLS. Classical nested F has q numerator and n-k-q denominator df; HC3 uses the sandwich covariance and a chi-square(q) Wald statistic.

## Inputs, settings and limitations

Dependent observations and full-rank design with constant. powers is a nonempty tuple of unique integers >=2. covariance=nonrobust assumes homoskedastic independent Gaussian regression errors for exact F inference. HC3 permits heteroskedasticity asymptotically but not serial correlation. Unit leverage, singular augmentations and constant fitted values are rejected. Rejection does not identify a unique omitted variable.

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

result = m.reset_test(Y, X)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `0.845887023`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
