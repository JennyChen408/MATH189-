"""
04_control_selection.py
=======================
Select matched control ZIP codes for the analysis.

Steps:
  1. Load Census Gazetteer (ZCTA centroids + land area).
  2. Compute great-circle distance from each SD ZIP centroid to UCSD campus.
  3. Compute population density (ACS population / land area sq mi).
  4. Candidate controls = SD ZIPs > 10 miles from UCSD (excludes treated).
  5. Match: standardize baseline (2017 ACS) income, renter share, and
     log density; keep the candidate controls closest (in standardized
     Euclidean distance) to the treated group's average profile.

Output:
  - data/zip_geo.csv          (all 40 SD ZIPs: centroid, distance, density)
  - data/control_zips.csv     (selected matched control ZIPs)
"""

import pandas as pd
import numpy as np
import os
from config import TREATED_ZIPS

DATA_DIR = "data"

# UCSD campus coordinates (Geisel Library area)
UCSD_LAT, UCSD_LON = 32.8801, -117.2340

N_CONTROLS = 16          # number of matched controls to keep
DIST_THRESHOLD = 10.0    # miles; controls must be farther than this

# -----------------------------------------------------------------------------
# 1. Load Gazetteer and ACS, restrict to our 40 analysis ZIPs
# -----------------------------------------------------------------------------
gaz = pd.read_csv(os.path.join(DATA_DIR, "2024_Gaz_zcta_national.txt"),
                  sep="\t", dtype={"GEOID": str})
gaz.columns = [c.strip() for c in gaz.columns]
gaz["zip"] = gaz["GEOID"].astype(int)
gaz = gaz[["zip", "ALAND_SQMI", "INTPTLAT", "INTPTLONG"]]

sd_long = pd.read_csv(os.path.join(DATA_DIR, "zori_sd_long.csv"))
analysis_zips = sorted(sd_long["zip"].unique().tolist())
gaz = gaz[gaz["zip"].isin(analysis_zips)].copy()
print(f"Analysis ZIPs with geo data: {len(gaz)} / {len(analysis_zips)}")

# -----------------------------------------------------------------------------
# 2. Great-circle distance to UCSD (Haversine formula)
# -----------------------------------------------------------------------------
def haversine_miles(lat1, lon1, lat2, lon2):
    R = 3958.8  # Earth radius in miles
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

gaz["dist_to_ucsd"] = haversine_miles(
    gaz["INTPTLAT"], gaz["INTPTLONG"], UCSD_LAT, UCSD_LON)

# -----------------------------------------------------------------------------
# 3. Population density from baseline ACS (2017)
# -----------------------------------------------------------------------------
acs = pd.read_csv(os.path.join(DATA_DIR, "acs_sd_panel.csv"))
acs_base = acs[acs["acs_year"] == 2017][
    ["zip", "median_income", "renter_share", "population"]].copy()

geo = gaz.merge(acs_base, on="zip", how="left")
geo["pop_density"] = geo["population"] / geo["ALAND_SQMI"]
geo["log_density"] = np.log(geo["pop_density"])
geo["treated"] = geo["zip"].isin(TREATED_ZIPS).astype(int)

geo.to_csv(os.path.join(DATA_DIR, "zip_geo.csv"), index=False)
print(f"Saved: data/zip_geo.csv")

# -----------------------------------------------------------------------------
# 4. Treated profile + candidate controls
# -----------------------------------------------------------------------------
treated = geo[geo["treated"] == 1]
print("\nTreated ZIPs:")
for _, r in treated.iterrows():
    print(f"  {r['zip']}: dist={r['dist_to_ucsd']:.1f}mi, "
          f"income=${r['median_income']:,.0f}, "
          f"renter={r['renter_share']:.0%}, "
          f"density={r['pop_density']:,.0f}/sqmi")

candidates = geo[(geo["treated"] == 0) &
                 (geo["dist_to_ucsd"] > DIST_THRESHOLD)].copy()
candidates = candidates.dropna(subset=["median_income", "renter_share",
                                       "log_density"])
print(f"\nCandidate controls (>{DIST_THRESHOLD}mi, complete data): "
      f"{len(candidates)}")

# -----------------------------------------------------------------------------
# 5. Standardized nearest-neighbor matching
# -----------------------------------------------------------------------------
match_vars = ["median_income", "renter_share", "log_density"]

# Standardize using all SD ZIPs (treated + candidates) as reference
ref = geo.dropna(subset=match_vars)
means = ref[match_vars].mean()
stds = ref[match_vars].std()

treated_z = (treated[match_vars] - means) / stds
treated_centroid = treated_z.mean()

cand_z = (candidates[match_vars] - means) / stds
candidates["match_dist"] = np.sqrt(
    ((cand_z - treated_centroid) ** 2).sum(axis=1))

candidates = candidates.sort_values("match_dist")
selected = candidates.head(N_CONTROLS).copy()

selected[["zip", "dist_to_ucsd", "median_income", "renter_share",
          "pop_density", "match_dist"]].to_csv(
    os.path.join(DATA_DIR, "control_zips.csv"), index=False)
print(f"\nSaved: data/control_zips.csv ({len(selected)} matched controls)")

print("\nSelected matched control ZIPs:")
for _, r in selected.iterrows():
    print(f"  {r['zip']}: dist={r['dist_to_ucsd']:.1f}mi, "
          f"income=${r['median_income']:,.0f}, "
          f"renter={r['renter_share']:.0%}, "
          f"density={r['pop_density']:,.0f}/sqmi, "
          f"match_dist={r['match_dist']:.2f}")

# -----------------------------------------------------------------------------
# 6. Balance check: treated vs selected controls
# -----------------------------------------------------------------------------
print("\n=== Balance check (mean values) ===")
print(f"{'Variable':<18}{'Treated':>14}{'Matched Ctrl':>16}")
for v in ["dist_to_ucsd", "median_income", "renter_share", "pop_density"]:
    t_mean = treated[v].mean()
    c_mean = selected[v].mean()
    print(f"  {v:<16}{t_mean:>14,.1f}{c_mean:>16,.1f}")
print("\nDONE.")
