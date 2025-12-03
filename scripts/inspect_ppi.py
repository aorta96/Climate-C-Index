"""
Quick PPI Data Inspector
========================

This script quickly inspects your PPI dataset to show column names,
sample data, and help debug any issues before running the full compilation.

Usage:
    python scripts/inspect_ppi.py
"""

import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"

ppi_file = DATA_RAW / "Public_Participation_in_Infrastructure-2023-H1-Stata.dta"

print("=" * 80)
print("PPI DATA INSPECTOR")
print("=" * 80)

if not ppi_file.exists():
    print(f"\n✗ ERROR: PPI file not found at {ppi_file}")
    print("  Please place the PPI Stata file in data/raw/")
    exit(1)

print(f"\nLoading: {ppi_file}")
print(f"File size: {ppi_file.stat().st_size / 1024 / 1024:.1f} MB")

try:
    ppi = pd.read_stata(ppi_file)
    print(f"✓ Loaded successfully: {ppi.shape}")
except Exception as e:
    print(f"✗ Error loading file: {e}")
    exit(1)

print("\n" + "=" * 80)
print("COLUMN NAMES")
print("=" * 80)

print(f"\nTotal columns: {len(ppi.columns)}\n")

for i, col in enumerate(ppi.columns, 1):
    dtype = ppi[col].dtype
    non_null = ppi[col].notna().sum()
    pct = (non_null / len(ppi) * 100)
    print(f"{i:2d}. {col:40s} {str(dtype):10s} {non_null:6d}/{len(ppi):6d} ({pct:5.1f}%)")

print("\n" + "=" * 80)
print("KEY COLUMNS DETECTION")
print("=" * 80)

# Detect key columns
col_lower = {col.lower(): col for col in ppi.columns}

# Country columns
country_candidates = ['country', 'countryname', 'economy', 'economyname']
code_candidates = ['countrycode', 'economycode', 'iso3', 'countryiso3']

print("\nCountry columns:")
for candidate in country_candidates:
    if candidate in col_lower:
        col = col_lower[candidate]
        unique = ppi[col].nunique()
        print(f"  ✓ {col}: {unique} unique values")
        print(f"    Sample: {', '.join(map(str, ppi[col].dropna().unique()[:5]))}")

print("\nCountry code columns:")
for candidate in code_candidates:
    if candidate in col_lower:
        col = col_lower[candidate]
        unique = ppi[col].nunique()
        print(f"  ✓ {col}: {unique} unique values")
        print(f"    Sample: {', '.join(map(str, ppi[col].dropna().unique()[:10]))}")

# Sector columns
sector_candidates = ['sector', 'sectormain', 'primarysector']
print("\nSector columns:")
for candidate in sector_candidates:
    if candidate in col_lower:
        col = col_lower[candidate]
        unique = ppi[col].nunique()
        print(f"  ✓ {col}: {unique} unique sectors")
        for sector in sorted(ppi[col].unique()):
            count = (ppi[col] == sector).sum()
            print(f"      - {sector}: {count} projects")

# Year/Date columns
year_candidates = ['year', 'financialclosureyear', 'closureyear']
date_candidates = ['financialclosuredate', 'closuredate', 'date']

print("\nYear/Date columns:")
for candidate in year_candidates:
    if candidate in col_lower:
        col = col_lower[candidate]
        print(f"  ✓ {col}")
        print(f"    Range: {ppi[col].min():.0f} - {ppi[col].max():.0f}")

for candidate in date_candidates:
    if candidate in col_lower:
        col = col_lower[candidate]
        print(f"  ✓ {col}")
        print(f"    Sample: {', '.join(map(str, ppi[col].dropna().head(3)))}")

# Investment columns
investment_candidates = ['totalinvestment', 'investment', 'totalcommitment', 'commitmentamount']
print("\nInvestment columns:")
for candidate in investment_candidates:
    if candidate in col_lower:
        col = col_lower[candidate]
        print(f"  ✓ {col}")
        print(f"    Range: ${ppi[col].min():,.0f} - ${ppi[col].max():,.0f}")
        print(f"    Mean: ${ppi[col].mean():,.0f}")
        print(f"    Total: ${ppi[col].sum():,.0f}")

print("\n" + "=" * 80)
print("SAMPLE DATA (First 5 rows)")
print("=" * 80)

# Show first few rows with key columns
key_cols = []
for candidate in country_candidates + code_candidates + sector_candidates + year_candidates + investment_candidates:
    if candidate in col_lower:
        key_cols.append(col_lower[candidate])
        if len(key_cols) >= 6:
            break

if key_cols:
    print("\n" + ppi[key_cols].head().to_string())
else:
    print("\n" + ppi.head().to_string())

print("\n" + "=" * 80)
print("INSPECTION COMPLETE")
print("=" * 80)
print("\nYou can now run the full compilation script:")
print("  python scripts/compile_infrastructure_dataset.py")
