# scripts/02_visualize.R
# Purpose: Load cleaned data and generate visualizations using ggplot2.

# 1. Load Libraries
if (!require("tidyverse")) stop("Please install tidyverse")

message("Step 3: Generating Visualizations...")

# 2. Load Cleaned Data
clean_df <- read_csv("data/clean_sales.csv", show_col_types = FALSE)

# 3. Create Plot
# The "Grammar of Graphics":
# Data + Aes (Aesthetics: x, y, color) + Geom (Geometry: bar, point, line)
plot <- clean_df |>
  group_by(Product) |>
  summarise(TotalSales = sum(Sales)) |>
  ggplot(aes(x = Product, y = TotalSales, fill = Product)) +
  geom_col() + # Column chart (Bar chart)
  labs(
    title = "Total Sales by Product",
    subtitle = "Q1 2023 Performance",
    x = "Product Name",
    y = "Sales ($)"
  ) +
  theme_minimal() # Clean theme

# 4. Save Plot
ggsave("output/sales_by_product.png", plot = plot, width = 6, height = 4)

message("Plot saved to output/sales_by_product.png")
