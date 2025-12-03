# Adding Climate Readiness Data Sources

The compilation script is now ready to automatically process three additional data sources for your Climate C Index. Simply add the files to `data/raw/` and the script will detect and process them.

## 1. ND-GAIN Climate Readiness & Vulnerability

**What it is**: University of Notre Dame's Global Adaptation Initiative (ND-GAIN) Country Index measures climate vulnerability and readiness to improve resilience.

**Where to get it**: https://gain.nd.edu/our-work/country-index/download-data/

**File formats supported**: CSV or Excel

**What to name it**: Any filename containing "gain" or "GAIN"
- Examples: `ndgain_data.csv`, `GAIN_Index_2024.xlsx`, `climate_gain_scores.csv`

**What the script will extract**:
- Climate readiness scores
- Climate vulnerability scores
- All columns will be prefixed with `NDGAIN_`

**Variables added to your dataset**:
- `NDGAIN_Readiness` - Overall readiness score
- `NDGAIN_Vulnerability` - Overall vulnerability score
- Plus any sub-components available in the data

---

## 2. WRI Aqueduct Water Risk

**What it is**: World Resources Institute's Aqueduct tool measures water stress and scarcity by country.

**Where to get it**: https://www.wri.org/aqueduct/data

**File formats supported**: CSV or Excel

**What to name it**: Any filename containing "aqueduct"
- Examples: `aqueduct_40.csv`, `Aqueduct_water_risk.xlsx`, `wri_aqueduct_data.csv`

**What the script will extract**:
- Baseline water stress
- Water scarcity indicators
- Flooding risk
- All water-related risk columns

**Variables added to your dataset**:
- `Aqueduct_baseline_water_stress` (typical name)
- `Aqueduct_*` - All water risk indicators
- **Note**: Aqueduct data is typically country-level (not time-varying), so values will be constant across years for each country

---

## 3. Climate Bonds Initiative - Green Finance

**What it is**: Climate Bonds Initiative tracks green bond and sustainable finance issuance globally.

**Where to get it**:
- https://www.climatebonds.net/
- May require contacting CBI for access
- Look for "new makers" dataset or annual issuance data

**File formats supported**: CSV or Excel

**What to name it**: Any filename containing "climate" and "bond" OR "green" and "bond"
- Examples: `climate_bonds_newmakers.csv`, `green_bond_issuance.xlsx`, `climate_bonds_data_2024.csv`

**What the script will extract**:
- Green bond issuance amounts by country and year
- Number of green bonds issued
- Will aggregate to country-year level

**Variables added to your dataset**:
- `Green_Bond_Issuance_USD` - Annual green bond issuance (USD)
- `Green_Bond_Issuance_Log` - Log-transformed for regression
- `Green_Bond_Count` - Number of green bonds issued

---

## Quick Start

1. **Download the data files** from the sources above

2. **Place them in `data/raw/`** with appropriate filenames:
   ```
   data/raw/
   ├── Public_Participation_in_Infrastructure-2023-H1-Stata.dta  ✓ (already there)
   ├── ndgain_index_2024.csv                                      ← Add this
   ├── aqueduct_water_risk_4.0.csv                                ← Add this
   └── climate_bonds_newmakers_2024.xlsx                          ← Add this
   ```

3. **Run the compilation script**:
   ```bash
   python scripts/compile_infrastructure_dataset.py
   ```

4. **Check the output** - the script will report:
   - ✓ if each data source was found and processed
   - ○ if a data source was not found
   - Details on variables added

---

## Expected Output

When all three data sources are added, you'll see in the compilation:

```
================================================================================
SECTION 4: ND-GAIN CLIMATE READINESS & VULNERABILITY
================================================================================

Found ND-GAIN file: ndgain_index_2024.csv
✓ ND-GAIN data loaded: (3000, 25)
  ...
✓ ND-GAIN data processed: (450, 12)
  Countries: 30
  Years: 2005-2024

================================================================================
SECTION 5: WRI AQUEDUCT WATER RISK
================================================================================

Found Aqueduct file: aqueduct_water_risk_4.0.csv
✓ Aqueduct data loaded: (150, 40)
  ...
✓ Aqueduct data processed: (33, 15)
  Countries: 33

================================================================================
SECTION 6: CLIMATE BONDS INITIATIVE - GREEN FINANCE
================================================================================

Found Climate Bonds file: climate_bonds_newmakers_2024.xlsx
✓ Climate Bonds data loaded: (1200, 20)
  ...
✓ Climate Bonds data processed: (85, 5)
  Countries: 15
  Years: 2015-2024
  Total issuance: $45,000,000,000
```

---

## What If I Don't Have All Three?

**No problem!** The script works with whatever data you provide:

- ✅ **All three** → Complete Climate C Index
- ✅ **One or two** → Partial Climate C Index (still useful)
- ✅ **None** → Original dataset (WDI, WGI, Ember, PPI)

The script will automatically skip missing data sources and note them in the output.

---

## Troubleshooting

### "File not found" warning

**Cause**: The filename doesn't match the expected patterns

**Solution**: Rename your file to include keywords:
- ND-GAIN: Must contain "gain" (case-insensitive)
- Aqueduct: Must contain "aqueduct" (case-insensitive)
- Climate Bonds: Must contain "climate" + "bond" OR "green" + "bond"

### "Could not identify columns" warning

**Cause**: The data file has unexpected column names

**Solution**: The script tries common variations. If it fails:
1. Check the output - it shows what columns were found
2. Open an issue with the column names from your file
3. Or manually edit the script to add your column names to the detection lists

### Data looks wrong after merging

**Check**:
- ND-GAIN and Climate Bonds should vary by year
- Aqueduct is country-level only (same value across all years)
- Missing data is normal for some countries/years

---

## Questions?

Check the main README.md or open an issue on GitHub with:
- Which data source you're having trouble with
- The filename you're using
- The first few column names from your file
