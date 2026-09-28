# breusch_pagan_test

```python
breusch_pagan_test(resid, variance_design, *, variant='koenker', alpha=0.05)
```

## Hypotheses and calculation

**H0:** Variance-regressor slopes, excluding the constant, are zero. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Koenker LM = n R² from squared residuals on Z. Classical BP = explained sum of squares / 2 for e²/mean(e²). Both use chi-square(k-1); an auxiliary F row is also returned.

## Inputs, settings and limitations

Residuals and a user-specified full-rank variance design with explicit constant and at least one nonconstant column. variant=koenker is studentised; variant=classical assumes normally distributed errors. Koenker permits nonnormal iid errors with finite relevant moments. Neither variant corrects for serial dependence. Constant squared residuals are undefined and rejected.

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

result = m.breusch_pagan_test(Y, X)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `7.8685802, 8.50876439`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
