# Bayesian error rate

Find the minimum empirical misclassification rate over score thresholds.

```python
meliora.bayesian_error_rate(df, default_flag, prob_default)
```

## Parameters

**`df`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`default_flag`** (str)

Binary 0/1 outcome column name; booleans are accepted.

**`prob_default`** (str)

Finite numeric score column name. Larger means outcome 1; unbounded scores are
accepted despite the historical name.

## Returns

**`float`**

Minimum empirical misclassification fraction in [0, 0.5], unrounded.

## Formula, assumptions and interpretation

For every threshold, error=(1-prevalence)\*FPR+prevalence\*(1-TPR). Return the minimum,
including all/none-positive predictions. This is empirical threshold-optimized error
with equal costs, not irreducible Bayes error. Higher scores mean outcome 1. Training-
set optimization is optimistic: evaluate on held-out data. Requires both classes;
returns no p-value.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'y': [0, 0, 1, 1], 'score': [1, 2, 2, 3]})
>>> result = m.bayesian_error_rate(data, 'y', 'score')
>>> assert np.isclose(result, .25)
```

A positive and negative tie at score 2, so at least one of four observations is misclassified.

## Exceptions

**`ValueError`**

Invalid classification data or an absent outcome class.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_curve.html)
