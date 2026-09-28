# Extension verification — 2026-09-28

All 30 planned entries are delivered as 31 APIs, with the original 29 APIs
unchanged. The implementations are divided into time-series, calibration,
distributional and structural/survival modules. Shared validation and tabular
inference contracts live in `meliora/_inference.py`.

## Recorded checks

- Final Python 3.13 suite: **566 passed, 81 skipped, 5 expected failures**.
  The skips comprise the existing 76 live/missing-language oracle skips and
  five opt-in simulation studies. The five expected failures are unchanged
  cross-language differences in the original catalogue.
- Separate seeded simulation run: **5 passed**, with 300 null and alternative
  repetitions each for Ljung-Box, DM, Chow, logistic calibration and log-rank.
- **32 executable documentation examples** completed successfully.
- Both example notebooks now contain and execute **all 60 public functions**,
  numbered consistently with the unified README catalogue. The detailed
  notebook includes **31 additional plots**, one for each new function.
- **32 independent R/provenance checks** passed. Every extension API has a
  reference statistic; unavailable or convention-incompatible p-values are
  explicitly omitted. Finite-sample differences are documented in the oracle
  README, with convention-matched independent calculations where needed.
- Minimum base environment (Python 3.11, NumPy 1.26.0, pandas 2.1.0,
  SciPy 1.11.0, scikit-learn 1.3.0): full suite passed with optional methods
  skipped before installing the extra.
- Minimum optional environment (pandas 2.1.1, statsmodels 0.14.4, arch 7.2.0,
  other minimum versions unchanged): full suite passed; **77 affected checks**
  passed again after final convergence/validation refinements and PP variants.
- Current environment: NumPy 2.2.4, pandas 2.2.3, SciPy 1.17.1,
  statsmodels 0.14.6, arch 7.2.0. SciPy AD API changes are handled explicitly.
- Base import isolation was tested with statsmodels/arch imports blocked.
  `git diff --check` passed.

## Explicit boundaries

The BDS API supports observed-series iid inference and rejects fitted-residual
inference without model-specific calibration. DW and sup-F simulation assume
fixed exogenous designs and homoskedastic Gaussian null errors. Sparse G-test
tables return unavailable asymptotic inference. Johansen returns matching
critical values and decisions without invented p-values. Normality-test sample
limits, constant/degenerate data, separation, singular designs and bounded
tables are documented in each reference page.

The optional dependency resolver excludes pandas 2.1.0 because statsmodels
does so; the base package continues to support it. Installing the optional
extra therefore selects pandas 2.1.1 or later.
