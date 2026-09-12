# Spiegelhalter test

Test probability calibration with the observation-level Spiegelhalter z statistic.

```python
meliora.spiegelhalter_test(data, ratings, default_flag, predicted_pd, alpha_level=0.05)
```

## Parameters

**`data`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`ratings`** (str)

Grade column name, validated for compatibility. The statistic uses individual
observations without grade aggregation.

**`default_flag`** (str)

Binary 0/1 outcome column name; booleans are accepted.

**`predicted_pd`** (str)

Finite predicted probability column name, values in [0, 1].

**`alpha_level`** (float, default 0.05)

Tail threshold strictly between 0 and 1. Reject for a strictly smaller documented
tail probability.

## Returns

**`tuple`**

(z\_statistic, reject), with two-sided boolean rejection.

## Formula, assumptions and interpretation

z=sum((y-p)\*(1-2\*p))/sqrt(sum(p\*(1-p)\*(1-2\*p)\*\*2)), using individual observations. Under
independent Bernoulli outcomes with correct fixed PDs the statistic is approximately
normal. Reject when 2\*normal.sf(abs(z)) &lt; alpha\_level. Calibration errors can cancel.
PDs of 0, 0.5 or 1 contribute zero null variance; entirely zero variance makes inference
undefined.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'grade': ['A'] * 4 + ['B'] * 4, 'outcome': [0, 0, 1, 1] * 2, 'pd': [.2] * 4 + [.6] * 4})
>>> result = m.spiegelhalter_test(data, 'grade', 'outcome', 'pd')
>>> assert np.isclose(result[0], .8 / np.sqrt(.2688))
>>> assert result[1] is False
```

The statistic is about 1.54 and does not reject at 5% under the two-sided convention.

## Exceptions

**`ValueError`**

Invalid data/alpha or zero null variance.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://doi.org/10.1002/sim.4780050506)
