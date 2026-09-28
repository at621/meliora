# anderson_darling_normal_test

```python
anderson_darling_normal_test(x, *, alpha=0.05)
```

## Hypotheses and calculation

**H0:** The sample is normal with unknown mean and variance. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

A²=-n-(1/n)sum((2i-1)[log F(x_(i))+log(1-F(x_(n+1-i)))]), where F fits the sample mean and sample SD. Stephens fitted-normal p-value calibration includes the finite-sample adjustment.

## Inputs, settings and limitations

At least eight nonconstant finite observations. Assumes iid continuous observations. Fitting mean and variance requires a different calibration from a completely specified normal CDF. This is a one-sample fitted-normal test, separate from the k-sample equality-of-distributions test.

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

result = m.anderson_darling_normal_test(Y)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `0.63206033`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
