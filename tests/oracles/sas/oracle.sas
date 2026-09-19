/*----------------------------------------------------------------------------
 SAS oracle for the Meliora cross-language comparison (SAS 9.4).

 Reads the CSV datasets written by tests/oracles/cases.py, computes every case
 with SAS procedures where they exist (PROC FREQ, NPAR1WAY, CORR, TTEST) and
 with DATA-step / PROC SQL formulas from the book, Basel working paper 14 and
 the ECB validation instructions otherwise, and writes the (case, field, value)
 records compared by tests/test_cross_language.py through PROC JSON.

 Run either through tests/oracles/run_oracles.py (saspy fills the two macro
 variables below) or by hand: set data_dir to the folder holding the CSV files
 and out_path to the JSON file to write, submit, then adopt the output with
     python tests/oracles/run_oracles.py sas --stamp <out_path>

 STATUS: written without access to a SAS installation and not yet executed.
 Expect to fix ODS table column names on the first run; every such dependency
 is marked with a "check:" comment.
----------------------------------------------------------------------------*/

%let data_dir = ;
%let out_path = ;

ods graphics off;
ods select none;

/* ---- Input ---------------------------------------------------------------*/

%macro rd(name, rename=);
proc import datafile="&data_dir/&name..csv" out=&name dbms=csv replace;
    guessingrows=32767;
run;
%if %length(&rename) %then %do;
data &name; set &name(rename=(&rename)); run;
%end;
%mend;

%rd(pd_small) %rd(jeffreys_small) %rd(score_small) %rd(score_small_noties)
%rd(clar_small) %rd(lcr_small) %rd(iv_small) %rd(lgd_small)
%rd(migration_small, rename=start=g1 end=g2)
%rd(psi_small) %rd(assoc_small) %rd(somers_small)
%rd(grades_small_initial) %rd(grades_small_current) %rd(entropy_small)
%rd(normal_small) %rd(redelmeier_small)
%rd(pd_large) %rd(lgd_large)
%rd(migration_large, rename=start=g1 end=g2)
%rd(migration_large_initial_counts, rename=count=n0)
%rd(psi_large) %rd(grades_large_initial) %rd(grades_large_current)
%rd(entropy_large) %rd(normal_large)

data levels_abc; length bin $8; do bin = "A", "B", "C"; output; end; run;

/* ---- Result accumulation -------------------------------------------------*/

data results; length case $64 field $64 value 8; stop; run;

%macro emit_ds(ds);
proc append base=results data=&ds(keep=case field value) force; run;
%mend;

%macro emit(case, field, value);
data _e; length case $64 field $64; case="&case"; field="&field"; value=&value; output; run;
%emit_ds(_e)
%mend;

/* ---- Discrimination ------------------------------------------------------*/

/* Somers' D C|R of the y*score table equals 2*AUC-1 with midrank tie credit. */
%macro auc_gini(sfx, ds);
proc freq data=&ds; tables y*score / measures; ods output Measures=_m; run;
data _e; set _m; length case $64 field $64;
    if index(Statistic, "C|R") then do;             /* check: column names Statistic, Value */
        case="roc_auc_&sfx"; field="auc"; value=(Value+1)/2; output;
        case="gini_&sfx"; field="gini"; value=Value; output;
    end;
run;
%emit_ds(_e)
%mend;
%auc_gini(small, score_small)
%auc_gini(large, pd_large)

%macro ks(case, ds);
proc npar1way data=&ds edf; class y; var score; ods output KolSmir2Stats=_k; run;
data _e; set _k; length case $64 field $64; case="&case";
    if Label1="D" then do; field="statistic"; value=nValue1; output; end;      /* check: Label1/nValue1 */
    if index(Label2, "Pr") then do; field="pvalue"; value=nValue2; output; end; /* asymptotic Pr > KSa */
run;
%emit_ds(_e)
%mend;
%ks(ks_small_noties, score_small_noties)
%ks(ks_small_ties, score_small)
%ks(ks_large, pd_large)

