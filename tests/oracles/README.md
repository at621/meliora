# Cross-language oracles

`tests/test_cross_language.py` compares all 29 Meliora methods with the same
calculations done in R, SAS and MATLAB. This folder holds everything that
comparison needs.

| Path | Contents |
|---|---|
| `cases.py` | Datasets, the Meliora call for every case and the flat result contract |
| `data/*.csv` | Generated inputs; identical bytes for every language |
| `python/results.json` | Meliora's own output, kept for reference |
| `r/oracle.R`, `r/results.json` | R oracle and its frozen output |
| `matlab/oracle.m`, `matlab/results.json` | MATLAB oracle and its frozen output |
| `sas/oracle.sas` | SAS oracle; no frozen output yet |
| `run_oracles.py` | Regenerates data and frozen outputs, adds the provenance stamp |
| `report.py`, `RESULTS.md`, `RESULTS.csv` | Every field's value in Python, R, MATLAB and SAS, by test number |

## Contract

Every oracle writes `{"meta": {...}, "results": [{"case", "field", "value"}, ...]}`.
Case ids and field names are defined in `cases.py`. Table outputs are flattened
to `field.<label>` keys, so row order never matters. Booleans may be written as
`true`/`false` or `1`/`0`. Undefined values are `null`.

The stamp in `meta` records the SHA-256 of the datasets, of `cases.py` and of
the oracle script. `test_oracle_is_current` fails when any of them changed
after the oracle ran.

## Regenerating

```bash
python tests/oracles/run_oracles.py data        # datasets and python/results.json
python tests/oracles/run_oracles.py r matlab    # live R and MATLAB runs
MELIORA_ORACLES=r,matlab python -m pytest tests/test_cross_language.py
python tests/oracles/report.py                  # rewrite RESULTS.md
```

R is found through `MELIORA_RSCRIPT`, the PATH or `C:/Program Files/R`; it
needs the packages jsonlite, pROC and DescTools. MATLAB is found through
`MELIORA_MATLAB`, the PATH or `C:/Program Files/MATLAB`; it runs in `-batch`
mode and needs the Statistics and Machine Learning Toolbox.

SAS runs through saspy when a session is configured. Otherwise submit
`sas/oracle.sas` by hand with `data_dir` and `out_path` filled in, then adopt
the JSON it writes:

```bash
python tests/oracles/run_oracles.py sas --stamp downloaded.json
```

## Known divergences

`KNOWN_DIVERGENCE` in the test module lists the fields where an oracle
legitimately differs, all of them p-value algorithms (asymptotic versus exact
Kolmogorov-Smirnov, Spearman and Kendall distributions). Each entry is
verified to still diverge, so the list cannot go stale.
