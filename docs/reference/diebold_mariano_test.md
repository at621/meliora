# diebold_mariano_test

```python
diebold_mariano_test(loss_a, loss_b, *, horizon=1, bandwidth=None, estimator='bartlett', correction=True, alternative='two-sided', alpha=0.05)
```

## Hypotheses and calculation

**H0:** The expected out-of-sample loss differential loss_A-loss_B is zero. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

DM = mean(d)/sqrt(LRV/n), with divisor-n autocovariances. Bartlett weights are 1-j/(bandwidth+1); acf uses unweighted autocovariances. HLN multiplies by sqrt((n+1-2h+h(h-1)/n)/n) and uses t(n-1); uncorrected inference uses normal.

## Inputs, settings and limitations

Two aligned ordered out-of-sample loss vectors. horizon h is 1..n-1; default bandwidth=h-1, or choose explicitly. estimator=bartlett or acf; correction=True enables HLN. less/greater refer to mean loss_A-loss_B. Requires covariance-stationary loss differences and a suitable horizon/bandwidth; nonpositive LRV returns undefined inference. Identical losses have no evidence to test. This differs from the midpoint-null redelmeier_test.

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

result = m.diebold_mariano_test(Y, np.zeros(80))
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `8.83339543`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://www.nber.org/papers/w18391.pdf)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
