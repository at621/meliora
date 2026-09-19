function oracle(data_dir, out_path)
% MATLAB oracle for the Meliora cross-language comparison.
%
%   matlab -batch "oracle('tests/oracles/data', 'tests/oracles/matlab/results.json')"
%
% Reads the CSV datasets written by tests/oracles/cases.py, computes every case
% with MATLAB (Statistics and Machine Learning Toolbox functions where they
% exist, hand formulas from the book, Basel working paper 14 and the ECB
% validation instructions otherwise) and writes the long (case, field, value)
% records compared by tests/test_cross_language.py. Written for R2021a.

records = struct('case', {}, 'field', {}, 'value', {});

    function emit(c, f, v)
        records(end + 1) = struct('case', char(c), 'field', char(f), 'value', v);
    end

    function emit_named(c, f, labels, values)
        for k = 1:numel(values)
            emit(c, sprintf('%s.%s', f, label_text(labels(k))), values(k));
        end
    end

    function t = rd(name)
        t = readtable(fullfile(data_dir, [name '.csv']), 'TextType', 'string', 'VariableNamingRule', 'preserve');
    end

% --- Discrimination ---------------------------------------------------------

names = {'small', 'large'};
for ix = 1:2
    if ix == 1, tbl = rd('score_small'); else, tbl = rd('pd_large'); end
    [~, ~, ~, auc_value] = perfcurve(tbl.y, tbl.score, 1);
    emit(['roc_auc_' names{ix}], 'auc', auc_value);
    emit(['gini_' names{ix}], 'gini', 2 * auc_value - 1);
end

ks('ks_small_noties', rd('score_small_noties'));
ks('ks_small_ties', rd('score_small'));
ks('ks_large', rd('pd_large'));
    function ks(c, f)
        [~, p, d] = kstest2(f.score(f.y == 0), f.score(f.y == 1));
        emit(c, 'statistic', d);
        emit(c, 'pvalue', p);
    end

emit('bayesian_error_rate_small', 'error', ber(rd('score_small')));
emit('bayesian_error_rate_large', 'error', ber(rd('pd_large')));
    function e = ber(f)
        thresholds = [unique(f.score); Inf];
        e = min(arrayfun(@(t) mean((f.score >= t) ~= (f.y == 1)), thresholds));
    end

tbl = rd('iv_small');
iv('information_value_small', tbl.bin, tbl.y, 0, unique(tbl.bin));
iv('information_value_declared', tbl.bin, tbl.y, 0.5, ["A" "B" "C"]);
tbl = rd('pd_large');
iv('information_value_large', tbl.grade, tbl.y, 0.5, unique(tbl.grade));
    function iv(c, bins, y, smoothing, levels)
        cat = categorical(bins, levels);
        good = countcats(cat(y == 0));
        bad = countcats(cat(y == 1));
        gs = (good + smoothing) / sum(good + smoothing);
        bs = (bad + smoothing) / sum(bad + smoothing);
        woe = log(gs ./ bs);
        emit_named(c, 'good', levels, good);
        emit_named(c, 'bad', levels, bad);
        emit_named(c, 'good_share', levels, gs);
        emit_named(c, 'bad_share', levels, bs);
        emit_named(c, 'woe', levels, woe);
        emit(c, 'iv', sum((gs - bs) .* woe));
    end

entropy('small', rd('entropy_small'));
entropy('large', rd('entropy_large'));
    function entropy(suffix, f)
        w = f.n / sum(f.n);
        h0 = binary_entropy(sum(w .* f.rate));
        h1 = sum(w .* binary_entropy(f.rate));
        emit(['cier_' suffix], 'ratio', max(0, h0 - h1) / h0);
        emit(['mutual_information_' suffix], 'mi', max(0, h0 - h1));
    end

