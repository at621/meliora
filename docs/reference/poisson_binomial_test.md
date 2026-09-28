# poisson_binomial_test

```python
poisson_binomial_test(probabilities, count, *, alternative='two-sided', alpha=0.05)
```

## Hypotheses and calculation

**H0:** Total events follow the sum of independent Bernoulli variables with the specified individual probabilities. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Exact PMF from repeated convolution of [1-p_i,p_i]. less sums P(K<=k); greater sums P(K>=k); two-sided sums masses no larger than the observed mass (relative comparison tolerance 1e-12).

## Inputs, settings and limitations

A finite probability vector, including 0 and 1, and integer event count 0..n. Count is the statistic; no df parameter. Equal probabilities reduce to the binomial law. Complexity is O(n²), and extreme tail probabilities may underflow in floating point. Heterogeneous probabilities are supported without requiring the newer scipy.stats.poisson_binom.

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

result = m.poisson_binomial_test([0.1, 0.4, 0.8], 1)
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `1`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson_binom.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