/* Minimum over thresholds t of the error rate of "score >= t means default". */
%macro ber(case, ds);
proc sql noprint; select count(*), sum(y=1) into :n, :n1 from &ds; quit;
proc sort data=&ds out=_s; by descending score; run;
data _e; set _s end=eof; by descending score; length case $64 field $64;
    retain fp tp 0 best;
    if _n_=1 then best=&n1/&n;                        /* no obligor flagged */
    if y=1 then tp+1; else fp+1;
    if last.score then do; err=(fp+(&n1-tp))/&n; if err<best then best=err; end;
    if eof then do; case="&case"; field="error"; value=best; output; end;
run;
%emit_ds(_e)
%mend;
%ber(bayesian_error_rate_small, score_small)
%ber(bayesian_error_rate_large, pd_large)

%macro iv(case, ds, binvar, smoothing, levels=);
proc sql; create table _c as select &binvar as bin, sum(y=0) as good, sum(y=1) as bad from &ds group by &binvar; quit;
%if %length(&levels) %then %do;
proc sql; create table _c as select l.bin, coalesce(c.good, 0) as good, coalesce(c.bad, 0) as bad
    from &levels l left join _c c on l.bin=c.bin order by l.bin; quit;
%end;
proc sql; create table _sh as select bin, good, bad,
    (good+&smoothing)/sum(good+&smoothing) as gs, (bad+&smoothing)/sum(bad+&smoothing) as bs from _c; quit;
data _e; set _sh end=eof; length case $64 field $64; retain iv 0; case="&case";
    woe=log(gs/bs); iv+(gs-bs)*woe;
    field=cats("good.", bin); value=good; output;
    field=cats("bad.", bin); value=bad; output;
    field=cats("good_share.", bin); value=gs; output;
    field=cats("bad_share.", bin); value=bs; output;
    field=cats("woe.", bin); value=woe; output;
    if eof then do; field="iv"; value=iv; output; end;
run;
%emit_ds(_e)
%mend;
%iv(information_value_small, iv_small, bin, 0)
%iv(information_value_declared, iv_small, bin, 0.5, levels=levels_abc)
%iv(information_value_large, pd_large, grade, 0.5)

%macro entropy(sfx, ds);
proc sql noprint; select sum(n*rate)/sum(n) into :pbar from &ds; quit;
data _e; set &ds end=eof; length case $64 field $64; retain h1 wsum 0;
    if rate>0 and rate<1 then h=-rate*log(rate)-(1-rate)*log(1-rate); else h=0;
    h1+n*h; wsum+n;
    if eof then do;
        pm=&pbar;
        if pm>0 and pm<1 then h0=-pm*log(pm)-(1-pm)*log(1-pm); else h0=0;
        mi=max(0, h0-h1/wsum);
        case="cier_&sfx"; field="ratio"; value=mi/h0; output;
        case="mutual_information_&sfx"; field="mi"; value=mi; output;
    end;
run;
%emit_ds(_e)
%mend;
%entropy(small, entropy_small)
%entropy(large, entropy_large)

/* VUROCS clar: from the highest grade down, x=P(pred>=t), y=P(pred>=t and real>=t). */
%macro clar(case, ds, pvar, rvar);
proc sql; create table _lv as select distinct &pvar as g from &ds union select distinct &rvar as g from &ds order by g; quit;
data _lv; set _lv; code=_n_; run;
proc sql;
    create table _d as select lp.code as pc, lr.code as rc
        from &ds d inner join _lv lp on d.&pvar=lp.g inner join _lv lr on d.&rvar=lr.g;
    create table _t as select l.code as t, mean(d.pc>=l.code) as x, mean(d.pc>=l.code and d.rc>=l.code) as y
        from _lv l, _d d group by l.code order by t desc;
quit;
data _e; set _t end=eof; length case $64 field $64; retain xp yp area 0;
    area+(x-xp)*(y+yp)/2; xp=x; yp=y;
    if eof then do; case="&case"; field="clar"; value=2*area; output; end;
run;
%emit_ds(_e)
%mend;
%clar(clar_small, clar_small, p, y)
%clar(clar_large, lgd_large, pgrade, rgrade)

/* Trapezoid area of the cumulative loss curve over cumulative exposure, ties pooled. */
%macro capture_area(ds, w, score, loss, mvar);
proc sql noprint; select sum(&w), sum(&loss) into :wt, :lt from &ds; quit;
proc sort data=&ds out=_s; by descending &score; run;
data _null_; set _s end=eof; by descending &score; retain cw cl xp yp area 0;
    cw+&w; cl+&loss;
    if last.&score then do; x=cw/&wt; y=cl/&lt; area+(x-xp)*(y+yp)/2; xp=x; yp=y; end;
    if eof then call symputx("&mvar", area);
