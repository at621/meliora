"""Build examples 30–60 while preserving the original 29 notebook examples.

Run from the repository root, then execute both notebooks with nbclient.
"""
from pathlib import Path
import re
import sys

import nbformat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import meliora as m

# Public catalogue order is shared with the numbered README rows.
CATALOGUE = [
    ('ljung_box_test', 'Ljung-Box', 'Serial dependence', 'Residuals', 'Tests whether autocorrelations through the selected lag are jointly zero.'),
    ('breusch_godfrey_test', 'Breusch-Godfrey', 'Serial dependence', 'Regression', 'Tests regression errors for serial correlation using the original design.'),
    ('arch_lm_test', 'ARCH LM', 'Variance', 'Residuals', 'Tests for dependence in squared residuals.'),
    ('breusch_pagan_test', 'Breusch-Pagan / Koenker', 'Variance', 'Regression', 'Tests whether specified regressors explain changing error variance.'),
    ('jarque_bera_test', 'Jarque-Bera', 'Normality', 'Continuous observations', 'Tests normal skewness and kurtosis.'),
    ('adf_test', 'Augmented Dickey-Fuller', 'Unit roots', 'Time series', 'Tests a unit-root null against stationarity.'),
    ('kpss_test', 'KPSS', 'Stationarity', 'Time series', 'Tests stationarity around a constant or trend.'),
    ('reset_test', 'Ramsey RESET', 'Specification', 'Regression', 'Tests nonlinear fitted-value terms for omitted structure.'),
    ('box_pierce_test', 'Box-Pierce', 'Serial dependence', 'Residuals', 'Tests joint autocorrelation with the Box-Pierce statistic.'),
    ('durbin_watson_test', 'Durbin-Watson', 'Serial dependence', 'Regression', 'Uses design-conditional simulation to test first-order error autocorrelation.'),
    ('bds_test', 'BDS', 'Independence', 'Observed time series', 'Tests whether observed data are independent and identically distributed.'),
    ('white_test', 'White', 'Variance', 'Regression', 'Tests constant variance against squares and interactions of regressors.'),
    ('shapiro_wilk_test', 'Shapiro-Wilk', 'Normality', 'Continuous observations', 'Tests normality using ordered observations.'),
    ('anderson_darling_normal_test', 'Fitted-normal Anderson-Darling', 'Normality', 'Continuous observations', 'Tests normality with estimated mean and variance.'),
    ('phillips_perron_test', 'Phillips-Perron', 'Unit roots', 'Time series', 'Tests a unit root using a long-run variance correction.'),
    ('logistic_calibration_lr_test', 'Logistic calibration LR', 'Calibration', 'PD', 'Jointly tests calibration intercept zero and slope one.'),
    ('poisson_binomial_test', 'Exact Poisson-binomial', 'Calibration', 'Event counts', 'Tests the total event count for heterogeneous independent probabilities.'),
    ('delong_test', 'Paired DeLong', 'Discrimination', 'AUC', 'Tests equality of two AUCs on the same observations.'),
    ('diebold_mariano_test', 'Diebold-Mariano', 'Forecast comparison', 'Forecast losses', 'Tests zero expected out-of-sample loss difference.'),
    ('wilcoxon_signed_rank_test', 'Wilcoxon signed-rank', 'Paired differences', 'Continuous outcomes', 'Tests a paired-difference distribution symmetric about zero.'),
    ('fisher_exact_test', 'Fisher exact', 'Categorical', '2×2 counts', 'Tests conditional odds ratio one using exact inference.'),
    ('g_test', 'Likelihood-ratio G-test', 'Categorical', 'Counts', 'Tests specified category probabilities or group homogeneity.'),
    ('stuart_maxwell_test', 'Stuart-Maxwell', 'Paired categorical', 'Category transitions', 'Tests equality of marginal distributions in paired categories.'),
    ('mcnemar_test', 'McNemar', 'Paired categorical', 'Binary outcomes', 'Tests marginal equality for paired binary observations.'),
    ('anderson_darling_ksample_test', 'Anderson-Darling k-sample', 'Distributional', 'Independent samples', 'Tests whether independent samples share a distribution.'),
    ('cusum_test', 'OLS CUSUM', 'Structural stability', 'Regression', 'Tests coefficient stability using cumulative OLS residuals.'),
    ('chow_test', 'Chow', 'Structural breaks', 'Regression', 'Tests coefficient equality at a prespecified breakpoint.'),
    ('sup_f_test', 'Sup-F', 'Structural breaks', 'Regression', 'Searches for a break with search-adjusted simulation inference.'),
    ('logrank_test', 'Log-rank', 'Survival', 'Right-censored outcomes', 'Tests equality of survival functions across groups.'),
    ('engle_granger_test', 'Engle-Granger', 'Cointegration', 'Integrated series', 'Tests for cointegration with residual-based critical values.'),
    ('johansen_test', 'Johansen trace / maximum eigenvalue', 'Cointegration', 'Integrated series', 'Tests each cointegration-rank hypothesis using matching critical values.'),
]

