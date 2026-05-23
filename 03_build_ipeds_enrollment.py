"""
03_build_ipeds_enrollment.py
=============================
Extract UCSD (UNITID=110680) Fall enrollment from IPEDS EF Complete Data Files
for years 2010-2023, and append the Fall 2024 value from UCSD's official
Campus Profile (IPEDS 2024 data not yet released as of project start).

Source: NCES IPEDS Complete Data Files
  https://nces.ed.gov/ipeds/use-the-data/download-access-database
  Direct download: https://nces.ed.gov/ipeds/datacenter/data/EF{YYYY}A.zip

Extraction logic:
  - EFALEVEL=1, LINE=29, LSTUDY=4 ->  Grand total all students
  - EFALEVEL=2                    ->  Total undergraduate
  - EFALEVEL=12                   ->  Total graduate

Output: data/ucsd_enrollment.csv
"""

import pandas as pd
import os

DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "ipeds_raw")
UCSD_UNITID = 110680

records = []

for year in range(2010, 2024):
    fname = os.path.join(RAW_DIR, f"ef{year}a.csv")
    if not os.path.exists(fname):
        print(f"  {year}: missing file, skip")
        continue
    df = pd.read_csv(fname, encoding="latin-1", low_memory=False)
    ucsd = df[df.UNITID == UCSD_UNITID]
    if len(ucsd) == 0:
        print(f"  {year}: no UCSD rows!")
        continue

    total_row = ucsd[ucsd.EFALEVEL == 1]
    ug_row = ucsd[ucsd.EFALEVEL == 2]
    grad_row = ucsd[ucsd.EFALEVEL == 12]

    total = int(total_row.EFTOTLT.iloc[0]) if len(total_row) else None
    ug = int(ug_row.EFTOTLT.iloc[0]) if len(ug_row) else None
    grad = int(grad_row.EFTOTLT.iloc[0]) if len(grad_row) else None

    records.append({
        "year": year,
        "total_enrollment": total,
        "undergrad": ug,
        "graduate": grad,
        "source": "IPEDS EF{}A.csv (NCES)".format(year),
    })
    print(f"  {year}: total={total}, ug={ug}, grad={grad}")

# Fall 2024: IPEDS Provisional release (March 2026) contains Fall 2024 data
# in the Access database, but a direct CSV is not yet available. The values
# below are sourced from the IPEDS Institution Profile web interface
# (https://nces.ed.gov/ipeds/datacenter/InstitutionProfile.aspx?unitId=110680)
# which displays the same Fall 2024 figures from the provisional release.
records.append({
    "year": 2024,
    "total_enrollment": 44256,
    "undergrad": 34955,
    "graduate": 9301,
    "source": "IPEDS Institution Profile Fall 2024 (Provisional release, March 2026)",
})
print(f"  2024: total=44256 (IPEDS Institution Profile, Provisional release)")

out = pd.DataFrame(records)
out_path = os.path.join(DATA_DIR, "ucsd_enrollment.csv")
out.to_csv(out_path, index=False)
print(f"\nSaved: {out_path} ({len(out)} rows)")
print()
print(out.to_string(index=False))
print()
print(f"Growth 2010 -> 2024: {(out.total_enrollment.iloc[-1] / out.total_enrollment.iloc[0] - 1) * 100:.1f}%")
