"""
config.py
=========
Configuration constants.

The Census API key is required only by `02_acs_pull.py` to download fresh
ACS data; the notebook itself reads from the already-saved CSV and does not
need the key. Sign up for a free key at:
https://api.census.gov/data/key_signup.html
"""

CENSUS_API_KEY = "YOUR_CENSUS_API_KEY_HERE"

# Main treated ZIPs (UCSD-adjacent student rental areas)
TREATED_ZIPS = [92122, 92037, 92126]  # UTC, La Jolla, Mira Mesa

# Robustness expansion (added in robustness checks)
ROBUST_EXTRA_ZIPS = [92117, 92109]  # Clairemont, Pacific Beach
