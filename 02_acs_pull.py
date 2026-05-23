"""
02_acs_pull.py
==============
Pull ACS 5-Year Estimates for ZCTA-level demographic and housing variables.

Variables:
  - B19013_001E: Median household income (past 12 months)
  - B25003_001E: Total occupied housing units
  - B25003_003E: Renter-occupied housing units
  - B01003_001E: Total population
  - B25010_001E: Average household size

Years: 2017, 2019, 2021, 2023 (ACS 5-year estimates centered on each)

Outputs:
  - data/acs_sd_panel.csv  (long-format SD ZCTA x year panel)
"""

import pandas as pd
import requests
import os
from config import CENSUS_API_KEY

# -----------------------------------------------------------------------------
# Setup
# -----------------------------------------------------------------------------
DATA_DIR = "data"

# Load SD County ZIPs (the 40 usable ones from Step 1)
sd_long = pd.read_csv(os.path.join(DATA_DIR, "zori_sd_long.csv"))
SD_ZIPS = sorted(sd_long["zip"].unique().tolist())
SD_ZIPS_STR = set(f"{z:05d}" for z in SD_ZIPS)
print(f"SD County usable ZIPs: {len(SD_ZIPS)}")

# Variables to pull
VARIABLES = {
    "B19013_001E": "median_income",
    "B25003_001E": "occupied_total",
    "B25003_003E": "renter_occupied",
    "B01003_001E": "population",
    "B25010_001E": "avg_household_size",
}

YEARS = [2017, 2019, 2021, 2023]

# -----------------------------------------------------------------------------
# Pull ACS by year
# -----------------------------------------------------------------------------
all_dfs = []
for year in YEARS:
    print(f"\nPulling ACS 5-year {year}...")
    var_str = ",".join(VARIABLES.keys())
    url = (
        f"https://api.census.gov/data/{year}/acs/acs5"
        f"?get=NAME,{var_str}"
        f"&for=zip%20code%20tabulation%20area:*"
        f"&key={CENSUS_API_KEY}"
    )
    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"  ERROR for {year}: {e}")
        continue

    df = pd.DataFrame(data[1:], columns=data[0])
    print(f"  Total US ZCTAs returned: {len(df)}")

    # Filter to SD County ZIPs
    zcta_col = "zip code tabulation area"
    df = df[df[zcta_col].isin(SD_ZIPS_STR)].copy()
    print(f"  Filtered to SD ZCTAs: {len(df)}")

    df = df.rename(columns={**VARIABLES, zcta_col: "zip"})
    df["zip"] = df["zip"].astype(int)
    df["acs_year"] = year

    # Cast numerics
    for v in VARIABLES.values():
        df[v] = pd.to_numeric(df[v], errors="coerce")

    # Derived: renter share
    df["renter_share"] = df["renter_occupied"] / df["occupied_total"]

    all_dfs.append(df)

# -----------------------------------------------------------------------------
# Combine and save
# -----------------------------------------------------------------------------
acs = pd.concat(all_dfs, ignore_index=True)
out_cols = ["zip", "acs_year", "median_income", "renter_share",
            "population", "avg_household_size",
            "occupied_total", "renter_occupied"]
acs = acs[out_cols].sort_values(["zip", "acs_year"])

out_path = os.path.join(DATA_DIR, "acs_sd_panel.csv")
acs.to_csv(out_path, index=False)
print(f"\nSaved: {out_path} ({len(acs)} rows)")

# -----------------------------------------------------------------------------
# Quick summary
# -----------------------------------------------------------------------------
print("\n=== Sample: 2023 ACS for treated ZIPs + a few controls ===")
sample = acs[(acs.acs_year == 2023) &
             (acs["zip"].isin([92122, 92037, 92126, 91913, 91942, 91910]))]
print(sample.to_string(index=False))

print("\nDONE.")