SETUP = '''
# Setup for examples 30–60. Install .[timeseries,notebook] before starting the kernel.
import numpy as np
from IPython.display import display

def extension_data():
    """Disclosed, reproducible synthetic scenarios; no fitted Bernoulli normality tests."""
    rng = np.random.default_rng(20260928)
    n = 240
    driver = rng.normal(size=n)
    design = np.column_stack([np.ones(n), driver])
    innovation = rng.normal(size=n)
    serial = innovation.copy()
    arch = innovation.copy()
    for i in range(1, n):
        serial[i] += .65 * serial[i-1]
        arch[i] *= np.sqrt(.3 + .65 * arch[i-1]**2)
    stationary = rng.normal(size=n)
    walk = np.cumsum(rng.normal(size=n))
    y_serial = design @ [1., 1.5] + serial
    y_variance = design @ [1., 1.5] + (.35 + abs(driver)) * innovation
    variance_resid = y_variance - design @ np.linalg.lstsq(design, y_variance, rcond=None)[0]
    y_curve = design @ [1., 1.5] + 1.3 * driver**2 + .6 * innovation
    y_break = design @ [1., 1.5] + innovation + 1.4 * (np.arange(n) >= 120)
    break_resid = y_break - design @ np.linalg.lstsq(design, y_break, rcond=None)[0]
    heavy = rng.standard_t(df=4, size=n)
    p = rng.uniform(.03, .35, size=600)
    outcomes = rng.binomial(1, np.minimum(.9, p + .07))
    score_a = np.log(p/(1-p)) + rng.normal(0, .35, len(p))
    score_b = np.log(p/(1-p)) + rng.normal(0, 1.2, len(p))
    forecast_error = rng.normal(size=360)
    loss_a, loss_b = (forecast_error + .45)**2, forecast_error**2
    differences = rng.normal(.03, .08, size=160)
    sample_a, sample_b = rng.normal(0, 1, 100), rng.normal(.5, 1.3, 100)
    groups = np.repeat(np.arange(3), 100)
    event_time = rng.exponential(scale=18/(1 + .7*groups))
    censor_time = rng.uniform(6, 30, size=len(groups))
    durations = np.minimum(event_time, censor_time)
    events = (event_time <= censor_time).astype(int)
    integrated = np.column_stack([walk, 1.6*walk + rng.normal(size=n)])
    return locals()

def explain_inference(frame):
    """Keep undefined/bounded decisions visible in the narrative as well as the table."""
    for _, row in frame.iterrows():
        if pd.isna(row['reject']):
            decision = 'No rejection decision is available.'
        elif row['reject']:
            decision = 'Reject this row’s null at the selected alpha.'
        else:
            decision = 'Do not reject this row’s null; this does not establish it is true.'
        print(f"{row['test']} ({row['method']}, {row['status']}): {decision}")
'''

