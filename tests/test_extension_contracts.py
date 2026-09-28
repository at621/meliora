"""Extension schema, validation and dependency isolation."""
import importlib.abc
import subprocess
import sys

import numpy as np
import pandas as pd
import pytest

import meliora as m
from extension_cases import EXTENSION_CASES, OPTIONAL


@pytest.mark.parametrize('name,args,kwargs', EXTENSION_CASES)
def test_result_schema_and_alpha(name, args, kwargs):
    if name in OPTIONAL:
        pytest.importorskip('arch.unitroot' if name == 'phillips_perron_test' else 'statsmodels')
    r = getattr(m, name)(*args, **kwargs)
    assert {'test', 'statistic', 'pvalue', 'nobs', 'df', 'alternative', 'method',
            'status', 'reference_distribution', 'reject', 'alpha'} <= set(r)
    assert str(r.reject.dtype) == 'boolean'
    assert ((r.pvalue.dropna() >= 0) & (r.pvalue.dropna() <= 1)).all()
    for alpha in [0, 1, np.nan, None, 'bad', True]:
        with pytest.raises(ValueError):
            getattr(m, name)(*args, **kwargs, alpha=alpha)


def test_base_import_does_not_load_optional_packages():
    code = '''
import sys
import importlib.abc
class Block(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if fullname.split('.')[0] in {'statsmodels', 'arch'}:
            raise ImportError('blocked optional dependency')
sys.meta_path.insert(0, Block())
import meliora as m
assert m.poisson_binomial_test([.2,.3], 1).pvalue[0] > 0
try:
    m.adf_test([1,3,2,5,2,1,3,2,4,6], maxlag=0)
except ImportError as e:
    assert 'meliora[timeseries]' in str(e)
else:
    raise AssertionError('optional import was expected')
'''
    subprocess.run([sys.executable, '-c', code], check=True, capture_output=True, text=True)


@pytest.mark.parametrize('function', [m.breusch_godfrey_test, m.reset_test, m.chow_test])
def test_singular_designs(function):
    x = np.ones((20, 2))
    y = np.arange(20)
    with pytest.raises(ValueError, match='singular'):
        function(y, x, **({'breakpoint': 10} if function == m.chow_test else {}))


@pytest.mark.parametrize('lag', [-1, 0, 20, 1.5, True])
def test_invalid_lags(lag):
    with pytest.raises(ValueError):
        m.ljung_box_test(np.arange(20), lag)


def test_bounded_decision_is_nullable():
    r = m.anderson_darling_ksample_test([[1, 2, 3, 4], [1, 2, 3, 4]], alpha=.3)
    assert pd.isna(r.reject[0])


def test_bds_residual_inference_is_explicitly_unsupported():
    with pytest.raises(ValueError, match='model-specific'):
        m.bds_test(np.arange(20), residuals=True)
