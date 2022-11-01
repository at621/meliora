

test_data <- read.csv("pd_test_data.csv")


###############################################

# to install iterativeBMA package:
#if (!requireNamespace("BiocManager", quietly = TRUE))
#  install.packages("BiocManager")
#BiocManager::install("iterativeBMA")

library(iterativeBMA)

brier.score(test_data$predicted_pd, test_data$default_flag)/nrow(test_data)

# Agrees with Meliora (other than defining Brier score as sum rather than avg)

############

#install.packages("PDtoolkit")

library(PDtoolkit)

test_agg <- read.csv("pd_test_agg.csv")
pp.testing(rating.label = test_agg$ratings,
           pdc = test_agg$PD,
           no = test_agg$N,
           nb = test_agg$D, 
           alpha = 0.05)

# Jeffrey's and Binomial both agree with Meliora.
# Hosmer-Lemeshow differs only because the author computes a chi-squared cdf with
# k degrees of freedom rather than k-2 which is what our source says to use.
# (See hl.test at https://github.com/andrija-djurovic/PDtoolkit/blob/main/R/12_PREDICTIVE_POWER.R)

##########

# install.packages("remotes")
# remotes::install_github("ayhandis/creditR")

library(creditR)

df <- master.scale(test_data, "default_flag", "predicted_pd")
h <- Herfindahl.Hirschman.Index(df, "Total.Observations")
h

# Herfindahl index agrees, but I was unable to find any available Herfindahl TEST to compare with

##########

# There doesn't appear to be an R implementation of the Spiegelhalter test.
# The SAS implementation seems to be very limited in its scope: it doesn't let you
# specify the hypothesized success probabilities as far as I can tell.

