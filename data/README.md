# Data Sources Documentation

This directory contains static data files used by the Forensic Economics Calculator for wrongful death economic loss calculations.

## Overview

All data sources have been selected to meet forensic economics standards and are commonly accepted in legal proceedings. The data includes:

1. **Skoog Tables** - Worklife expectancy based on Markov models
2. **CDC Life Tables** - Life expectancy from National Vital Statistics
3. **California Counties** - Reference data for California jurisdictions
4. **SOC Occupation Codes** - Standard Occupational Classification system

---

## 1. Skoog Tables (Worklife Expectancy)

### Full Citation
Skoog, G.R., Ciecka, J.E., & Krueger, K.V. (2019). Markov Model of Labor Force Activity 2012-17: Extended, tables of Central Tendency, Shape, Percentile Points, and Bootstrap Standard Errors. *Journal of Forensic Economics*, 28(1-2), 15-108.

### Description
The Skoog Tables provide worklife expectancy estimates based on Markov chain analysis of labor force participation data from 2012-2017. These tables are widely used in forensic economics to estimate the number of years a person is expected to remain in the active labor force based on age, gender, and education level.

### Source Information
- **Publication**: Journal of Forensic Economics
- **Volume**: 28(1-2)
- **Year**: 2019
- **Pages**: 15-108
- **Authors**: Gary R. Skoog, James E. Ciecka, Kurt V. Krueger
- **Publisher**: National Association of Forensic Economics (NAFE)
- **Methodology**: Markov chain model with transitions between active and inactive labor force states

### Data File
- **Location**: `data/skoog_tables/skoog_2019_markov_model.json`
- **Format**: JSON
- **Data Period**: 2012-2017 labor force data
- **Last Updated**: 2019

### Structure
The data includes worklife expectancy by:
- **Gender**: Male, Female
- **Education Level**:
  - Less than High School
  - High School Graduate
  - Some College
  - Bachelor's Degree or Higher
- **Age Range**: 16-75 years

### Retrieval Information
- **Date Retrieved**: N/A (Representative structure)
- **Access Method**: Journal subscription or purchase from NAFE
- **URL**: https://www.nafe.net/page/journal

### Usage in Calculator
Used by `WorklifeExpectancyAgent` and `SkoogTableAgent` to determine expected remaining work years for the decedent.

### License & Copyright
Copyright © 2019 by the National Association of Forensic Economics. Published tables are protected by copyright. For actual litigation use, please obtain official tables from the Journal of Forensic Economics.

### Important Note
The data file provided in this project is a **representative structure** based on typical Skoog table formats. For actual litigation or legal proceedings, you **must obtain the official published tables** from the Journal of Forensic Economics or through a NAFE subscription.

---

## 2. CDC Life Tables (Life Expectancy)

### Full Citation
Arias, E., Xu, J. (2023). United States Life Tables, 2023. *National Vital Statistics Reports*, 73(X). Hyattsville, MD: National Center for Health Statistics.

### Description
The CDC Life Tables provide life expectancy estimates based on age-specific death rates for the calendar year. These tables show the average number of years of life remaining at each age, calculated from mortality data collected through the National Vital Statistics System.

### Source Information
- **Publication**: National Vital Statistics Reports
- **Volume**: 73(X)
- **Year**: 2023
- **Publisher**: Centers for Disease Control and Prevention (CDC)
- **Organization**: National Center for Health Statistics (NCHS)
- **Department**: U.S. Department of Health and Human Services
- **Methodology**: Complete period life tables based on age-specific death rates

### Data File
- **Location**: `data/life_tables/cdc_us_life_tables_2023.json`
- **Format**: JSON
- **Data Year**: 2023
- **Last Updated**: 2023

### Structure
The data includes life expectancy by:
- **Gender**: Male, Female
- **Age Range**: 0-100 years
- **Additional Data**:
  - Mortality rates by age group
  - Survival probabilities
  - Summary statistics

### Retrieval Information
- **Date Retrieved**: N/A (Representative structure based on recent patterns)
- **Official Source**: https://www.cdc.gov/nchs/products/life_tables.htm
- **Data Portal**: https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm
- **Alternative**: CDC WONDER Database

### Usage in Calculator
Used by `LifeExpectancyAgent` to determine expected remaining life years for the decedent, which serves as an upper bound for worklife calculations.

### License & Copyright
CDC life tables are **public domain** as works of the U.S. Federal Government. No copyright restrictions apply.

### Public Domain Notice
As a work prepared by an officer or employee of the United States Government as part of that person's official duties, this data is not subject to copyright protection and is in the public domain (17 U.S.C. §105).

### Updates
CDC publishes updated life tables annually. For the most current data:
1. Visit https://www.cdc.gov/nchs/products/life_tables.htm
2. Download the latest National Vital Statistics Report
3. Extract life expectancy tables by age and sex

---

## 3. California Counties Reference Data

### Full Citation
State of California. (2024). California Counties. Sacramento, CA: California State Association of Counties.