PLOT_SETUP = '''
def extension_plot(values, kind, title, labels=None):
    fig, ax = plt.subplots(figsize=(9, 3.8))
    values = np.asarray(values)
    if kind == 'hist':
        ax.hist(values, bins=24, alpha=.8)
        ax.set(xlabel='Observed value', ylabel='Count')
    elif kind == 'scatter':
        ax.scatter(values[:, 0], values[:, 1], s=14, alpha=.6)
        ax.set(xlabel=labels[0], ylabel=labels[1])
    elif kind == 'heatmap':
        image = ax.imshow(values, cmap='Blues', aspect='auto')
        ax.grid(False)
        fig.colorbar(image, ax=ax, label='Count')
        for i, j in np.ndindex(values.shape):
            ax.text(j, i, str(int(values[i, j])), ha='center', va='center')
        ax.set(xlabel='Second category', ylabel='First category',
               xticks=np.arange(values.shape[1]), yticks=np.arange(values.shape[0]))
    elif kind == 'bar':
        ax.bar(np.arange(len(values)), values)
        ax.set(xlabel='Category', ylabel='Count', xticks=np.arange(len(values)))
    elif kind == 'survival':
        for group in np.unique(values[:, 2]):
            t = values[values[:, 2] == group, 0]
            e = values[values[:, 2] == group, 1]
            event_times = np.unique(t[e == 1])
            survival = [1.]
            for time in event_times:
                survival.append(survival[-1]*(1-np.sum((t == time) & (e == 1))/np.sum(t >= time)))
            ax.step(np.r_[0, event_times], survival, where='post', label=f'Group {int(group)}')
        ax.set(xlabel='Months', ylabel='Estimated survival', ylim=(0, 1.02))
        ax.legend()
    else:
        ax.plot(values)
        ax.set(xlabel='Observation in temporal order', ylabel='Value')
        if labels:
            ax.legend(labels)
    ax.set_title(title)
    fig.tight_layout()
    plt.show()
    plt.close(fig)
'''

