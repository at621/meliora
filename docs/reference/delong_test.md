# delong_test

```python
delong_test(outcomes, scores_a, scores_b, *, alternative='two-sided', alpha=0.05)
```

## Hypotheses and calculation

**H0:** The population AUCs of two scores on the same observations are equal. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Z = (AUC_A-AUC_B)/sqrt(v), with v = [1,-1] Cov(AUC_A,AUC_B) [1,-1]ᵀ. Covariance is sample covariance of positive placements/n_positive plus negative placements/n_negative; asymptotic standard normal.

## Inputs, settings and limitations

Aligned binary outcomes and two scores. At least two observations in each class; larger scores indicate outcome 1. Pairwise wins count 1, ties .5. alternative=less/greater refers to AUC_A-AUC_B; two-sided is default. Variance <=1e-15 returns undefined inference, including identical scores. Paired samples only, with independent subjects. Memory O(n_positive*n_negative). Existing roc_auc is only an estimate.

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

result = m.delong_test([1, 1, 0, 0], [1, 2, 0, 1], [1, 1, 0, 2])
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `0.948683298`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://pubmed.ncbi.nlm.nih.gov/3203132/)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
