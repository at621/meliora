#!/usr/bin/env Rscript
# R oracle for the Meliora cross-language comparison.
#
# Usage: Rscript --vanilla oracle.R <data_dir> <results.json>
#
# Reads the CSV datasets written by tests/oracles/cases.py, computes every case
# with R (base stats plus pROC and DescTools where a library implementation
# exists) and writes the long (case, field, value) records that
# tests/test_cross_language.py compares against Meliora. Hand formulas follow
# the book, the Basel working paper 14 and the ECB validation instructions
# rather than Meliora's source, so they are an independent re-implementation.

suppressPackageStartupMessages({
  library(jsonlite)
  library(pROC)
  library(DescTools)
})

args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("usage: oracle.R <data_dir> <results.json>")
data_dir <- args[1]
out_path <- args[2]

rd <- function(name) read.csv(file.path(data_dir, paste0(name, ".csv")), stringsAsFactors = FALSE)

records <- list()
emit <- function(case, field, value) {
  records[[length(records) + 1]] <<- data.frame(case = case, field = field, value = as.numeric(value))
}
emit_named <- function(case, field, values) {
  for (label in names(values)) emit(case, paste0(field, ".", label), values[[label]])
}

h <- function(p) ifelse(p <= 0 | p >= 1, 0, -p * log(p) - (1 - p) * log(1 - p))

# --- Discrimination ---------------------------------------------------------

auc_of <- function(frame) as.numeric(pROC::auc(pROC::roc(frame$y, frame$score, quiet = TRUE, direction = "<")))
for (nm in c("small", "large")) {
  frame <- rd(if (nm == "small") "score_small" else "pd_large")
  a <- auc_of(frame)
  emit(paste0("roc_auc_", nm), "auc", a)
  emit(paste0("gini_", nm), "gini", 2 * a - 1)
}

ks <- function(case, frame) {
  s0 <- frame$score[frame$y == 0]
  s1 <- frame$score[frame$y == 1]
  exact <- !any(duplicated(c(s0, s1)))
  result <- suppressWarnings(ks.test(s0, s1, exact = exact))
  emit(case, "statistic", result$statistic)
  emit(case, "pvalue", result$p.value)
}
ks("ks_small_noties", rd("score_small_noties"))
ks("ks_small_ties", rd("score_small"))
ks("ks_large", rd("pd_large"))

ber <- function(frame) {
  thresholds <- c(sort(unique(frame$score)), Inf)
  min(sapply(thresholds, function(t) mean((frame$score >= t) != (frame$y == 1))))
}
emit("bayesian_error_rate_small", "error", ber(rd("score_small")))
emit("bayesian_error_rate_large", "error", ber(rd("pd_large")))

iv <- function(case, bins, y, smoothing, levels = sort(unique(bins))) {
  counts <- table(factor(bins, levels = levels), factor(y, levels = c(0, 1)))
  good <- counts[, 1] + smoothing
  bad <- counts[, 2] + smoothing
  gs <- good / sum(good)
  bs <- bad / sum(bad)
  woe <- log(gs / bs)
  emit_named(case, "good", counts[, 1])
  emit_named(case, "bad", counts[, 2])
  emit_named(case, "good_share", gs)
  emit_named(case, "bad_share", bs)
  emit_named(case, "woe", woe)
  emit(case, "iv", sum((gs - bs) * woe))
}
f <- rd("iv_small")
iv("information_value_small", f$bin, f$y, 0)
iv("information_value_declared", f$bin, f$y, 0.5, levels = c("A", "B", "C"))
f <- rd("pd_large")
iv("information_value_large", f$grade, f$y, 0.5)

entropy <- function(case_prefix, frame) {
  w <- frame$n / sum(frame$n)
  h0 <- h(sum(w * frame$rate))
  h1 <- sum(w * h(frame$rate))
  emit(paste0("cier_", case_prefix), "ratio", max(0, h0 - h1) / h0)
  emit(paste0("mutual_information_", case_prefix), "mi", max(0, h0 - h1))
}
entropy("small", rd("entropy_small"))
entropy("large", rd("entropy_large"))

# Cumulative LGD accuracy ratio, VUROCS clar convention: at each threshold from
# the highest grade downwards, x = P(pred >= t), y = P(pred >= t & real >= t).
clar <- function(pred, real) {
  levels <- sort(unique(c(pred, real)))
  p <- match(pred, levels)
  r <- match(real, levels)
  x <- 0
  y <- 0
  for (t in rev(seq_along(levels))) {
    x <- c(x, mean(p >= t))
    y <- c(y, mean(p >= t & r >= t))
  }
  2 * sum(diff(x) * (head(y, -1) + tail(y, -1)) / 2)
}
f <- rd("clar_small")
emit("clar_small", "clar", clar(f$p, f$y))
f <- rd("lgd_large")
emit("clar_large", "clar", clar(f$pgrade, f$rgrade))

