# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#' @title Identify the WPA metrics that have the biggest change between two
#'   periods.
#'
#' @description
#' `r lifecycle::badge('experimental')`
#'
#' This function uses the Information Value algorithm to predict
#' which Workplace Analytics metrics are most explained by the change in dates.
#'
#' @author Mark Powers <mark.powers@@microsoft.com>
#'
#' @param data Person Query as a dataframe including date column named "Date"
#'   This function assumes the data format is `MM/DD/YYYY` as is standard in a
#'   Workplace Analytics query output.
#' @param before_start Start date of "before" time period in `YYYY-MM-DD`.
#'   Defaults to earliest date in dataset.
#' @param before_end End date of "before" time period in `YYYY-MM-DD`
#' @param after_start Start date of "after" time period in `YYYY-MM-DD`.
#'   Defaults to day after before_end.
#' @param after_end End date of "after" time period in `YYYY-MM-DD`. Defaults to
#'   latest date in dataset.
#' @param mybins Number of bins to cut the data into for Information Value
#'   analysis. Defaults to 10.
#' @param return  String specifying what to return. The current only valid
#' option is `"table"`.
#'
#' @return
#' data frame containing all the variables and the corresponding Information
#' Value.
#'
#' @import dplyr
#'
#' @family Variable Association
#' @family Information Value
#' @family Time-series
#'
#' @examples
#' # Returns a data frame
#' sq_data %>%
#'     IV_by_period(
#'         before_start = "2019-11-03",
#'         before_end = "2019-11-09",
#'         after_start = "2019-11-10",
#'         after_end = "2019-11-16"
#'     )
#'
#' @export

IV_by_period <-
    function(data,
             before_start = min(as.Date(data$Date, "%m/%d/%Y")),
             before_end,
             after_start = as.Date(before_end) + 1,
             after_end = max(as.Date(data$Date, "%m/%d/%Y")),
             mybins = 10,
             return = "table") {

        ## Check inputs
        required_variables <- c(
            "Date",
            "PersonId"
        )
        ## Error message if variables are not present
        ## Nothing happens if all present
        data %>%
            check_inputs(requirements = required_variables)

        daterange_1_start <- as.Date(before_start)
        daterange_1_end <- as.Date(before_end)
        daterange_2_start <- as.Date(after_start)
        daterange_2_end <- as.Date(after_end)

        WpA_dataset <- data %>% mutate(Date = as.Date(Date, "%m/%d/%Y"))


        # Check for dates in data file
        if (daterange_1_start < min(WpA_dataset$Date) |
            daterange_1_start > max(WpA_dataset$Date) |
            daterange_1_end < min(WpA_dataset$Date) |
            daterange_1_end > max(WpA_dataset$Date) |
            daterange_2_start < min(WpA_dataset$Date) |
            daterange_2_start > max(WpA_dataset$Date) |
            daterange_2_end < min(WpA_dataset$Date) |
            daterange_2_end > max(WpA_dataset$Date)) {
            stop("Dates not found in dataset")
            geterrmessage()
        }

        # Create variable => Period
        WpA_dataset_table <-
            WpA_dataset %>%
            mutate(
                Period = case_when(
                    Date >= daterange_1_start &
                        Date <= daterange_1_end ~ "Before",
                    Date >= daterange_2_start &
                        Date <= daterange_2_end ~ "After"
                )
            ) %>%
            filter(Period == "Before" | Period == "After")

        WpA_dataset_table <-
            WpA_dataset_table %>% mutate(outcome = case_when(
                Period == "Before" ~ "0",
                Period == "After" ~ "1"
            ))

        # De-select character columns
        train <-
            WpA_dataset_table %>%
            transform(outcome = as.numeric(outcome)) %>%
            select_if(is.numeric)

        # Filter out NAs
        train <- train %>%
            filter(rowSums(is.na(.[, ])) < 1)

        # Rename Outcome Variable
        # train <- transform(train, outcome = as.numeric(outcome))
        train <- rename(train, "Outcome" = "outcome")
        colnames(train)


        # Calculate Odds
        odds <-
            sum(train$Outcome) / (length(train$Outcome) - sum(train$Outcome))
        lnodds <- log(odds)

        # IV Analysis
        # IV <- create_infotables(data = train, y = "Outcome", bins = mybins)
        IV <- map_IV(
            data = train,
            outcome = "Outcome",
            bins = mybins
        )


        # if(return == "detailed"){
        #   # Ranking variables using  IV
        #   wb <- createWorkbook()
        #   addWorksheet(wb, "Ranking")
        #   writeDataTable(wb, "Ranking", x = data.frame(IV$Summary))
        #
        #   # Export Individual Tables
        #   for(i in names(IV$Tables)){
        #     print(i)
        #     addWorksheet(wb, substr(i, start = nchar(i) - 30, stop = nchar(i)))
        #     temp <- IV$Tables[[i]]
        #     temp$ODDS <- exp(temp$WOE + lnodds)
        #     temp$PROB <- (temp$ODDS / (temp$ODDS + 1))
        #     writeDataTable(wb, substr(i, start = nchar(i) - 30, stop = nchar(i)) , x = data.frame(temp))
        #   }
        #
        #   # Save Workbook
        #   saveWorkbook(wb, "Output_IV_v2.xlsx", overwrite = TRUE)
        #
        #   # Plot Graph
        #   pdf("Output_IV_v2.pdf")
        #   plot_infotables(IV, IV$Summary$Variable[], same_scale=TRUE)
        #   dev.off()
        # } else
        if (return == "table") {
            # Store all individual dataframes
            Tables <- c()
            Summary <- data.frame(IV$Summary)
            Tables$Summary <- Summary
            for (i in names(IV$Tables)) {
                temp <- IV$Tables[[i]]
                temp$ODDS <- exp(temp$WOE + lnodds)
                temp$PROB <- (temp$ODDS / (temp$ODDS + 1))
                Tables[[i]] <- create_dt(temp, rounding = 2)
            }

            # Return ranking table
            return(Tables$Summary)
            # print("Access individual metrics via Outputs[[metric_name]], e.g., Outputs[[Workweek_span]]")

            # # Store each variable's plot
            # plots <- c()
            # for (i in names(IV$Tables)) {
            #   plots[[i]] <- plot_infotables(IV, i)
            # }
        } else {
            stop("Please enter a valid input for `return`, either detailed or table.")
        }
    }



# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#' @title Generate a Information Value HTML Report
#'
#' @description
#' The function generates an interactive HTML report using Standard Person Query
#' data as an input. The report contains a full Information Value analysis,  a
#' data exploration technique that helps determine which columns in a data set
#' have predictive power or influence on the value of a specified dependent
#' variable.
#'
#' @param data A Standard Person Query dataset in the form of a data frame.
#' @param predictors A character vector specifying the columns to be used as
#'   predictors. Defaults to NULL, where all numeric vectors in the data will be
#'   used as predictors.
#' @param outcome A string specifying a binary variable, i.e. can only contain
#'   the values 1 or 0.
#' @param bins Number of bins to use in `Information::create_infotables()`,
#'   defaults to 10.
#' @param max_var Numeric value to represent the maximum number of variables to
#' show on plots.
#' @param path Pass the file path and the desired file name, _excluding the file
#'   extension_. For example, `"IV report"`.
#' @param timestamp Logical vector specifying whether to include a timestamp in
#'   the file name. Defaults to TRUE.
#'
#' @section Creating a report:
#'
#' Below is an example on how to run the report.
#'
#' ```
#' library(dplyr)
#'
#' sq_data %>%
#'   mutate(CH_binary = ifelse(Collaboration_hours > 12, 1, 0)) %>% # Simulate binary variable
#'   IV_report(outcome =  "CH_binary",
#'             predictors = c("Email_hours", "Workweek_span"))
#' ```
#'
#' @family Reports
#' @family Variable Association
#' @family Information Value
#'
#' @inherit generate_report return
#'
#' @export
IV_report <- function(data,
                      predictors = NULL,
                      outcome,
                      bins = 5,
                      max_var = 9,
                      path = "IV report",
                      timestamp = TRUE){

  # Create timestamped path (if applicable) -----------------------------------

  if(timestamp == TRUE){
    newpath <- paste(path, wpa::tstamp())
  } else {
    newpath <- path
  }

  # Return IV object directly -------------------------------------------------

  # Call `calculate_IV()` only once
  IV_obj <-
    data %>%
    create_IV(outcome = outcome,
              predictors = predictors,
              bins = bins,
              return = "IV")

  # IV_names
  IV_names <- names(IV_obj$Tables)

  # List of tables -----------------------------------------------------------

  table_list <-
    IV_names %>%
    purrr::map(function(x){
      IV_obj$Tables[[x]] %>%
         mutate(ODDS = exp(WOE + IV_obj$lnodds),
                PROB = ODDS / (ODDS + 1))
    }) %>%
    purrr::set_names(IV_names)

  # List of ggplot objects ----------------------------------------------------

  plot_list <-
   IV_obj$Summary$Variable %>%
   as.character() %>%
   purrr::map(~plot_WOE(IV = IV_obj, predictor = .))

  # Restrict maximum plots to `max_var` ---------------------------------------

  if(length(plot_list) > max_var){

    plot_list <- plot_list[1:max_var]
    table_list <- table_list[1:max_var]

  }

  table_names <- gsub("_", " ", x = names(table_list))

  # Output list ---------------------------------------------------------------

  output_list <-
    list(
      data %>% check_query(return = "text"),
      data %>% create_IV(outcome = outcome, predictors=predictors, bins= bins),
      data %>% create_IV(outcome = outcome,
                         predictors = predictors,
                         bins = bins,
                         return="summary"),
      read_preamble("blank.md") # Header for WOE Analysis
         ) %>%
    c(plot_list) %>%
    c(list(read_preamble("blank.md"))) %>% # Header for Summary Tables
    c(table_list)  %>%
    purrr::map_if(is.data.frame, create_dt) %>%
    purrr::map_if(is.character, md2html)

  title_list <-
    c("Data Overview",
      "Top Predictors",
      "",
      "WOE Analysis",
      rep("", length(plot_list)),
      "Summary - Predictors",
      table_names)


  n_title <- length(title_list)

  title_levels <-
    c(
      2,
      2,
      4,
      2, # Header for WOE Analysis
      rep(4, length(plot_list)),
      2, # Header for WOE Analysis
      rep(3, length(table_list))
      )

  generate_report(title = "Information Value Report",
                  filename = newpath,
                  outputs = output_list,
                  titles = title_list,
                  subheaders = rep("", n_title),
                  echos = rep(FALSE, n_title),
                  levels = title_levels,
                  theme = "cosmo",
                  preamble = read_preamble("IV_report.md"))

}


# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#' @title
#' Calculate Weight of Evidence (WOE) and Information Value (IV) between a
#' single predictor and a single outcome variable.
#'
#' @description
#' Calculates Weight of Evidence (WOE) and Information Value (IV) between a
#' single predictor and a single outcome variable. This function implements the
#' common Information Value calculations whilst maintaining the minimum reliance
#' on external dependencies. Use `map_IV()` for the equivalent of
#' `Information::create_infotables()`, which performs calculations for multiple
#' predictors and a single outcome variable.
#'
#' @details
#' The approach used mirrors the one used in `Information::create_infotables()`.
#'
#' @param data Data frame containing the data.
#' @param outcome String containing the name of the outcome variable.
#' @param predictor String containing the name of the predictor variable.
#' @param bins Numeric value representing the number of bins to use.
#'
#' @import dplyr
#'
#' @return A data frame is returned as an output.
#'
calculate_IV <- function(data,
                         outcome,
                         predictor,
                         bins){

  pred_var <- data[[predictor]]
  outc_var <- data[[outcome]]

  # Check inputs
  if(sum(is.na(outc_var)) > 0){

    stop(
      glue::glue(
        "dependent variable {outcome} has missing values in the input training data frame"
      )
      )
  }

  # Compute q
  q <- stats::quantile(
    pred_var,
    probs = c(1:(bins - 1) / bins),
    na.rm = TRUE,
    type = 3
    )

  # Compute cuts
  cuts <- unique(q)

  # Compute intervals
  intervals <-
    findInterval(
      pred_var,
      vec = cuts,
      rightmost.closed = FALSE)

  # Compute cut_table
  cut_table <-
    table(
      intervals,
      outc_var) %>%
    as.data.frame.matrix()

  ## get min/max
  cut_table_2 <-
    data.frame(
    var = pred_var,
    intervals
  ) %>%
    group_by(intervals) %>%
    summarise(
      min = min(var, na.rm = TRUE) %>% round(digits = 1),
      max = max(var, na.rm = TRUE) %>% round(digits = 1),
      n = n(),
      .groups = "drop"
    ) %>%
    mutate(!!sym(predictor) :=
    glue::glue("[{round(min, digits = 1)},{round(max, digits = 1)}]")) %>%
    mutate(percentage = n / sum(n)) %>%
    select(!!sym(predictor), intervals, n, percentage)

  # Create variables that are double
  cut_table_1 <- as.numeric(cut_table$`1`)
  cut_table_0 <- as.numeric(cut_table$`0`)

  # Non-events in group
  n_non_event <- cut_table_1 * sum(cut_table_0) # t$y_1*sum_y_0
  n_yes_event <- cut_table_0 * sum(cut_table_1) # t$y_0*sum_y_1

  # Compute WOE

  cut_table_2$WOE <-
    ifelse(
      cut_table$`1` > 0 & cut_table$`0` > 0, # Both positive
      log(n_non_event / n_yes_event), # % of non-events divided by % of events
           0) # Otherwise impute 0

  # Compute IV_weight
  p1 <- cut_table$`1` / sum(cut_table$`1`)
  p0 <- cut_table$`0` / sum(cut_table$`0`)

  cut_table_2$IV_weight <- p1 - p0
  cut_table_2$IV <- cut_table_2$WOE * cut_table_2$IV_weight

  cut_table_2 %>%
    mutate(IV = cumsum(IV)) %>%
    # Maintain consistency with `Information::create_infotables()`
    select(
      !!sym(predictor),
      N = "n",
      Percent = "percentage",
      WOE,
      IV)
}

