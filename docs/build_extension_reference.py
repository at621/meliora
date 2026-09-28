"""Regenerate extension reference pages from reviewed specifications and examples."""
from pathlib import Path
import inspect
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'tests')]
import meliora as m
from extension_cases import EXTENSION_CASES, OPTIONAL

# H0; statistic/reference; inputs/settings/assumptions and limitations.
SPECS = {
'ljung_box_test': (
 'Autocorrelations at lags 1 through h are jointly zero.',
 'Q = n(n+2) sum(r_j²/(n-j)); asymptotic chi-square with h-model_df degrees of freedom. Autocorrelations use demeaned observations and divisor sum(x-mean(x))².',
 'Ordered series or residuals. Integer lags returns 1..h; a unique sequence returns those lags in requested order. Each lag must be below n. model_df is the number of fitted dynamic parameters deducted from h, not automatically every regression coefficient. Nonpositive df returns NaN p-value and nullable reject. Large h relative to n weakens the approximation.'),
'breusch_godfrey_test': (
 'Regression errors have no serial correlation through the requested order.',
 'LM = n R² from OLS residuals regressed on the original design and lagged residuals; chi-square(h). F = ((SSE_restricted-SSE_full)/h)/(SSE_full/(n-k-h)).',
 'Raw ordered dependent observations y and the original full-rank regression design x including a constant. OLS is refitted. Pre-sample residuals are zero-padded and all n rows retained. Return LM and F rows. Requires positive residual df and a full-rank augmented design. Standard regression exogeneity assumptions apply; F is an auxiliary-regression approximation.'),
'arch_lm_test': (
 'Squared errors have no serial dependence through the requested order (no ARCH effects).',
 'Regress e_t² on a constant and h lagged squares after dropping h rows. LM = (n-h-model_df)R², asymptotic chi-square(h). Auxiliary F uses n-h-h-1 denominator df.',
 'Ordered residual vector. center=False leaves residuals unchanged; True subtracts their sample mean before squaring. lags is explicit, model_df only adjusts the LM multiplier. Constant squares, singular lag designs and insufficient residual df raise ValueError. Requires finite fourth moments; this is not a general test against all heteroskedasticity.'),
'breusch_pagan_test': (
 'Variance-regressor slopes, excluding the constant, are zero.',
 'Koenker LM = n R² from squared residuals on Z. Classical BP = explained sum of squares / 2 for e²/mean(e²). Both use chi-square(k-1); an auxiliary F row is also returned.',
 'Residuals and a user-specified full-rank variance design with explicit constant and at least one nonconstant column. variant=koenker is studentised; variant=classical assumes normally distributed errors. Koenker permits nonnormal iid errors with finite relevant moments. Neither variant corrects for serial dependence. Constant squared residuals are undefined and rejected.'),
'jarque_bera_test': (
 'Observations have normal skewness and kurtosis.',
 'JB = n(S²/6 + (K-3)²/24), asymptotic chi-square(2). S and Pearson K use central moments with divisor n, without bias corrections.',
 'At least three nonconstant finite observations. Inference assumes iid sampling and can be inaccurate in small samples. Rejection concerns skewness/kurtosis; nonrejection cannot establish normality. Unlike normal_test, this tests distribution shape, not annual PD forecast errors.'),
'adf_test': (
 'The series has a unit root.',
 'OLS t statistic on the lagged level in a regression of first differences on that level, lagged differences and deterministic terms. MacKinnon unit-root p-value and 1%, 5%, 10% critical values, not a Student t reference.',
 'Ordered nonconstant series, at least five observations. regression=n/c/ct/ctt means none/constant/linear trend/quadratic trend. maxlag=None uses the statsmodels Schwert-style maximum, capped for sample size; autolag=AIC/BIC minimises that criterion on a common comparison sample, t-stat drops lags by the 5% last-lag rule, None uses maxlag. Return selected lag and effective nobs. Inference is against stationarity under the chosen deterministic specification and has low power near a unit root.'),
'kpss_test': (
 'The series is stationary around a constant or deterministic linear trend.',
 'KPSS = sum(S_t²)/(n² LRV), with S_t cumulative detrended residuals and Bartlett long-run variance. Interpolated KPSS table, with p bounded below at .10 or above at .01 outside its range.',
 'Ordered nonconstant series. regression=c or ct. bandwidth is an integer 0..n-1, auto uses the statsmodels Hobijn data-dependent rule, legacy uses ceil(12(n/100)^.25). Return selected bandwidth, deterministic terms and critical values. Small-sample and bandwidth sensitivity can be substantial. Its null is the opposite of ADF/PP; inconsistent conclusions can be inconclusive rather than contradictory.'),
'reset_test': (
 'All selected nonlinear fitted-value augmentation coefficients are zero.',
 'Add centred, standardised fitted-value powers to OLS. Classical nested F has q numerator and n-k-q denominator df; HC3 uses the sandwich covariance and a chi-square(q) Wald statistic.',
 'Dependent observations and full-rank design with constant. powers is a nonempty tuple of unique integers >=2. covariance=nonrobust assumes homoskedastic independent Gaussian regression errors for exact F inference. HC3 permits heteroskedasticity asymptotically but not serial correlation. Unit leverage, singular augmentations and constant fitted values are rejected. Rejection does not identify a unique omitted variable.'),
'logistic_calibration_lr_test': (
 'In logit P(Y=1)=a+b logit(p), a=0 and b=1 jointly.',
 'LR = 2(log L_unrestricted - log L_at_(0,1)), asymptotic chi-square(2). Bernoulli log likelihood is evaluated with stable logaddexp arithmetic.',
 'Aligned validation outcomes (both binary classes) and at least four distinct-observation slots of interior PDs 0<p<1. Constant forecasts, boundary PDs, complete or quasi-complete separation and ill-conditioned information are rejected. A failed optimizer returns status=nonconvergence and nullable reject. Forecasts must be fixed relative to independent validation outcomes; regular identifiable finite MLEs are required. This joint calibration-curve test differs from grade-level binomial tests.'),
'poisson_binomial_test': (
 'Total events follow the sum of independent Bernoulli variables with the specified individual probabilities.',
 'Exact PMF from repeated convolution of [1-p_i,p_i]. less sums P(K<=k); greater sums P(K>=k); two-sided sums masses no larger than the observed mass (relative comparison tolerance 1e-12).',
 'A finite probability vector, including 0 and 1, and integer event count 0..n. Count is the statistic; no df parameter. Equal probabilities reduce to the binomial law. Complexity is O(n²), and extreme tail probabilities may underflow in floating point. Heterogeneous probabilities are supported without requiring the newer scipy.stats.poisson_binom.'),
'delong_test': (
 'The population AUCs of two scores on the same observations are equal.',
 'Z = (AUC_A-AUC_B)/sqrt(v), with v = [1,-1] Cov(AUC_A,AUC_B) [1,-1]ᵀ. Covariance is sample covariance of positive placements/n_positive plus negative placements/n_negative; asymptotic standard normal.',
 'Aligned binary outcomes and two scores. At least two observations in each class; larger scores indicate outcome 1. Pairwise wins count 1, ties .5. alternative=less/greater refers to AUC_A-AUC_B; two-sided is default. Variance <=1e-15 returns undefined inference, including identical scores. Paired samples only, with independent subjects. Memory O(n_positive*n_negative). Existing roc_auc is only an estimate.'),
'diebold_mariano_test': (
 'The expected out-of-sample loss differential loss_A-loss_B is zero.',
 'DM = mean(d)/sqrt(LRV/n), with divisor-n autocovariances. Bartlett weights are 1-j/(bandwidth+1); acf uses unweighted autocovariances. HLN multiplies by sqrt((n+1-2h+h(h-1)/n)/n) and uses t(n-1); uncorrected inference uses normal.',
 'Two aligned ordered out-of-sample loss vectors. horizon h is 1..n-1; default bandwidth=h-1, or choose explicitly. estimator=bartlett or acf; correction=True enables HLN. less/greater refer to mean loss_A-loss_B. Requires covariance-stationary loss differences and a suitable horizon/bandwidth; nonpositive LRV returns undefined inference. Identical losses have no evidence to test. This differs from the midpoint-null redelmeier_test.'),
'box_pierce_test': (
 'Autocorrelations at lags 1 through h are jointly zero.',
 'Q = n sum(r_j²), asymptotic chi-square(h-model_df). The autocorrelation estimates and contracts match Ljung-Box.',
 'Ordered nonconstant series. Integer lags returns 1..h, a sequence returns those lags. model_df adjusts degrees of freedom, with unavailable inference at h<=model_df. The Box-Pierce approximation is generally less accurate in small samples than the Ljung-Box finite-sample scaling.'),
'durbin_watson_test': (
 'Classical regression errors have zero first-order autocorrelation.',
 'D = sum((e_t-e_(t-1))²)/sum(e_t²). Conditional on fixed X, simulate iid Gaussian errors, project off X and recompute D. Rank Monte Carlo tails use (exceedances+1)/(simulations+1), doubling the smaller tail for two-sided inference.',
 'Ordered dependent observations and original full-rank design with constant, refitted by OLS. Assumes fixed exogenous regressors and iid homoskedastic Gaussian errors under H0. lagged_dependent=True is rejected; callers must not label lagged dependent regressors as fixed. greater means positive autocorrelation (small D), less negative autocorrelation (large D). At least 99 simulations; seed is explicit and defaults to 0. No published-bounds inconclusive region is needed because design-aware null simulation is used; Monte Carlo uncertainty remains near alpha.'),
'bds_test': (
 'The observed series is independent and identically distributed.',
 'For dimensions m=2..max_dim, Z_m=sqrt(n-m+1)(C_m-C_1^m)/sigma_m, asymptotic normal. C_m counts embedded pairs closer than epsilon in sup norm; the one-dimensional numerator uses the sample conditional on the first m-1 observations (Kanzler convention).',
 'Ordered observed series, max_dim<n-1. epsilon defaults to distance*sample SD with distance=1.5. Returns a row per dimension and chosen threshold. residuals=True is deliberately rejected because fitted-model residual inference needs a model-specific calibration. Nonfinite statistics have undefined p-values. Requires sufficiently large samples; O(n²) storage restricts long series. It tests iid, not only zero autocorrelation.'),
'white_test': (
 'Regression errors have constant variance against the quadratic variance alternative.',
 'Create every Z_i Z_j for i<=j, including linear terms through the constant. Regress squared residuals on an orthonormal basis of that space; LM=n R², chi-square(rank-1), plus auxiliary F with n-rank denominator df.',
 'Residuals and original variance design with explicit constant. The input design must be full rank, but collinear squares/interactions are handled through effective SVD rank. Saturated auxiliary designs and constant squares are rejected. Independent errors and sufficient finite moments are needed; many regressors can consume sample size rapidly. Broader alternative than a specified linear BP variance design.'),
'shapiro_wilk_test': (
 'The sample comes from a normal distribution.',
 'W = (sum a_i x_(i))²/sum(x_i-mean(x))², using normal-order-statistic weights; Shapiro-Wilk/Royston calibration as implemented in SciPy.',
 'At least three finite nonconstant observations; iid continuous sampling. Ties are permitted and flagged, but rounding/discreteness can affect calibration. W is returned for n>5000 while pvalue and reject remain unavailable because p-value accuracy is not established there. Normality is not a blanket requirement for Bernoulli default residuals.'),
'anderson_darling_normal_test': (
 'The sample is normal with unknown mean and variance.',
 'A²=-n-(1/n)sum((2i-1)[log F(x_(i))+log(1-F(x_(n+1-i)))]), where F fits the sample mean and sample SD. Stephens fitted-normal p-value calibration includes the finite-sample adjustment.',
 'At least eight nonconstant finite observations. Assumes iid continuous observations. Fitting mean and variance requires a different calibration from a completely specified normal CDF. This is a one-sample fitted-normal test, separate from the k-sample equality-of-distributions test.'),
'phillips_perron_test': (
 'The series has a unit root.',
 'Fit y_t=rho y_(t-1)+deterministic terms. Z_tau=sqrt(gamma0/LRV)t_rho - .5(LRV-gamma0)/sqrt(LRV) * N*SE(rho)/s. Z_rho=N(rho-1)-.5 N² SE(rho)²/s²*(LRV-gamma0). s²=SSE/(N-k), gamma0=SSE/N.',
 'Ordered nonconstant series with at least six observations. regression=n/c/ct; statistic=tau/rho. Bartlett bandwidth defaults to min(n-2,ceil(12(n/100)^.25)); explicit bandwidth 0..n-2. arch supplies statistic-specific MacKinnon p-values and critical values. No lagged differences are added, unlike ADF. Assumes a suitable weak-dependence long-run variance approximation. The arch lagged-regression variance convention differs slightly from urca current-level scaling.'),
'wilcoxon_signed_rank_test': (
 'The paired-difference distribution is symmetric about zero.',
 'Rank absolute differences; W is min(W+,W-) for two-sided and W+ for directional alternatives. Exact signed-rank distribution without zeros/ties; otherwise a tie/zero-adjusted normal approximation.',
 'A difference vector or aligned x,y. zero_method=wilcox discards zero differences, pratt includes them in ranking, zsplit splits their ranks. method=auto selects exact only without ties/zeros and n<=50; method=exact rejects ties/zeros, approx uses normal. correction controls continuity correction. All-zero differences give undefined inference. Round scientifically equivalent differences before calling if subtraction introduces artificial ties. Not an unrestricted test of mean error.'),
'fisher_exact_test': (
 'The population odds ratio is one, conditional on the table margins.',
 'Sample odds ratio ad/bc is reported as statistic; hypergeometric conditional tails supply the p-value. Two-sided sums tables no more likely than the observed table.',
 'Exactly a 2x2 table of nonnegative integer counts with positive total. alternative=less/greater refers to the odds ratio. Degenerate margins give p=1 and an undefined odds-ratio estimate, explicitly flagged. Independent subjects are assumed; use McNemar for paired binary observations.'),
'g_test': (
 'Specified multinomial probabilities hold (goodness-of-fit), or independent groups share category probabilities (homogeneity).',
 'G=2 sum O log(O/E), with 0 log 0=0. Goodness-of-fit E=Np, df=k-1-ddof. Homogeneity E_ij=row_i*column_j/N, df=(r-1)(c-1). Asymptotic chi-square.',
 'mode=goodness-of-fit takes count vector and strictly positive probabilities summing to one; ddof accounts for independently justified fitted parameters. mode=homogeneity takes a table and derives expectations. Empty margins must be removed explicitly. If any E<5, statistic/expectations are returned but pvalue and reject are unavailable, status=sparse-asymptotic-unreliable; pool categories only with scientific justification or use a suitable exact test.'),
'stuart_maxwell_test': (
 'Paired categorical observations have equal marginal distributions.',
 'd=row totals-column totals; V_ii=row_i+column_i-2n_ii, V_ij=-(n_ij+n_ji). Q=dᵀ V⁺ d with chi-square(rank(V)). Eigenvalues <=1e-12*max(1,largest eigenvalue) are treated as zero.',
 'Square integer paired transition table. Singularity due to disconnected category components is handled by a pseudoinverse and effective rank, not invented degrees of freedom. All-diagonal tables have rank zero and undefined inference. Large-sample marginal-homogeneity approximation; sparse discordance can invalidate it. Binary reduction matches uncorrected asymptotic McNemar. This is not migration_matrix_stability, which checks within-matrix shape.'),
'mcnemar_test': (
 'The two marginal probabilities in paired binary observations are equal.',
 'For discordances b,c, exact two-sided binomial inference on min(b,c) conditional on b+c. Asymptotic Q=max(0,abs(b-c)-correction)²/(b+c), chi-square(1).',
 'Exactly a 2x2 paired count table. exact=True by default; correction=True only affects asymptotic inference. With no discordance, exact p=1 while asymptotic inference is undefined. Independent pairs are assumed. Exact and asymptotic variants are distinct; continuity-corrected Q does not equal binary Stuart-Maxwell.'),
'anderson_darling_ksample_test': (
 'All independent samples come from the same distribution.',
 'Scholz-Stephens standardised k-sample Anderson-Darling statistic, based on weighted squared differences between group and pooled empirical CDFs. Table-based p-values are bounded to [.001,.25]; permutation inference uses a pooled-label randomisation with the +1 Monte Carlo correction.',
 'Sequence of at least two samples, each with at least two observations and at least two distinct values pooled. midrank=True handles ties via midranks, False uses right-side EDFs. method=asymptotic or permutation; permutations and seed are returned for the latter. Exchangeability across independent groups is essential. New SciPy variants omit critical values, so that field is empty when unavailable; no values are fabricated.'),
'cusum_test': (
 'Regression coefficients are constant over time.',
 'Q=max_t abs(sum_(i<=t)e_i)/sqrt(SSE*n/(n-model_df)); asymptotic supremum absolute Brownian bridge (Kolmogorov) reference.',
 'Ordered OLS residuals from a model with a constant, supplied by the caller; model_df is an explicit degrees-of-freedom scaling adjustment. The API cannot infer the original design from residuals. Assumes exogenous regressors and suitable iid homoskedastic errors; OLS CUSUM can have weak power for some regressor patterns. This is parameter-stability inference, not a process-control chart.'),
'chow_test': (
 'All regression coefficients are equal before and after the prespecified breakpoint.',
 'F=((SSE_pooled-SSE_1-SSE_2)/k)/((SSE_1+SSE_2)/(n-2k)); F(k,n-2k).',
 'Ordered dependent observations and full-rank original design including constant. breakpoint is the zero-based row starting segment two, with each segment having more than k rows and full-rank design. Independent Gaussian errors, common variance and a breakpoint fixed independently of the data are required for classical F inference. Use sup_f_test when selecting the breakpoint by search.'),
'sup_f_test': (
 'No coefficient break exists anywhere in the admissible search interval.',
 'Maximum Chow F over all integer breakpoints with both segments >=max(k+1,ceil(n*trim),min_segment). Simulate Gaussian null outcomes conditional on fixed X and recompute the entire maximum; p=(exceedances+1)/(simulations+1).',
 'Ordered dependent observations and original full-rank design with constant. trim strictly between 0 and .5; min_segment optional. Every candidate subsample design is checked. At least 99 simulations, default 999, seed=0. Return selected breakpoint, actual endpoints, minimum segment, seed and simulated critical value. Assumes fixed exogenous regressors and homoskedastic Gaussian iid errors; this calibration does not support lagged dependent regressors or generic heteroskedastic errors. Monte Carlo uncertainty matters near alpha.'),
'logrank_test': (
 'All groups have equal survival functions.',
 'At each event time use the multivariate hypergeometric expected group deaths and covariance d(N-d)/(N-1)*(diag(p)-ppᵀ). Sum O-E and V, then Q=(O-E)ᵀV⁺(O-E), chi-square(rank(V)).',
 'Aligned nonnegative durations, event indicators exactly 0/1 and complete group labels (>=2 groups). Supports tied event times and multiple groups; subjects censored at an event time remain in its risk set. Independent right censoring within groups is required. Competing-event codes are rejected; never silently recode them as censoring. No event information returns undefined inference. Nonproportional hazards can reduce power.'),
'engle_granger_test': (
 'There is no cointegration between the specified integrated series.',
 'OLS cointegrating regression followed by an unaugmented-deterministic residual ADF statistic, with cointegration-specific MacKinnon p-values/critical values depending on the number of series and deterministic terms.',
 'Ordered dependent series and one or more aligned regressors, assumed I(1). regression=n/c/ct/ctt, maxlag and autolag=aic/bic/t-stat/None follow ADF residual lag selection. Return selected lag and residual ADF effective sample. Constant, collinear and near-perfect regression fits are rejected. Critical values for regression=n are unavailable in statsmodels and remain NaN. This is not ordinary ADF inference on estimated residuals.'),
'johansen_test': (
 'Trace: cointegration rank is at most r. Maximum eigenvalue: rank r against rank r+1.',
 'Trace=-T sum_(i>r)log(1-lambda_i); max-eigen=-T log(1-lambda_(r+1)). Johansen critical values at 10%, 5%, 1%; no p-values supplied or invented.',
 'Ordered matrix of 2..12 noncollinear varying I(1) series. k_ar_diff is the number of lagged differences (VAR level order minus one); det_order=-1/0/1 uses statsmodels no-deterministic/constant/linear-trend detrending convention. This is not the complete set of restricted/unrestricted VECM deterministic cases. Return both tests for every rank, effective nobs, critical values and decisions only for alpha=.10/.05/.01. Short samples, near-singular covariance and lag/deterministic misspecification can distort inference.'),
}

