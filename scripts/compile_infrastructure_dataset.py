"""
Climate C-Index: Infrastructure Investment Dataset Compilation
==============================================================

This script compiles a comprehensive panel dataset for analyzing digital
infrastructure investment and climate readiness in emerging markets.

Data Sources:
1. World Bank WDI - Macroeconomic, infrastructure, and climate indicators
2. World Bank WGI - Governance indicators
3. Ember Energy - Electricity generation, emissions, and carbon intensity
4. World Bank PPI - Private Participation in Infrastructure (ICT/digital sector)

Author: Climate C-Index Research Team
Date: 2025-12-03
"""

import numpy as np
import pandas as pd
import warnings
import requests
import os
from pathlib import Path

warnings.filterwarnings('ignore')

# Setup paths
BASE_DIR = Path(__file__).parent.parent
DATA_RAW = BASE_DIR / "data" / "raw"
DATA_PROCESSED = BASE_DIR / "data" / "processed"

# Create directories if they don't exist
DATA_RAW.mkdir(parents=True, exist_ok=True)
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)

print("=" * 80)
print("CLIMATE C-INDEX: INFRASTRUCTURE INVESTMENT DATASET COMPILATION")
print("=" * 80)

# ============================================================================
# COUNTRY DEFINITIONS
# ============================================================================

tier_1 = {
    "Paraguay": "PRY",
    "El Salvador": "SLV",
    "Nicaragua": "NIC",
    "Serbia": "SRB",
    "Bulgaria": "BGR",
    "Lao PDR": "LAO",
    "Lebanon": "LBN",
    "Kyrgyz Republic": "KGZ"
}

tier_2 = {
    "Peru": "PER",
    "Malaysia": "MYS",
    "Ghana": "GHA",
    "Mozambique": "MOZ",
    "Angola": "AGO",
    "Nepal": "NPL",
    "Venezuela, RB": "VEN",
    "Zambia": "ZMB",
    "Sri Lanka": "LKA",
    "Mali": "MLI"
}

tier_3 = {
    "Argentina": "ARG",
    "Algeria": "DZA",
    "Iraq": "IRQ",
    "Morocco": "MAR",
    "Kenya": "KEN",
    "South Africa": "ZAF",
    "Myanmar": "MMR",
    "Colombia": "COL",
    "Uzbekistan": "UZB"
}

tier_4 = {
    "Egypt, Arab Rep.": "EGY",
    "Ethiopia": "ETH",
    "Philippines": "PHL",
    "Vietnam": "VNM",
    "Iran, Islamic Rep.": "IRN",
    "Turkey": "TUR"
}

# Combine all countries
all_countries = {**tier_1, **tier_2, **tier_3, **tier_4}
country_codes = list(all_countries.values())

print(f"\nTarget countries: {len(country_codes)}")
print(f"  Tier 1: {len(tier_1)}")
print(f"  Tier 2: {len(tier_2)}")
print(f"  Tier 3: {len(tier_3)}")
print(f"  Tier 4: {len(tier_4)}")

# Year range
START_YEAR = 2005
END_YEAR = 2024
time_range = range(START_YEAR, END_YEAR + 1)

print(f"\nTime period: {START_YEAR}-{END_YEAR}")

# ============================================================================
# WORLD BANK DATA
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 1: WORLD BANK DATA")
print("=" * 80)

# Import wbgapi
try:
    import wbgapi as wb
    print("✓ wbgapi library loaded")
except ImportError:
    print("✗ wbgapi not installed. Installing...")
    os.system("pip install wbgapi")
    import wbgapi as wb

