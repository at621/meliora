# Migration-weighted bandwidth

Calculate ECB normalized migration-weighted bandwidth above and below the diagonal.

```python
meliora.migration_matrices_statistics(df, period_1_ratings, period_2_ratings, *, rating_order=None)
```

## Parameters

**`df`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`period_1_ratings`** (str)

Initial grade column name.

**`period_2_ratings`** (str)

Final grade column name, paired by row with initial grades.

**`rating_order`** (sequence, optional)

Unique complete grade labels from lowest to highest; unobserved grades are retained.
Otherwise use consistent ordered categorical metadata, then naturally sort the
observed union. Specify business order explicitly.

## Returns

**`tuple of float`**

(upper\_MWB, lower\_MWB), each in [0, 1]. Directions without migrations return 0.

## Formula, assumptions and interpretation

For each side of the diagonal, divide sum(abs(i-j)\*N\_ij) by sum(max(i,K-1-i)\*N\_ij), using
zero-based grades. This is ECB normalized migration-weighted bandwidth. Upper means a
later grade in rating\_order; economic direction depends on that order. A side with no
migrations has bandwidth 0 by convention. Describes distance, not frequency or
significance.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'start': [1] * 4 + [2] * 4 + [3] * 4, 'end': [1, 1, 2, 3, 1, 2, 2, 3, 1, 2, 3, 3]})
>>> result = m.migration_matrices_statistics(data, 'start', 'end')
>>> assert np.allclose(result, [.8, .8])
```

Each side has distance-weighted count 4 and maximum-distance-weighted count 5, giving 0.8.

## Exceptions

**`ValueError`**

Invalid grade columns or rating order.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://www.bankingsupervision.europa.eu/activities/internal_models/shared/pdf/instructions_validation_reporting_credit_risk.en.pdf)