capture_area <- function(w, score, loss) {
  g <- aggregate(cbind(w, loss) ~ score, FUN = sum)
  g <- g[order(-g$score), ]
  x <- c(0, cumsum(g$w) / sum(w))
  y <- c(0, cumsum(g$loss) / sum(loss))
  sum(diff(x) * (head(y, -1) + tail(y, -1)) / 2)
}
lcr <- function(w, p, y) {
  loss <- w * y
  (capture_area(w, p, loss) - 0.5) / (capture_area(w, y, loss) - 0.5)
}
f <- rd("lcr_small")
emit("loss_capture_ratio_small", "lcr", lcr(f$ead, f$p, f$y))
f <- rd("lgd_large")
emit("loss_capture_ratio_large", "lcr", lcr(f$ead, f$predicted, f$realised))

# --- Calibration ------------------------------------------------------------

grade_summary <- function(frame) {
  g <- split(frame, frame$grade)
  data.frame(
    grade = names(g),
    p = sapply(g, function(s) mean(s$pd)),
    n = sapply(g, nrow),
    d = sapply(g, function(s) sum(s$y)),
    stringsAsFactors = FALSE
  )
}
emit_grades <- function(case, s, p_value, alpha = 0.05) {
  names(p_value) <- s$grade
  emit_named(case, "predicted_pd", setNames(s$p, s$grade))
  emit_named(case, "n", setNames(s$n, s$grade))
  emit_named(case, "defaults", setNames(s$d, s$grade))
  emit_named(case, "default_rate", setNames(s$d / s$n, s$grade))
  emit_named(case, "p_value", p_value)
  emit_named(case, "reject", p_value < alpha)
}
for (nm in c("small", "large")) {
  frame <- rd(if (nm == "small") "pd_small" else "pd_large")
  s <- grade_summary(frame)
  binom <- mapply(function(d, n, p) binom.test(d, n, p, alternative = "greater")$p.value, s$d, s$n, s$p)
  emit_grades(paste0("binomial_", nm), s, binom)
  frame <- rd(if (nm == "small") "jeffreys_small" else "pd_large")
  s <- grade_summary(frame)
  emit_grades(paste0("jeffreys_", nm), s, pbeta(s$p, s$d + 0.5, s$n - s$d + 0.5))
}

hosmer <- function(case, frame, ddof = 0) {
  s <- grade_summary(frame)
  q <- sum((s$d - s$n * s$p)^2 / (s$n * s$p * (1 - s$p)))
  p_value <- pchisq(q, df = nrow(s) - ddof, lower.tail = FALSE)
  emit(case, "p_value", p_value)
  emit(case, "reject", p_value < 0.05)
}
hosmer("hosmer_small", rd("pd_small"))
hosmer("hosmer_large", rd("pd_large"))
hosmer("hosmer_large_ddof2", rd("pd_large"), ddof = 2)

spiegelhalter <- function(case, frame) {
  y <- frame$y
  p <- frame$pd
  z <- sum((y - p) * (1 - 2 * p)) / sqrt(sum(p * (1 - p) * (1 - 2 * p)^2))
  emit(case, "z", z)
  emit(case, "reject", 2 * pnorm(-abs(z)) < 0.05)
}
spiegelhalter("spiegelhalter_small", rd("pd_small"))
spiegelhalter("spiegelhalter_large", rd("pd_large"))

f <- rd("pd_small")
emit("brier_small", "brier", mean((f$y - f$pd)^2))
f <- rd("pd_large")
emit("brier_large", "brier", mean((f$y - f$pd)^2))

redelmeier <- function(case, y, p1, p2) {
  diff <- p1 - p2
  total <- p1 + p2
  z <- sum(diff * (total - 2 * y)) / sqrt(sum(diff^2 * total * (2 - total)))
  emit(case, "z", z)
  emit(case, "p_value", 2 * pnorm(-abs(z)))
}
f <- rd("redelmeier_small")
redelmeier("redelmeier_small", f$y, f$p1, f$p2)
f <- rd("pd_large")
redelmeier("redelmeier_large", f$y, f$pd, f$pd2)