run;
%mend;
%macro lcr(case, ds, w, p, y);
data _l; set &ds; loss=&w*&y; run;
%capture_area(_l, &w, &p, loss, am)
%capture_area(_l, &w, &y, loss, ai)
%emit(&case, lcr, (&am-0.5)/(&ai-0.5))
%mend;
%lcr(loss_capture_ratio_small, lcr_small, ead, p, y)
%lcr(loss_capture_ratio_large, lgd_large, ead, predicted, realised)

/* ---- Calibration ---------------------------------------------------------*/

%macro grade_summary(ds);
proc sql; create table _g as select grade, mean(pd) as p, count(*) as n, sum(y) as d from &ds group by grade; quit;
%mend;

%macro emit_grades(case, pvcode);
data _e; set _g; length case $64 field $64; case="&case";
    &pvcode
    field=cats("predicted_pd.", grade); value=p; output;
    field=cats("n.", grade); value=n; output;
    field=cats("defaults.", grade); value=d; output;
    field=cats("default_rate.", grade); value=d/n; output;
    field=cats("p_value.", grade); value=pv; output;
    field=cats("reject.", grade); value=(pv<0.05); output;
run;
%emit_ds(_e)
%mend;

%grade_summary(pd_small)
%emit_grades(binomial_small, %nrstr(if d=0 then pv=1; else pv=sdf("BINOMIAL", d-1, p, n);))
%grade_summary(pd_large)
%emit_grades(binomial_large, %nrstr(if d=0 then pv=1; else pv=sdf("BINOMIAL", d-1, p, n);))
%grade_summary(jeffreys_small)
%emit_grades(jeffreys_small, %nrstr(pv=cdf("BETA", p, d+0.5, n-d+0.5);))
%grade_summary(pd_large)
%emit_grades(jeffreys_large, %nrstr(pv=cdf("BETA", p, d+0.5, n-d+0.5);))

%macro hosmer(case, ds, ddof);
%grade_summary(&ds)
data _e; set _g end=eof; length case $64 field $64; retain q k 0;
    q+(d-n*p)**2/(n*p*(1-p)); k+1;
    if eof then do;
        pv=sdf("CHISQ", q, k-&ddof);
        case="&case"; field="p_value"; value=pv; output; field="reject"; value=(pv<0.05); output;
    end;
run;
%emit_ds(_e)
%mend;
%hosmer(hosmer_small, pd_small, 0)
%hosmer(hosmer_large, pd_large, 0)
%hosmer(hosmer_large_ddof2, pd_large, 2)

%macro spiegelhalter(case, ds);
data _e; set &ds end=eof; length case $64 field $64; retain num var 0;
    num+(y-pd)*(1-2*pd); var+pd*(1-pd)*(1-2*pd)**2;
    if eof then do;
        z=num/sqrt(var);
        case="&case"; field="z"; value=z; output;
        field="reject"; value=(2*sdf("NORMAL", abs(z))<0.05); output;
    end;
run;
%emit_ds(_e)
%mend;
%spiegelhalter(spiegelhalter_small, pd_small)
%spiegelhalter(spiegelhalter_large, pd_large)

%macro brier(case, ds);
proc sql noprint; select mean((y-pd)**2) into :b from &ds; quit;
%emit(&case, brier, &b)
%mend;
%brier(brier_small, pd_small)
%brier(brier_large, pd_large)

%macro redelmeier(case, ds, p1, p2);
data _e; set &ds end=eof; length case $64 field $64; retain num var 0;
    dd=&p1-&p2; ss=&p1+&p2;
    num+dd*(ss-2*y); var+dd**2*ss*(2-ss);
    if eof then do;
        z=num/sqrt(var);
        case="&case"; field="z"; value=z; output;
        field="p_value"; value=2*sdf("NORMAL", abs(z)); output;
    end;
run;
%emit_ds(_e)
%mend;
%redelmeier(redelmeier_small, redelmeier_small, p1, p2)
%redelmeier(redelmeier_large, pd_large, pd, pd2)

