# breusch_godfrey_test

```python
breusch_godfrey_test(y, x, lags=1, *, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Regression errors have no serial correlation through the requested order. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

LM = n R² from OLS residuals regressed on the original design and lagged residuals; chi-square(h). F = ((SSE_restricted-SSE_full)/h)/(SSE_full/(n-k-h)).

## Inputs, settings and limitations

Raw ordered dependent observations y and the original full-rank regression design x including a constant. OLS is refitted. Pre-sample residuals are zero-padded and all n rows retained. Return LM and F rows. Requires positive residual df and a full-rank augmented design. Standard regression exogeneity assumptions apply; F is an auxiliary-regression approximation.

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

result = m.breusch_godfrey_test(Y, X, lags=2)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `2.87595654, 1.41702047`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
