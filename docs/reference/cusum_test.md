# cusum_test

```python
cusum_test(resid, *, model_df=0, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Regression coefficients are constant over time. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Q=max_t abs(sum_(i<=t)e_i)/sqrt(SSE*n/(n-model_df)); asymptotic supremum absolute Brownian bridge (Kolmogorov) reference.

## Inputs, settings and limitations

Ordered OLS residuals from a model with a constant, supplied by the caller; model_df is an explicit degrees-of-freedom scaling adjustment. The API cannot infer the original design from residuals. Assumes exogenous regressors and suitable iid homoskedastic errors; OLS CUSUM can have weak power for some regressor patterns. This is parameter-stability inference, not a process-control chart.

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

result = m.cusum_test(Y)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `6.30496829`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.jstatsoft.org/article/view/v007i02)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
