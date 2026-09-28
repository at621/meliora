"""Independent R values; missing oracles are skipped, never treated as verified."""
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import meliora as m
from extension_cases import EXTENSION_CASES, OPTIONAL

HERE = Path(__file__).parent/'oracles'/'extensions'


@pytest.mark.parametrize('name,args,kwargs', EXTENSION_CASES)
def test_independent_r(name, args, kwargs):
    if not (HERE/'r_results.csv').exists():
        pytest.skip('R extension references not generated')
    if name in OPTIONAL:
        pytest.importorskip('arch.unitroot' if name == 'phillips_perron_test' else 'statsmodels')
    reference = pd.read_csv(HERE/'r_results.csv').set_index('name')
    if name not in reference.index:
        pytest.skip(f'R reference unavailable for {name}')
    data = pd.read_csv(HERE/'regression.csv')
    y = data.y.to_numpy()
    x = np.column_stack([np.ones(len(y)), data.x])
    e = y-x@np.linalg.lstsq(x,y,rcond=None)[0]
    args = list(args)
    kwargs = dict(kwargs)
    if name in {'breusch_pagan_test','white_test'}:
        args = [e, x]
    if name in {'adf_test','engle_granger_test'}:
        kwargs['autolag'] = None
    r = getattr(m,name)(*args,**kwargs)
    # Portmanteau integer input returns lag 1..3; oracle reports lag 3.
    row = r.iloc[-1] if name in {'ljung_box_test','box_pierce_test'} else r.iloc[0]
    expected = reference.loc[name]
    if name == 'anderson_darling_ksample_test':
        # kSamples::ad.test explicitly rounds T.AD to five significant figures.
        assert float(format(row.statistic, '.5g')) == expected.statistic
    else:
        assert row.statistic == pytest.approx(expected.statistic, rel=2e-7, abs=1e-10)
    if pd.notna(expected.pvalue):
        # SciPy 1.11's swilk stores coefficients/results in single precision.
        # Its 2.36e-6 absolute p-value difference disappears in modern SciPy.
        from scipy import __version__
        precision = 3e-6 if name == 'shapiro_wilk_test' and __version__.startswith('1.11.') else 1e-10
        assert row.pvalue == pytest.approx(expected.pvalue, rel=2e-6, abs=precision)


def test_extension_oracle_provenance():
    if not (HERE/'provenance.json').exists():
        pytest.skip('R extension references not generated')
    for name, expected in json.loads((HERE/'provenance.json').read_text())['files'].items():
        assert hashlib.sha256((HERE/name).read_bytes().replace(b'\r\n', b'\n')).hexdigest() == expected, name