# WDI Indicators
wdi_indicator_names = {
    # Population & Demographics
    "SP.POP.TOTL": "Population_total",
    "SP.URB.TOTL.IN.ZS": "Urban_population_pct_total",

    # GDP & Economic Growth
    "NY.GDP.MKTP.KD": "GDP_constant_2015_USD",
    "NY.GDP.MKTP.CD": "GDP_current_USD",
    "NY.GDP.PCAP.KD": "GDP_per_capita_constant_2015_USD",
    "NY.GDP.MKTP.KD.ZG": "GDP_growth_annual_pct",

    # Energy & Climate
    "EG.ELC.ACCS.ZS": "Access_to_Electricity_pct",
    "EG.USE.PCAP.KG.OE": "Energy_use_kg_of_oil_equivalent_per_capita",
    "EG.FEC.RNEW.ZS": "Renewable_energy_consumption_pct_total",
    "EG.ELC.RNEW.ZS": "Renewable_electricity_output_pct_total",

    # Digital Infrastructure & Connectivity
    "IT.NET.USER.ZS": "Individuals_using_Internet_pct",
    "IT.CEL.SETS.P2": "Mobile_cellular_subscriptions_per_100",
    "IT.NET.BBND.P2": "Fixed_broadband_subscriptions_per_100",

    # Financial Development
    "FS.AST.PRVT.GD.ZS": "Domestic_credit_to_private_sector_pct_GDP",
    "CM.MKT.LCAP.GD.ZS": "Market_capitalization_pct_GDP",
    "FR.INR.LNDP": "Lending_interest_rate_pct",

    # Trade & FDI
    "NE.TRD.GNFS.ZS": "Trade_pct_GDP",
    "BX.KLT.DINV.CD.WD": "FDI_net_inflows_current_USD",
    "NE.EXP.GNFS.ZS": "Exports_goods_services_pct_GDP",
    "NE.IMP.GNFS.ZS": "Imports_goods_services_pct_GDP",

    # Fiscal & Debt
    "GC.DOD.TOTL.GD.ZS": "Central_government_debt_pct_GDP",
    "GC.TAX.TOTL.GD.ZS": "Tax_revenue_pct_GDP",
    "DT.DOD.DECT.GD.ZS": "External_debt_stocks_pct_GNI",

    # Inequality & Poverty
    "SI.POV.GINI": "GINI_Index",

    # Human Capital
    "SE.TER.ENRR": "Tertiary_education_enrollment_pct_gross",
    "SE.XPD.TOTL.GD.ZS": "Education_expenditure_pct_GDP",

    # Infrastructure
    "IS.ROD.PAVE.ZS": "Roads_paved_pct_total",
}

# WGI Indicators
wgi_indicator_names = {
    "PV.PER.RNK": "Political_Stability_percentile",
    "GE.PER.RNK": "Government_Effectiveness_percentile",
    "RQ.PER.RNK": "Regulatory_Quality_percentile",
    "RL.PER.RNK": "Rule_of_Law_percentile",
    "CC.PER.RNK": "Control_of_Corruption_percentile",
    "VA.PER.RNK": "Voice_and_Accountability_percentile"
}

print(f"\nFetching {len(wdi_indicator_names)} WDI indicators...")
print(f"Fetching {len(wgi_indicator_names)} WGI indicators...")

# Fetch WDI data
print("\nFetching WDI data...")
wdi_data_raw = wb.data.DataFrame(
    list(wdi_indicator_names.keys()),
    country_codes,
    time=time_range,
    labels=True,
    numericTimeKeys=True
)
print(f"✓ WDI data fetched: {wdi_data_raw.shape}")

# Fetch WGI data
print("\nFetching WGI data...")
wgi_data_raw = wb.data.DataFrame(
    list(wgi_indicator_names.keys()),
    country_codes,
    time=time_range,
    labels=True,
    numericTimeKeys=True,
    db=3
)
print(f"✓ WGI data fetched: {wgi_data_raw.shape}")

# Process WDI data
print("\nProcessing WDI data...")
wdi_data_raw = wdi_data_raw.reset_index()

country_col = None
series_col = None

for col in ['country', 'economy', 'Country', 'Economy']:
    if col in wdi_data_raw.columns:
        country_col = col
        break

for col in ['series', 'indicator', 'Series', 'Indicator']:
    if col in wdi_data_raw.columns:
        series_col = col
        break

year_cols = [col for col in wdi_data_raw.columns
             if col not in [country_col, series_col, 'Country', 'Series']
             and (isinstance(col, (int, np.integer)) or (isinstance(col, str) and col.isdigit()))]

wdi_long = wdi_data_raw.melt(
    id_vars=[country_col, series_col],
    value_vars=year_cols,
    var_name='year',
    value_name='value'
)

wdi_long['year'] = wdi_long['year'].astype(int)

wdi_data = wdi_long.pivot_table(
    index=[country_col, 'year'],
    columns=series_col,
    values='value'
).reset_index()

if country_col != 'country':
    wdi_data = wdi_data.rename(columns={country_col: 'country'})

wdi_data.columns.name = None