# Code, graph expression/type/labels, question, interpretation, experiment.
DETAIL = {
'ljung_box_test': ("result = m.ljung_box_test(d['serial'], lags=[1, 5, 10], model_df=0)", "d['serial']", 'line', None,
 'Do monthly model errors retain serial dependence?', 'The errors were generated with AR coefficient .65. Each row tests all autocorrelations through its lag; the rows are overlapping hypotheses.', 'Reduce the AR coefficient in the setup and compare the statistics.'),
'breusch_godfrey_test': ("result = m.breusch_godfrey_test(d['y_serial'], d['design'], lags=3)", "d['serial']", 'line', None,
 'Does serial dependence remain after fitting the original regression?', 'The API refits OLS and retains the original design in the auxiliary regression. LM and F are two inference variants for the same order-three null.', 'Change lags from 3 to 1 and inspect the reported degrees of freedom.'),
'arch_lm_test': ("result = m.arch_lm_test(d['arch'], lags=5, center=False)", "d['arch']**2", 'line', None,
 'Do large errors tend to follow large errors?', 'The simulated conditional variance depends on the previous squared error. The test uses squared residuals and drops the first five observations.', 'Set the ARCH coefficient in the generator to zero.'),
'breusch_pagan_test': ("result = pd.concat([m.breusch_pagan_test(d['variance_resid'], np.column_stack([np.ones(d['n']), abs(d['driver'])]), variant=v) for v in ['koenker', 'classical']], ignore_index=True)", "np.column_stack([abs(d['driver']), d['variance_resid']**2])", 'scatter', ['Absolute driver', 'Squared OLS residual'],
 'Does error variance grow with the magnitude of a model driver?', 'The variance design includes a constant and the absolute driver. Classical BP assumes normal errors; Koenker relaxes normality, but neither addresses serial dependence.', 'Compare the two variants after replacing Gaussian innovations with heavy-tailed innovations.'),
'jarque_bera_test': ("result = m.jarque_bera_test(d['heavy'])", "d['heavy']", 'hist', None,
 'Do continuous errors have normal skewness and kurtosis?', 'Student-t errors have heavier tails. JB examines moments, and its asymptotic calibration needs adequate sample size. These are continuous errors, not Bernoulli default residuals.', 'Increase the Student-t degrees of freedom and inspect kurtosis.'),
'adf_test': ("result = m.adf_test(d['walk'], maxlag=8, regression='c', autolag='AIC')", "d['walk']", 'line', None,
 'Can a unit root be rejected for a cumulative shock series?', 'A random walk is constructed by summing independent shocks. ADF has a unit-root null; a large p-value is not proof of a unit root.', "Replace d['walk'] with d['stationary'] and compare the selected lag."),
'kpss_test': ("result = m.kpss_test(d['walk'], regression='c', bandwidth=6)", "d['walk']", 'line', None,
 'Is a random-walk scenario compatible with level stationarity?', 'KPSS reverses the ADF null. Its tabulated p-value may be a bound; inspect status and the bound columns before interpreting a displayed boundary.', 'Compare bandwidth 2, 6 and 12 without silently changing the deterministic specification.'),
'reset_test': ("result = m.reset_test(d['y_curve'], d['design'], powers=(2, 3), covariance='HC3')", "np.column_stack([d['driver'], d['y_curve']])", 'scatter', ['Driver', 'Response'],
 'Does a linear regression miss the constructed quadratic relationship?', 'RESET adds powers of fitted values. HC3 uses an asymptotic Wald test. Rejection indicates specification evidence, not the unique correct omitted variable.', 'Remove the quadratic term from the data-generating equation.'),
'box_pierce_test': ("result = m.box_pierce_test(d['serial'], lags=[1, 5, 10], model_df=0)", "d['serial']", 'line', None,
 'How does the Box-Pierce autocorrelation diagnostic behave?', 'It tests the same joint autocorrelation null as Ljung-Box with different finite-sample scaling. Values should not be substituted for Ljung-Box statistics.', 'Compare both tests on the first 30 observations at lag 5.'),
'durbin_watson_test': ("result = m.durbin_watson_test(d['y_serial'], d['design'], alternative='greater', simulations=999, seed=42)", "d['serial']", 'line', None,
 'Is there evidence of positive first-order regression-error correlation?', 'The greater alternative means positive autocorrelation, hence small DW. Null simulation conditions on the fixed design; lagged dependent regressors are excluded.', 'Increase simulations to 4999 and compare Monte Carlo variation using another seed.'),
'bds_test': ("result = m.bds_test(d['serial'], max_dim=3, distance=1.5)", "np.column_stack([d['serial'][:-1], d['serial'][1:]])", 'scatter', ['Previous observation', 'Current observation'],
 'Is the observed serial process consistent with iid sampling?', 'This is an observed synthetic series, not fitted-model residuals. BDS tests iid, which is stronger than absence of linear autocorrelation.', "Replace the observed series with d['stationary']."),
'white_test': ("result = m.white_test(d['variance_resid'], d['design'])", "np.column_stack([d['driver'], d['variance_resid']**2])", 'scatter', ['Driver', 'Squared OLS residual'],
 'Can a quadratic variance alternative detect a widening error distribution?', 'The expanded variance design includes squares and interactions. Effective rank determines the degrees of freedom when these columns overlap.', 'Compare White with BP using only the signed driver as variance regressor.'),
'shapiro_wilk_test': ("result = m.shapiro_wilk_test(d['heavy'])", "d['heavy']", 'hist', None,
 'Does an order-statistic diagnostic support normality of continuous errors?', 'Shapiro-Wilk tests the normal family. Heavy tails are visible here; nonrejection on a small sample would not validate a normal-error model.', 'Compare the first 20 observations with the full sample.'),
'anderson_darling_normal_test': ("result = m.anderson_darling_normal_test(d['heavy'])", "d['heavy']", 'hist', None,
 'Does a tail-sensitive fitted-normal test detect the heavy-tail scenario?', 'The mean and variance are estimated, so the fitted-normal calibration is essential. This is different from comparing independent samples.', 'Replace the heavy-tailed sample with Gaussian observations.'),
'phillips_perron_test': ("result = m.phillips_perron_test(d['walk'], bandwidth=6, regression='c', statistic='tau')", "d['walk']", 'line', None,
 'What does a long-run variance correction say about the unit-root null?', 'PP corrects the level-regression statistic rather than adding lagged differences. The displayed critical values match the selected tau variant.', "Compare statistic='rho' with its own returned critical values."),
'logistic_calibration_lr_test': ("result = m.logistic_calibration_lr_test(d['outcomes'], d['p'])", "np.column_stack([d['p'], d['p']+.07])", 'scatter', ['Forecast PD', 'Generating event probability'],
 'Are forecasts compatible with calibration intercept zero and slope one?', 'The generating probability is seven percentage points above each forecast. The LR test jointly assesses intercept and slope on independent validation observations.', 'Set the uplift to zero in the generator and regenerate outcomes.'),
'poisson_binomial_test': ("result = m.poisson_binomial_test(d['p'], int(d['outcomes'].sum()), alternative='greater')", "d['p']", 'hist', None,
 'Is the total number of events unusually high for the individual PD forecasts?', 'The count distribution allows heterogeneous probabilities but assumes independent events. This is a total-count calibration question, not a discrimination test.', 'Replace the PDs by their mean and compare with the heterogeneous calculation.'),
'delong_test': ("result = m.delong_test(d['outcomes'], d['score_a'], d['score_b'])", "np.column_stack([d['score_a'], d['score_b']])", 'scatter', ['Score A', 'Score B'],
 'Do two noisy scores on the same validation subjects have different AUCs?', 'AUC orientation is larger score = outcome one. Paired covariance matters because both models score the same people; ranking accuracy does not establish calibration.', 'Make score B identical to score A and inspect undefined zero-variance inference.'),
'diebold_mariano_test': ("result = m.diebold_mariano_test(d['loss_a'], d['loss_b'], horizon=1, bandwidth=0, correction=True)", "d['loss_a']-d['loss_b']", 'line', None,
 'Does a shifted forecast have larger expected out-of-sample squared loss?', 'The simulated forecast errors are independent one-step validation errors. Positive differences favour model B. HLN at h=1 and bandwidth zero reduces to a paired t statistic.', 'Use a serial loss process and choose a justified nonzero bandwidth.'),
'wilcoxon_signed_rank_test': ("result = m.wilcoxon_signed_rank_test(d['differences'], zero_method='wilcox', method='approx', alternative='greater')", "d['differences']", 'hist', None,
 'Do paired continuous errors show a positive location shift under symmetry?', 'The differences are generated from a symmetric shifted normal distribution. The signed-rank null concerns symmetry about zero, not an unrestricted mean.', 'Round the differences and compare zero-handling conventions.'),
'fisher_exact_test': ("counts = np.array([[4, 26], [14, 16]])\nresult = m.fisher_exact_test(counts, alternative='two-sided')", 'counts', 'heatmap', None,
 'Are two independent groups associated with a binary outcome in a small table?', 'Rows are groups and columns are event/no event. Fisher conditions on margins; this example is not a paired table.', 'Reduce the event counts and compare with asymptotic categorical tests.'),
'g_test': ("counts = np.array([[45, 35, 20], [25, 40, 35]])\nresult = m.g_test(counts, mode='homogeneity')", 'counts', 'heatmap', None,
 'Do independent cohorts share the same three-category distribution?', 'Expected counts are derived from row and column margins. The table has adequate expected cells; sparse cells would leave inference unavailable.', 'Scale the counts down until an expected count falls below five.'),
'stuart_maxwell_test': ("counts = np.array([[80, 25, 5], [8, 70, 22], [2, 10, 78]])\nresult = m.stuart_maxwell_test(counts)", 'counts', 'heatmap', None,
 'Are the marginal category distributions equal for the same subjects measured twice?', 'Rows are initial categories and columns follow-up categories. This tests marginal equality, not symmetry of every off-diagonal pair or migration shape.', 'Transpose the table and verify the same statistic.'),
'mcnemar_test': ("counts = np.array([[90, 30], [10, 70]])\nresult = pd.concat([m.mcnemar_test(counts, exact=True), m.mcnemar_test(counts, exact=False, correction=False)], ignore_index=True)", 'counts', 'heatmap', None,
 'Do paired binary decisions have equal marginal rates?', 'Only the 30 versus 10 discordant pairs drive this comparison. Exact inference conditions on their total; the uncorrected asymptotic row matches binary Stuart-Maxwell.', 'Change the concordant diagonal counts while keeping discordance fixed.'),
'anderson_darling_ksample_test': ("result = m.anderson_darling_ksample_test([d['sample_a'], d['sample_b']], method='permutation', permutations=499, seed=42)", "np.column_stack([np.sort(d['sample_a']), np.sort(d['sample_b'])])", 'line', ['Sorted sample A', 'Sorted sample B'],
 'Do two independent continuous samples share a distribution?', 'Location and scale both differ in the construction. Permutation inference needs exchangeable labels under the null and retains Monte Carlo uncertainty.', 'Use the asymptotic method and inspect any p-value bounds.'),
'cusum_test': ("result = m.cusum_test(d['break_resid'], model_df=2)", "np.cumsum(d['break_resid'])", 'line', None,
 'Does cumulative residual drift indicate coefficient instability?', 'These are OLS residuals from a model including a constant. The mean shifts at observation 120; the plotted cumulative sum is a diagnostic, not a process-control threshold.', 'Remove the constructed shift while keeping the same innovations.'),
'chow_test': ("result = m.chow_test(d['y_break'], d['design'], breakpoint=120)", "d['y_break']", 'line', None,
 'Do coefficients differ across a break specified before inspecting outcomes?', 'The split is fixed by the generating scenario. Classical F inference assumes common error variance and independent Gaussian errors.', 'Move the prespecified split to 80 and compare sensitivity.'),
'sup_f_test': ("result = m.sup_f_test(d['y_break'], d['design'], trim=.15, simulations=499, seed=42)", "d['y_break']", 'line', None,
 'Where is the strongest admissible coefficient break, accounting for the search?', 'The reported p-value simulates the maximum over the full candidate range. An ordinary Chow p-value at the selected point would ignore the search.', 'Increase trimming and inspect search_start/search_end and the selected breakpoint.'),
'logrank_test': ("result = m.logrank_test(d['durations'], d['events'], d['groups'])", "np.column_stack([d['durations'], d['events'], d['groups']])", 'survival', None,
 'Do three groups have equal event-time distributions with right censoring?', 'Group hazards differ while censoring is independently generated. Step curves account for censoring; competing events would require an explicitly different analysis.', 'Give every group the same exponential scale in the generator.'),
'engle_granger_test': ("result = m.engle_granger_test(d['integrated'][:, 1], d['integrated'][:, 0], regression='c', maxlag=6, autolag='aic')", "d['integrated']", 'line', ['Random walk', '1.6 × walk + stationary noise'],
 'Do two integrated series share a stationary long-run combination?', 'Both levels share the same random walk. The cointegration-specific calibration accounts for estimating the first-stage regression; ordinary residual ADF p-values would be inappropriate.', 'Replace the second column by an independent random walk.'),
'johansen_test': ("result = m.johansen_test(d['integrated'], det_order=0, k_ar_diff=1)", "d['integrated']", 'line', ['Random walk', '1.6 × walk + stationary noise'],
 'How many cointegrating relations are supported in a two-series system?', 'The construction contains one common stochastic trend. Read rank hypotheses sequentially within each test family; critical values provide decisions and p-values remain unavailable.', 'Change the number of lagged differences and compare rank evidence.'),
}

