# Adjacent-cell shape checks

Calculate ECB adjacent-cell migration z statistics and their normal CDFs.

```python
meliora.migration_matrix_stability(df, initial_ratings_col, final_ratings_col, *, rating_order=None, initial_counts=None)
```

## Parameters

**`df`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`initial_ratings_col`** (str)

Initial grade column name, paired by DataFrame row with final grades.

**`final_ratings_col`** (str)

Final grade column name, on the same scale as initial grades.

**`rating_order`** (sequence, optional)

Unique complete grade labels from lowest to highest; unobserved grades are retained.
Otherwise use consistent ordered categorical metadata, then naturally sort the
observed union. Specify business order explicitly.

**`initial_counts`** (mapping or pandas.Series, optional)

Nonnegative integer counts keyed by every grade in the resolved rating order,
including empty grades. Counts refer to the eligible cohort at the start of
the period, including subsequent defaults, exits and model transfers. Each
count must be at least its matched performing-row total. If omitted, row
totals are used: with departures this is conditional on remaining rated,
rather than the full-cohort ECB calculation.

## Returns

**`tuple of pandas.DataFrame`**

(z\_table, normal\_cdf\_table), square with the same ordered grades. Diagonals, empty rows and zero-variance comparisons are NaN.

## Formula, assumptions and interpretation

For off-diagonal probability f and adjacent probability n one step nearer the diagonal,
z=(n-f)/sqrt((f\*(1-f)+n\*(1-n)+2\*f\*n)/N\_i). Return Phi(z), as in ECB 2019 instructions.
Small CDFs indicate violations of decreasing off-diagonal mass. These are asymptotic
multinomial comparisons, not time-series equality tests. Retain empty grades. NaN means
undefined, not passed. Cell probabilities are not multiplicity-adjusted.
For ECB reporting, divide performing destination counts by initial_counts.
Non-performing destinations contribute to those totals but are not ordinal
grades and must not be added to rating_order. Omitting initial_counts gives
the ECB denominator only when all initial customers remain in the table.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'start': [1] * 4 + [2] * 4 + [3] * 4, 'end': [1, 1, 2, 3, 1, 2, 2, 3, 1, 2, 3, 3]})
>>> result = m.migration_matrix_stability(data, 'start', 'end')
>>> assert np.isclose(result[0].loc[1, 2], 2 / np.sqrt(11))
>>> assert np.isnan(np.diag(result[0])).all()
```

Cell (1,2) compares 2/4 on the diagonal against 1/4 nearby. Cell (1,3) has equal adjacent probabilities, giving CDF 0.5.

## Exceptions

**`ValueError`**

Invalid grade columns, rating order, or initial cohort counts.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://www.bankingsupervision.europa.eu/activities/internal_models/shared/pdf/instructions_validation_reporting_credit_risk.en.pdf)