# Rename indicator columns
for code, name in wdi_indicator_names.items():
    matching_cols = [col for col in wdi_data.columns if code in str(col)]
    if matching_cols:
        wdi_data = wdi_data.rename(columns={matching_cols[0]: name})

print(f"✓ WDI data processed: {wdi_data.shape}")

# Process WGI data
print("\nProcessing WGI data...")
wgi_data_raw = wgi_data_raw.reset_index()

country_col_wgi = None
series_col_wgi = None

for col in ['country', 'economy', 'Country', 'Economy']:
    if col in wgi_data_raw.columns:
        country_col_wgi = col
        break

for col in ['series', 'indicator', 'Series', 'Indicator']:
    if col in wgi_data_raw.columns:
        series_col_wgi = col
        break

year_cols = [col for col in wgi_data_raw.columns
             if col not in [country_col_wgi, series_col_wgi, 'Country', 'Series']
             and (isinstance(col, (int, np.integer)) or (isinstance(col, str) and col.isdigit()))]

wgi_long = wgi_data_raw.melt(
    id_vars=[country_col_wgi, series_col_wgi],
    value_vars=year_cols,
    var_name='year',
    value_name='value'
)

wgi_long['year'] = wgi_long['year'].astype(int)

wgi_data = wgi_long.pivot_table(
    index=[country_col_wgi, 'year'],
    columns=series_col_wgi,
    values='value'
).reset_index()

if country_col_wgi != 'country':
    wgi_data = wgi_data.rename(columns={country_col_wgi: 'country'})

wgi_data.columns.name = None

# Rename WGI columns
for code, name in wgi_indicator_names.items():
    matching_cols = [col for col in wgi_data.columns if code in str(col)]
    if matching_cols:
        wgi_data = wgi_data.rename(columns={matching_cols[0]: name})

print(f"✓ WGI data processed: {wgi_data.shape}")

# ============================================================================
# EMBER ENERGY DATA
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 2: EMBER ENERGY DATA")
print("=" * 80)

API_KEY = "4d03d06d-a89e-4aba-4310-26e4197abd5b"
BASE_URL = "https://api.ember-energy.org"

def fetch_ember(endpoint, countries, start_year=2000, end_year=2024):
    """Fetch data from Ember Energy API"""
    all_records = []
    errors = []

    for i, code in enumerate(countries, 1):
        url = (
            f"{BASE_URL}/v1/{endpoint}"
            f"?entity_code={code}&is_aggregate_series=false"
            f"&start_date={start_year}&end_date={end_year}"
            f"&api_key={API_KEY}"
        )

        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                payload = response.json()
                if "data" in payload:
                    for rec in payload["data"]:
                        rec["country_code"] = code
                        all_records.append(rec)
                else:
                    errors.append(f"{code}: No 'data' field")
            else:
                errors.append(f"{code}: HTTP {response.status_code}")
        except Exception as e:
            errors.append(f"{code}: {str(e)}")

        if i % 10 == 0:
            print(f"  Progress: {i}/{len(countries)} countries")

    if errors:
        print(f"  ⚠ Errors: {len(errors)}")
        for err in errors[:5]:  # Show first 5 errors
            print(f"    {err}")

    return pd.DataFrame(all_records)

# Fetch Ember datasets
print("\nFetching electricity generation data...")
gen_df = fetch_ember("electricity-generation/yearly", country_codes, START_YEAR, END_YEAR)
print(f"✓ Generation data: {gen_df.shape}")

print("\nFetching carbon intensity data...")
intensity_df = fetch_ember("carbon-intensity/yearly", country_codes, START_YEAR, END_YEAR)
print(f"✓ Carbon intensity data: {intensity_df.shape}")

print("\nFetching power sector emissions data...")
emissions_df = fetch_ember("power-sector-emissions/yearly", country_codes, START_YEAR, END_YEAR)
print(f"✓ Emissions data: {emissions_df.shape}")

