# mcnemar_test

```python
mcnemar_test(table, *, exact=True, correction=True, alpha=0.05)
```

## Hypotheses and calculation

**H0:** The two marginal probabilities in paired binary observations are equal. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

For discordances b,c, exact two-sided binomial inference on min(b,c) conditional on b+c. Asymptotic Q=max(0,abs(b-c)-correction)²/(b+c), chi-square(1).

## Inputs, settings and limitations

Exactly a 2x2 paired count table. exact=True by default; correction=True only affects asymptotic inference. With no discordance, exact p=1 while asymptotic inference is undefined. Independent pairs are assumed. Exact and asymptotic variants are distinct; continuity-corrected Q does not equal binary Stuart-Maxwell.

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

result = m.mcnemar_test([[12, 7], [3, 20]])
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `3`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
