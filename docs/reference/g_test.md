# g_test

```python
g_test(observed, probabilities=None, *, mode='goodness-of-fit', ddof=0, alpha=0.05)
```

## Hypotheses and calculation

**H0:** Specified multinomial probabilities hold (goodness-of-fit), or independent groups share category probabilities (homogeneity). **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

G=2 sum O log(O/E), with 0 log 0=0. Goodness-of-fit E=Np, df=k-1-ddof. Homogeneity E_ij=row_i*column_j/N, df=(r-1)(c-1). Asymptotic chi-square.

## Inputs, settings and limitations

mode=goodness-of-fit takes count vector and strictly positive probabilities summing to one; ddof accounts for independently justified fitted parameters. mode=homogeneity takes a table and derives expectations. Empty margins must be removed explicitly. If any E<5, statistic/expectations are returned but pvalue and reject are unavailable, status=sparse-asymptotic-unreliable; pool categories only with scientific justification or use a suitable exact test.

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

result = m.g_test([10, 20], [0.5, 0.5])
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `3.39798074`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