# Process Ember data
def process_ember_data(df, prefix):
    """Process Ember dataframe into wide format"""
    if df.empty:
        return pd.DataFrame()

    # Identify value columns
    id_cols = ['country_code', 'year', 'date']
    existing_id_cols = [col for col in id_cols if col in df.columns]
    value_cols = [col for col in df.columns if col not in existing_id_cols]

    # Extract year from date if needed
    if 'date' in df.columns and 'year' not in df.columns:
        df['year'] = pd.to_datetime(df['date']).dt.year

    # Select and rename columns
    keep_cols = ['country_code', 'year'] + value_cols
    keep_cols = [col for col in keep_cols if col in df.columns]

    df_proc = df[keep_cols].copy()

    # Rename value columns with prefix
    rename_dict = {col: f'{prefix}_{col}' for col in value_cols if col in df_proc.columns}
    df_proc = df_proc.rename(columns=rename_dict)

    # Aggregate by country-year (take mean if multiple entries)
    group_cols = ['country_code', 'year']
    df_proc = df_proc.groupby(group_cols, as_index=False).mean(numeric_only=True)

    return df_proc

print("\nProcessing Ember data...")
ember_gen = process_ember_data(gen_df, 'Ember_Gen')
ember_intensity = process_ember_data(intensity_df, 'Ember_Intensity')
ember_emissions = process_ember_data(emissions_df, 'Ember_Emissions')

# Merge Ember datasets
ember_data = ember_gen
if not ember_intensity.empty:
    ember_data = pd.merge(ember_data, ember_intensity, on=['country_code', 'year'], how='outer')
if not ember_emissions.empty:
    ember_data = pd.merge(ember_data, ember_emissions, on=['country_code', 'year'], how='outer')

print(f"✓ Ember data merged: {ember_data.shape}")

# ============================================================================
# PPI DATA (ICT/DIGITAL INFRASTRUCTURE)
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 3: WORLD BANK PPI DATA (ICT/DIGITAL INFRASTRUCTURE)")
print("=" * 80)

ppi_file = DATA_RAW / "Public_Participation_in_Infrastructure-2023-H1-Stata.dta"

