# box_pierce_test

```python
box_pierce_test(x, lags=10, *, model_df=0, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Autocorrelations at lags 1 through h are jointly zero. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Q = n sum(r_j²), asymptotic chi-square(h-model_df). The autocorrelation estimates and contracts match Ljung-Box.

## Inputs, settings and limitations

Ordered nonconstant series. Integer lags returns 1..h, a sequence returns those lags. model_df adjusts degrees of freedom, with unavailable inference at h<=model_df. The Box-Pierce approximation is generally less accurate in small samples than the Ljung-Box finite-sample scaling.

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

result = m.box_pierce_test(Y, lags=3)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `0.369586843, 0.385840869, 0.758484437`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
