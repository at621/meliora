# bds_test

```python
bds_test(x, *, max_dim=2, epsilon=None, distance=1.5, residuals=False, alpha=0.05)
```

## Hypotheses and calculation

**H0:** The observed series is independent and identically distributed. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

For dimensions m=2..max_dim, Z_m=sqrt(n-m+1)(C_m-C_1^m)/sigma_m, asymptotic normal. C_m counts embedded pairs closer than epsilon in sup norm; the one-dimensional numerator uses the sample conditional on the first m-1 observations (Kanzler convention).

## Inputs, settings and limitations

Ordered observed series, max_dim<n-1. epsilon defaults to distance*sample SD with distance=1.5. Returns a row per dimension and chosen threshold. residuals=True is deliberately rejected because fitted-model residual inference needs a model-specific calibration. Nonfinite statistics have undefined p-values. Requires sufficiently large samples; O(n²) storage restricts long series. It tests iid, not only zero autocorrelation.

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

result = m.bds_test(Y)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `-2.56212538`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