if ppi_file.exists():
    print(f"Loading PPI data from {ppi_file}...")
    ppi_raw = pd.read_stata(ppi_file)
    print(f"✓ PPI data loaded: {ppi_raw.shape}")

    # Display all column names for debugging
    print(f"\nPPI columns available ({len(ppi_raw.columns)}):")
    print(", ".join(ppi_raw.columns[:20]))  # Show first 20 columns
    if len(ppi_raw.columns) > 20:
        print(f"  ... and {len(ppi_raw.columns) - 20} more")

    # Detect column names (case-insensitive)
    col_lower = {col.lower(): col for col in ppi_raw.columns}

    # Find country column
    country_col = None
    for potential in ['country', 'countryname', 'economy', 'economyname']:
        if potential in col_lower:
            country_col = col_lower[potential]
            break

    # Find country code column
    code_col = None
    for potential in ['countrycode', 'economycode', 'iso3', 'countryiso3']:
        if potential in col_lower:
            code_col = col_lower[potential]
            break

    # Find sector column
    sector_col = None
    for potential in ['sector', 'sectormain', 'primarysector']:
        if potential in col_lower:
            sector_col = col_lower[potential]
            break

    # Find year column
    year_col = None
    for potential in ['year', 'financialclosureyear', 'closureyear', 'fcy']:
        if potential in col_lower:
            year_col = col_lower[potential]
            break

    # Find date column if no year
    date_col = None
    if not year_col:
        for potential in ['financialclosuredate', 'closuredate', 'date']:
            if potential in col_lower:
                date_col = col_lower[potential]
                break

    # Find investment column
    investment_col = None
    for potential in ['totalinvestment', 'investment', 'totalcommitment', 'commitmentamount']:
        if potential in col_lower:
            investment_col = col_lower[potential]
            break

    # Find project ID column
    project_col = None
    for potential in ['projectid', 'id', 'project_id', 'iy']:
        if potential in col_lower:
            project_col = col_lower[potential]
            break

    print(f"\nDetected columns:")
    print(f"  Country: {country_col}")
    print(f"  Country Code: {code_col}")
    print(f"  Sector: {sector_col}")
    print(f"  Year: {year_col if year_col else (date_col + ' (will extract year)' if date_col else 'NOT FOUND')}")
    print(f"  Investment: {investment_col}")
    print(f"  Project ID: {project_col}")

    # Display available sectors if sector column found
    if sector_col and sector_col in ppi_raw.columns:
        unique_sectors = ppi_raw[sector_col].unique()
        print(f"\nAvailable sectors ({len(unique_sectors)}):")
        for sector in sorted(unique_sectors):
            count = (ppi_raw[sector_col] == sector).sum()
            print(f"  - {sector}: {count} projects")

    # Filter for ICT/Telecom sector
    if sector_col:
        # Try exact match first (faster)
        ict_exact_matches = ['ICT', 'Telecom', 'Information and Communication Technology']
        exact_match = ppi_raw[sector_col].isin(ict_exact_matches)

        if exact_match.any():
            ppi_filtered = ppi_raw[exact_match].copy()
            print(f"\n✓ Filtered for ICT/Telecom sector: {len(ppi_filtered)} projects")
        else:
            # Fall back to keyword matching
            ict_keywords = ['telecom', 'ict', 'information', 'communication', 'technology', 'digital']
            sector_mask = ppi_raw[sector_col].str.lower().str.contains('|'.join(ict_keywords), na=False)
            ppi_filtered = ppi_raw[sector_mask].copy()
            print(f"\n✓ Filtered for ICT/Telecom sector (keyword match): {len(ppi_filtered)} projects")
    else:
        print("\n⚠ Warning: Could not identify sector column, using all sectors")
        ppi_filtered = ppi_raw.copy()

    # Filter for our countries
    if country_col and code_col:
        # Try both country name and code
        country_mask = (
            ppi_filtered[country_col].isin(list(all_countries.keys())) |
            ppi_filtered[code_col].isin(country_codes)
        )
        ppi_filtered = ppi_filtered[country_mask]
    elif country_col:
        ppi_filtered = ppi_filtered[ppi_filtered[country_col].isin(list(all_countries.keys()))]
    elif code_col:
        ppi_filtered = ppi_filtered[ppi_filtered[code_col].isin(country_codes)]
    else:
        print("⚠ Warning: Could not identify country columns")

    print(f"✓ Filtered for target countries: {len(ppi_filtered)} projects")

    # Map to country codes
    name_to_code = {v: k for k, v in all_countries.items()}

    # Add alternative country name mappings for PPI database
    ppi_name_mapping = {
        'Turkiye': 'Turkey',
        'Türkiye': 'Turkey',
        'Turkey': 'Turkey',
        'Egypt, Arab Rep.': 'Egypt, Arab Rep.',
        'Egypt': 'Egypt, Arab Rep.',
        'Iran, Islamic Rep.': 'Iran, Islamic Rep.',
        'Iran': 'Iran, Islamic Rep.',
        'Venezuela, RB': 'Venezuela, RB',
        'Venezuela': 'Venezuela, RB',
        'Kyrgyz Republic': 'Kyrgyz Republic',
        'Kyrgyzstan': 'Kyrgyz Republic',
        'Lao PDR': 'Lao PDR',
        'Laos': 'Lao PDR',
    }

    if code_col and code_col in ppi_filtered.columns:
        ppi_filtered['country_code'] = ppi_filtered[code_col]
    elif country_col and country_col in ppi_filtered.columns:
        # First normalize PPI country names
        ppi_filtered['country_normalized'] = ppi_filtered[country_col].map(
            lambda x: ppi_name_mapping.get(x, x) if pd.notna(x) else x
        )
        # Then map to codes
        ppi_filtered['country_code'] = ppi_filtered['country_normalized'].map(name_to_code)

        # For any unmapped, try direct mapping
        missing_mask = ppi_filtered['country_code'].isna()
        if missing_mask.any():
            ppi_filtered.loc[missing_mask, 'country_code'] = ppi_filtered.loc[missing_mask, country_col].map(name_to_code)

    # Extract year
    if year_col and year_col in ppi_filtered.columns:
        ppi_filtered['year'] = ppi_filtered[year_col]
    elif date_col and date_col in ppi_filtered.columns:
        ppi_filtered['year'] = pd.to_datetime(ppi_filtered[date_col], errors='coerce').dt.year

    # Filter for our time period
    if 'year' in ppi_filtered.columns:
        ppi_filtered = ppi_filtered[
            (ppi_filtered['year'] >= START_YEAR) &
            (ppi_filtered['year'] <= END_YEAR)
        ]
        print(f"✓ Filtered for {START_YEAR}-{END_YEAR}: {len(ppi_filtered)} projects")

    # Aggregate by country-year
    if 'country_code' in ppi_filtered.columns and 'year' in ppi_filtered.columns:
        # Prepare aggregation
        agg_dict = {}

        if investment_col and investment_col in ppi_filtered.columns:
            agg_dict[investment_col] = 'sum'

        if project_col and project_col in ppi_filtered.columns:
            agg_dict[project_col] = 'count'
        elif len(ppi_filtered) > 0:
            # Use any column for counting if project_col not found
            agg_dict[ppi_filtered.columns[0]] = 'count'

        if agg_dict:
            ppi_aggregated = ppi_filtered.groupby(['country_code', 'year'], as_index=False).agg(agg_dict)

            # Rename columns
            if investment_col and investment_col in agg_dict:
                ppi_aggregated = ppi_aggregated.rename(columns={investment_col: 'PPI_ICT_Investment_USD'})

            if project_col and project_col in agg_dict:
                ppi_aggregated = ppi_aggregated.rename(columns={project_col: 'PPI_ICT_Project_Count'})
            else:
                # Rename the count column
                count_col = [col for col in ppi_aggregated.columns if col not in ['country_code', 'year', 'PPI_ICT_Investment_USD']]
                if count_col:
                    ppi_aggregated = ppi_aggregated.rename(columns={count_col[0]: 'PPI_ICT_Project_Count'})

            # Log transformation of investment
            if 'PPI_ICT_Investment_USD' in ppi_aggregated.columns:
                ppi_aggregated['PPI_ICT_Investment_Log'] = np.log1p(ppi_aggregated['PPI_ICT_Investment_USD'])

            print(f"\n✓ PPI data aggregated: {ppi_aggregated.shape}")
            print(f"  Countries: {ppi_aggregated['country_code'].nunique()}")
            print(f"  Years: {ppi_aggregated['year'].min():.0f}-{ppi_aggregated['year'].max():.0f}")

            if 'PPI_ICT_Investment_USD' in ppi_aggregated.columns:
                total_investment = ppi_aggregated['PPI_ICT_Investment_USD'].sum()
                print(f"  Total ICT Investment: ${total_investment:,.0f}")
                print(f"  Mean annual investment: ${ppi_aggregated['PPI_ICT_Investment_USD'].mean():,.0f}")

            if 'PPI_ICT_Project_Count' in ppi_aggregated.columns:
                total_projects = ppi_aggregated['PPI_ICT_Project_Count'].sum()
                print(f"  Total projects: {total_projects:.0f}")
        else:
            print("⚠ Warning: Could not create aggregations")
            ppi_aggregated = pd.DataFrame()
    else:
        print("⚠ Warning: Missing country_code or year columns")
        ppi_aggregated = pd.DataFrame()

