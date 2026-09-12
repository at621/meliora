# Brier score

Calculate the observation-level mean squared probability error.

```python
meliora.brier_score(data, ratings, default_flag, predicted_pd)
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

## Returns

**`float`**

Mean squared error in [0, 1]; lower is better.

## Formula, assumptions and interpretation

Brier = mean((outcome - predicted PD)\*\*2) over individual observations. Grades are
validated but do not alter weighting; ratings is retained for compatibility. This proper
scoring rule measures calibration and discrimination, depends on prevalence, and has no
null hypothesis or p-value.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'grade': ['A'] * 4 + ['B'] * 4, 'outcome': [0, 0, 1, 1] * 2, 'pd': [.2] * 4 + [.6] * 4})
>>> result = m.brier_score(data, 'grade', 'outcome', 'pd')
>>> assert np.isclose(result, .30)
```

Mean squared probability error is 0.30. Compare models on the same observations and event definition.

## Exceptions

**`ValueError`**

Invalid columns, nonbinary outcomes, or PDs outside [0, 1].

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.brier_score_loss.html)