SHORT_INTERPRETATIONS = {
 'ljung_box_test': 'Rows correspond to requested lags 1–3 and test cumulative autocorrelation through each lag. They are overlapping hypotheses, not three independent confirmations.',
 'breusch_godfrey_test': 'The original design contains a constant and a trend. The auxiliary regression adds two lagged residuals; LM and F rows test the same serial-correlation null.',
 'arch_lm_test': 'OLS residuals are squared and lagged twice. The effective sample loses two rows; this diagnoses variance dependence rather than mean autocorrelation.',
 'breusch_pagan_test': 'Squared OLS residuals are regressed on the supplied constant and trend. The default Koenker variant produces LM and auxiliary F rows.',
 'jarque_bera_test': 'Inspect the skewness and Pearson kurtosis columns as well as the statistic. The reference is asymptotic chi-square with two degrees of freedom.',
 'adf_test': 'The null is a unit root. AIC chooses among lags zero through two; lag and nobs record the actual fitted specification.',
 'kpss_test': 'The null is level stationarity and bandwidth is fixed at two. A boundary p-value is only a bound; inspect status and the bound columns.',
 'reset_test': 'Powers two and three of the linear fitted values are jointly tested. Rejection does not identify which omitted relationship is correct.',
 'box_pierce_test': 'The same autocorrelation inputs as Ljung-Box use different scaling. Compare the statistics, keeping each method’s own p-value.',
 'durbin_watson_test': 'The p-value uses 99 seeded simulations conditional on the supplied design. This low count demonstrates the API; use more simulations for precise tail estimates.',
 'bds_test': 'The input is an observed synthetic series. Dimension two and epsilon = 1.5 times sample SD are reported; a residual-specific calibration is not assumed.',
 'white_test': 'Squares and interactions expand the original constant-and-trend variance design. Its effective rank determines degrees of freedom.',
 'shapiro_wilk_test': 'The finite nonconstant sample is assessed against the normal family. A nonrejection does not establish normality, and raw Bernoulli residuals are not suitable normality targets.',
 'anderson_darling_normal_test': 'The sample mean and sample variance are estimated before calculating normality evidence; the fitted-normal calibration accounts for that estimation.',
 'phillips_perron_test': 'The tau statistic uses bandwidth two and a constant. Its MacKinnon critical values match the unit-root null and selected statistic.',
 'logistic_calibration_lr_test': 'Each PD group has observed event frequency one half, so the unrestricted fit has intercept and slope zero. Compare its likelihood with intercept zero and slope one; four observations illustrate the calculation, not reliable asymptotic inference.',
 'poisson_binomial_test': 'The event-count masses for probabilities .1, .4, .8 are [.108, .516, .344, .032]. Count one is the most probable outcome, so the probability-ordered two-sided p-value is one.',
 'delong_test': 'Hand-counted tied-score AUCs are .875 and .5. The paired difference variance is .15625; two observations per class illustrate the formula rather than a strong normal approximation.',
 'diebold_mariano_test': 'The first loss sequence is compared with zeros. At horizon one, bandwidth zero and HLN correction, the statistic equals the one-sample t statistic of loss differences.',
 'wilcoxon_signed_rank_test': 'Positive ranks sum to 7 and negative ranks to 3, so the two-sided statistic is 3. Exact inference enumerates all 16 possible sign assignments.',
 'fisher_exact_test': 'The sample odds ratio is 9. Fixed margins give probabilities [1,16,36,16,1]/70; the two-sided p-value is 34/70.',
 'g_test': 'The expected counts are [15,15]. The statistic is 2 × (10 log(10/15) + 20 log(20/15)), with one reference degree of freedom.',
 'stuart_maxwell_test': 'The binary table reduces to uncorrected asymptotic McNemar: (7−3)²/(7+3) = 1.6. This is paired marginal equality, not within-matrix shape.',
 'mcnemar_test': 'There are ten discordant pairs, split 7 versus 3. The default exact test uses a two-sided Binomial(10,.5) tail; diagonal counts do not affect that p-value.',
 'anderson_darling_ksample_test': 'The two samples are identical, and the approximate p-value is capped at .25. It means p≥.25, not p=.25.',
 'cusum_test': 'The input is refitted OLS residuals from a constant-and-trend design. Their cumulative sum is compared with a Brownian-bridge reference.',
 'chow_test': 'The break is fixed at row 40 before inference. The two subsamples each estimate the same constant-and-trend model; the numerator df is two.',
 'sup_f_test': 'The maximum is selected over the trimmed range, and the whole search is repeated in each null simulation. Inspect search endpoints and the selected breakpoint; 99 simulations give coarse tail resolution.',
 'logrank_test': 'Risk sets at times one and two give a group difference of 1/6 and variance 1/4+2/9. The statistic is (1/6)²/(1/4+2/9); the very small dataset demonstrates arithmetic.',
 'engle_granger_test': 'Both levels share a random walk, while y−1.5x is stationary noise by construction. The displayed p-value uses cointegration-specific calibration, accounting for estimation of that combination.',
 'johansen_test': 'The two random walks generate trace and maximum-eigenvalue rows for ranks zero and one. Matching critical values supply decisions; p-values remain NaN by design.',
}


