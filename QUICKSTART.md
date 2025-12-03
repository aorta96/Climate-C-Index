# Quick Start Guide

## Get Started in 5 Minutes

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Get Your PPI Data
1. You mentioned you already have the PPI data file
2. Copy it to: `data/raw/Public_Participation_in_Infrastructure-2023-H1-Stata.dta`

### Step 3: Run the Compilation Script
```bash
cd Climate-C-Index
python scripts/compile_infrastructure_dataset.py
```

The script will:
- ✓ Fetch World Bank WDI data (27 indicators)
- ✓ Fetch World Bank WGI data (6 governance indicators)
- ✓ Fetch Ember energy data (generation, emissions, carbon intensity)
- ✓ Process your PPI ICT infrastructure investment data
- ✓ Merge everything into a single panel dataset
- ✓ Create derived variables (indices, log transformations)
- ✓ Generate data quality reports
- ✓ Save in both CSV and Stata formats

### Step 4: Check Your Output
Look in `data/processed/` for:
- `infrastructure_climate_dataset_full.csv` - Your main dataset
- `infrastructure_climate_dataset_full.dta` - Stata format
- `data_dictionary.csv` - Variable documentation
- `summary_statistics.csv` - Descriptive statistics

## What You Get

### Dependent Variable (Your Main DV)
- **PPI_ICT_Investment_USD** - Annual private investment in ICT/digital infrastructure
- **PPI_ICT_Investment_Log** - Log-transformed for regression analysis
- **PPI_ICT_Project_Count** - Number of ICT projects per country-year

### Climate C Index Components

1. **Energy Sustainability**
   - Renewable electricity % of total generation
   - Renewable energy consumption
   - Energy_Score (normalized index)

2. **Governance Quality**
   - Governance_Index (from WGI indicators)
   - Regulatory quality, rule of law, corruption control

3. **Digital Readiness**
   - Digital_Demand_Index
   - Internet penetration, broadband subscriptions

4. **Environmental Intensity**
   - Carbon intensity of electricity (Ember data)
   - Power sector emissions
   - Energy use per capita

### Control Variables
- GDP (level and growth)
- FDI inflows
- Trade openness
- Financial development
- Human capital
- Population and urbanization

## Expected Dataset Size
- **Countries**: 33 emerging markets
- **Years**: 2005-2024 (20 years)
- **Observations**: ~660 country-year pairs
- **Variables**: 50+ indicators

## Common Issues & Solutions

### Issue: "PPI file not found"
**Solution**: Make sure the PPI Stata file is in `data/raw/` with the exact filename

### Issue: World Bank API timeout
**Solution**: The script has retry logic. If it fails, wait a few minutes and try again during off-peak hours

### Issue: Ember API rate limit
**Solution**: The script fetches data sequentially with built-in delays. This is normal and takes 2-3 minutes

## Next Steps for Your Analysis

### 1. Explore the Data
```python
import pandas as pd

# Load the dataset
data = pd.read_stata('data/processed/infrastructure_climate_dataset_full.dta')

# Check your key variables
print(data[['country', 'year', 'PPI_ICT_Investment_Log', 'Renewable_electricity_output_pct_total']].head(20))

# Summary statistics
print(data[['PPI_ICT_Investment_USD', 'GDP_per_capita_Log', 'Governance_Index']].describe())
```

### 2. Construct Your Climate C Index
```python
# Example: Simple weighted average
weights = {
    'Energy_Score': 0.3,
    'Governance_Index': 0.3,
    'Digital_Demand_Index': 0.2,
    # Add more components based on your framework
}

# Normalize all components to 0-100 scale first
for var in weights.keys():
    data[f'{var}_norm'] = 100 * (data[var] - data[var].min()) / (data[var].max() - data[var].min())

# Calculate Climate C Index
data['Climate_C_Index'] = sum(data[f'{var}_norm'] * weight for var, weight in weights.items())
```

### 3. Run Your Baseline Regression
```python
import statsmodels.formula.api as smf

# Example panel regression
model = smf.ols(
    'PPI_ICT_Investment_Log ~ Climate_C_Index + GDP_Log + Governance_Index + Trade_Openness + C(year)',
    data=data
).fit(cov_type='cluster', cov_kwds={'groups': data['country_code']})

print(model.summary())
```

## Getting Help

If something isn't working:
1. Check the full README.md for detailed documentation
2. Review the data_dictionary.csv to understand your variables
3. Look at summary_statistics.csv to check data coverage
4. Open an issue on GitHub with the error message

## Time Estimate

- Script runtime: 3-5 minutes (depends on API speed)
- Your time: 5 minutes setup + review outputs
- Total: ~10 minutes to get your full panel dataset ready for analysis

---

**You're all set!** Run the script and start analyzing the relationship between climate readiness and digital infrastructure investment.
