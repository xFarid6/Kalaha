# Setup Guide: R for Data Analysis

This guide will help you install R and set up a modern development environment.

## 1. Install R (The Language)
R is the statistical computing engine.

1.  **Download**: Go to [The CRAN Project](https://cran.r-project.org/bin/windows/base/).
2.  **Install**: Download `R-x.x.x-win.exe` and run the installer. Use default settings.
3.  **Verify**: Open PowerShell and try running `R --version`.
    *   *Note*: You might need to add `C:\Program Files\R\R-x.x.x\bin` to your System Path manually if the installer doesn't do it.

## 2. Tools (The IDE)

### Option A: VSCode (Recommended for you)
Since you are already using VSCode for Go/Flutter, stick with it!

1.  **Install R Extension**: Search for "R" (by Yuki Ueda) in VSCode Extensions.
2.  **Install Radian (Optional but better)**: A modern console for R.
    ```powershell
    pip install -U radian
    ```
    *   *Requires Python installed.*
3.  **Enable Plot Viewer**: The extension usually detects active R sessions and opens a side pane for plots.

### Option B: RStudio (The Classic)
RStudio is the standard IDE for R. It's excellent but is a separate app.
*   Download from [Posit.co](https://posit.co/download/rstudio-desktop/).

## 3. Install Packages (The Tidyverse)
R uses CRAN to host libraries. We need the "Tidyverse" suite (dplyr, ggplot2, readr).

1.  Open an R terminal (or just `R.exe`).
2.  Run:
    ```r
    install.packages("tidyverse")
    install.packages("rmarkdown")
    ```
    *   *This will download a lot of dependencies. It might take a few minutes.*

## 4. Running the Project
To run the analysis pipeline:
```powershell
Rscript main.R
```
Or interactively source files in VSCode using `Ctrl+Enter`.