tbl = rd('clar_small');
emit('clar_small', 'clar', clar(tbl.p, tbl.y));
tbl = rd('lgd_large');
emit('clar_large', 'clar', clar(tbl.pgrade, tbl.rgrade));
    function v = clar(pred, real)
        % VUROCS clar: thresholds from the highest grade down, x = P(pred >= t),
        % y = P(pred >= t and real >= t), twice the trapezoid area from (0, 0).
        levels = unique([pred; real]);
        [~, p] = ismember(pred, levels);
        [~, r] = ismember(real, levels);
        x = 0; y = 0;
        for t = numel(levels):-1:1
            x(end + 1) = mean(p >= t); %#ok<AGROW>
            y(end + 1) = mean(p >= t & r >= t); %#ok<AGROW>
        end
        v = 2 * sum(diff(x) .* (y(1:end - 1) + y(2:end)) / 2);
    end

tbl = rd('lcr_small');
emit('loss_capture_ratio_small', 'lcr', lcr(tbl.ead, tbl.p, tbl.y));
tbl = rd('lgd_large');
emit('loss_capture_ratio_large', 'lcr', lcr(tbl.ead, tbl.predicted, tbl.realised));
    function a = capture_area(w, score, loss)
        [~, ~, gi] = unique(score);
        wg = accumarray(gi, w);
        lg = accumarray(gi, loss);
        x = [0; cumsum(flipud(wg)) / sum(w)];
        y = [0; cumsum(flipud(lg)) / sum(loss)];
        a = sum(diff(x) .* (y(1:end - 1) + y(2:end)) / 2);
    end
    function v = lcr(w, p, y)
        loss = w .* y;
        v = (capture_area(w, p, loss) - 0.5) / (capture_area(w, y, loss) - 0.5);
    end

% --- Calibration ------------------------------------------------------------

for ix = 1:2
    if ix == 1, tbl = rd('pd_small'); else, tbl = rd('pd_large'); end
    [gr, pp, nn, dd] = grade_summary(tbl);
    emit_grades(['binomial_' names{ix}], gr, pp, nn, dd, binocdf(dd - 1, nn, pp, 'upper'));
    if ix == 1, tbl = rd('jeffreys_small'); end
    [gr, pp, nn, dd] = grade_summary(tbl);
    emit_grades(['jeffreys_' names{ix}], gr, pp, nn, dd, betacdf(pp, dd + 0.5, nn - dd + 0.5));
end
    function [g, p, n, d] = grade_summary(f)
        [g, ~, gi] = unique(f.grade);
        p = accumarray(gi, f.pd, [], @mean);
        n = accumarray(gi, 1);
        d = accumarray(gi, f.y);
    end
    function emit_grades(c, g, p, n, d, p_value)
        emit_named(c, 'predicted_pd', g, p);
        emit_named(c, 'n', g, n);
        emit_named(c, 'defaults', g, d);
        emit_named(c, 'default_rate', g, d ./ n);
        emit_named(c, 'p_value', g, p_value);
        emit_named(c, 'reject', g, p_value < 0.05);
    end

hosmer('hosmer_small', rd('pd_small'), 0);
hosmer('hosmer_large', rd('pd_large'), 0);
hosmer('hosmer_large_ddof2', rd('pd_large'), 2);
    function hosmer(c, f, ddof)
        [~, p, n, d] = grade_summary(f);
        q = sum((d - n .* p) .^ 2 ./ (n .* p .* (1 - p)));
        p_value = chi2cdf(q, numel(p) - ddof, 'upper');
        emit(c, 'p_value', p_value);
        emit(c, 'reject', p_value < 0.05);
    end

spiegelhalter('spiegelhalter_small', rd('pd_small'));
spiegelhalter('spiegelhalter_large', rd('pd_large'));
    function spiegelhalter(c, f)
        p = f.pd;
        z = sum((f.y - p) .* (1 - 2 * p)) / sqrt(sum(p .* (1 - p) .* (1 - 2 * p) .^ 2));
        emit(c, 'z', z);
        emit(c, 'reject', 2 * normcdf(-abs(z)) < 0.05);
    end

