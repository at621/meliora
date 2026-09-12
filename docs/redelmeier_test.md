# Redelmeier-style test

Compare paired Brier losses under an explicit midpoint-Bernoulli null model.

```python
meliora.redelmeier_test(df, *, default_flag='DEFAULT_FLAG', first_pd='ADJUSTED_PD', second_pd='min_PD')
```

## Parameters

**`df`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`default_flag`** (str, default 'DEFAULT\_FLAG')

Binary 0/1 outcome column name.

**`first_pd`** (str, default 'ADJUSTED\_PD')

First fixed forecast probability column name, values in [0, 1].

**`second_pd`** (str, default 'min\_PD')

Second fixed forecast probability column name, values in [0, 1].

## Returns

**`tuple of float`**

(z\_statistic, two\_sided\_p\_value). Identical prediction vectors return (0, 1).

## Formula, assumptions and interpretation

This Redelmeier-style comparison explicitly assumes independent Y\_i~Bernoulli(q\_i),
q\_i=(p1\_i+p2\_i)/2, with fixed forecasts. Paired squared-loss difference is
(p1-p2)\*(p1+p2-2Y), with null mean zero and variance (p1-p2)\*\*2\*(p1+p2)\*(2-p1-p2). Sum
differences and variances to form z; return 2\*normal.sf(abs(z)). Positive z favors the
second forecast. This normal approximation uses the stronger midpoint null, not
unrestricted equality of average Brier scores. The variance is derived from this stated
model; the original paper motivates paired Brier comparisons, not certification of this
convention. Identical forecasts provide no comparative evidence.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'y': [0, 1, 1, 0], 'p1': [.1, .4, .7, .3], 'p2': [.2, .6, .6, .1]})
>>> result = m.redelmeier_test(data, default_flag='y', first_pd='p1', second_pd='p2')
>>> assert np.isclose(result[0], .18 / np.sqrt(.0798))
>>> assert 0 < result[1] < 1
```

First-forecast total squared loss exceeds the second by 0.18. Swapping forecasts reverses z and preserves the two-sided p-value.

## Exceptions

**`ValueError`**

Missing columns, nonbinary outcomes or invalid probabilities.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://pubmed.ncbi.nlm.nih.gov/1941009/)
