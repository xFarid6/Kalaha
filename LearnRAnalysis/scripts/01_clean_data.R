# scripts/01_clean_data.R
# Purpose: Load raw CSV, clean missing values, and summarize data.

# 1. Load Libraries
# We check if tidyverse is installed, if not we stop.
if (!require("tidyverse")) stop("Please install tidyverse: install.packages('tidyverse')")

message("Step 1: Loading Data...")

# 2. Load Data
# read_csv is faster and smarter than base R's read.csv
df <- read_csv("data/sales_data.csv", show_col_types = FALSE)

# 3. Data Inspection
print(head(df))
print(summary(df))

# 4. Data Cleaning
# We use the pipe operator (|>) to chain operations.
clean_df <- df |>
  # Remove rows where Product name is missing (NA)
  filter(!is.na(Product)) |> 
  # Create a new column 'RevenuePerUnit'
  mutate(RevenuePerUnit = Sales / Units) |>
  # Parse Date correctly (readr usually guesses right, but good to be explicit)
  mutate(Date = as.Date(Date))

message("Step 2: Summarizing Data...")

# 5. Grouping and Aggregation
summary_df <- clean_df |>
  group_by(Region, Product) |>
  summarise(
    TotalSales = sum(Sales),
    TotalUnits = sum(Units),
    AvgPrice = mean(RevenuePerUnit),
    .groups = "drop" # Drop grouping structure after efficient calculation
  )

print(summary_df)

# 6. Save Cleaned Data
write_csv(clean_df, "data/clean_sales.csv")
write_csv(summary_df, "data/summary_sales.csv")

message("Data cleaning complete. Files saved to data/")