tbl = rd('pd_small');
emit('brier_small', 'brier', mean((tbl.y - tbl.pd) .^ 2));
tbl = rd('pd_large');
emit('brier_large', 'brier', mean((tbl.y - tbl.pd) .^ 2));

tbl = rd('redelmeier_small');
redelmeier('redelmeier_small', tbl.y, tbl.p1, tbl.p2);
tbl = rd('pd_large');
redelmeier('redelmeier_large', tbl.y, tbl.pd, tbl.pd2);
    function redelmeier(c, y, p1, p2)
        d = p1 - p2;
        s = p1 + p2;
        z = sum(d .* (s - 2 * y)) / sqrt(sum(d .^ 2 .* s .* (2 - s)));
        emit(c, 'z', z);
        emit(c, 'p_value', 2 * normcdf(-abs(z)));
    end

normal_test('normal_test_small', rd('normal_small'));
normal_test('normal_test_large', rd('normal_large'));
    function normal_test(c, f)
        [~, ~, ~, st] = ttest(f.realised, f.predicted, 'Tail', 'right');
        p_value = normcdf(-st.tstat);
        emit(c, 'estimate', mean(f.realised - f.predicted));
        emit(c, 'z', st.tstat);
        emit(c, 'p_value', p_value);
        emit(c, 'reject', p_value < 0.05);
    end

% --- Association ------------------------------------------------------------

tbl = rd('assoc_small');
[tau, pv] = corr(tbl.x, tbl.y, 'type', 'Kendall');
emit('kendall_small', 'tau', tau);
emit('kendall_small', 'p_value', pv);
tbl = rd('lgd_large');
[tau, pv] = corr(tbl.predicted, tbl.realised, 'type', 'Kendall');
emit('kendall_large', 'tau', tau);
emit('kendall_large', 'p_value', pv);
emit('kendall_large_tau_c', 'tau', tau_c(tbl.pgrade, tbl.rgrade));
    function [cd, untied_x] = concordance(x, y)
        % Sum over pairs of sign(dx) * sign(dy) and the number of pairs untied on x.
        n = numel(x);
        cd = 0;
        untied_x = 0;
        for i = 1:n - 1
            sx = sign(x(i) - x(i + 1:n));
            sy = sign(y(i) - y(i + 1:n));
            cd = cd + sum(sx .* sy);
            untied_x = untied_x + sum(sx ~= 0);
        end
    end
    function v = tau_c(x, y)
        n = numel(x);
        m = min(numel(unique(x)), numel(unique(y)));
        cd = concordance(x, y);
        v = 2 * m * cd / (n ^ 2 * (m - 1));
    end
    function v = somers_d(x, y)
        [cd, untied_x] = concordance(x, y);
        v = cd / untied_x;
    end

tbl = rd('somers_small');
emit('somersd_small_table', 'd', somers_d(tbl.x, tbl.y));
tbl = rd('lgd_large');
emit('somersd_large', 'd', somers_d(tbl.pgrade, tbl.rgrade));

tbl = rd('assoc_small');
[rho, pv] = corr(tbl.x, tbl.y, 'type', 'Spearman');
emit('spearman_small', 'rho', rho);
emit('spearman_small', 'p_value', pv);
[rr, pv] = corr(tbl.x, tbl.y, 'type', 'Pearson');
emit('pearson_small', 'r', rr);
emit('pearson_small', 'p_value', pv);
tbl = rd('lgd_large');
[rho, pv] = corr(tbl.predicted, tbl.realised, 'type', 'Spearman');
emit('spearman_large', 'rho', rho);
emit('spearman_large', 'p_value', pv);
[rr, pv] = corr(tbl.predicted, tbl.realised, 'type', 'Pearson');
emit('pearson_large', 'r', rr);
emit('pearson_large', 'p_value', pv);

