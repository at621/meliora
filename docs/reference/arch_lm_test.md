# arch_lm_test

```python
arch_lm_test(resid, lags=1, *, center=False, model_df=0, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Squared errors have no serial dependence through the requested order (no ARCH effects). **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Regress e_t² on a constant and h lagged squares after dropping h rows. LM = (n-h-model_df)R², asymptotic chi-square(h). Auxiliary F uses n-h-h-1 denominator df.

## Inputs, settings and limitations

Ordered residual vector. center=False leaves residuals unchanged; True subtracts their sample mean before squaring. lags is explicit, model_df only adjusts the LM multiplier. Constant squares, singular lag designs and insufficient residual df raise ValueError. Requires finite fourth moments; this is not a general test against all heteroskedasticity.

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

result = m.arch_lm_test(Y, lags=2)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `0.269464619, 0.129999403`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.statsmodels.org/stable/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
