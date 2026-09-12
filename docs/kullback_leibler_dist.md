# Kullback–Leibler information measure

Calculate mutual information between rating grade and binary default outcome.

```python
meliora.kullback_leibler_dist(data, realised_pd, count)
```

## Parameters

**`data`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`realised_pd`** (str)

Grade-level realised default-rate column name, finite values in [0, 1].

**`count`** (str)

Nonnegative finite count/weight column with positive total. Zero and fractional
weights are allowed.

## Returns

**`float`**

H0-H1 in nats, between 0 and log(2): mutual information.

## Formula, assumptions and interpretation

The historical name denotes grade/default mutual information, not a general two-
distribution KL function. Compute marginal minus count-weighted conditional binary
entropy, with natural logs and 0\*log(0)=0. Equivalently, average grade Bernoulli KL
divergences from the portfolio Bernoulli distribution. Zero weights contribute nothing;
all-zero/all-one outcomes return 0. No p-value applies.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'rate': [0, 1], 'n': [10, 10]})
>>> result = m.kullback_leibler_dist(data, 'rate', 'n')
>>> assert np.isclose(result, np.log(2))
```

Perfect grade separation removes log(2) nats of uncertainty from a balanced binary outcome.

## Exceptions

**`ValueError`**

Invalid columns/rates/counts or nonpositive total count.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://doi.org/10.1214/aoms/1177729694)