% --- Stability --------------------------------------------------------------

hhi('herfindahl_small', rd('grades_small_initial'), []);
hhi('herfindahl_declared', rd('grades_small_initial'), ["A" "B" "C"]);
hhi('herfindahl_large', rd('grades_large_initial'), []);
    function [cv, h] = concentration(counts)
        s = counts / sum(counts);
        k = numel(s);
        cv = sqrt(k * sum((s - 1 / k) .^ 2));
        h = sum(s .^ 2);
    end
    function hhi(c, f, levels)
        if isempty(levels), levels = unique(f.grade); end
        [cv, h] = concentration(countcats(categorical(f.grade, levels)));
        emit(c, 'cv', cv);
        emit(c, 'hhi', h);
    end

hhi_multi('herfindahl_multi_small', rd('grades_small_initial'), rd('grades_small_current'));
hhi_multi('herfindahl_multi_large', rd('grades_large_initial'), rd('grades_large_current'));
    function hhi_multi(c, initial, current)
        levels = unique([initial.grade; current.grade]);
        n1 = countcats(categorical(initial.grade, levels));
        n2 = countcats(categorical(current.grade, levels));
        [c1, h1] = concentration(n1);
        [c2, h2] = concentration(n2);
        z = sqrt(numel(levels) - 1) * (c2 - c1) / sqrt(c2 ^ 2 * (0.5 + c2 ^ 2));
        p_value = normcdf(-z);
        emit_named(c, 'n_initial', levels, n1);
        emit_named(c, 'n_current', levels, n2);
        emit(c, 'h_initial', h1);
        emit(c, 'h_current', h2);
        emit(c, 'z', z);
        emit(c, 'p_value', p_value);
        emit(c, 'reject', p_value < 0.05);
    end

psi('psi_small', rd('psi_small'), 0, []);
psi('psi_declared', rd('psi_small'), 0.5, ["A" "B" "C"]);
psi('psi_large', rd('psi_large'), 0.5, []);
    function psi(c, f, smoothing, levels)
        if isempty(levels), levels = unique(f.bin); end
        cat = categorical(f.bin, levels);
        e = countcats(cat(f.period == "old")) + smoothing;
        a = countcats(cat(f.period == "new")) + smoothing;
        e = e / sum(e);
        a = a / sum(a);
        emit_named(c, 'expected', levels, e);
        emit_named(c, 'actual', levels, a);
        emit(c, 'psi', sum((a - e) .* log(a ./ e)));
    end

bandwidth('migration_bandwidth_small', rd('migration_small'));
bandwidth('migration_bandwidth_large', rd('migration_large'));
    function [counts, levels] = migration_counts(f)
        levels = unique([f.("start"); f.("end")]);
        [~, i] = ismember(f.("start"), levels);
        [~, j] = ismember(f.("end"), levels);
        counts = accumarray([i j], 1, [numel(levels) numel(levels)]);
    end
    function bandwidth(c, f)
        counts = migration_counts(f);
        k = size(counts, 1);
        [i, j] = ndgrid(0:k - 1, 0:k - 1);
        distance = abs(i - j);
        maximum = max(i, k - 1 - i);
        emit(c, 'upper', side(j > i));
        emit(c, 'lower', side(j < i));
        function v = side(mask)
            denominator = sum(counts(mask) .* maximum(mask));
            if denominator > 0
                v = sum(counts(mask) .* distance(mask)) / denominator;
            else
                v = 0;
            end
        end
    end

