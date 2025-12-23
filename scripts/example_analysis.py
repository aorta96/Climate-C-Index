"""
Example Analysis Script
=======================

This script demonstrates how to use the compiled infrastructure dataset
for panel regression analysis.

It includes:
1. Data loading and exploration
2. Climate C Index construction
3. Descriptive statistics
4. Panel regression models
5. Visualization

Usage:
    python scripts/example_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_PROCESSED = BASE_DIR / "data" / "processed"

print("=" * 80)
print("INFRASTRUCTURE INVESTMENT & CLIMATE READINESS")
print("Example Analysis")
print("=" * 80)

# ============================================================================
# 1. LOAD DATA
# ============================================================================

print("\n1. Loading data...")
data = pd.read_csv(DATA_PROCESSED / "infrastructure_climate_dataset_full.csv")
print(f"   ✓ Loaded {len(data):,} observations")

# ============================================================================
# 2. DATA PREPARATION
# ============================================================================

print("\n2. Preparing data...")

# Create a working dataset with key variables
analysis_vars = [
    'country', 'country_code', 'year', 'Tier',
    'PPI_ICT_Investment_USD', 'PPI_ICT_Investment_Log', 'PPI_ICT_Project_Count',
    'GDP_constant_2015_USD', 'GDP_per_capita_constant_2015_USD', 'GDP_growth_annual_pct',
    'Renewable_electricity_output_pct_total', 'Renewable_energy_consumption_pct_total',
    'Energy_use_kg_of_oil_equivalent_per_capita',
    'Governance_Index', 'Regulatory_Quality_percentile', 'Rule_of_Law_percentile',
    'Digital_Demand_Index', 'Individuals_using_Internet_pct',
    'FDI_net_inflows_current_USD', 'Trade_Openness',
    'Population_total', 'Urban_population_pct_total'
]

# Keep only available variables
available_vars = [v for v in analysis_vars if v in data.columns]
df = data[available_vars].copy()

print(f"   ✓ Selected {len(available_vars)} variables for analysis")

# ============================================================================
# 3. CONSTRUCT CLIMATE C INDEX
# ============================================================================

print("\n3. Constructing Climate C Index...")

# Components of Climate C
climate_components = {
    'Renewable_electricity_output_pct_total': 0.35,  # Energy sustainability
    'Governance_Index': 0.30,                         # Institutional quality
    'Digital_Demand_Index': 0.20,                     # Digital readiness
    'Urban_population_pct_total': 0.15                # Urbanization proxy for infrastructure readiness
}

# Check which components are available
available_components = {k: v for k, v in climate_components.items() if k in df.columns}
print(f"   Available components: {len(available_components)}/{len(climate_components)}")

if len(available_components) >= 2:
    # Normalize each component to 0-100 scale
    for var in available_components.keys():
        var_data = df[var].dropna()
        if len(var_data) > 0:
            df[f'{var}_norm'] = 100 * (df[var] - var_data.min()) / (var_data.max() - var_data.min())

    # Calculate weighted Climate C Index
    total_weight = sum(available_components.values())
    df['Climate_C_Index'] = 0

    for var, weight in available_components.items():
        df['Climate_C_Index'] += df[f'{var}_norm'] * (weight / total_weight)

    print(f"   ✓ Climate C Index created")
    print(f"     Range: {df['Climate_C_Index'].min():.1f} - {df['Climate_C_Index'].max():.1f}")
    print(f"     Mean: {df['Climate_C_Index'].mean():.1f}")
else:
    print("   ⚠ Insufficient components for Climate C Index")
    df['Climate_C_Index'] = np.nan

# ============================================================================
# 4. DESCRIPTIVE STATISTICS
# ============================================================================

print("\n4. Descriptive Statistics")
print("=" * 80)

# Key variables summary
key_vars = [
    'PPI_ICT_Investment_USD',
    'Climate_C_Index',
    'GDP_per_capita_constant_2015_USD',
    'Renewable_electricity_output_pct_total',
    'Governance_Index'
]
key_vars = [v for v in key_vars if v in df.columns]

if len(key_vars) > 0:
    summary = df[key_vars].describe().T
    summary['missing_pct'] = (df[key_vars].isnull().sum() / len(df) * 100)
    print("\nKey Variables Summary:")
    print(summary.to_string())

# Investment by tier
if 'PPI_ICT_Investment_USD' in df.columns and 'Tier' in df.columns:
    print("\n" + "-" * 80)
    print("ICT Investment by Tier:")
    print("-" * 80)
    tier_stats = df.groupby('Tier').agg({
        'PPI_ICT_Investment_USD': ['count', 'sum', 'mean', 'median']
    }).round(0)
    tier_stats.columns = ['Observations', 'Total_Investment', 'Mean', 'Median']
    print(tier_stats.to_string())

# ============================================================================
# 5. CORRELATION ANALYSIS
# ============================================================================

print("\n5. Correlation Analysis")
print("=" * 80)

corr_vars = [
    'PPI_ICT_Investment_Log',
    'Climate_C_Index',
    'GDP_per_capita_constant_2015_USD',
    'Governance_Index',
    'Digital_Demand_Index'
]
corr_vars = [v for v in corr_vars if v in df.columns]

if len(corr_vars) >= 2:
    corr_matrix = df[corr_vars].corr()
    print("\nCorrelation Matrix:")
    print(corr_matrix.round(3).to_string())

    # Save correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Correlation Matrix: Key Variables', fontsize=14, pad=20)
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED / 'correlation_matrix.png', dpi=300, bbox_inches='tight')
    print("\n   ✓ Correlation matrix saved: correlation_matrix.png")
    plt.close()

# ============================================================================
# 6. PANEL REGRESSION ANALYSIS
# ============================================================================

print("\n6. Panel Regression Analysis")
print("=" * 80)

# Create regression dataset (only complete cases for key variables)
reg_vars = [
    'country_code', 'year',
    'PPI_ICT_Investment_Log',
    'Climate_C_Index',
    'GDP_per_capita_constant_2015_USD',
    'Governance_Index',
    'Trade_Openness'
]
reg_vars = [v for v in reg_vars if v in df.columns]

if 'PPI_ICT_Investment_Log' in df.columns and 'Climate_C_Index' in df.columns:
    reg_df = df[reg_vars].dropna()
    print(f"\nRegression sample: {len(reg_df)} observations")

    # Log transform GDP per capita if needed
    if 'GDP_per_capita_constant_2015_USD' in reg_df.columns:
        reg_df['GDP_per_capita_Log'] = np.log(reg_df['GDP_per_capita_constant_2015_USD'])

    # Model 1: Baseline (Climate C + GDP)
    print("\n" + "-" * 80)
    print("Model 1: Baseline (Climate C + GDP)")
    print("-" * 80)

    formula = 'PPI_ICT_Investment_Log ~ Climate_C_Index'
    if 'GDP_per_capita_Log' in reg_df.columns:
        formula += ' + GDP_per_capita_Log'

    try:
        model1 = smf.ols(formula, data=reg_df).fit(
            cov_type='cluster',
            cov_kwds={'groups': reg_df['country_code']}
        )
        print(model1.summary())
    except Exception as e:
        print(f"   ⚠ Model estimation failed: {e}")

    # Model 2: Full specification
    if all(v in reg_df.columns for v in ['Governance_Index', 'Trade_Openness', 'GDP_per_capita_Log']):
        print("\n" + "-" * 80)
        print("Model 2: Full Specification")
        print("-" * 80)

        formula = ('PPI_ICT_Investment_Log ~ Climate_C_Index + GDP_per_capita_Log + '
                   'Governance_Index + Trade_Openness')

        try:
            model2 = smf.ols(formula, data=reg_df).fit(
                cov_type='cluster',
                cov_kwds={'groups': reg_df['country_code']}
            )
            print(model2.summary())
        except Exception as e:
            print(f"   ⚠ Model estimation failed: {e}")

else:
    print("   ⚠ Insufficient data for regression analysis")
    print("   Check that PPI data and Climate C components are available")

# ============================================================================
# 7. VISUALIZATION
# ============================================================================

print("\n7. Creating Visualizations")
print("=" * 80)

# Plot 1: Climate C Index over time by tier
if 'Climate_C_Index' in df.columns and 'Tier' in df.columns:
    plt.figure(figsize=(12, 6))
    for tier in sorted(df['Tier'].unique()):
        tier_data = df[df['Tier'] == tier].groupby('year')['Climate_C_Index'].mean()
        plt.plot(tier_data.index, tier_data.values, marker='o', label=tier, linewidth=2)

    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Climate C Index', fontsize=12)
    plt.title('Climate C Index Evolution by Country Tier', fontsize=14, pad=20)
    plt.legend(title='Country Tier', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED / 'climate_c_by_tier.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: climate_c_by_tier.png")
    plt.close()

# Plot 2: ICT Investment vs Climate C scatter
if 'PPI_ICT_Investment_Log' in df.columns and 'Climate_C_Index' in df.columns:
    plt.figure(figsize=(10, 6))

    scatter_df = df[['PPI_ICT_Investment_Log', 'Climate_C_Index', 'Tier']].dropna()

    for tier in sorted(scatter_df['Tier'].unique()):
        tier_data = scatter_df[scatter_df['Tier'] == tier]
        plt.scatter(tier_data['Climate_C_Index'], tier_data['PPI_ICT_Investment_Log'],
                   label=tier, alpha=0.6, s=50)

    # Add regression line
    from scipy import stats
    x = scatter_df['Climate_C_Index']
    y = scatter_df['PPI_ICT_Investment_Log']
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    line = slope * x + intercept
    plt.plot(x, line, 'r--', alpha=0.8, linewidth=2, label=f'Fit (R²={r_value**2:.3f})')

    plt.xlabel('Climate C Index', fontsize=12)
    plt.ylabel('Log(ICT Investment)', fontsize=12)
    plt.title('Digital Infrastructure Investment vs Climate Readiness', fontsize=14, pad=20)
    plt.legend(title='Country Tier', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(DATA_PROCESSED / 'investment_vs_climate_c.png', dpi=300, bbox_inches='tight')
    print("   ✓ Saved: investment_vs_climate_c.png")
    plt.close()

# ============================================================================
# 8. EXPORT RESULTS
# ============================================================================

print("\n8. Exporting Results")
print("=" * 80)

# Save analysis dataset
analysis_file = DATA_PROCESSED / "analysis_dataset.csv"
df.to_csv(analysis_file, index=False)
print(f"   ✓ Analysis dataset saved: {analysis_file}")

# Save summary statistics
if len(key_vars) > 0:
    summary_file = DATA_PROCESSED / "analysis_summary_stats.csv"
    summary.to_csv(summary_file)
    print(f"   ✓ Summary statistics saved: {summary_file}")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE!")
print("=" * 80)

print("""
Files created:
  - analysis_dataset.csv: Dataset with Climate C Index
  - correlation_matrix.png: Variable correlations
  - climate_c_by_tier.png: Climate C trends by tier
  - investment_vs_climate_c.png: Scatter plot

Next steps:
  1. Review the regression results above
  2. Check the visualizations in data/processed/
  3. Extend the analysis with:
     - Fixed effects models
     - Interaction terms (e.g., Climate_C × Green_Finance)
     - Robustness checks
     - Additional control variables
""")