/* Basel normal test: the paired t statistic of realised minus predicted, normal tail. */
%macro normal_test(case, ds);
proc ttest data=&ds; paired realised*predicted; ods output TTests=_t Statistics=_st; run;
data _e; merge _t(keep=tValue) _st(keep=Mean); length case $64 field $64; case="&case"; /* check: tValue, Mean */
    pv=sdf("NORMAL", tValue);
    field="estimate"; value=Mean; output;
    field="z"; value=tValue; output;
    field="p_value"; value=pv; output;
    field="reject"; value=(pv<0.05); output;
run;
%emit_ds(_e)
%mend;
%normal_test(normal_test_small, normal_small)
%normal_test(normal_test_large, normal_large)

/* ---- Association ---------------------------------------------------------*/

/* PROC CORR ODS tables hold one row per variable with the partner's coefficient
   in a column named after the partner and its p-value in P<partner>. check: names */
%macro corr(case, ds, a, b, type, table, field);
proc corr data=&ds &type; var &a &b; ods output &table=_c; run;
data _e; set _c; where Variable="&a"; length case $64 field $64; case="&case";
    field="&field"; value=&b; output;
    field="p_value"; value=P&b; output;
run;
%emit_ds(_e)
%mend;
%corr(kendall_small, assoc_small, x, y, kendall, KendallCorr, tau)
%corr(kendall_large, lgd_large, predicted, realised, kendall, KendallCorr, tau)
%corr(spearman_small, assoc_small, x, y, spearman, SpearmanCorr, rho)
%corr(spearman_large, lgd_large, predicted, realised, spearman, SpearmanCorr, rho)
%corr(pearson_small, assoc_small, x, y, pearson, PearsonCorr, r)
%corr(pearson_large, lgd_large, predicted, realised, pearson, PearsonCorr, r)

/* PROC FREQ measures: Stuart's tau-c and Somers' D C|R = D(column | row). */
%macro freq_measure(case, ds, a, b, pattern, field);
proc freq data=&ds; tables &a*&b / measures; ods output Measures=_m; run;
data _e; set _m; length case $64 field $64;
    if index(Statistic, "&pattern") then do; case="&case"; field="&field"; value=Value; output; end;
run;
%emit_ds(_e)
%mend;
%freq_measure(kendall_large_tau_c, lgd_large, pgrade, rgrade, Tau-c, tau)
%freq_measure(somersd_small_table, somers_small, x, y, C|R, d)
%freq_measure(somersd_large, lgd_large, pgrade, rgrade, C|R, d)

/* ---- Stability -----------------------------------------------------------*/

%macro hhi(case, ds, levels=);
proc sql; create table _c as select grade as bin, count(*) as n from &ds group by grade; quit;
%if %length(&levels) %then %do;
proc sql; create table _c as select l.bin, coalesce(c.n, 0) as n from &levels l left join _c c on l.bin=c.bin order by l.bin; quit;
%end;
proc sql noprint; select count(*), sum(n) into :k, :tot from _c; quit;
data _e; set _c end=eof; length case $64 field $64; retain ss cv 0;
    s=n/&tot; ss+s**2; cv+(s-1/&k)**2;
    if eof then do; case="&case"; field="cv"; value=sqrt(&k*cv); output; field="hhi"; value=ss; output; end;
run;
%emit_ds(_e)
%mend;
%hhi(herfindahl_small, grades_small_initial)
%hhi(herfindahl_declared, grades_small_initial, levels=levels_abc)
%hhi(herfindahl_large, grades_large_initial)

%macro hhi_multi(case, initial, current);
data _both; set &initial(in=a) &current; length period $8; if a then period="initial"; else period="current"; run;
proc freq data=_both; tables grade*period / sparse out=_c(drop=percent); run;
proc sql;
    create table _n as select grade, sum(count*(period="initial")) as n1, sum(count*(period="current")) as n2
        from _c group by grade order by grade;
    select count(*), sum(n1), sum(n2) into :k, :t1, :t2 from _n;
