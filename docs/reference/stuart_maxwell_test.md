# stuart_maxwell_test

```python
stuart_maxwell_test(table, *, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Paired categorical observations have equal marginal distributions. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

d=row totals-column totals; V_ii=row_i+column_i-2n_ii, V_ij=-(n_ij+n_ji). Q=dᵀ V⁺ d with chi-square(rank(V)). Eigenvalues <=1e-12*max(1,largest eigenvalue) are treated as zero.

## Inputs, settings and limitations

Square integer paired transition table. Singularity due to disconnected category components is handled by a pseudoinverse and effective rank, not invented degrees of freedom. All-diagonal tables have rank zero and undefined inference. Large-sample marginal-homogeneity approximation; sparse discordance can invalidate it. Binary reduction matches uncorrected asymptotic McNemar. This is not migration_matrix_stability, which checks within-matrix shape.

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

result = m.stuart_maxwell_test([[12, 7], [3, 20]])
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `1.6`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