else:
    print(f"⚠ PPI data file not found at {ppi_file}")
    print("  Please place the PPI Stata file in data/raw/")
    print("  Continuing without PPI data...")
    ppi_aggregated = pd.DataFrame()

# ============================================================================
# MERGE ALL DATASETS
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 4: MERGING ALL DATASETS")
print("=" * 80)

# Create country code mapping
name_to_code = {v: k for k, v in all_countries.items()}
wdi_data['country_code'] = wdi_data['country'].map(name_to_code)
wgi_data['country_code'] = wgi_data['country'].map(name_to_code)

# Start with WDI data
data = wdi_data.copy()
print(f"Starting with WDI: {data.shape}")

# Merge WGI
data = pd.merge(
    data,
    wgi_data.drop(columns=['country'], errors='ignore'),
    on=['country_code', 'year'],
    how='outer'
)
print(f"After WGI merge: {data.shape}")

# Merge Ember
if not ember_data.empty:
    data = pd.merge(
        data,
        ember_data,
        on=['country_code', 'year'],
        how='left'
    )
    print(f"After Ember merge: {data.shape}")

# Merge PPI
if not ppi_aggregated.empty:
    data = pd.merge(
        data,
        ppi_aggregated,
        on=['country_code', 'year'],
        how='left'
    )
    print(f"After PPI merge: {data.shape}")

# Add tier information
def assign_tier(country_code):
    for name, code in tier_1.items():
        if code == country_code:
            return 'Tier 1'
    for name, code in tier_2.items():
        if code == country_code:
            return 'Tier 2'
    for name, code in tier_3.items():
        if code == country_code:
            return 'Tier 3'
    for name, code in tier_4.items():
        if code == country_code:
            return 'Tier 4'
    return 'Unknown'

data['Tier'] = data['country_code'].apply(assign_tier)

