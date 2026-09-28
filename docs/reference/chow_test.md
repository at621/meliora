# chow_test

```python
chow_test(y, x, breakpoint, *, alpha=0.05)
```

## Hypotheses and calculation

**H0:** All regression coefficients are equal before and after the prespecified breakpoint. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

F=((SSE_pooled-SSE_1-SSE_2)/k)/((SSE_1+SSE_2)/(n-2k)); F(k,n-2k).

## Inputs, settings and limitations

Ordered dependent observations and full-rank original design including constant. breakpoint is the zero-based row starting segment two, with each segment having more than k rows and full-rank design. Independent Gaussian errors, common variance and a breakpoint fixed independently of the data are required for classical F inference. Use sup_f_test when selecting the breakpoint by search.

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

result = m.chow_test(Y, X, 40)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `2.79863941`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.jstatsoft.org/article/view/v007i02)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
