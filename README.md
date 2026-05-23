# MATH189-
MATH 189 final project: UCSD enrollment and San Diego rental market


## How to Reproduce

1. **Clone or download** this repository.
2. **Install dependencies** — the analysis uses `pandas`, `numpy`, `matplotlib`, and `statsmodels`. All come with Anaconda.
3. **Open `analysis.ipynb`** in JupyterLab (e.g., via Anaconda Navigator) and `Run All Cells`. The notebook reads from the already-cleaned files in `data/` and reproduces every figure and statistical result.

The four `0X_*.py` scripts are the data preparation pipeline. Their outputs are already saved in `data/`, so you do not need to re-run them. If you want to re-pull fresh ACS data, sign up for a free Census API key at https://api.census.gov/data/key_signup.html and paste it into `config.py`.

## Methods

- **Sample:** 3 treated ZIP codes (92037 La Jolla, 92122 University City, 92126 Mira Mesa) plus 16 matched San Diego County control ZIPs more than 10 miles from campus.
- **Main specification:** two-way fixed-effects panel regression of `log(rent)` on the interaction of a treated dummy with `log(UCSD enrollment)`, with ZIP and month fixed effects and a log-income control. Standard errors clustered at the ZIP level.
- **Robustness:** wild cluster bootstrap (for the small number of clusters), leave-one-treated-out, expanded control set, expanded treated set (adding Clairemont and Pacific Beach), pre-COVID-only subsample, and an event-study specification estimating the treated-control rent gap year by year.

## Course

Created for MATH 189 (Statistical Methods), UC San Diego.