# Reorder columns
cols = ['country', 'country_code', 'year', 'Tier'] + [col for col in data.columns
                                                        if col not in ['country', 'country_code', 'year', 'Tier']]
data = data[cols]

# Sort by country and year
data = data.sort_values(['country', 'year']).reset_index(drop=True)

print(f"\n✓ Final merged dataset: {data.shape}")

# ============================================================================
# CONSTRUCT DERIVED VARIABLES
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 5: CONSTRUCTING DERIVED VARIABLES")
print("=" * 80)

# Climate C Index Components
print("\nConstructing Climate C components...")

# 1. Energy Score (normalized)
energy_vars = [
    'Renewable_electricity_output_pct_total',
    'Renewable_energy_consumption_pct_total',
]
available_energy_vars = [v for v in energy_vars if v in data.columns]

if available_energy_vars:
    # Normalize each variable to 0-100 scale
    for var in available_energy_vars:
        data[f'{var}_norm'] = 100 * (data[var] - data[var].min()) / (data[var].max() - data[var].min())

    # Average the normalized scores
    norm_vars = [f'{v}_norm' for v in available_energy_vars]
    data['Energy_Score'] = data[norm_vars].mean(axis=1)
    print(f"  ✓ Energy_Score created from {len(available_energy_vars)} variables")

# 2. Governance Index
gov_vars = [
    'Regulatory_Quality_percentile',
    'Rule_of_Law_percentile',
    'Government_Effectiveness_percentile',
    'Control_of_Corruption_percentile'
]
available_gov_vars = [v for v in gov_vars if v in data.columns]

if available_gov_vars:
    data['Governance_Index'] = data[available_gov_vars].mean(axis=1)
    print(f"  ✓ Governance_Index created from {len(available_gov_vars)} variables")

# 3. Digital Demand Index
digital_vars = [
    'Individuals_using_Internet_pct',
    'Mobile_cellular_subscriptions_per_100',
    'Fixed_broadband_subscriptions_per_100'
]
available_digital_vars = [v for v in digital_vars if v in data.columns]

if available_digital_vars:
    # Normalize
    for var in available_digital_vars:
        data[f'{var}_norm'] = 100 * (data[var] - data[var].min()) / (data[var].max() - data[var].min())

    norm_vars = [f'{v}_norm' for v in available_digital_vars]
    data['Digital_Demand_Index'] = data[norm_vars].mean(axis=1)
    print(f"  ✓ Digital_Demand_Index created from {len(available_digital_vars)} variables")

# 4. Trade Openness
if 'Exports_goods_services_pct_GDP' in data.columns and 'Imports_goods_services_pct_GDP' in data.columns:
    data['Trade_Openness'] = data['Exports_goods_services_pct_GDP'] + data['Imports_goods_services_pct_GDP']
    print("  ✓ Trade_Openness created")

# 5. Log transformations for key variables
log_vars = {
    'GDP_constant_2015_USD': 'GDP_Log',
    'GDP_per_capita_constant_2015_USD': 'GDP_per_capita_Log',
    'Population_total': 'Population_Log',
    'FDI_net_inflows_current_USD': 'FDI_Log'
}

for var, new_name in log_vars.items():
    if var in data.columns:
        data[new_name] = np.log1p(data[var])
        print(f"  ✓ {new_name} created")

print("\n✓ Derived variables constructed")

# ============================================================================
# DATA QUALITY REPORT
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 6: DATA QUALITY REPORT")
print("=" * 80)

print(f"\nFinal Dataset Summary:")
print(f"  Total observations: {len(data):,}")
print(f"  Countries: {data['country'].nunique()}")
print(f"  Years: {data['year'].min()}-{data['year'].max()}")
print(f"  Total variables: {len(data.columns)}")

# Count variables by source
wb_vars = [col for col in data.columns if not col.startswith('Ember_') and not col.startswith('PPI_')]
ember_vars = [col for col in data.columns if col.startswith('Ember_')]
ppi_vars = [col for col in data.columns if col.startswith('PPI_')]
derived_vars = ['Energy_Score', 'Governance_Index', 'Digital_Demand_Index', 'Trade_Openness'] + \
               [col for col in data.columns if col.endswith('_Log') or col.endswith('_norm')]

print(f"\nVariables by source:")
print(f"  World Bank (WDI + WGI): {len(wb_vars)}")
print(f"  Ember Energy: {len(ember_vars)}")
print(f"  PPI (ICT Infrastructure): {len(ppi_vars)}")
print(f"  Derived variables: {len([v for v in derived_vars if v in data.columns])}")

