# adf_test

```python
adf_test(x, *, maxlag=None, regression='c', autolag='AIC', alpha=0.05)
```

## Hypotheses and calculation

**H0:** The series has a unit root. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

OLS t statistic on the lagged level in a regression of first differences on that level, lagged differences and deterministic terms. MacKinnon unit-root p-value and 1%, 5%, 10% critical values, not a Student t reference.

## Inputs, settings and limitations

Ordered nonconstant series, at least five observations. regression=n/c/ct/ctt means none/constant/linear trend/quadratic trend. maxlag=None uses the statsmodels Schwert-style maximum, capped for sample size; autolag=AIC/BIC minimises that criterion on a common comparison sample, t-stat drops lags by the 5% last-lag rule, None uses maxlag. Return selected lag and effective nobs. Inference is against stationarity under the chosen deterministic specification and has low power near a unit root.

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

result = m.adf_test(Y, maxlag=2)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `-8.3474828`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
