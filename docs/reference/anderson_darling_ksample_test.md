# anderson_darling_ksample_test

```python
anderson_darling_ksample_test(samples, *, midrank=True, method='asymptotic', permutations=9999, seed=0, alpha=0.05)
```

## Hypotheses and calculation

**H0:** All independent samples come from the same distribution. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Scholz-Stephens standardised k-sample Anderson-Darling statistic, based on weighted squared differences between group and pooled empirical CDFs. Table-based p-values are bounded to [.001,.25]; permutation inference uses a pooled-label randomisation with the +1 Monte Carlo correction.

## Inputs, settings and limitations

Sequence of at least two samples, each with at least two observations and at least two distinct values pooled. midrank=True handles ties via midranks, False uses right-side EDFs. method=asymptotic or permutation; permutations and seed are returned for the latter. Exchangeability across independent groups is essential. New SciPy variants omit critical values, so that field is empty when unavailable; no values are fabricated.

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

result = m.anderson_darling_ksample_test([[1, 2, 3, 4], [1, 2, 3, 4]])
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `-1.6399445`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
