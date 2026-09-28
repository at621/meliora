# engle_granger_test

```python
engle_granger_test(y, x, *, regression='c', maxlag=None, autolag='aic', alpha=0.05)
```

## Hypotheses and calculation

**H0:** There is no cointegration between the specified integrated series. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

OLS cointegrating regression followed by an unaugmented-deterministic residual ADF statistic, with cointegration-specific MacKinnon p-values/critical values depending on the number of series and deterministic terms.

## Inputs, settings and limitations

Ordered dependent series and one or more aligned regressors, assumed I(1). regression=n/c/ct/ctt, maxlag and autolag=aic/bic/t-stat/None follow ADF residual lag selection. Return selected lag and residual ADF effective sample. Constant, collinear and near-perfect regression fits are rejected. Critical values for regression=n are unavailable in statsmodels and remain NaN. This is not ordinary ADF inference on estimated residuals.

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

result = m.engle_granger_test(Y, WALK[:, 0], maxlag=1)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `-9.20232774`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.coint.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
