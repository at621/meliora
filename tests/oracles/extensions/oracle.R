# Independent R references. Run from repository root through regenerate.py.
.libPaths(c('.r-libs', .libPaths()))
options(digits=17)
root <- 'tests/oracles/extensions'
dat <- read.csv(file.path(root, 'regression.csv'))
y <- dat$y; x <- dat$x; n <- length(y)
fit <- lm(y ~ x); e <- resid(fit)
rows <- list()
emit <- function(name, statistic, pvalue=NA_real_) {
  rows[[length(rows)+1]] <<- data.frame(name=name, statistic=as.numeric(statistic)[1], pvalue=as.numeric(pvalue)[1])
}
ht <- function(name, obj) emit(name, obj$statistic, obj$p.value)
ht('ljung_box_test', Box.test(y, lag=3, type='Ljung-Box'))
ht('box_pierce_test', Box.test(y, lag=3, type='Box-Pierce'))
ht('breusch_godfrey_test', lmtest::bgtest(fit, order=2))
# Auxiliary ARCH regression independently formed in R, first two rows truncated.
sq <- y^2
aux <- lm(sq[3:n] ~ sq[2:(n-1)] + sq[1:(n-2)])
lmstat <- (n-2)*summary(aux)$r.squared
emit('arch_lm_test', lmstat, pchisq(lmstat, 2, lower.tail=FALSE))
# BP contract takes residuals directly; use a zero-mean response fit so these
# residuals match an independently computed OLS regression.
ht('breusch_pagan_test', lmtest::bptest(fit, studentize=TRUE))
ht('breusch_pagan_classical', lmtest::bptest(fit, studentize=FALSE))
ht('jarque_bera_test', tseries::jarque.bera.test(y))
emit('adf_test', urca::ur.df(y, type='drift', lags=2, selectlags='Fixed')@teststat[1])
emit('kpss_test', urca::ur.kpss(y, type='mu', use.lag=2)@teststat)
ht('reset_test', lmtest::resettest(fit, power=2:3, type='fitted'))
emit('durbin_watson_test', sum(diff(e)^2)/sum(e^2))
bds <- tseries::bds.test(y, m=2, eps=1.5*sd(y))
emit('bds_tseries_full_sample', bds$statistic, bds$p.value)
# Condition C1 on the first m-1 observations, as in Kanzler footnote 10.
# Enumerate pairs/triples explicitly, independent of statsmodels' matrix sums.
eps <- 1.5*sd(y)
pairs <- combn(n,2)
C1 <- mean(abs(y[pairs[1,]]-y[pairs[2,]]) < eps)
triples <- combn(n,3)
K <- mean(apply(triples,2,function(v) {
  a <- abs(y[v[1]]-y[v[2]]) < eps; b <- abs(y[v[1]]-y[v[3]]) < eps
  c <- abs(y[v[2]]-y[v[3]]) < eps
  (a*b+a*c+b*c)/3
}))
histpairs <- combn(2:n,2)
C1conditional <- mean(abs(y[histpairs[1,]]-y[histpairs[2,]]) < eps)
C2 <- mean(apply(histpairs,2,function(v) max(abs(y[c(v[1]-1,v[1])]-y[c(v[2]-1,v[2])])) < eps))
bdsconditional <- sqrt(n-1)*(C2-C1conditional^2)/(2*abs(K-C1^2))
emit('bds_test',bdsconditional,2*pnorm(-abs(bdsconditional)))
white <- lm(e^2 ~ x + I(x^2))
lmstat <- n*summary(white)$r.squared
emit('white_test', lmstat, pchisq(lmstat, 2, lower.tail=FALSE))
ht('shapiro_wilk_test', shapiro.test(y))
ht('anderson_darling_normal_test', nortest::ad.test(y))
emit('phillips_perron_urca', urca::ur.pp(y, type='Z-tau', model='constant', use.lag=2)@teststat)
# urca uses the current-level centred sum of squares; arch uses the lagged
# regression coefficient variance. Independently compute the latter convention.
pp <- lm(y[-1] ~ y[-n]); u <- resid(pp); N <- n-1
gamma0 <- sum(u^2)/N
lrv <- gamma0+2/N*sum(sapply(1:2,function(j) (1-j/3)*sum(u[(j+1):N]*u[1:(N-j)])))
se <- summary(pp)$coefficients[2,2]; rho <- coef(pp)[2]
tau <- sqrt(gamma0/lrv)*(rho-1)/se-.5*(lrv-gamma0)/sqrt(lrv)*(N*se/sqrt(sum(u^2)/(N-2)))
emit('phillips_perron_test',tau)
binary <- c(0,1,0,1); pd <- c(.2,.2,.8,.8)
logistic <- glm(binary ~ qlogis(pd), family=binomial())
lr <- 2*(as.numeric(logLik(logistic))-sum(dbinom(binary, 1, pd, log=TRUE)))
emit('logistic_calibration_lr_test', lr, pchisq(lr,2,lower.tail=FALSE))
# Exhaustive Bernoulli enumeration, not convolution.
events <- expand.grid(a=0:1,b=0:1,c=0:1)
pr <- apply(events,1,function(row) prod(c(.1,.4,.8)^row*c(.9,.6,.2)^(1-row)))
pmf <- tapply(pr,rowSums(events),sum)
emit('poisson_binomial_test',1,sum(pmf[pmf <= pmf[2]*(1+1e-12)]))
a <- pROC::roc(c(1,1,0,0),c(1,2,0,1),direction='<',quiet=TRUE)
b <- pROC::roc(c(1,1,0,0),c(1,1,0,2),direction='<',quiet=TRUE)
ht('delong_test',pROC::roc.test(a,b,paired=TRUE,method='delong'))
ht('diebold_mariano_test',t.test(y)) # h=1, bandwidth=0, HLN = one-sample t
ht('wilcoxon_signed_rank_test',wilcox.test(c(1,2,-3,4),exact=TRUE))
# R reports W+; Meliora two-sided reports min(W+, W-).
rows[[length(rows)]]$statistic <- 3
f <- fisher.test(matrix(c(3,1,1,3),2,byrow=TRUE))
emit('fisher_exact_test',9,f$p.value) # sample OR, R estimates conditional OR
g <- 2*sum(c(10,20)*log(c(10,20)/15))
emit('g_test',g,pchisq(g,1,lower.tail=FALSE))
tab <- matrix(c(12,7,3,20),2,byrow=TRUE)
ht('stuart_maxwell_test',DescTools::StuartMaxwellTest(tab))
emit('mcnemar_test',3,binom.test(3,10,.5)$p.value)
ad <- kSamples::ad.test(c(1,2,3,4),c(1,2,3,4),method='asymptotic')
emit('anderson_darling_ksample_test',ad$ad[1,2])
# CUSUM scaling by raw sum of squares, no model-df correction.
emit('cusum_test',max(abs(cumsum(y)))/sqrt(sum(y^2)))
chow <- function(b) {
  split <- sum(resid(lm(y[1:b] ~ x[1:b]))^2)+sum(resid(lm(y[(b+1):n] ~ x[(b+1):n]))^2)
  (sum(e^2)-split)/2/(split/(n-4))
}
emit('chow_test',chow(40),pf(chow(40),2,n-4,lower.tail=FALSE))
emit('sup_f_test',max(sapply(12:68,chow)))
lr <- survival::survdiff(survival::Surv(c(1,3,2,3),c(1,0,1,0)) ~ c('a','a','b','b'))
emit('logrank_test',lr$chisq,pchisq(lr$chisq,1,lower.tail=FALSE))
walk <- read.csv(file.path(root,'walk.csv'))
egres <- resid(lm(y ~ walk$a))
emit('engle_granger_test',urca::ur.df(egres,type='none',lags=1,selectlags='Fixed')@teststat[1])
# Independent canonical-correlation eigenproblem, constant removed from all
# variables, one differenced lag. Matches det_order=0, k_ar_diff=1.
z <- as.matrix(walk); z <- scale(z,scale=FALSE)
dz <- diff(z); lagdiff <- scale(dz[-nrow(dz),,drop=FALSE],scale=FALSE)
d <- scale(dz[-1,,drop=FALSE],scale=FALSE)
level <- scale(z[2:(n-1),,drop=FALSE],scale=FALSE)
r0 <- qr.resid(qr(lagdiff),d); rk <- qr.resid(qr(lagdiff),level)
s00 <- crossprod(r0)/nrow(r0); skk <- crossprod(rk)/nrow(rk); sk0 <- crossprod(rk,r0)/nrow(r0)
ev <- sort(Re(eigen(solve(skk,sk0 %*% solve(s00,t(sk0))))$values),decreasing=TRUE)
emit('johansen_test',-nrow(r0)*sum(log(1-ev)))
write.csv(do.call(rbind,rows),file.path(root,'r_results.csv'),row.names=FALSE,na='')
writeLines(c(R.version.string, capture.output(sessionInfo())),file.path(root,'r_session.txt'))