stability('migration_stability_small', rd('migration_small'), []);
stability('migration_stability_large', rd('migration_large'), []);
ic = rd('migration_large_initial_counts');
stability('migration_stability_large_initial_counts', rd('migration_large'), ic);
    function stability(c, f, initial)
        [counts, levels] = migration_counts(f);
        totals = sum(counts, 2);
        if ~isempty(initial)
            [~, pos] = ismember(levels, initial.grade);
            totals = initial.count(pos);
        end
        k = numel(levels);
        for i = 1:k
            n = totals(i);
            for j = 1:k
                if i == j, continue; end
                z = NaN;
                if n > 0
                    p = counts(i, :) / n;
                    far = p(j);
                    if j < i, near = p(j + 1); else, near = p(j - 1); end
                    variance = (far * (1 - far) + near * (1 - near) + 2 * far * near) / n;
                    if variance > 0, z = (near - far) / sqrt(variance); end
                end
                key = sprintf('%s.%s', label_text(levels(i)), label_text(levels(j)));
                emit(c, ['z.' key], z);
                if isnan(z), cdf = NaN; else, cdf = normcdf(z); end
                emit(c, ['cdf.' key], cdf);
            end
        end
    end

% --- LGD validation ---------------------------------------------------------

for ix = 1:2
    tbl = rd(['lgd_' names{ix}]);
    paired(['lgd_t_test_portfolio_' names{ix}], 'portfolio', tbl.realised, tbl.predicted, 'right');
    segments = unique(tbl.segment, 'stable');
    for si = 1:numel(segments)
        rows = tbl.segment == segments(si);
        paired(['lgd_t_test_segment_' names{ix}], segments(si), tbl.realised(rows), tbl.predicted(rows), 'right');
    end
    [~, pv, ~, stt] = ttest(tbl.realised, tbl.predicted, 'Tail', 'both');
    cname = ['elbe_t_test_' names{ix}];
    emit(cname, 'facilities', height(tbl));
    emit(cname, 'lgd_mean', mean(tbl.realised));
    emit(cname, 'elbe_mean', mean(tbl.predicted));
    emit(cname, 't', stt.tstat);
    emit(cname, 'p_value', pv);
    emit(['loss_shortfall_' names{ix}], 'shortfall', 1 - sum(tbl.ead .* tbl.predicted) / sum(tbl.ead .* tbl.realised));
    emit(['mean_absolute_deviation_' names{ix}], 'mad', sum(tbl.ead .* abs(tbl.realised - tbl.predicted)) / sum(tbl.ead));
end
    function paired(c, label, realised, predicted, tail)
        [~, p, ~, st] = ttest(realised, predicted, 'Tail', tail);
        e = realised - predicted;
        label = label_text(label);
        emit(c, ['n.' label], numel(e));
        emit(c, ['realised_mean.' label], mean(realised));
        emit(c, ['pred_mean.' label], mean(predicted));
        emit(c, ['s2.' label], var(e));
        emit(c, ['mean_error.' label], mean(e));
        emit(c, ['t.' label], st.tstat);
        emit(c, ['p_value.' label], p);
    end

% --- Output -----------------------------------------------------------------

toolboxes = ver;
packages = struct();
for ix = 1:numel(toolboxes)
    if any(strcmp(toolboxes(ix).Name, {'MATLAB', 'Statistics and Machine Learning Toolbox', 'Risk Management Toolbox', 'Financial Toolbox'}))
        packages.(matlab.lang.makeValidName(toolboxes(ix).Name)) = toolboxes(ix).Version;
    end
end
meta = struct('language', 'matlab', 'version', version, 'packages', packages, ...
    'generated', datestr(now, 'yyyy-mm-dd'), 'platform', computer);
fid = fopen(out_path, 'w');
fwrite(fid, jsonencode(struct('meta', meta, 'results', records)), 'char');
fclose(fid);
fprintf('%d records -> %s\n', numel(records), out_path);
end

function h = binary_entropy(p)
h = zeros(size(p));
inside = p > 0 & p < 1;
q = p(inside);
h(inside) = -q .* log(q) - (1 - q) .* log(1 - q);
end

function s = label_text(label)
if isnumeric(label)
    s = num2str(label);
else
    s = char(string(label));
end
end
