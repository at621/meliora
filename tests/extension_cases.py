"""One valid, reusable input contract for each extension export."""
import numpy as np

Y = (np.random.default_rng(812).normal(size=80)+np.linspace(0, 2, 80)).tolist()
X = np.column_stack([np.ones(80), np.linspace(-1, 1, 80)]).tolist()
WALK = np.cumsum(np.random.default_rng(921).normal(size=(80, 2)), axis=0).tolist()

EXTENSION_CASES = [
    ('ljung_box_test', [Y], {'lags': 3}),
    ('breusch_godfrey_test', [Y, X], {'lags': 2}),
    ('arch_lm_test', [Y], {'lags': 2}),
    ('breusch_pagan_test', [Y, X], {}),
    ('jarque_bera_test', [Y], {}),
    ('adf_test', [Y], {'maxlag': 2}),
    ('kpss_test', [Y], {'bandwidth': 2}),
    ('reset_test', [Y, X], {}),
    ('box_pierce_test', [Y], {'lags': 3}),
    ('durbin_watson_test', [Y, X], {'simulations': 99}),
    ('bds_test', [Y], {}),
    ('white_test', [Y, X], {}),
    ('shapiro_wilk_test', [Y], {}),
    ('anderson_darling_normal_test', [Y], {}),
    ('phillips_perron_test', [Y], {'bandwidth': 2}),
    ('logistic_calibration_lr_test', [[0, 1, 0, 1], [.2, .2, .8, .8]], {}),
    ('poisson_binomial_test', [[.1, .4, .8], 1], {}),
    ('delong_test', [[1, 1, 0, 0], [1, 2, 0, 1], [1, 1, 0, 2]], {}),
    ('diebold_mariano_test', [Y, [0.]*80], {}),
    ('wilcoxon_signed_rank_test', [[1, 2, -3, 4]], {}),
    ('fisher_exact_test', [[[3, 1], [1, 3]]], {}),
    ('g_test', [[10, 20], [.5, .5]], {}),
    ('stuart_maxwell_test', [[[12, 7], [3, 20]]], {}),
    ('mcnemar_test', [[[12, 7], [3, 20]]], {}),
    ('anderson_darling_ksample_test', [[[1, 2, 3, 4], [1, 2, 3, 4]]], {}),
    ('cusum_test', [Y], {}),
    ('chow_test', [Y, X, 40], {}),
    ('sup_f_test', [Y, X], {'simulations': 99}),
    ('logrank_test', [[1, 3, 2, 3], [1, 0, 1, 0], ['a', 'a', 'b', 'b']], {}),
    ('engle_granger_test', [Y, [v[0] for v in WALK]], {'maxlag': 1}),
    ('johansen_test', [WALK], {}),
]

OPTIONAL = {'adf_test', 'kpss_test', 'bds_test', 'anderson_darling_normal_test',
            'phillips_perron_test', 'engle_granger_test', 'johansen_test'}
