# kpss_test

```python
kpss_test(x, *, regression='c', bandwidth='auto', alpha=0.05)
```

## Hypotheses and calculation

**H0:** The series is stationary around a constant or deterministic linear trend. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

KPSS = sum(S_t²)/(n² LRV), with S_t cumulative detrended residuals and Bartlett long-run variance. Interpolated KPSS table, with p bounded below at .10 or above at .01 outside its range.

## Inputs, settings and limitations

Ordered nonconstant series. regression=c or ct. bandwidth is an integer 0..n-1, auto uses the statsmodels Hobijn data-dependent rule, legacy uses ceil(12(n/100)^.25). Return selected bandwidth, deterministic terms and critical values. Small-sample and bandwidth sensitivity can be substantial. Its null is the opposite of ADF/PP; inconsistent conclusions can be inconclusive rather than contradictory.

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

result = m.kpss_test(Y, bandwidth=2)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `1.07052139`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
