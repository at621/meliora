# durbin_watson_test

```python
durbin_watson_test(y, x, *, alternative='two-sided', simulations=9999, seed=0, lagged_dependent=False, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Classical regression errors have zero first-order autocorrelation. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

D = sum((e_t-e_(t-1))²)/sum(e_t²). Conditional on fixed X, simulate iid Gaussian errors, project off X and recompute D. Rank Monte Carlo tails use (exceedances+1)/(simulations+1), doubling the smaller tail for two-sided inference.

## Inputs, settings and limitations

Ordered dependent observations and original full-rank design with constant, refitted by OLS. Assumes fixed exogenous regressors and iid homoskedastic Gaussian errors under H0. lagged_dependent=True is rejected; callers must not label lagged dependent regressors as fixed. greater means positive autocorrelation (small D), less negative autocorrelation (large D). At least 99 simulations; seed is explicit and defaults to 0. No published-bounds inconclusive region is needed because design-aware null simulation is used; Monte Carlo uncertainty remains near alpha.

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

result = m.durbin_watson_test(Y, X, simulations=99)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `2.13348822`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