#' @title
#' Calculate Weight of Evidence (WOE) and Information Value (IV) between
#' multiple predictors and a single outcome variable, returning a list of
#' statistics.
#'
#' @description
#' This is a wrapper around `calculate_IV()` to loop through multiple predictors
#' and calculate their Weight of Evidence (WOE) and Information Value (IV) with
#' respect to an outcome variable.
#'
#' @details
#' The approach used mirrors the one used in `Information::create_infotables()`.
#'
#' @param data Data frame containing the data.
#' @param outcome String containing the name of the outcome variable.
#' @param predictors Character vector containing the names of the predictor
#'   variables. If `NULL` (default) is supplied, all numeric variables in the
#'   data will be used.
#' @param bins Numeric value representing the number of bins to use. Defaults to
#'   10.
#'
#' @import dplyr
#'
#' @return A list of data frames is returned as an output. The first layer of
#' the list contains `Tables` and `Summary`:
#'   -  `Tables` is a list of data frames containing the WOE and cumulative sum
#'   IV for each predictor.
#'   - `Summary` is a single data frame containing the IV for all predictors.
#'
map_IV <- function(data,
                   predictors = NULL,
                   outcome,
                   bins = 10){

  if(is.null(predictors)){

    predictors <-
      data %>%
      select(-!!sym(outcome)) %>%
      select(
        where(is.numeric)
      ) %>%
      names()
  }

  # List of individual tables
  Tables <-
    predictors %>%
    purrr::map(function(pred){

      calculate_IV(
        data = data,
        outcome = outcome,
        predictor = pred,
        bins = bins
      )
    }) %>%
    purrr::set_names(
      nm = purrr::map(
        .,
        function(df){
          names(df)[[1]]
        }
      )
    )

  # Compile Summary Table
  Summary <-
    list("df" = Tables,
         "names" = names(Tables)) %>%
    purrr::pmap(function(df, names){

      IV_final <-
        df %>%
        slice(nrow(df)) %>%
        pull(IV)

      data.frame(
        Variable = names,
        IV = IV_final
      )
    }) %>%
    bind_rows() %>%
    arrange(desc(IV))

  # Reorder and combine list
  c(
    list("Tables" = Tables[Summary$Variable]), # Reordered
    list("Summary" = Summary)
  )
}
