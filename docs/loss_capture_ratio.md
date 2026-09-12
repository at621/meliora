# Loss capture ratio

Compare model and ideal loss-capture gains using cumulative exposure on the x axis.

```python
meliora.loss_capture_ratio(ead, predicted_ratings, realised_outcomes)
```

## Parameters

**`ead`** (array-like)

Finite nonnegative exposures with positive total, positionally paired with LGDs.

**`predicted_ratings`** (array-like)

Finite predicted LGD fractions in [0, 1], despite the historical ratings name.

**`realised_outcomes`** (array-like)

Equal-length finite realised LGD fractions in [0, 1]. Series indices are ignored.

## Returns

**`float`**

Model/ideal area gain ratio in [-1, 1], up to floating-point error.

## Formula, assumptions and interpretation

Sort predicted LGD descending; x=cumulative EAD share, y=cumulative realised monetary
loss share. Pool tied scores and include the origin. The ideal curve sorts realised LGD;
LCR=(area\_model-0.5)/(area\_ideal-0.5). This explicitly uses exposure on the x axis;
account-count variants differ. Perfect/reverse ordering yields 1/-1; constant predicted
scores yield 0. Zero EAD has no influence. This is descriptive with no p-value.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> result = m.loss_capture_ratio([1, 1, 1], [.1, .4, .9], [.1, .4, .9])
>>> assert np.isclose(result, 1)
```

Sorting on true loss rates reproduces the ideal curve. Match the area convention when comparing implementations.

## Exceptions

**`ValueError`**

Invalid paired LGDs/exposures, nonpositive total EAD/loss, or zero ideal gain
(constant LGD on positive exposures).

## References

- [Statistical reference 1](https://aptivaa.com/pdf/ifrs9-model-risk-management-1594098423-1.pdf)
