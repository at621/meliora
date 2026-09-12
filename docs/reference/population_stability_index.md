# Population stability index

Compare two distributions on a common set of pre-defined bins using PSI.

```python
meliora.population_stability_index(data, bin_flag, variable, *, expected=None, actual=None, smoothing=0.5, bin_order=None)
```

## Parameters

**`data`** (pandas.DataFrame)

Nonempty table with unique columns and no missing required values. Extra columns are
ignored; input is not modified.

**`bin_flag`** (str)

Sample/period column name, containing exactly two distinct labels.

**`variable`** (str)

Shared pre-defined bin column name; uses the union of observed bins.

**`expected`** (scalar, optional)

Reference sample label, specified together with actual. Defaults to the first sorted
sample label.

**`actual`** (scalar, optional)

Comparison sample label, distinct from expected. Defaults to the second sorted
label.

**`smoothing`** (float, default 0.5)

Finite nonnegative pseudo-count added to every contingency cell. Zero requires
positive raw cells.

**`bin_order`** (sequence, optional)

Complete unique bin universe. Retain empty declared bins before smoothing;
otherwise use the observed union. Must include every observed bin.

## Returns

**`tuple`**

(table, PSI). Bin-indexed table columns: expected, actual (normalized smoothed shares), PSI contributions; scalar sums contributions.

## Formula, assumptions and interpretation

Require exactly two samples and shared pre-defined bins. Add smoothing per sample/bin
cell, normalize samples to shares E,A, then PSI=sum((A-E)\*log(A/E)). Defaults choose
expected/actual in natural or categorical order; explicit labels are clearer. Default
smoothing=0.5; zero requires positive cells. PSI is symmetric and descriptive, not a
significance test. Binning and smoothing change the value; no universal cutoffs are
imposed.

bin\_order explicitly retains empty declared bins before smoothing. Omitting it
preserves the observed-union convention, even for categorical inputs. An empty
declared bin needs positive smoothing; normalization uses all declared bins.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> data = pd.DataFrame({'period': ['old'] * 4 + ['new'] * 4, 'bin': ['A', 'A', 'A', 'B', 'A', 'B', 'B', 'B']})
>>> result = m.population_stability_index(data, 'period', 'bin', expected='old', actual='new', smoothing=0)
>>> assert np.isclose(result[1], np.log(3))
>>> assert np.allclose(result[0][["expected", "actual"]].sum(), 1)
```

Shares change from (.75,.25) to (.25,.75), giving PSI=log(3). Significance requires a separate sampling model.

## Exceptions

**`ValueError`**

Missing columns, other than two samples, invalid/partial sample labels, invalid
smoothing or zero unsmoothed cells.

**`TypeError`**

If a required table is not a pandas DataFrame.

## References

- [Statistical reference 1](https://doi.org/10.1214/aoms/1177729694)
