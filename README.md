# Climate C-Index: Infrastructure Investment Dataset

This repository compiles a comprehensive panel dataset for analyzing digital infrastructure investment and climate readiness in emerging markets.

## Overview

This dataset combines multiple international data sources to support research on:
- Digital infrastructure investment patterns
- Climate readiness and sustainability metrics
- Green finance development
- Governance and macroeconomic controls
- Environmental intensity of infrastructure

## Dataset Coverage

- **Countries**: 33 emerging markets across 4 tiers
- **Time Period**: 2005-2024
- **Observations**: ~660 country-year observations
- **Variables**: 50+ indicators from multiple sources

### Country Tiers

**Tier 1** (8 countries): Paraguay, El Salvador, Nicaragua, Serbia, Bulgaria, Laos, Lebanon, Kyrgyzstan

**Tier 2** (10 countries): Peru, Malaysia, Ghana, Mozambique, Angola, Nepal, Venezuela, Zambia, Sri Lanka, Mali

**Tier 3** (9 countries): Argentina, Algeria, Iraq, Morocco, Kenya, South Africa, Myanmar, Colombia, Uzbekistan

**Tier 4** (6 countries): Egypt, Ethiopia, Philippines, Vietnam, Iran, Turkey

## Data Sources

### 1. World Bank World Development Indicators (WDI)
- GDP and economic growth indicators
- Energy and climate metrics
- Digital infrastructure and connectivity
- Financial development indicators
- Trade, FDI, and fiscal variables
- Human capital and inequality measures

### 2. World Bank Worldwide Governance Indicators (WGI)
- Political stability
- Government effectiveness
- Regulatory quality
- Rule of law
- Control of corruption
- Voice and accountability

### 3. Ember Energy Data API
- Electricity generation by source
- Carbon intensity of electricity
- Power sector emissions
- Renewable energy capacity

### 4. World Bank Private Participation in Infrastructure (PPI) Database
- ICT/digital infrastructure investments
- Project counts and investment volumes
- Primary dependent variable for the analysis

## Repository Structure

```
Climate-C-Index/
├── data/
│   ├── raw/                    # Raw data files (not in git)
│   └── processed/              # Compiled datasets
├── scripts/
│   ├── compile_infrastructure_dataset.py    # Main compilation script
│   └── validate_data.py                     # Data validation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/aorta96/Climate-C-Index.git
cd Climate-C-Index
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Obtain PPI Data

1. Download the World Bank PPI Database from:
   https://ppi.worldbank.org/en/ppidata

2. Place the Stata file in `data/raw/`:
   ```
   data/raw/Public_Participation_in_Infrastructure-2023-H1-Stata.dta
   ```

### 4. Run the Compilation Script

```bash
python scripts/compile_infrastructure_dataset.py
```

This will:
- Fetch World Bank WDI and WGI data
- Fetch Ember energy data via API
- Process your PPI data
- Merge all sources into a single panel dataset
- Generate data quality reports
- Save outputs in CSV and Stata formats

## Output Files

After running the script, you'll find in `data/processed/`:

1. **infrastructure_climate_dataset_full.csv**
   - Complete panel dataset with all variables
   - Ready for analysis in any statistical software

2. **infrastructure_climate_dataset_full.dta**
   - Stata format for econometric analysis
   - Compatible with Stata 15+

3. **data_dictionary.csv**
   - Variable names, types, and sources
   - Missing data statistics
   - Use this to understand your dataset

4. **summary_statistics.csv**
   - Descriptive statistics for all variables
   - Mean, median, min, max, standard deviation
   - Missing data percentages

## Key Variables

### Dependent Variable (DV)
- `PPI_ICT_Investment_USD` - Annual ICT infrastructure investment
- `PPI_ICT_Investment_Log` - Log-transformed investment
- `PPI_ICT_Project_Count` - Number of ICT projects

### Climate C Components

**Energy Sustainability:**
- `Renewable_electricity_output_pct_total`
- `Renewable_energy_consumption_pct_total`
- `Energy_Score` (derived index)

**Governance & Institutions:**
- `Governance_Index` (derived from WGI indicators)
- `Regulatory_Quality_percentile`
- `Rule_of_Law_percentile`

**Digital Readiness:**
- `Digital_Demand_Index` (derived)
- `Individuals_using_Internet_pct`
- `Fixed_broadband_subscriptions_per_100`

**Environmental Intensity:**
- `Ember_Intensity_*` - Carbon intensity metrics
- `Ember_Emissions_*` - Power sector emissions
- `Energy_use_kg_of_oil_equivalent_per_capita`

### Control Variables

**Macroeconomic:**
- `GDP_Log`, `GDP_per_capita_Log`
- `GDP_growth_annual_pct`
- `FDI_Log`
- `Trade_Openness`

**Financial Development:**
- `Domestic_credit_to_private_sector_pct_GDP`
- `Market_capitalization_pct_GDP`

**Human Capital:**
- `Tertiary_education_enrollment_pct_gross`
- `Education_expenditure_pct_GDP`

## Next Steps

### Additional Data Sources to Consider

1. **ND-GAIN Climate Index**
   - Climate vulnerability scores
   - Climate readiness scores
   - Download from: https://gain.nd.edu/our-work/country-index/download-data/

2. **WRI Aqueduct Water Risk**
   - Water stress indicators
   - Baseline water stress by country
   - Download from: https://www.wri.org/aqueduct/data

3. **Climate Bonds Initiative**
   - Green bond issuance data
   - Sustainable finance metrics
   - Contact: https://www.climatebonds.net/

4. **Carbon Pricing Dashboard**
   - National carbon pricing policies
   - World Bank: https://carbonpricingdashboard.worldbank.org/

### Recommended Workflow

1. **Explore the Data**
   ```python
   import pandas as pd
   data = pd.read_stata('data/processed/infrastructure_climate_dataset_full.dta')
   print(data.head())
   print(data.describe())
   ```

2. **Check Missing Data Patterns**
   ```python
   # Review the data dictionary
   data_dict = pd.read_csv('data/processed/data_dictionary.csv')
   print(data_dict[data_dict['Missing_Pct'] > 50])
   ```

3. **Construct Additional Indices**
   - Climate C composite index
   - Green finance depth indicator
   - Additional interaction terms

4. **Run Panel Regressions**
   - Fixed effects models
   - Random effects models
   - Two-way clustering by country and year

## Troubleshooting

### World Bank API Issues
If you encounter connection errors with the World Bank API:
- Check your internet connection
- Try running during off-peak hours
- Consider downloading WDI/WGI data manually from: https://databank.worldbank.org/

### Ember API Issues
- Verify the API key is valid
- Check rate limits (60 requests per minute)
- Use the provided retry logic in the script

### PPI Data Issues
- Ensure the Stata file is in `data/raw/`
- Check that the file name matches exactly
- Verify you have the latest PPI database version

## Citation

If you use this dataset, please cite:

- World Bank. (2023). World Development Indicators. Washington, DC: World Bank.
- Kaufmann, D., Kraay, A., & Mastruzzi, M. (2023). Worldwide Governance Indicators. World Bank.
- Ember. (2024). Global Electricity Review. Ember Energy.
- World Bank. (2023). Private Participation in Infrastructure Database. Washington, DC: World Bank.

## Contact

For questions or issues:
- Open an issue on GitHub
- Email: [your contact]

## License

This dataset compilation is provided for research purposes. Please check individual data source licenses for specific terms of use.

---

**Last Updated**: December 3, 2025
