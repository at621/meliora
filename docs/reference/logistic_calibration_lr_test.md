# logistic_calibration_lr_test

```python
logistic_calibration_lr_test(outcomes, probabilities, *, alpha=0.05, maxiter=1000)
```

## Hypotheses and calculation

**H0:** In logit P(Y=1)=a+b logit(p), a=0 and b=1 jointly. **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

LR = 2(log L_unrestricted - log L_at_(0,1)), asymptotic chi-square(2). Bernoulli log likelihood is evaluated with stable logaddexp arithmetic.

## Inputs, settings and limitations

Aligned validation outcomes (both binary classes) and at least four distinct-observation slots of interior PDs 0<p<1. Constant forecasts, boundary PDs, complete or quasi-complete separation and ill-conditioned information are rejected. A failed optimizer returns status=nonconvergence and nullable reject. Forecasts must be fixed relative to independent validation outcomes; regular identifiable finite MLEs are required. This joint calibration-curve test differs from grade-level binomial tests.

Uses base NumPy/SciPy dependencies. See the [shared contracts](../extensions.md) for missing data,
time indexes, non-mutation, result fields and nullable decisions. Only the
alternatives shown in the signature/description are supported; omnibus tests
have no directional switch. All tests use `alpha=0.05` unless specified.

## Result and worked example

Returns a pandas DataFrame: `test`, `statistic`, `pvalue`, `nobs`, `df`,
`alternative`, `method`, `reference_distribution`, `status`, `alpha`, `reject`,
plus the method-specific settings described above. `df` is NaN where inapplicable;
`reject` uses pandas nullable boolean. Multiple hypotheses/variants return multiple rows.

```python
import numpy as np
import meliora as m

result = m.logistic_calibration_lr_test([0, 1, 0, 1], [0.2, 0.2, 0.8, 0.8])
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `1.78514841`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference](https://link.springer.com/article/10.1186/s12916-019-1466-7)
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
