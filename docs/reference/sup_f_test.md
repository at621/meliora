# sup_f_test

```python
sup_f_test(y, x, *, trim=0.15, min_segment=None, simulations=999, seed=0, alpha=0.05)
```

## Hypotheses and calculation

**H0:** No coefficient break exists anywhere in the admissible search interval. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Maximum Chow F over all integer breakpoints with both segments >=max(k+1,ceil(n*trim),min_segment). Simulate Gaussian null outcomes conditional on fixed X and recompute the entire maximum; p=(exceedances+1)/(simulations+1).

## Inputs, settings and limitations

Ordered dependent observations and original full-rank design with constant. trim strictly between 0 and .5; min_segment optional. Every candidate subsample design is checked. At least 99 simulations, default 999, seed=0. Return selected breakpoint, actual endpoints, minimum segment, seed and simulated critical value. Assumes fixed exogenous regressors and homoskedastic Gaussian iid errors; this calibration does not support lagged dependent regressors or generic heteroskedastic errors. Monte Carlo uncertainty matters near alpha.

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

result = m.sup_f_test(Y, X, simulations=99)
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