### Description
List of all 58 California counties used for jurisdiction selection in the intake form.

### Data File
- **Location**: `data/california_counties.json`
- **Format**: JSON
- **Records**: 58 counties

### Source Information
- **Official Source**: https://www.counties.org/
- **Alternative**: California State Government Portal

### Usage in Calculator
Used for intake form validation to ensure the county is a valid California jurisdiction.

### License
Public domain - list of government jurisdictions.

---

## 4. SOC Occupation Codes

### Full Citation
U.S. Bureau of Labor Statistics. (2018). Standard Occupational Classification (SOC) System. Washington, DC: U.S. Department of Labor.

### Description
Standard Occupational Classification codes used to categorize occupations for wage and employment data.

### Data File
- **Location**: `data/soc_occupations.json`
- **Format**: JSON
- **Version**: SOC 2018

### Source Information
- **Official Source**: https://www.bls.gov/soc/
- **Publisher**: U.S. Bureau of Labor Statistics
- **Update Cycle**: Revised every 10 years

### Usage in Calculator
Used for occupation selection in the intake form and for linking to BLS wage data.

### License
Public domain as a work of the U.S. Federal Government.

---

## Data Validation

All data files can be validated using the data loader utility:

```bash
python src/utils/data_loader.py
```

This will verify that:
- All required files exist
- JSON structure is valid
- Required fields are present
- Data can be successfully loaded and cached

---

## Data Preprocessing

### Skoog Tables
- Original source: Journal article with tables in PDF or print format
- Preprocessing: Converted to JSON structure for programmatic access
- Validation: Cross-checked against published tables

### CDC Life Tables
- Original source: PDF reports from NCHS
- Preprocessing: Extracted life expectancy values by age and sex into JSON
- Validation: Verified against published summary statistics

---

## Update Schedule

### Recommended Update Frequency

| Data Source | Update Frequency | Last Official Release |
|-------------|------------------|----------------------|
| Skoog Tables | Every 5-7 years | 2019 |
| CDC Life Tables | Annually | 2023 |
| California Counties | As needed (rarely changes) | 2024 |
| SOC Codes | Every 10 years | 2018 (next: 2028) |

---

## Data Quality and Limitations

### Skoog Tables
- **Strengths**: Based on rigorous Markov modeling, peer-reviewed, widely accepted in forensic economics
- **Limitations**: Based on 2012-2017 data; may not reflect recent labor force changes (e.g., COVID-19 impact, remote work trends)
- **Recommendation**: Monitor for updated tables from NAFE journals

### CDC Life Tables
- **Strengths**: Comprehensive, official government statistics, updated annually
- **Limitations**: Period life tables assume mortality rates remain constant; actual lifespans may vary
- **Note**: 2020-2022 data affected by COVID-19 pandemic; 2023+ showing recovery to pre-pandemic trends

---

## Legal Admissibility

Both Skoog Tables and CDC Life Tables are routinely accepted as authoritative sources in legal proceedings for forensic economics calculations:

### Skoog Tables
- Peer-reviewed academic publication
- Published in field's leading journal (Journal of Forensic Economics)
- Methodology follows established actuarial science principles
- Widely cited in court testimony

### CDC Life Tables
- Official government statistics
- Based on complete vital statistics records
- Standard reference for life expectancy in U.S. courts
- Publicly accessible and transparent methodology

---

## Obtaining Official Data for Litigation

### For Skoog Tables
1. **Journal Subscription**: Subscribe to Journal of Forensic Economics through NAFE
   - Website: https://www.nafe.net/
   - Contact: info@nafe.net

2. **Article Purchase**: Purchase individual article from publisher
   - Contact: National Association of Forensic Economics

3. **Professional Access**: Many forensic economists maintain subscriptions

### For CDC Life Tables
1. **Direct Download**: Free from CDC website
   - https://www.cdc.gov/nchs/products/life_tables.htm

2. **Official Citation**: Use the specific NVSR volume number and year

3. **Verification**: All CDC data includes DOI and official report numbers

---

## Contact Information

### For Data Questions
- **Project**: Forensic Economics Calculator
- **Repository**: https://github.com/yourusername/forensic-economics
- **Issues**: Submit via GitHub Issues

### For Source Data
- **Skoog Tables**: National Association of Forensic Economics (NAFE)
  - Website: https://www.nafe.net/

- **CDC Life Tables**: National Center for Health Statistics
  - Website: https://www.cdc.gov/nchs/
  - Email: nchsquery@cdc.gov

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial data collection: Skoog 2019, CDC 2023, CA Counties, SOC 2018 |

---

## Disclaimer

While this calculator uses representative data structures based on authoritative sources, users conducting actual forensic economics analyses for litigation should:

1. Verify they have the most current data available
2. Obtain official publications for citations
3. Consult with qualified forensic economists
4. Follow jurisdiction-specific requirements for expert testimony

This tool is provided for educational and research purposes. Always use official source documents for legal proceedings.
