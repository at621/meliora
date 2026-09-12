# Cumulative LGD accuracy ratio

Calculate the VUROCS cumulative LGD accuracy measure for ordinal grades.

```python
meliora.cumulative_lgd_accuracy_ratio(df, predicted_ratings, realised_outcomes, *, rating_order=None)
```

## Parameters

**`df`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`predicted_ratings`** (str)

Predicted ordinal loss-grade column name; higher grades mean greater loss.

**`realised_outcomes`** (str)

Realised ordinal loss-grade column name, on the same scale as predictions.

**`rating_order`** (sequence, optional)

Unique complete grade labels from lowest to highest; unobserved grades are retained.
Otherwise use consistent ordered categorical metadata, then naturally sort the
observed union. Specify business order explicitly.

## Returns

**`float`**

Twice the cumulative ordinal ROC area, in [0, 1].

## Formula, assumptions and interpretation

At each threshold from highest to lowest grade, x=P(predicted &gt;= threshold),
y=P(predicted &gt;= threshold AND realised &gt;= threshold). Include (0,0), integrate whole
tied-grade bands by trapezoids and return twice the area. This follows VUROCS clar
(Ozdemir and Miu convention). It is ordinal accuracy, not a chance-adjusted Gini.
Predictions and outcomes share a grade scale, higher meaning more loss. Accounts have
equal weight; no p-value applies.

Constant lowest-grade predictions attain 1, even with no discrimination.
Any predictions never exceeding their realised grades attain the maximum.
This asymmetric threshold agreement is not a standalone model-quality criterion;
inspect the cross-table and use a separate Somers/gAUC or LCR ranking assessment.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'p': [1, 2, 3, 3, 4], 'y': [1, 3, 2, 4, 4]})
>>> result = m.cumulative_lgd_accuracy_ratio(data, 'p', 'y')
>>> assert np.isclose(result, .88)
```

Threshold points (0,0), (.2,.2), (.6,.4), (.8,.8), (1,1) give twice the trapezoidal area 0.88. Constant lowest-grade predictions give 1.0; maximizing CLAR alone cannot select a good ranking.

## Exceptions

**`ValueError`**

Invalid columns, missing grades or invalid/ambiguous grade order.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://cran.r-universe.dev/VUROCS/VUROCS.pdf)
