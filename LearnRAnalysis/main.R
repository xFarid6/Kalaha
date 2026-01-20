# main.R
# Purpose: Orchestrate the entire analysis pipeline.

message(">>> Starting Pipeline <<<")

# 1. Run Data Cleaning
source("scripts/01_clean_data.R")

# 2. Run Visualization
source("scripts/02_visualize.R")

# 3. Render Report
if (require("rmarkdown")) {
  message("Step 4: Rendering HTML Report...")
  render("report.Rmd", output_file = "output/report.html", quiet = TRUE)
  message("Report saved to output/report.html")
} else {
  warning("rmarkdown package not installed. Skipping report generation.")
}

message(">>> Pipeline Complete! Check the 'output' folder. <<<")