normal_test <- function(case, frame) {
  e <- frame$realised - frame$predicted
  z <- as.numeric(t.test(frame$realised, frame$predicted, paired = TRUE)$statistic)
  p_value <- pnorm(z, lower.tail = FALSE)
  emit(case, "estimate", mean(e))
  emit(case, "z", z)
  emit(case, "p_value", p_value)
  emit(case, "reject", p_value < 0.05)
}
normal_test("normal_test_small", rd("normal_small"))
normal_test("normal_test_large", rd("normal_large"))

# --- Association ------------------------------------------------------------

kendall <- function(case, x, y) {
  result <- suppressWarnings(cor.test(x, y, method = "kendall"))
  emit(case, "tau", result$estimate)
  emit(case, "p_value", result$p.value)
}
f <- rd("assoc_small")
kendall("kendall_small", f$x, f$y)
f <- rd("lgd_large")
kendall("kendall_large", f$predicted, f$realised)
emit("kendall_large_tau_c", "tau", DescTools::StuartTauC(f$pgrade, f$rgrade))

# DescTools direction = "column" is D(column | row) = D(y | x), SciPy's convention.
f <- rd("somers_small")
emit("somersd_small_table", "d", DescTools::SomersDelta(f$x, f$y, direction = "column"))
f <- rd("lgd_large")
emit("somersd_large", "d", DescTools::SomersDelta(f$pgrade, f$rgrade, direction = "column"))

correlation <- function(case, x, y, method, field) {
  result <- suppressWarnings(cor.test(x, y, method = method, exact = FALSE))
  emit(case, field, result$estimate)
  emit(case, "p_value", result$p.value)
}
f <- rd("assoc_small")
correlation("spearman_small", f$x, f$y, "spearman", "rho")
correlation("pearson_small", f$x, f$y, "pearson", "r")
f <- rd("lgd_large")
correlation("spearman_large", f$predicted, f$realised, "spearman", "rho")
correlation("pearson_large", f$predicted, f$realised, "pearson", "r")

# --- Stability --------------------------------------------------------------

concentration <- function(counts) {
  s <- counts / sum(counts)
  k <- length(s)
  c(cv = sqrt(k * sum((s - 1 / k)^2)), hhi = sum(s^2))
}
hhi <- function(case, frame, levels = sort(unique(frame$grade))) {
  counts <- table(factor(frame$grade, levels = levels))
  result <- concentration(as.numeric(counts))
  emit(case, "cv", result["cv"])
  emit(case, "hhi", result["hhi"])
}
hhi("herfindahl_small", rd("grades_small_initial"))
hhi("herfindahl_declared", rd("grades_small_initial"), levels = c("A", "B", "C"))
hhi("herfindahl_large", rd("grades_large_initial"))

hhi_multi <- function(case, initial, current) {
  levels <- sort(unique(c(initial$grade, current$grade)))
  n1 <- table(factor(initial$grade, levels = levels))
  n2 <- table(factor(current$grade, levels = levels))
  c1 <- concentration(as.numeric(n1))
  c2 <- concentration(as.numeric(n2))
  z <- sqrt(length(levels) - 1) * (c2["cv"] - c1["cv"]) / sqrt(c2["cv"]^2 * (0.5 + c2["cv"]^2))
  p_value <- pnorm(z, lower.tail = FALSE)
  emit_named(case, "n_initial", setNames(as.numeric(n1), levels))
  emit_named(case, "n_current", setNames(as.numeric(n2), levels))
  emit(case, "h_initial", c1["hhi"])
  emit(case, "h_current", c2["hhi"])
  emit(case, "z", z)
  emit(case, "p_value", p_value)
  emit(case, "reject", p_value < 0.05)
}
hhi_multi("herfindahl_multi_small", rd("grades_small_initial"), rd("grades_small_current"))
hhi_multi("herfindahl_multi_large", rd("grades_large_initial"), rd("grades_large_current"))

psi <- function(case, frame, smoothing, levels = sort(unique(frame$bin))) {
  counts <- table(factor(frame$bin, levels = levels), factor(frame$period, levels = c("old", "new")))
  e <- (counts[, "old"] + smoothing)
  a <- (counts[, "new"] + smoothing)
  e <- e / sum(e)
  a <- a / sum(a)
  emit_named(case, "expected", e)
  emit_named(case, "actual", a)
  emit(case, "psi", sum((a - e) * log(a / e)))
}
psi("psi_small", rd("psi_small"), 0)
psi("psi_declared", rd("psi_small"), 0.5, levels = c("A", "B", "C"))
psi("psi_large", rd("psi_large"), 0.5)