SOURCES = {
 'timeseries': 'https://www.statsmodels.org/stable/stats.html',
 'calibration': 'https://pubmed.ncbi.nlm.nih.gov/3203132/',
 'distributions': 'https://docs.scipy.org/doc/scipy/reference/stats.html',
 'structural': 'https://www.jstatsoft.org/article/view/v007i02',
}

SPECIFIC_SOURCES = {
 'logistic_calibration_lr_test': 'https://link.springer.com/article/10.1186/s12916-019-1466-7',
 'poisson_binomial_test': 'https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson_binom.html',
 'diebold_mariano_test': 'https://www.nber.org/papers/w18391.pdf',
 'phillips_perron_test': 'https://arch.readthedocs.io/en/latest/unitroot/generated/arch.unitroot.PhillipsPerron.html',
 'johansen_test': 'https://www.statsmodels.org/stable/generated/statsmodels.tsa.vector_ar.vecm.coint_johansen.html',
 'engle_granger_test': 'https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.coint.html',
 'logrank_test': 'https://scikit-survival.readthedocs.io/en/stable/api/generated/sksurv.compare.compare_survival.html',
}


def main():
    catalogue = []
    for name, args, kwargs in EXTENSION_CASES:
        h0, formula, contract = SPECS[name]
        function = getattr(m,name)
        module = function.__module__.split('.')[-1]
        arguments = []
        for arg in args:
            if isinstance(arg,list) and len(arg)==80:
                arguments.append('X' if isinstance(arg[0],list) and arg[0][0]==1 else
                                 'WALK' if isinstance(arg[0],list) else
                                 'np.zeros(80)' if arg==[0.]*80 else
                                 'WALK[:, 0]' if name=='engle_granger_test' and len(arguments)==1 else 'Y')
            else:
                arguments.append(repr(arg))
        arguments += [f'{key}={value!r}' for key,value in kwargs.items()]
        call = f'm.{name}('+', '.join(arguments)+')'
        output = function(*args,**kwargs)
        values = ', '.join(f'{v:.9g}' for v in output.statistic)
        setup = ''
        if any(token in call for token in ['Y','X','WALK']):
            setup = ('Y = np.random.default_rng(812).normal(size=80) + np.linspace(0, 2, 80)\n'
                     'X = np.column_stack([np.ones(80), np.linspace(-1, 1, 80)])\n'
                     'WALK = np.cumsum(np.random.default_rng(921).normal(size=(80, 2)), axis=0)\n')
        dependency = "Requires `pip install 'meliora[timeseries]'`." if name in OPTIONAL else 'Uses base NumPy/SciPy dependencies.'
        text = f'''# {name}

```python
{name}{inspect.signature(function)}
```

## Hypotheses and calculation

**H0:** {h0} **H1:** departure from this null, restricted to the selected direction where the API supports `alternative`.

{formula}

## Inputs, settings and limitations

{contract}

{dependency} See the [shared contracts](../extensions.md) for missing data,
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
{setup}
result = {call}
print(result[['statistic', 'pvalue', 'status', 'reject']])
```

Statistics in row order: `{values}`. The formula above explains the calculation.
Small arithmetic examples and reductions are checked in the relevant
[numerical tests](../../tests/); reproducible independent R calculations, including
the precise finite-sample conventions, are in
[the extension oracle](../../tests/oracles/extensions/README.md).

## Sources

- [Statistical reference]({SPECIFIC_SOURCES.get(name, SOURCES[module])})
- [Verification record](../extension_verification.md)
- [Independent R implementation and provenance](../../tests/oracles/extensions/oracle.R)
'''
        (ROOT/'docs'/'reference'/f'{name}.md').write_text(text,encoding='utf-8')
        catalogue.append(f'- [{name}](reference/{name}.md)')
    (ROOT/'docs'/'extension_catalogue.md').write_text('# Extension catalogue\n\n30 backlog entries, 31 public functions. The original book-aligned 29-method catalogue is unchanged.\n\n'+'\n'.join(catalogue)+'\n',encoding='utf-8')


if __name__ == '__main__':
    main()
