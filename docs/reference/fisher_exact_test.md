# fisher_exact_test

```python
fisher_exact_test(table, *, alternative='two-sided', alpha=0.05)
```

## Hypotheses and calculation

**H0:** The population odds ratio is one, conditional on the table margins. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

Sample odds ratio ad/bc is reported as statistic; hypergeometric conditional tails supply the p-value. Two-sided sums tables no more likely than the observed table.

## Inputs, settings and limitations

Exactly a 2x2 table of nonnegative integer counts with positive total. alternative=less/greater refers to the odds ratio. Degenerate margins give p=1 and an undefined odds-ratio estimate, explicitly flagged. Independent subjects are assumed; use McNemar for paired binary observations.

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

result = m.fisher_exact_test([[3, 1], [1, 3]])
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `9`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