quit;
data _e; set _n end=eof; length case $64 field $64; case="&case"; retain ss1 ss2 cv1 cv2 0;
    s1=n1/&t1; s2=n2/&t2; ss1+s1**2; ss2+s2**2; cv1+(s1-1/&k)**2; cv2+(s2-1/&k)**2;
    field=cats("n_initial.", grade); value=n1; output;
    field=cats("n_current.", grade); value=n2; output;
    if eof then do;
        c1=sqrt(&k*cv1); c2=sqrt(&k*cv2);
        z=sqrt(&k-1)*(c2-c1)/sqrt(c2**2*(0.5+c2**2)); pv=sdf("NORMAL", z);
        field="h_initial"; value=ss1; output; field="h_current"; value=ss2; output;
        field="z"; value=z; output; field="p_value"; value=pv; output; field="reject"; value=(pv<0.05); output;
    end;
run;
%emit_ds(_e)
%mend;
%hhi_multi(herfindahl_multi_small, grades_small_initial, grades_small_current)
%hhi_multi(herfindahl_multi_large, grades_large_initial, grades_large_current)

%macro psi(case, ds, smoothing, levels=);
proc freq data=&ds; tables bin*period / sparse out=_c(drop=percent); run;
proc sql; create table _n as select bin, sum(count*(period="old")) as e, sum(count*(period="new")) as a from _c group by bin; quit;
%if %length(&levels) %then %do;
proc sql; create table _n as select l.bin, coalesce(c.e, 0) as e, coalesce(c.a, 0) as a from &levels l left join _n c on l.bin=c.bin order by l.bin; quit;
%end;
proc sql; create table _sh as select bin, (e+&smoothing)/sum(e+&smoothing) as es, (a+&smoothing)/sum(a+&smoothing) as as_ from _n; quit;
data _e; set _sh end=eof; length case $64 field $64; case="&case"; retain psi 0;
    psi+(as_-es)*log(as_/es);
    field=cats("expected.", bin); value=es; output;
    field=cats("actual.", bin); value=as_; output;
    if eof then do; field="psi"; value=psi; output; end;
run;
%emit_ds(_e)
%mend;
%psi(psi_small, psi_small, 0)
%psi(psi_declared, psi_small, 0.5, levels=levels_abc)
%psi(psi_large, psi_large, 0.5)

/* Square migration count table on the ordered union of grades, zero cells included. */
%macro migration_cells(ds);
proc sql; create table _lv as select distinct g1 as g from &ds union select distinct g2 as g from &ds order by g; quit;
data _lv; set _lv; code=_n_; run;
proc sql;
    create table _cnt as select g1, g2, count(*) as cnt from &ds group by g1, g2;
    create table _grid as select l1.code as i, l2.code as j, l1.g as gi, l2.g as gj from _lv l1, _lv l2;
    create table _cells as select g.i, g.j, g.gi, g.gj, coalesce(c.cnt, 0) as cnt
        from _grid g left join _cnt c on g.gi=c.g1 and g.gj=c.g2 order by i, j;
    select count(*) into :k from _lv;
quit;
%mend;

%macro bandwidth(case, ds);
%migration_cells(&ds)
data _e; set _cells end=eof; length case $64 field $64; retain un ud ln ld 0;
    i0=i-1; j0=j-1; dist=abs(i0-j0); mx=max(i0, &k-1-i0);
    if j0>i0 then do; un+cnt*dist; ud+cnt*mx; end;
    else if j0<i0 then do; ln+cnt*dist; ld+cnt*mx; end;
    if eof then do;
        case="&case";
        field="upper"; if ud>0 then value=un/ud; else value=0; output;
        field="lower"; if ld>0 then value=ln/ld; else value=0; output;
    end;
run;
%emit_ds(_e)
%mend;
%bandwidth(migration_bandwidth_small, migration_small)
%bandwidth(migration_bandwidth_large, migration_large)

%macro stability(case, ds, initial=);
%migration_cells(&ds)
%if %length(&initial) %then %do;
proc sql; create table _rt as select l.code as i, ic.n0 as tot from _lv l inner join &initial ic on l.g=ic.grade; quit;
%end;
%else %do;
proc sql; create table _rt as select i, sum(cnt) as tot from _cells group by i; quit;
%end;
proc sql;
    create table _p as select c.i, c.j, c.gi, c.gj, r.tot, case when r.tot>0 then c.cnt/r.tot else . end as p
        from _cells c inner join _rt r on c.i=r.i;
    create table _z as select a.i, a.j, a.gi, a.gj, a.tot, a.p as far, b.p as near
        from _p a inner join _p b on a.i=b.i and b.j=(case when a.j<a.i then a.j+1 else a.j-1 end)
        where a.i ne a.j order by a.i, a.j;
