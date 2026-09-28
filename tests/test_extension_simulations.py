"""Opt-in seeded size and sensitivity studies, not significance tests on one sample."""
import os

import numpy as np
import pytest

import meliora as m

pytestmark = [pytest.mark.slow, pytest.mark.skipif(os.environ.get('MELIORA_SLOW') != '1',
                                                reason='set MELIORA_SLOW=1 for Monte Carlo studies')]


@pytest.mark.parametrize('method', ['ljung_box', 'dm', 'chow', 'logistic', 'logrank'])
def test_null_size_and_power(method):
    rng = np.random.default_rng(519)
    null, alternative = [], []
    repetitions = 300
    for _ in range(repetitions):
        n = 120
        z = rng.normal(size=n)
        if method == 'ljung_box':
            a = z.copy()
            for i in range(1,n):
                a[i] += .7*a[i-1]
            null.append(m.ljung_box_test(z,[5]).pvalue[0])
            alternative.append(m.ljung_box_test(a,[5]).pvalue[0])
        elif method == 'dm':
            null.append(m.diebold_mariano_test(z,np.zeros(n)).pvalue[0])
            alternative.append(m.diebold_mariano_test(z+.6,np.zeros(n)).pvalue[0])
        elif method == 'chow':
            x = np.column_stack([np.ones(n),rng.normal(size=n)])
            y = x@[1,2]+z
            null.append(m.chow_test(y,x,n//2).pvalue[0])
            y[n//2:] += 2
            alternative.append(m.chow_test(y,x,n//2).pvalue[0])
        elif method == 'logistic':
            p = rng.uniform(.1,.7,n)
            null.append(m.logistic_calibration_lr_test(rng.binomial(1,p),p).pvalue[0])
            alternative.append(m.logistic_calibration_lr_test(rng.binomial(1,np.minimum(.95,p+.25)),p).pvalue[0])
        else:
            groups = np.repeat([0,1],n//2)
            t = rng.exponential(size=n)
            censor = rng.exponential(scale=3,size=n)
            null.append(m.logrank_test(np.minimum(t,censor),(t<=censor).astype(int),groups).pvalue[0])
            t[groups==1] /= 3
            alternative.append(m.logrank_test(np.minimum(t,censor),(t<=censor).astype(int),groups).pvalue[0])
    assert np.isfinite(null).all() and np.isfinite(alternative).all()
    # Five binomial standard errors around nominal size, no single-draw decision.
    tolerance = 5*np.sqrt(.05*.95/repetitions)
    assert abs(np.mean(np.array(null)<.05)-.05) < tolerance
    assert np.mean(np.array(alternative)<.05) > .65
