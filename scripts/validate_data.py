"""
Data Validation Script
======================

Run this script after compiling your dataset to validate:
- Data completeness
- Variable coverage
- Missing data patterns
- Potential outliers
- Time series consistency

Usage:
    python scripts/validate_data.py
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

BASE_DIR = Path(__file__).parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"

print("=" * 80)
print("DATA VALIDATION REPORT")
print("=" * 80)

# Load the compiled dataset
data_file = DATA_PROCESSED / "infrastructure_climate_dataset_full.csv"

if not data_file.exists():
    print(f"\n✗ ERROR: Dataset not found at {data_file}")
    print("  Please run compile_infrastructure_dataset.py first")
    exit(1)

print(f"\nLoading dataset from: {data_file}")
data = pd.read_csv(data_file)
print(f"✓ Dataset loaded: {data.shape}")

# ============================================================================
# 1. BASIC STRUCTURE VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("1. BASIC STRUCTURE")
print("=" * 80)

print(f"\n✓ Total observations: {len(data):,}")
print(f"✓ Total variables: {len(data.columns)}")
print(f"✓ Countries: {data['country'].nunique()}")
print(f"✓ Years covered: {data['year'].min()}-{data['year'].max()}")
print(f"✓ Year span: {data['year'].max() - data['year'].min() + 1} years")

# Expected coverage
expected_countries = 33
expected_years = 20  # 2005-2024
expected_obs = expected_countries * expected_years

print(f"\nExpected observations: {expected_obs}")
print(f"Actual observations: {len(data)}")
coverage_pct = (len(data) / expected_obs * 100)
print(f"Coverage: {coverage_pct:.1f}%")

if coverage_pct < 95:
    print("⚠ WARNING: Coverage is less than 95%")

# ============================================================================
# 2. COUNTRY COVERAGE
# ============================================================================

print("\n" + "=" * 80)
print("2. COUNTRY COVERAGE")
print("=" * 80)

country_obs = data.groupby('country').size().sort_values(ascending=False)
print(f"\nObservations per country:")
print(country_obs.to_string())

# Countries with incomplete data
incomplete = country_obs[country_obs < expected_years]
if len(incomplete) > 0:
    print(f"\n⚠ {len(incomplete)} countries have incomplete data:")
    print(incomplete.to_string())
else:
    print(f"\n✓ All countries have complete year coverage")

# ============================================================================
# 3. VARIABLE COVERAGE
# ============================================================================

print("\n" + "=" * 80)
print("3. VARIABLE COVERAGE BY SOURCE")
print("=" * 80)

# Count variables by source
wb_vars = [col for col in data.columns if not col.startswith('Ember_') and not col.startswith('PPI_') and not col.startswith('OWID_')]
ember_vars = [col for col in data.columns if col.startswith('Ember_')]
ppi_vars = [col for col in data.columns if col.startswith('PPI_')]
owid_vars = [col for col in data.columns if col.startswith('OWID_')]

print(f"\nWorld Bank (WDI + WGI): {len(wb_vars)} variables")
print(f"Ember Energy: {len(ember_vars)} variables")
print(f"PPI: {len(ppi_vars)} variables")
print(f"OWID: {len(owid_vars)} variables")

# Check for critical variables
critical_vars = [
    'PPI_ICT_Investment_USD',
    'GDP_constant_2015_USD',
    'Renewable_electricity_output_pct_total',
    'Governance_Index',
]

print("\nCritical variables check:")
for var in critical_vars:
    if var in data.columns:
        non_null = data[var].notna().sum()
        pct = (non_null / len(data) * 100)
        status = "✓" if pct > 50 else "⚠"
        print(f"  {status} {var}: {non_null}/{len(data)} ({pct:.1f}%)")
    else:
        print(f"  ✗ {var}: NOT FOUND")

# ============================================================================
# 4. MISSING DATA ANALYSIS
# ============================================================================

print("\n" + "=" * 80)
print("4. MISSING DATA ANALYSIS")
print("=" * 80)

missing = data.isnull().sum()
missing_pct = (missing / len(data) * 100)
missing_summary = pd.DataFrame({
    'Missing_Count': missing,
    'Missing_Pct': missing_pct
})
missing_summary = missing_summary[missing_summary['Missing_Count'] > 0].sort_values('Missing_Pct', ascending=False)

print(f"\nVariables with missing data: {len(missing_summary)}/{len(data.columns)}")

# Categorize by missing percentage
high_missing = missing_summary[missing_summary['Missing_Pct'] > 50]
medium_missing = missing_summary[(missing_summary['Missing_Pct'] > 20) & (missing_summary['Missing_Pct'] <= 50)]
low_missing = missing_summary[(missing_summary['Missing_Pct'] > 0) & (missing_summary['Missing_Pct'] <= 20)]

print(f"\nMissing data severity:")
print(f"  High (>50%): {len(high_missing)} variables")
print(f"  Medium (20-50%): {len(medium_missing)} variables")
print(f"  Low (<20%): {len(low_missing)} variables")

if len(high_missing) > 0:
    print(f"\n⚠ Variables with >50% missing data:")
    print(high_missing.head(10).to_string())

# ============================================================================
# 5. PPI DATA VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("5. PPI ICT INVESTMENT DATA")
print("=" * 80)

if 'PPI_ICT_Investment_USD' in data.columns:
    ppi_data = data[data['PPI_ICT_Investment_USD'].notna()]
    print(f"\nObservations with PPI investment data: {len(ppi_data)}")
    print(f"Countries with PPI data: {ppi_data['country'].nunique()}")
    print(f"Years covered: {ppi_data['year'].min()}-{ppi_data['year'].max()}")

    # Summary statistics
    print(f"\nPPI Investment Summary:")
    print(f"  Total investment: ${ppi_data['PPI_ICT_Investment_USD'].sum():,.0f}")
    print(f"  Mean annual investment: ${ppi_data['PPI_ICT_Investment_USD'].mean():,.0f}")
    print(f"  Median annual investment: ${ppi_data['PPI_ICT_Investment_USD'].median():,.0f}")
    print(f"  Max annual investment: ${ppi_data['PPI_ICT_Investment_USD'].max():,.0f}")

    # Projects
    if 'PPI_ICT_Project_Count' in data.columns:
        print(f"\nTotal projects: {ppi_data['PPI_ICT_Project_Count'].sum():,.0f}")
        print(f"Mean projects per country-year: {ppi_data['PPI_ICT_Project_Count'].mean():.1f}")

    # Coverage by country
    ppi_by_country = ppi_data.groupby('country').agg({
        'PPI_ICT_Investment_USD': ['count', 'sum', 'mean']
    }).round(0)
    ppi_by_country.columns = ['Years_with_data', 'Total_Investment', 'Avg_Investment']
    print(f"\nPPI Coverage by Country:")
    print(ppi_by_country.to_string())

else:
    print("\n⚠ WARNING: PPI investment data not found")
    print("  This is your primary dependent variable!")
    print("  Check that the PPI file was in data/raw/")

# ============================================================================
# 6. EMBER ENERGY DATA VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("6. EMBER ENERGY DATA")
print("=" * 80)

if len(ember_vars) > 0:
    print(f"\n✓ Found {len(ember_vars)} Ember variables")

    # Sample Ember variables
    key_ember = [v for v in ember_vars if 'intensity' in v.lower() or 'emission' in v.lower()]
    if key_ember:
        print(f"\nKey Ember variables (sample):")
        for var in key_ember[:5]:
            non_null = data[var].notna().sum()
            pct = (non_null / len(data) * 100)
            print(f"  {var}: {pct:.1f}% coverage")
else:
    print("\n⚠ WARNING: No Ember energy data found")
    print("  Check Ember API key and connection")

# ============================================================================
# 7. OUTLIER DETECTION
# ============================================================================

print("\n" + "=" * 80)
print("7. OUTLIER DETECTION")
print("=" * 80)

# Check for extreme values in key variables
outlier_checks = {
    'GDP_growth_annual_pct': (-50, 50),
    'FDI_net_inflows_current_USD': (None, None),  # Can be negative
    'Renewable_electricity_output_pct_total': (0, 100),
}

print("\nChecking for potential outliers...")
outliers_found = False

for var, (min_val, max_val) in outlier_checks.items():
    if var in data.columns:
        var_data = data[var].dropna()
        if len(var_data) > 0:
            if min_val is not None:
                below_min = var_data[var_data < min_val]
                if len(below_min) > 0:
                    print(f"  ⚠ {var}: {len(below_min)} values below {min_val}")
                    outliers_found = True

            if max_val is not None:
                above_max = var_data[var_data > max_val]
                if len(above_max) > 0:
                    print(f"  ⚠ {var}: {len(above_max)} values above {max_val}")
                    outliers_found = True

if not outliers_found:
    print("  ✓ No obvious outliers detected in key variables")

# ============================================================================
# 8. TIME SERIES CONSISTENCY
# ============================================================================

print("\n" + "=" * 80)
print("8. TIME SERIES CONSISTENCY")
print("=" * 80)

# Check for gaps in time series
print("\nChecking for time series gaps...")
gaps_found = False

for country in data['country'].unique():
    country_data = data[data['country'] == country]
    years = sorted(country_data['year'].unique())

    if len(years) > 1:
        expected_years = list(range(min(years), max(years) + 1))
        missing_years = set(expected_years) - set(years)

        if missing_years:
            print(f"  ⚠ {country}: Missing years {sorted(missing_years)}")
            gaps_found = True

if not gaps_found:
    print("  ✓ No gaps in time series")

# ============================================================================
# 9. DERIVED VARIABLES VALIDATION
# ============================================================================

print("\n" + "=" * 80)
print("9. DERIVED VARIABLES")
print("=" * 80)

derived_vars = [
    'Energy_Score',
    'Governance_Index',
    'Digital_Demand_Index',
    'GDP_Log',
    'Trade_Openness'
]

print("\nDerived variables check:")
for var in derived_vars:
    if var in data.columns:
        non_null = data[var].notna().sum()
        pct = (non_null / len(data) * 100)
        status = "✓" if pct > 0 else "✗"
        print(f"  {status} {var}: {pct:.1f}% coverage")
    else:
        print(f"  ✗ {var}: NOT FOUND (check script)")

# ============================================================================
# 10. OVERALL ASSESSMENT
# ============================================================================

print("\n" + "=" * 80)
print("10. OVERALL ASSESSMENT")
print("=" * 80)

issues = []
warnings = []

# Check critical issues
if 'PPI_ICT_Investment_USD' not in data.columns:
    issues.append("Primary DV (PPI investment) not found")
elif data['PPI_ICT_Investment_USD'].notna().sum() < 50:
    warnings.append("Limited PPI investment data (<50 observations)")

if len(ember_vars) == 0:
    warnings.append("No Ember energy data found")

if coverage_pct < 90:
    warnings.append(f"Low overall coverage ({coverage_pct:.1f}%)")

if len(high_missing) > 20:
    warnings.append(f"{len(high_missing)} variables with >50% missing data")

# Print assessment
if len(issues) > 0:
    print("\n✗ CRITICAL ISSUES:")
    for issue in issues:
        print(f"  - {issue}")
else:
    print("\n✓ No critical issues found")

if len(warnings) > 0:
    print("\n⚠ WARNINGS:")
    for warning in warnings:
        print(f"  - {warning}")
else:
    print("✓ No warnings")

if len(issues) == 0 and len(warnings) == 0:
    print("\n" + "=" * 80)
    print("✓✓✓ DATASET VALIDATION PASSED ✓✓✓")
    print("=" * 80)
    print("\nYour dataset is ready for analysis!")
    print(f"Main file: {data_file}")
else:
    print("\n" + "=" * 80)
    print("⚠ VALIDATION COMPLETED WITH WARNINGS")
    print("=" * 80)
    print("\nPlease review the issues above before proceeding.")

print("\n" + "=" * 80)
print("VALIDATION COMPLETE")
print("=" * 80)