quit;
data _e; set _z; length case $64 field $64; case="&case"; z=.; cdfv=.;
    if tot>0 then do;
        v=(far*(1-far)+near*(1-near)+2*far*near)/tot;
        if v>0 then do; z=(near-far)/sqrt(v); cdfv=cdf("NORMAL", z); end;
    end;
    field=cats("z.", gi, ".", gj); value=z; output;
    field=cats("cdf.", gi, ".", gj); value=cdfv; output;
run;
%emit_ds(_e)
%mend;
%stability(migration_stability_small, migration_small)
%stability(migration_stability_large, migration_large)
%stability(migration_stability_large_initial_counts, migration_large, initial=migration_large_initial_counts)

/* ---- LGD validation ------------------------------------------------------*/

/* Paired t test of realised minus predicted; SIDES=U is the one-sided
   underestimation alternative, SIDES=2 the two-sided ELBE test. check: column names */
%macro paired(case, ds, sides, by=);
%if %length(&by) %then %do; proc sort data=&ds out=_s; by &by; run; %end;
%else %do; data _s; set &ds; run; %end;
proc ttest data=_s sides=&sides;
    %if %length(&by) %then %do; by &by; %end;
    paired realised*predicted;
    ods output TTests=_t Statistics=_st;
run;
proc sql; create table _mn as select %if %length(&by) %then &by,; mean(realised) as rm, mean(predicted) as pm from _s
    %if %length(&by) %then group by &by;; quit;
data _e; merge _t(keep=%if %length(&by) %then &by; tValue Probt) _st(keep=%if %length(&by) %then &by; N Mean StdDev) _mn;
    %if %length(&by) %then %do; by &by; %end;
    length case $64 field $64 lbl $32; case="&case";
    %if %length(&by) %then %do; lbl=&by; %end; %else %do; lbl="portfolio"; %end;
    field=cats("n.", lbl); value=N; output;
    field=cats("realised_mean.", lbl); value=rm; output;
    field=cats("pred_mean.", lbl); value=pm; output;
    field=cats("s2.", lbl); value=StdDev**2; output;
    field=cats("mean_error.", lbl); value=Mean; output;
    field=cats("t.", lbl); value=tValue; output;
    field=cats("p_value.", lbl); value=Probt; output;
run;
%emit_ds(_e)
%mend;
%paired(lgd_t_test_portfolio_small, lgd_small, U)
%paired(lgd_t_test_segment_small, lgd_small, U, by=segment)
%paired(lgd_t_test_portfolio_large, lgd_large, U)
%paired(lgd_t_test_segment_large, lgd_large, U, by=segment)

%macro elbe(case, ds);
proc ttest data=&ds sides=2; paired realised*predicted; ods output TTests=_t Statistics=_st; run;
proc sql noprint; select count(*), mean(realised), mean(predicted) into :n, :rm, :pm from &ds; quit;
data _e; merge _t(keep=tValue Probt) _st(keep=N); length case $64 field $64; case="&case";
    field="facilities"; value=N; output;
    field="lgd_mean"; value=&rm; output;
    field="elbe_mean"; value=&pm; output;
    field="t"; value=tValue; output;
    field="p_value"; value=Probt; output;
run;
%emit_ds(_e)
%mend;
%elbe(elbe_t_test_small, lgd_small)
%elbe(elbe_t_test_large, lgd_large)

%macro loss(sfx, ds);
proc sql noprint;
    select 1-sum(ead*predicted)/sum(ead*realised), sum(ead*abs(realised-predicted))/sum(ead) into :ls, :mad from &ds;
quit;
%emit(loss_shortfall_&sfx, shortfall, &ls)
%emit(mean_absolute_deviation_&sfx, mad, &mad)
%mend;
%loss(small, lgd_small)
%loss(large, lgd_large)

/* ---- Output --------------------------------------------------------------*/

ods select all;

data meta; length language $16 version $64 generated $10 platform $32;
    language="sas"; version="&sysvlong"; generated=put(today(), yymmdd10.); platform="&sysscp";
run;

proc json out="&out_path" pretty;
    export meta;
    export results;
run;
