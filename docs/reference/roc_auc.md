# ROC AUC

Calculate binary ROC area, assigning half credit to tied scores.

```python
meliora.roc_auc(data, target, prediction)
```

## Parameters

**`data`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`target`** (str)

Binary target column name, with both 0 and 1 present.

**`prediction`** (str)

Finite numeric score column name. Larger means outcome 1; scores need not be
probabilities.

## Returns

**`float`**

AUC in [0, 1]; 0.5 means random pairwise ordering.

## Formula, assumptions and interpretation

AUC=P(score of outcome 1 &gt; score of outcome 0)+0.5\*P(tie). Larger finite scores must
mean greater default risk; scores need not be probabilities. Both binary classes are
required. Uses scikit-learn ROC AUC. This descriptive measure has no p-value and does
not measure calibration.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'y': [0, 0, 1, 1], 'score': [1, 2, 2, 3]})
>>> result = m.roc_auc(data, 'y', 'score')
>>> assert np.isclose(result, .875)
```

Three positive-negative pairs are correctly ordered and one ties: (3+0.5)/4=0.875.

## Exceptions

**`ValueError`**

Invalid columns, nonfinite scores, nonbinary target or an absent class.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html)