# Missing data analysis
print("\nMissing Data Analysis:")
missing = data.isnull().sum()
missing_pct = (missing / len(data) * 100).round(1)
missing_summary = pd.DataFrame({
    'Missing_Count': missing,
    'Missing_Pct': missing_pct
})
missing_summary = missing_summary[missing_summary['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)

print(f"\nVariables with missing data: {len(missing_summary)}/{len(data.columns)}")
print(f"\nTop 10 variables with most missing data:")
print(missing_summary.head(10).to_string())

# Coverage by country
print("\nData coverage by country:")
coverage = data.groupby('country').agg({
    'year': ['count', 'min', 'max']
}).round()
coverage.columns = ['Observations', 'First_Year', 'Last_Year']
print(coverage.to_string())

# ============================================================================
# SAVE DATASETS
# ============================================================================

print("\n" + "=" * 80)
print("SECTION 7: SAVING DATASETS")
print("=" * 80)

# Save full dataset
output_file = DATA_PROCESSED / "infrastructure_climate_dataset_full.csv"
data.to_csv(output_file, index=False)
print(f"✓ Full dataset saved: {output_file}")

# Save Stata format
output_stata = DATA_PROCESSED / "infrastructure_climate_dataset_full.dta"
data.to_stata(output_stata, write_index=False, version=118)
print(f"✓ Stata dataset saved: {output_stata}")

# Save data dictionary
print("\nCreating data dictionary...")
data_dict = pd.DataFrame({
    'Variable': data.columns,
    'Type': data.dtypes,
    'Missing_Count': data.isnull().sum(),
    'Missing_Pct': (data.isnull().sum() / len(data) * 100).round(1)
})

# Add source information
def get_source(col):
    if col in ['country', 'country_code', 'year', 'Tier']:
        return 'Identifier'
    elif col.startswith('Ember_'):
        return 'Ember Energy API'
    elif col.startswith('PPI_'):
        return 'World Bank PPI Database'
    elif col.endswith('_Log') or col.endswith('_norm') or col in ['Energy_Score', 'Governance_Index', 'Digital_Demand_Index', 'Trade_Openness']:
        return 'Derived Variable'
    elif col in list(wdi_indicator_names.values()):
        return 'World Bank WDI'
    elif col in list(wgi_indicator_names.values()):
        return 'World Bank WGI'
    else:
        return 'Unknown'

data_dict['Source'] = data_dict['Variable'].apply(get_source)

dict_file = DATA_PROCESSED / "data_dictionary.csv"
data_dict.to_csv(dict_file, index=False)
print(f"✓ Data dictionary saved: {dict_file}")

# Create summary statistics
print("\nCreating summary statistics...")
summary_stats = data.describe().T
summary_stats['missing_pct'] = (data.isnull().sum() / len(data) * 100).round(1)
summary_file = DATA_PROCESSED / "summary_statistics.csv"
summary_stats.to_csv(summary_file)
print(f"✓ Summary statistics saved: {summary_file}")

# ============================================================================
# COMPLETION MESSAGE
# ============================================================================

print("\n" + "=" * 80)
print("DATASET COMPILATION COMPLETE!")
print("=" * 80)

print(f"""
Your infrastructure investment dataset is ready!

Files created:
1. {output_file.name}
   - Full panel dataset ({len(data):,} observations, {len(data.columns)} variables)

2. {output_stata.name}
   - Stata format for econometric analysis

3. {dict_file.name}
   - Complete data dictionary with variable descriptions

4. {summary_file.name}
   - Summary statistics for all variables

Next steps:
1. Review the data dictionary to understand all variables
2. Check missing data patterns in your key variables
3. Consider additional data sources for:
   - ND-GAIN climate vulnerability/readiness scores
   - WRI Aqueduct water risk indicators
   - Climate Bonds Initiative green finance data
   - National carbon pricing policies

Key variables for your analysis:
- DV: PPI_ICT_Investment_Log (digital infrastructure investment)
- Climate C components: Energy_Score, Renewable_electricity_output_pct_total
- Controls: Governance_Index, GDP_Log, Digital_Demand_Index
- Environmental intensity: Ember_Intensity_* and Ember_Emissions_* variables

""")

print("=" * 80)
