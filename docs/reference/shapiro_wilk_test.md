# shapiro_wilk_test

```python
shapiro_wilk_test(x, *, alpha=0.05)
```

## Hypotheses and calculation

**H0:** The sample comes from a normal distribution. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

W = (sum a_i x_(i))²/sum(x_i-mean(x))², using normal-order-statistic weights; Shapiro-Wilk/Royston calibration as implemented in SciPy.

## Inputs, settings and limitations

At least three finite nonconstant observations; iid continuous sampling. Ties are permitted and flagged, but rounding/discreteness can affect calibration. W is returned for n>5000 while pvalue and reject remain unavailable because p-value accuracy is not established there. Normality is not a blanket requirement for Bernoulli default residuals.

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

result = m.shapiro_wilk_test(Y)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `0.974707256`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
