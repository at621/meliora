# logrank_test

```python
logrank_test(durations, events, groups, *, alpha=0.05)
```

## Hypotheses and calculation

**H0:** All groups have equal survival functions. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

At each event time use the multivariate hypergeometric expected group deaths and covariance d(N-d)/(N-1)*(diag(p)-ppᵀ). Sum O-E and V, then Q=(O-E)ᵀV⁺(O-E), chi-square(rank(V)).

## Inputs, settings and limitations

Aligned nonnegative durations, event indicators exactly 0/1 and complete group labels (>=2 groups). Supports tied event times and multiple groups; subjects censored at an event time remain in its risk set. Independent right censoring within groups is required. Competing-event codes are rejected; never silently recode them as censoring. No event information returns undefined inference. Nonproportional hazards can reduce power.

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

result = m.logrank_test([1, 3, 2, 3], [1, 0, 1, 0], ['a', 'a', 'b', 'b'])
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `0.0588235294`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://scikit-survival.readthedocs.io/en/stable/api/generated/sksurv.compare.compare_survival.html)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