def build_notebook(path, detailed):
    notebook = nbformat.read(path, as_version=4)
    # Idempotent: replace only our previously generated sections.
    notebook.cells = [c for c in notebook.cells if not c.metadata.get('extension_example')]
    if detailed:
        notebook.cells[0].source = notebook.cells[0].source.replace('29 investigations', '60 investigations')
        notebook.cells[0].source = notebook.cells[0].source.replace("in the handbook's order", 'in catalogue order')
        if 'python -m pip install' not in notebook.cells[0].source:
            notebook.cells[0].source = notebook.cells[0].source.replace('cd meliora\n', 'cd meliora\npython -m pip install -e ".[timeseries,notebook]"\n')
        if '(#additional-tests)' not in notebook.cells[0].source:
            notebook.cells[0].source += '\n\n[Model diagnostics, comparisons and inference](#additional-tests).\n'
        conclusion = notebook.cells.pop()
        conclusion.source = conclusion.source.replace('All 29 public methods', 'All 60 public functions')
    else:
        notebook.cells[0].source = notebook.cells[0].source.replace('These 29 examples follow the method names and chapter order in *Statistical Tests for Credit Risk*.', 'These 60 examples cover every public function in catalogue order, with each method introduced, calculated and interpreted.')
        if '(#additional-tests)' not in notebook.cells[0].source:
            notebook.cells[0].source += '\n\nInstall all example dependencies from the repository root with `python -m pip install -e ".[timeseries,notebook]"`. [Examples 30–60](#additional-tests) include optional time-series methods.\n'
    # All numbered additions can run after the initial setup cell alone.
    original_setup = notebook.cells[1].source.split('# Setup for examples 30–60.')[0].rstrip()
    notebook.cells[1].source = original_setup + '\n' + SETUP + (PLOT_SETUP if detailed else '')
    def append(cell):
        cell.metadata['extension_example'] = True
        notebook.cells.append(cell)
    append(nbformat.v4.new_markdown_cell('<a id="additional-tests"></a>\n## Model diagnostics and inference\n\nUse `import meliora as m` for each method. In tabular inference results, `pd.NA` means inference is unavailable or a bound cannot decide rejection. Synthetic scenarios illustrate hypotheses, not blanket validation requirements.'))
    for number, (name, title, area, target, explanation) in enumerate(CATALOGUE, 30):
        assert callable(getattr(m, name))
        if detailed:
            code, values, kind, labels, question, interpretation, experiment = DETAIL[name]
            append(nbformat.v4.new_markdown_cell(f'<a id="example-{number}"></a>\n### {number}. {title}\n\n**Question.** {question}\n\n{explanation}\n\n[Input contract, hypotheses and sources](../reference/{name}.md).'))
            append(nbformat.v4.new_code_cell('d = extension_data()\n'+code+f'\nextension_plot({values}, {kind!r}, {title!r}, {labels!r})\ndisplay(result)\nexplain_inference(result)'))
            append(nbformat.v4.new_markdown_cell(f'**What this shows.** {interpretation}\n\n**Try this.** {experiment}'))
        else:
            reference = (ROOT/'docs/reference'/f'{name}.md').read_text(encoding='utf-8')
            code = next(c for c in re.findall(r'```python\n(.*?)```', reference, re.S) if 'import meliora' in c)
            code = re.sub(r"print\(result\[\[.*?\]\]\)\n?", 'display(result)\nexplain_inference(result)\n', code)
            if name == 'engle_granger_test':
                code = ("rng = np.random.default_rng(47)\nx = np.cumsum(rng.normal(size=120))\n"
                        "y = 1.5*x + rng.normal(size=120)\n"
                        "result = m.engle_granger_test(y, x, regression='c', maxlag=3, autolag='aic')\n"
                        "display(result)\nexplain_inference(result)")
            if name in {'arch_lm_test', 'breusch_pagan_test', 'white_test', 'cusum_test'}:
                code = code.replace('result = ', 'E = Y - X @ np.linalg.lstsq(X, Y, rcond=None)[0]\nresult = ', 1)
                code = code.replace(f'm.{name}(Y', f'm.{name}(E')
            append(nbformat.v4.new_markdown_cell(f'### {number}. {title}\n\n{explanation}\n\n[Method reference and sources](../reference/{name}.md).'))
            append(nbformat.v4.new_code_cell(code))
            append(nbformat.v4.new_markdown_cell('**Interpretation.** '+SHORT_INTERPRETATIONS[name]))
    if detailed:
        notebook.cells.append(conclusion)
    # Outputs must be regenerated after setup/content changes.
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
    nbformat.write(notebook, path)


def update_readme():
    path = ROOT/'README.md'
    text = path.read_text(encoding='utf-8')
    # Update catalogue rows in place without introducing a separate class of methods.
    text = re.sub(r'^\| (?:3[0-9]|4[0-9]|5[0-9]|60) \|.*\n', '', text, flags=re.M)
    rows = '\n'.join(f'| {i} | [{title}](docs/reference/{name}.md) | {area} | {target} | {explanation} |' for i, (name,title,area,target,explanation) in enumerate(CATALOGUE, 30))
    last = re.search(r'^\| 29 \|.*$', text, re.M)
    if last is None:
        raise ValueError('The README catalogue must contain row 29')
    text = text[:last.end()]+'\n'+rows+text[last.end():]
    path.write_text(text, encoding='utf-8')


if __name__ == '__main__':
    build_notebook(ROOT/'docs/examples/examples.ipynb', False)
    build_notebook(ROOT/'docs/examples/detailed_examples.ipynb', True)
    update_readme()
