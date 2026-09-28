# phillips_perron_test

```python
phillips_perron_test(x, *, bandwidth=None, regression='c', statistic='tau', alpha=0.05)
```

## Hypotheses and calculation

**H0:** The series has a unit root. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Fit y_t=rho y_(t-1)+deterministic terms. Z_tau=sqrt(gamma0/LRV)t_rho - .5(LRV-gamma0)/sqrt(LRV) * N*SE(rho)/s. Z_rho=N(rho-1)-.5 N² SE(rho)²/s²*(LRV-gamma0). s²=SSE/(N-k), gamma0=SSE/N.

## Inputs, settings and limitations

Ordered nonconstant series with at least six observations. regression=n/c/ct; statistic=tau/rho. Bartlett bandwidth defaults to min(n-2,ceil(12(n/100)^.25)); explicit bandwidth 0..n-2. arch supplies statistic-specific MacKinnon p-values and critical values. No lagged differences are added, unlike ADF. Assumes a suitable weak-dependence long-run variance approximation. The arch lagged-regression variance convention differs slightly from urca current-level scaling.

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

result = m.phillips_perron_test(Y, bandwidth=2)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `-8.3423453`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.PhillipsPerron.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
