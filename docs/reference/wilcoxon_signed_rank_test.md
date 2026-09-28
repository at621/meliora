# wilcoxon_signed_rank_test

```python
wilcoxon_signed_rank_test(x, y=None, *, zero_method='wilcox', alternative='two-sided', method='auto', correction=False, alpha=0.05)
```

## Hypotheses and calculation

**H0:** The paired-difference distribution is symmetric about zero. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Rank absolute differences; W is min(W+,W-) for two-sided and W+ for directional alternatives. Exact signed-rank distribution without zeros/ties; otherwise a tie/zero-adjusted normal approximation.

## Inputs, settings and limitations

A difference vector or aligned x,y. zero_method=wilcox discards zero differences, pratt includes them in ranking, zsplit splits their ranks. method=auto selects exact only without ties/zeros and n<=50; method=exact rejects ties/zeros, approx uses normal. correction controls continuity correction. All-zero differences give undefined inference. Round scientifically equivalent differences before calling if subtraction introduces artificial ties. Not an unrestricted test of mean error.

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

result = m.wilcoxon_signed_rank_test([1, 2, -3, 4])
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
