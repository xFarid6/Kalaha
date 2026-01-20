# R Philosophy

R is not like Go or Dart. It is a **Functional Language** designed specifically for **Statistics**.

## 1. Everything is a Vector
In Go, `x := 5` is an integer. In R, `x <- 5` is a vector of length 1.
This means you don't write loops for math!

**Go Way:**
```go
arr := []float64{1, 2, 3}
out := []float64{}
for _, v := range arr {
    out = append(out, v * 2)
}
```

**R Way:**
```r
arr <- c(1, 2, 3)
out <- arr * 2  # Result: 2, 4, 6
```
*Why?* Data analysis involves applying the same math to millions of rows. Vectorization is fast and readable.

## 2. The Tidyverse & Pipelines
We use the pipe operator `|>` (or `%>%`). It passes the result of the left side as the first argument to the right side.

```r
data |> 
  filter(age > 30) |> 
  group_by(city) |> 
  summarise(avg_salary = mean(salary))
```
*Read it like English:* "Take data, then filter by age, then group by city, then summarise average salary."

## 3. One-Based Indexing
Arrays start at **1**, not 0.
*   `arr[1]` is the first element.
*   *Why?* In linear algebra and matrix math definitions, rows/cols starts at 1. R adheres to math notation, not CS notation.

## 4. Factors
R has a special data type for Categorical Data called `factor` (e.g., "High", "Medium", "Low").
It looks like strings, but acts like integers. This is crucial for statistical models (regression) and plotting orders.
