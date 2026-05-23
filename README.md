# MATH 189 Final Project: UCSD Enrollment Growth and the San Diego Rental Market

A ZIP-month panel analysis of whether UCSD's 2010–2024 enrollment growth is associated with faster rent growth in nearby San Diego County ZIP codes.

## Research Question

Did UCSD-adjacent ZIP codes (La Jolla, University City, Mira Mesa) experience faster rent growth from 2015 to 2024 than otherwise-comparable San Diego County ZIP codes, and is that pattern statistically associated with UCSD enrollment expansion?

## Main Finding

We find **no robust evidence** that UCSD enrollment growth is associated with faster rent growth in nearby ZIP codes. The interaction coefficient is small, slightly negative, and not statistically distinguishable from zero under wild cluster bootstrap inference (p = 0.15). The event-study confirms that the treated-control rent gap never trended upward. The pattern is better explained by region-wide forces — including the post-2020 "donut effect" in which rental demand shifted toward suburban areas — than by student-driven demand pressure near campus.

## Data Sources

All data are public and downloaded from official sources:

| Source | Variable | URL |
|---|---|---|
| Zillow Research (ZORI) | Monthly rent index, ZIP level | https://www.zillow.com/research/data/ |
| NCES IPEDS | UCSD Fall enrollment, 2010–2024 | https://nces.ed.gov/ipeds/use-the-data |
| U.S. Census Bureau ACS 5-Year | Demographic and housing controls | https://www.census.gov/data/developers/data-sets/acs-5year.html |
| U.S. Census Gazetteer | ZIP centroid coordinates and land area | https://www.census.gov/geographies/reference-files.html |

## Repository Structure

```
.
├── 01_zillow_setup.py              # Build SD County rent panel from Zillow ZORI
├── 02_acs_pull.py                  # Pull ACS demographic controls via Census API
├── 03_build_ipeds_enrollment.py    # Extract UCSD enrollment from IPEDS files
├── 04_control_selection.py         # Select matched control ZIP codes
├── analysis.ipynb                  # Main analysis (EDA → regression → robustness → event-study)
├── config.py                       # Configuration (Census API key placeholder)
├── data/                           # Cleaned data files (CSVs)
├── figures/                        # All figures produced by the analysis
├── Math_189_Proposal__1_.pdf       # Original project proposal
└── README.md
```

## How to Reproduce

1. **Clone or download** this repository.
2. **Install dependencies** — the analysis uses `pandas`, `numpy`, `matplotlib`, and `statsmodels`. All come with Anaconda.
3. **Open `analysis.ipynb`** in JupyterLab (e.g., via Anaconda Navigator) and `Run All Cells`. The notebook reads from the already-cleaned files in `data/` and reproduces every figure and statistical result.

The four `0X_*.py` scripts are the data preparation pipeline. Their outputs are already saved in `data/`, so you do not need to re-run them to reproduce the analysis. If you want to re-pull fresh ACS data, sign up for a free Census API key at https://api.census.gov/data/key_signup.html and paste it into `config.py`.

## Methods

- **Sample:** 3 treated ZIP codes (92037 La Jolla, 92122 University City, 92126 Mira Mesa) plus 16 matched San Diego County control ZIPs more than 10 miles from campus.
- **Main specification:** two-way fixed-effects panel regression of `log(rent)` on the interaction of a treated dummy with `log(UCSD enrollment)`, with ZIP and month fixed effects and a log-income control. Standard errors clustered at the ZIP level.
- **Robustness:** wild cluster bootstrap (for the small number of clusters), leave-one-treated-out, expanded control set, expanded treated set (adding Clairemont and Pacific Beach), pre-COVID-only subsample, and an event-study specification estimating the treated-control rent gap year by year.

## Course

Created for MATH 189 (Statistical Methods), UC San Diego.
