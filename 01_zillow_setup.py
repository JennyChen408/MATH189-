"""
01_zillow_setup.py
==================
Step 1: Load Zillow ZORI, filter to San Diego County, reshape to long format,
and produce a first EDA plot of treated vs control rent trends.

Outputs:
- data/zori_sd_long.csv  (clean long-format panel for SD County)
- figures/01_rent_trends_treated_vs_control.png
- figures/01_treated_zip_rent_levels.png
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# -----------------------------------------------------------------------------
# Paths
# -----------------------------------------------------------------------------
DATA_DIR = "data"
FIG_DIR = "figures"
os.makedirs(FIG_DIR, exist_ok=True)

# -----------------------------------------------------------------------------
# Treated ZIPs
# Revised from the original proposal after data availability checks:
#   - 92121 (Sorrento Valley) excluded: only 2 months of ZORI data, area is
#     predominantly biotech/commercial with very little rental housing.
#   - 92126 (Mira Mesa) added: widely recognized as a major UCSD student
#     rental area, full 136 months of ZORI data.
#   - 92109 (Pacific Beach) moved to robustness expanded set due to
#     tourism/lifestyle confounders.
# Main treated set focuses on the three cleanest student-rental ZIPs.
# -----------------------------------------------------------------------------
TREATED_ZIPS = [92122, 92037, 92126]  # UTC, La Jolla, Mira Mesa
TREATED_LABELS = {92122: "UTC (92122)", 92037: "La Jolla (92037)",
                  92126: "Mira Mesa (92126)"}

# Robustness expanded set (used in robustness checks, not main analysis)
ROBUST_EXTRA_ZIPS = [92117, 92109]  # Clairemont, Pacific Beach

# -----------------------------------------------------------------------------
# 1. Load Zillow ZORI and filter to SD County
# -----------------------------------------------------------------------------
print("Loading Zillow ZORI...")
zori = pd.read_csv(os.path.join(DATA_DIR, "zori_zip.csv"))
print(f"  US ZIPs total: {len(zori)}")

sd = zori[zori.CountyName == "San Diego County"].copy()
print(f"  SD County ZIPs: {len(sd)}")

# -----------------------------------------------------------------------------
# 2. Reshape wide -> long
# -----------------------------------------------------------------------------
meta_cols = ["RegionID", "SizeRank", "RegionName", "RegionType", "StateName",
             "State", "City", "Metro", "CountyName"]
date_cols = [c for c in sd.columns if c not in meta_cols]

sd_long = sd.melt(
    id_vars=meta_cols, value_vars=date_cols,
    var_name="month", value_name="zori"
)
sd_long["month"] = pd.to_datetime(sd_long["month"])
sd_long["zip"] = sd_long["RegionName"].astype(int)
sd_long = sd_long.dropna(subset=["zori"])
print(f"  Long-format rows (non-missing): {len(sd_long)}")

# -----------------------------------------------------------------------------
# 3. Tag treated vs candidate control
#    Candidate control: SD ZIPs that are NOT treated and have at least 100
#    months of data (so they have a usable time series)
# -----------------------------------------------------------------------------
zip_obs = sd_long.groupby("zip").size()
usable_zips = zip_obs[zip_obs >= 100].index.tolist()
print(f"  ZIPs with >= 100 months of data: {len(usable_zips)}")

sd_long = sd_long[sd_long["zip"].isin(usable_zips)].copy()
sd_long["treated"] = sd_long["zip"].isin(TREATED_ZIPS).astype(int)

candidate_control_zips = [z for z in usable_zips if z not in TREATED_ZIPS]
print(f"  Candidate control ZIPs: {len(candidate_control_zips)}")

# Save the long panel
out_path = os.path.join(DATA_DIR, "zori_sd_long.csv")
sd_long.to_csv(out_path, index=False)
print(f"  Saved: {out_path}")

# -----------------------------------------------------------------------------
# 4. Figure 1: Treated vs Control mean rent over time
# -----------------------------------------------------------------------------
agg = (sd_long.groupby(["month", "treated"])["zori"]
       .mean().unstack())
agg.columns = ["Control (all other SD ZIPs)", "Treated (UTC/La Jolla/PB)"]

fig, ax = plt.subplots(figsize=(10, 6))
agg.plot(ax=ax, linewidth=2)
ax.set_title("Mean Monthly Rent (ZORI): UCSD-Adjacent vs Other SD County ZIPs\n"
             "2015-01 to 2026-04", fontsize=13)
ax.set_xlabel("Month")
ax.set_ylabel("Mean ZORI ($/month)")
ax.axvline(pd.Timestamp("2020-03-01"), color="red", linestyle="--",
           alpha=0.5, label="COVID onset")
ax.legend(loc="upper left")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "01_rent_trends_treated_vs_control.png"),
            dpi=150)
print(f"  Saved figure: 01_rent_trends_treated_vs_control.png")
plt.close()

# -----------------------------------------------------------------------------
# 5. Figure 2: Each treated ZIP separately
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 6))
for z in TREATED_ZIPS:
    sub = sd_long[sd_long["zip"] == z].sort_values("month")
    ax.plot(sub["month"], sub["zori"], label=TREATED_LABELS[z], linewidth=2)
ax.set_title("Monthly Rent (ZORI) for UCSD-Adjacent ZIP Codes\n"
             "2015-01 to 2026-04", fontsize=13)
ax.set_xlabel("Month")
ax.set_ylabel("ZORI ($/month)")
ax.axvline(pd.Timestamp("2020-03-01"), color="red", linestyle="--",
           alpha=0.5, label="COVID onset")
ax.legend(loc="upper left")
ax.grid(True, alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "01_treated_zip_rent_levels.png"), dpi=150)
print(f"  Saved figure: 01_treated_zip_rent_levels.png")
plt.close()

# -----------------------------------------------------------------------------
# 6. Quick summary stats
# -----------------------------------------------------------------------------
print("\n=== Summary: rent levels by ZIP (first vs last observation) ===")
for z in TREATED_ZIPS + candidate_control_zips[:5]:
    sub = sd_long[sd_long["zip"] == z].sort_values("month")
    if len(sub) > 0:
        first, last = sub.iloc[0], sub.iloc[-1]
        growth = (last["zori"] / first["zori"] - 1) * 100
        label = TREATED_LABELS.get(z, f"ZIP {z}")
        tag = "TREATED" if z in TREATED_ZIPS else "control"
        print(f"  [{tag:7s}] {label:25s}  "
              f"{first['month'].date()}: ${first['zori']:7.0f}  ->  "
              f"{last['month'].date()}: ${last['zori']:7.0f}  ({growth:+.1f}%)")

print("\nDONE.")