migration_counts <- function(frame) {
  levels <- sort(unique(c(frame$start, frame$end)))
  table(factor(frame$start, levels = levels), factor(frame$end, levels = levels))
}
bandwidth <- function(case, frame) {
  counts <- migration_counts(frame)
  k <- nrow(counts)
  i <- row(counts) - 1
  j <- col(counts) - 1
  distance <- abs(i - j)
  maximum <- pmax(i, k - 1 - i)
  side <- function(mask) {
    denominator <- sum(counts * maximum * mask)
    if (denominator > 0) sum(counts * distance * mask) / denominator else 0
  }
  emit(case, "upper", side(j > i))
  emit(case, "lower", side(j < i))
}
bandwidth("migration_bandwidth_small", rd("migration_small"))
bandwidth("migration_bandwidth_large", rd("migration_large"))

stability <- function(case, frame, initial_counts = NULL) {
  counts <- migration_counts(frame)
  labels <- rownames(counts)
  totals <- rowSums(counts)
  if (!is.null(initial_counts)) totals <- initial_counts[match(labels, names(initial_counts))]
  k <- length(labels)
  for (i in seq_len(k)) {
    n <- totals[i]
    p <- if (n > 0) as.numeric(counts[i, ]) / n else rep(NA_real_, k)
    for (j in seq_len(k)) {
      if (i == j) next
      z <- NA_real_
      if (n > 0) {
        far <- p[j]
        near <- p[if (j < i) j + 1 else j - 1]
        variance <- (far * (1 - far) + near * (1 - near) + 2 * far * near) / n
        if (variance > 0) z <- (near - far) / sqrt(variance)
      }
      emit(case, paste("z", labels[i], labels[j], sep = "."), z)
      emit(case, paste("cdf", labels[i], labels[j], sep = "."), if (is.na(z)) NA_real_ else pnorm(z))
    }
  }
}
stability("migration_stability_small", rd("migration_small"))
stability("migration_stability_large", rd("migration_large"))
ic <- rd("migration_large_initial_counts")
stability("migration_stability_large_initial_counts", rd("migration_large"), setNames(ic$count, ic$grade))

# --- LGD validation ---------------------------------------------------------

paired <- function(case, label, realised, predicted, alternative) {
  result <- t.test(realised, predicted, paired = TRUE, alternative = alternative)
  e <- realised - predicted
  emit(case, paste0("n.", label), length(e))
  emit(case, paste0("realised_mean.", label), mean(realised))
  emit(case, paste0("pred_mean.", label), mean(predicted))
  emit(case, paste0("s2.", label), var(e))
  emit(case, paste0("mean_error.", label), mean(e))
  emit(case, paste0("t.", label), result$statistic)
  emit(case, paste0("p_value.", label), result$p.value)
}
for (nm in c("small", "large")) {
  f <- rd(paste0("lgd_", nm))
  paired(paste0("lgd_t_test_portfolio_", nm), "portfolio", f$realised, f$predicted, "greater")
  for (seg in unique(f$segment)) {
    s <- f[f$segment == seg, ]
    paired(paste0("lgd_t_test_segment_", nm), seg, s$realised, s$predicted, "greater")
  }
  result <- t.test(f$realised, f$predicted, paired = TRUE)
  case <- paste0("elbe_t_test_", nm)
  emit(case, "facilities", nrow(f))
  emit(case, "lgd_mean", mean(f$realised))
  emit(case, "elbe_mean", mean(f$predicted))
  emit(case, "t", result$statistic)
  emit(case, "p_value", result$p.value)
  emit(paste0("loss_shortfall_", nm), "shortfall", 1 - sum(f$ead * f$predicted) / sum(f$ead * f$realised))
  emit(paste0("mean_absolute_deviation_", nm), "mad", weighted.mean(abs(f$realised - f$predicted), f$ead))
}

# --- Output -----------------------------------------------------------------

results <- do.call(rbind, records)
meta <- list(
  language = "r",
  version = R.version.string,
  packages = list(
    jsonlite = as.character(packageVersion("jsonlite")),
    pROC = as.character(packageVersion("pROC")),
    DescTools = as.character(packageVersion("DescTools"))
  ),
  generated = format(Sys.Date()),
  platform = R.version$platform
)
writeLines(
  toJSON(list(meta = meta, results = results), auto_unbox = TRUE, digits = NA, na = "null", pretty = TRUE),
  out_path
)
cat(sprintf("%d records -> %s\n", nrow(results), out_path))
