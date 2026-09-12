# Normal test

Apply the Basel one-sided normal approximation to annual PD forecast errors.

```python
meliora.normal_test(predicted_pd, realised_pd, alpha=0.05)
```

## Parameters

**`predicted_pd`** (array-like)

At least two finite annual predicted rates in [0, 1] for one grade, in time order.

**`realised_pd`** (array-like)

Equal-length realised annual rates in [0, 1], paired by position. Series indices are
ignored.

**`alpha`** (float, default 0.05)

One-sided significance level strictly between zero and one.

## Returns

**`pandas.DataFrame`**

One row: estimate (mean realised-minus-predicted PD), t\_stat (historical name for normal z), p\_value, outcome (boolean rejection).

## Formula, assumptions and interpretation

For T annual observations of one grade, e=realised-predicted PD;
s2=sum((e-mean(e))\*\*2)/(T-1). Basel z=sum(e)/sqrt(T\*s2); p\_value=normal.sf(z).
Alternative: PD underestimation; reject when p\_value &lt; alpha. Assumes independent annual
errors with common finite variance and sufficient years. Uses a normal, not Student t,
reference; preserves historical column t\_stat. Not an obligor-level Bernoulli test.

Six annual observations do not justify independence.

## Example

```pycon
>>> import numpy as np
>>> import pandas as pd
>>> import meliora as m
>>> result = m.normal_test([.1, .1, .1, .1], [.1, .2, .3, .4])
>>> assert np.isclose(result.t_stat.iloc[0], .6 / np.sqrt(1 / 15))
>>> assert bool(result.outcome.iloc[0])
```

Errors 0, 0.1, 0.2, 0.3 give z about 2.324 and p about 0.010. Four years illustrate arithmetic, not a strong asymptotic basis.

## Exceptions

**`ValueError`**

Invalid alpha/rates/pairing, fewer than two years or zero annual-error variance.

## References

- [Statistical reference 1](https://www.bis.org/publ/bcbs_wp14.pdf)
