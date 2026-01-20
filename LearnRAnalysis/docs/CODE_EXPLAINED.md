# Code Explained

This document breaks down the R scripts to help you understand the syntax.

## 1. The Pipe Operator (`|>`)
In `scripts/01_clean_data.R`:
```r
clean_df <- df |>
  filter(!is.na(Product)) |> 
  mutate(...)
```
*   **Concept**: Passing the ball.
*   The result of `df` is passed to `filter`.
*   The result of `filter` is passed to `mutate`.
*   **Why?** It avoids nesting like `mutate(filter(df, ...), ...)`.

## 2. Vectors and Columns
In `scripts/02_visualize.R`:
```r
ggplot(aes(x = Product, y = TotalSales))
```
*   **Concept**: Aesthetics Mapping.
*   We map the **variable** `Product` (a column in the dataframe) to the **x-axis**.
*   We map `TotalSales` to the **y-axis**.
*   Use `fill = Product` to map the column to the color fill.

## 3. R Markdown (`report.Rmd`)
```r
```{r load_data}
df <- read_csv(...)
```
```
*   **Concept**: Literate Programming.
*   When you "Knit" (render) the file, R runs this code block and embeds the results (text or plots) directly into the final HTML.
*   `echo=FALSE` hides the code but shows the result.
*   `include=FALSE` runs the code but hides everything (good for setup).
