# Information value

Measure separation of pre-binned feature distributions between binary outcomes.

```python
meliora.information_value(df, feature, target, *, smoothing=0.5, bin_order=None)
```

## Parameters

**`df`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`feature`** (str)

Pre-binned feature column name; no automatic binning is performed.

**`target`** (str)

Binary target column name, with both 0 and 1 present.

**`smoothing`** (float, default 0.5)

Finite nonnegative pseudo-count added to every contingency cell. Zero requires
positive raw cells.

**`bin_order`** (sequence, optional)

Complete unique bin universe. Retain empty declared bins before smoothing;
otherwise use the observed union. Must include every observed bin.

## Returns

**`tuple`**

(table, IV). Bin-indexed table columns: good, bad (raw counts), good\_share, bad\_share (smoothed), WoE, IV; the scalar sums contributions.

## Formula, assumptions and interpretation

Pre-bin the feature. Add smoothing to every bin/class count and normalize classes
separately. WoE=log(good\_share/bad\_share); IV=sum((good\_share-bad\_share)\*WoE). Outcome 0
is good, 1 bad. Default smoothing=0.5 makes empty cells finite; smoothing=0 requires
positive cells. Uses the union of observed bins. Descriptive and nonnegative, with no
universal acceptance threshold or p-value. Sparse or selected bins can inflate IV.

bin\_order explicitly retains empty declared bins before smoothing. Omitting it
preserves the observed-union convention, even for categorical inputs. An empty
declared bin needs positive smoothing; normalization uses all declared bins.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'bin': ['A'] * 4 + ['B'] * 4, 'y': [0, 0, 0, 1, 0, 1, 1, 1]})
>>> result = m.information_value(data, 'bin', 'y', smoothing=0)
>>> assert np.isclose(result[1], np.log(3))
>>> assert np.allclose(result[0][["good_share", "bad_share"]].sum(), 1)
```

All cells are positive, allowing smoothing=0. The unsmoothed IV is log(3).

## Exceptions

**`ValueError`**

Invalid columns/classes/smoothing, or zero cells with smoothing=0.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://doi.org/10.1214/aoms/1177729694)
